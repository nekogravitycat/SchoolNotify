import os
import flask
import threading
import hashlib
import string
import random
from replit import db
import myemail
import mydb
from unilog import log
import re


app = flask.Flask("")
base: str = "https://sn.nekogc.com"


def verify_link(email: str, school:str, token:str) -> str:
	return f"{base}/verify?email={email}&school={school}&token={token}"

def unsub_link(email: str, school: str, token:str = "") -> str:
	if(not token):
		token = mydb.token.get(school, email)
	return f"{base}/unsub?email={email}&school={school}&token={token}"


@app.route("/", methods = ["POST", "GET"])
def home():
	#for GET method
	if(flask.request.method == "GET"):
		return flask.render_template("sub.html")

	#for POST method
	email: str = flask.request.form["email"]
	school: str = flask.request.form["school"]
	
	log(f"Ask to sub: {email}, {school}")
	
	if(not email or not school):
		log("Bad flask.request: no email or school")
		return flask.render_template("sub.html", pop_type="error", pop_title="不完整的資訊", pop_msg="請確認輸入的網址中包含完整的資訊")

	if(not myemail.is_vaild(email)):
		log("Invaild email address")
		return flask.render_template("sub.html", pop_type="error", pop_title="無效的電子郵件", pop_msg="請重新確認填寫的電子郵件是否正確")

	if(mydb.token.exist(school, email)):
		log("Already subscribed")
		return flask.render_template("sub.html", pop_type="error", pop_title="已訂閱", pop_msg="您已訂閱至此服務")

	if(mydb.ask.exist(school, email)):
		log("Already sent email")
		return flask.render_template("sub.html", pop_type="error", pop_title="請進行身分驗證", pop_msg="一封驗證電子郵件先前已送出，請至收件夾查收或是等 15 分鐘以再次發送")

	#generates a six-characters-long token
	token: str = "".join(random.choices(string.ascii_uppercase + string.digits, k = 6))
	hyperlink: str = verify_link(email, school, token)

	content: str = f"點擊以下連結以完成電子郵件認證<br><a href={hyperlink}>{hyperlink}</a><br><br>連結有效期限為 5 分鐘。若您並未要求此動作，請忽略這封郵件"
	
	email_thread = threading.Thread(target=myemail.send, args=([email], r"請驗證您的電子郵件", content))
	email_thread.start()

	mydb.ask.set(school, email, mydb.timestamp.get() + ";" + token)
	log(f"Passed: {school}, {token}")
	return flask.render_template("sub.html", email=email, school=school, again="1", pop_type="ok", pop_title="請進行身分驗證", pop_msg=f"一封驗證電子郵件已送出，請查收")


@app.route("/verify")
def ver():
	email: str = flask.request.args.get("email", default = "", type = str)
	school: str = flask.request.args.get("school", default = "", type = str)
	token: str = flask.request.args.get("token", default = "", type = str)

	log(f"Verify: {email}, {school}, {token}")
	
	if(not email or not school or not token):
		log("Bad flask.request")
		return show("身分驗證：無效的請求", "請確認輸入的網址中包含完整的資訊")

	if(mydb.token.exist(school, email)):
		log("Already subscribed")
		return show("成功訂閱！", "您已成功訂閱至此服務，感謝您的使用！", "circle-check")

	if((not mydb.ask.exist(school, email)) or (token != mydb.ask.get(school, email).split(";")[1])):
		log("Invalid email or token")
		return show("身分驗證：無效的資料", "無效的電子郵件或令牌（或是驗證連結已失效，需再次請求訂閱）")

	mydb.token.set(school, email, token)
	mydb.ask.delete(school, email)
	
	log("Successfully subscribed")
	return show("成功訂閱！", "您已成功訂閱至此服務，感謝您的使用！", "circle-check")


@app.route("/unsub", methods = ["POST", "GET"])
def unsub():
	#for GET method
	if(flask.request.method == "GET"):
		return flask.render_template("unsub.html")

	#for POST method
	email: str = flask.request.form["email"]
	school: str = flask.request.form["school"]
	token: str = flask.request.form["token"]

	log(f"Unsub: {email}, {school}, {token}")

	if(not email or not school or not token):
		log("Bad request")
		return flask.render_template("unsub.html", state="bad_request")

	if(not mydb.token.exist(school, email)):
		log("Invaild email or token")
		return flask.render_template("unsub.html", state="already_unsub")

	if(token != mydb.token.get(school, email)):
		return flask.render_template("unsub.html", state="invalid_token")

	mydb.token.delete(school, email)
	log("Successfully unsubscribed")
	return flask.render_template("unsub.html", state="succeed")


@app.route("/uptimebot")
def uptime():
	#For verifying
	token: str = flask.request.args.get("token", default = "", type = str)
	
	if(token != os.environ["uptimerobot_token"]):
		return show("You found me!", "Hello, visitor! This page is built for a service called UptimeRobot. The bot will visit here every 5 mins, triggering some special functions!", "circle-check")

	#The main part
	timestamp: str = mydb.timestamp.get()
	
	if(timestamp == "A"):
		ClearAsk("B")
		mydb.timestamp.set("B")
	
	elif(timestamp == "B"):
		ClearAsk("C")
		mydb.timestamp.set("C")
	
	elif(timestamp == "C"):
		ClearAsk("A")
		mydb.timestamp.set("A")
		
	return "Hello, uptimerobot!"


def ClearAsk(target: str):
	cleared: str = ""
	
	for a in mydb.ask.list():
		if(db[a].split(";")[0] == target):
			cleared += f"{a[4:]}\n"
			del db[a]
			
	if(len(cleared) > 0):
		log(f"request cleared:\n{cleared}")


@app.route("/login", methods = ["POST", "GET"])
def login():
	#For GET method
	if(flask.request.method == "GET"):
		token: str = flask.request.cookies.get("token")

		if(not token):
			return flask.render_template("login.html")
		
		elif(token != os.environ["db_token"]):
			return flask.render_template("login.html", wrong="1")
			
		return flask.redirect("/admin")

	#For POST method
	token = flask.request.form["token"]
	sha: str = hashlib.sha256(token.encode()).hexdigest()

	if(sha != os.environ["db_token"]):
		return flask.render_template("login.html", wrong="1")
	
	elif(token):
		resp = flask.make_response(flask.redirect("/admin"))
		resp.set_cookie("token", sha)
		return resp

	return flask.render_template("login.html", wrong="1")


@app.route("/admin")
def admin():
	token: str = flask.request.cookies.get("token")
	
	if(not token):
		return flask.redirect("/login")
		
	elif(token != os.environ["db_token"]):
		return flask.redirect("/login?w=1")

	return flask.render_template("admin.html")
		

@app.route("/db")
def ShowDB():
	token: str = flask.request.cookies.get("token")
	
	if(not token):
		return flask.redirect("/login")
		
	elif(token != os.environ["db_token"]):
		return flask.redirect("/login?w=1")
		
	ls: str = ""
		
	for k in sorted(db.keys()):
		ls += f"{k} : {db[k]}<br>"
		
	return ls + r"<style>:root{color-scheme:dark;}</style>"


@app.route("/db/sys")
def ShowRunDB():
	ls:str = ""
	
	for k in sorted(db.keys()):
		if("latest" in k):
			ls += f"{k} : {db[k]}<br>"
			
	return ls


@app.route("/db/edit", methods = ["POST", "GET"])
def EditDB():
	#For verifying
	token: str = flask.request.cookies.get("token")
	
	if(not token):
		return flask.redirect("/login")
		
	elif(token != os.environ["db_token"]):
		return flask.redirect("/login?w=1")

	#For GET method
	if(flask.request.method == "GET"):
		return flask.render_template("db.html")
		
	#For POST method
	key: str = flask.request.form["key"]
	value: str = flask.request.form["value"]
	action: str = flask.request.form["action"]
	
	action_vaild: bool = False
	action_vaild = (action == "delete")
	action_vaild = ((action in ["edit", "add"]) and (value != "") and (not value is None))
		
	if(not key or (not action_vaild)):
		return flask.render_template("db.html", msg="Bad request")

	if(action == "edit"):
		if(key not in db.keys()):
			return flask.render_template("db.html", msg="Key does not exist")
			
		db[key] = value
		
	elif(action == "add"):
		if(key in db.keys()):
			return flask.render_template("db.html", msg="Key already exists")
			
		if(not re.match(r"^[\w-]+$", key)):
			return flask.render_template("db.html", msg="Key name is illegle")
			
		db[key] = value

	#For the deleting action
	else:
		if(key not in db.keys()):
			return flask.render_template("db.html", msg="Key does not exist")
			
		del db[key]
		
	return flask.render_template("db.html", msg="Successed!")


def show(title: str, content, icon="") -> str:
	return flask.render_template("message.html", title=title, content=content.replace("\n", "<br>"), icon=icon)


def run():
	app.run(host = "0.0.0.0", port = 8080)


def alive():
	t = threading.Thread(target = run)
	t.start()
