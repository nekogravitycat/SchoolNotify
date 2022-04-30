import os
import flask
import threading
import hashlib
import string
import random
from myredis import db
import myemail
import mydb
import schools
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

def show(title: str, content, icon="") -> str:
	return flask.render_template("message.html", title=title, content=content.replace("\n", "<br>"), icon=icon)

def sub_page_error(title: str, msg: str):
	return flask.render_template("sub.html", pop_type="error", pop_title=title, pop_msg=msg)


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
		return sub_page_error("不完整的資訊", "請確認輸入的網址中包含完整的資訊")

	if(not myemail.is_vaild(email)):
		log("Invaild email address")
		return sub_page_error("無效的電子郵件", "請重新確認填寫的電子郵件是否正確")

	if(not schools.is_valid(school)):
		log("Invaild school id")
		return sub_page_error("無效的學校代碼", "請重新確認填寫的學校代碼是否正確")
	
	if(mydb.token.exist(school, email)):
		log("Already subscribed")
		return sub_page_error("已訂閱", "您已訂閱至此服務")

	if(mydb.ask.exist(school, email)):
		log("Already sent email")
		return sub_page_error("請進行身分驗證", "一封驗證電子郵件先前已送出，請至收件夾查收或是等 15 分鐘以再次發送")

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
	#verifying the bot
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
		if(db.get(a).split(";")[0] == target):
			cleared += f"{a[4:]}\n"
			db.delete(a)
			
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
	#verifying user
	token: str = flask.request.cookies.get("token")
	if(not token):
		return flask.redirect("/login")
	elif(token != os.environ["db_token"]):
		return flask.redirect("/login?w=1")

	#main function
	return flask.render_template("db.html")


@app.route("/api/db", methods=["POST", "GET"])
def AIP_DB():
	#verifying user
	token: str = flask.request.cookies.get("token")
	if(not token):
		return {"state":"token_is_empty"}
	elif(token != os.environ["db_token"]):
		return {"state":"token_is_invaild"}

	#main function
	data: dict = {}

	for key in db.keys_iter():
		data.update({key : db.get(key)})

	return flask.jsonify(data)


@app.route("/db/sys")
def ShowRunDB():
	data: dict = {}
	data.update({"timestamp" : db["timestamp"]})

	for key in db.keys_iter():
		if("latest" in key):
			data.update({key : db.get(key)})

	return flask.render_template("db.html", data=data)



@app.route("/db/edit", methods = ["POST", "GET"])
def EditDB():
	#verifying user
	token: str = flask.request.cookies.get("token")
	if(not token):
		return flask.redirect("/login")
	elif(token != os.environ["db_token"]):
		return flask.redirect("/login?w=1")

	#For GET method
	if(flask.request.method == "GET"):
		return flask.render_template("db_edit.html")
		
	#For POST method
	key: str = flask.request.form["key"]
	value: str = flask.request.form["value"]
	method: str = flask.request.form["method"]
	
	method_vaild: bool = (method == "delete") or ((method in ["edit", "add"]) and value)
		
	if(not key or not method_vaild):
		return flask.render_template("db_edit.html", pop_title="Bad request", pop_msg="method is not vaild")

	if(method == "edit"):
		if(key not in db.keys_iter()):
			return flask.render_template("db_edit.html", pop_title="Cannot perfrom the method", pop_msg="Key does not exist")
			
		db.set(key, value)
		
	elif(method == "add"):
		if(key in db.keys_iter()):
			return flask.render_template("db_edit.html", pop_title="Cannot perfrom the method", pop_msg="Key already exists")
			
		if(not re.match(r"^[\w-]+$", key)):
			return flask.render_template("db_edit.html", pop_title="Cannot perfrom the method", pop_msg="Key name is illegle")
			
		db.set(key, value)

	elif(method == "delete"):
		if(key not in db.keys_iter()):
			return flask.render_template("db_edit.html", pop_title="Cannot perfrom the method", pop_msg="Key does not exist")
			
		db.delete(key)
		
	return flask.render_template("db_edit.html", pop_title="Successed", pop_msg="Successed!", pop_type="ok")


@app.route("/spr", methods = ["POST", "GET"])
def supporter():
	#verifying user
	token: str = flask.request.cookies.get("token")
	if(not token):
		return flask.redirect("/login")
	elif(token != os.environ["db_token"]):
		return flask.redirect("/login?w=1")

	#for get method
	if(flask.request.method == "GET"):
		return flask.render_template("supporter.html")
	
	#for post method
	id: str = flask.request.form["id"]
	url: str = flask.request.form["url"]
	uid: str = flask.request.form["uid"]
	latest_date = flask.request.form["latest_date"]
	latest_id = flask.request.form["latest_id"]

	if(not mydb.is_leagal(id)):
		return flask.render_template("supporter.html", pop_title="School ID is invalid", pop_msg="The School ID contains illeagal characters")

	if(schools.is_valid(id)):
		return flask.render_template("supporter.html", pop_title="School ID is invalid", pop_msg="The School ID already exists")
	
	log(f"School_add: \n id={id} \n url={url} \n uid={uid} \n latest_date={latest_date} \n latest_id={latest_id} \n")
	
	schools.add(id, url, uid)
	mydb.info.set(id, "date", latest_date)
	
	if(latest_id):
		mydb.info.set(id, "id", latest_id)
	else:
		mydb.info.set(id, "id", "0")
		
	return flask.render_template("supporter.html", pop_title="Successed", pop_msg="Successed!", pop_type="ok")


def run():
	app.run(host = "0.0.0.0", port = 8080)


def alive():
	t = threading.Thread(target = run)
	t.start()
