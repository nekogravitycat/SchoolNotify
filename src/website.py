import os
import flask
import threading
import hashlib
import string
import random
from datetime import date, timedelta
from src import myemail, mydb, schools
from src.myredis import db
from src.unilog import log


app: flask.Flask = flask.Flask("")
app.config["JSON_AS_ASCII"] = False

base: str = "https://sn.nekogc.com"


#return the login page if the token is invaild, and None if vaild
def verify(token: str) -> flask.Response:
	#empty token
	if(not token):
		return flask.redirect("/login")
	#wrong token
	elif(token != os.environ["db_token"]):
		return flask.redirect("/login?w=1")
	#vaild token (pass)
	return None


def verify_link(email: str, school:str, token:str) -> str:
	return f"{base}/verify?email={email}&school={school}&token={token}"

def unsub_link(email: str, school: str, token:str = "") -> str:
	if(not token):
		token = mydb.token.get(school, email)
	return f"{base}/unsub?email={email}&school={school}&token={token}"

def show(title: str, content, icon="") -> str:
	return flask.render_template("message.html", title=title, content=content.replace("\n", "<br>"), icon=icon)

def sub_page_error(title: str, msg: str) -> str:
	return flask.render_template("sub.html", pop_type="error", pop_title=title, pop_msg=msg)

def ClearAsk(target: str):
	cleared: str = ""
	
	for a in mydb.ask.list():
		if(db.get(a).split(";")[0] == target):
			cleared += f"{a[4:]}\n"
			db.delete(a)
			
	if(len(cleared) > 0):
		log(f"request cleared:\n{cleared}")


@app.route("/", methods = ["POST", "GET"])
def home() -> str:
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
def ver() -> str:
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
def unsub() -> str:
	#for GET method
	if(flask.request.method == "GET"):
		school: str = flask.request.args.get("school", default = "", type = str)
		return flask.render_template("unsub.html", school=schools.get_name(school))

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


@app.route("/uptime")
def uptime() -> str:
	#verify the bot
	token: str = flask.request.args.get("bot", default = "", type = str)
	if(token != os.environ["uptimerobot_token"]):
		return show("You found me!", "Hello, visitor! This page is built for a service called UptimeRobot. The bot will visit here every 5 mins, triggering some special functions!", "circle-check")

	#main function
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


@app.route("/login", methods = ["POST", "GET"])
def login() -> str:
	#for GET method
	if(flask.request.method == "GET"):
		#verify user
		result = verify(flask.request.cookies.get("token"))
		if(not result is None):
			return flask.render_template("/login.html")
			
		#main function
		return flask.redirect("/admin")

	#for POST method
	token = flask.request.form["token"]
	sha: str = hashlib.sha256(token.encode()).hexdigest()

	if(sha != os.environ["db_token"]):
		return flask.render_template("login.html", wrong="1")
	
	elif(token):
		resp = flask.make_response(flask.redirect("/admin"))
		resp.set_cookie("token", value = sha, expires = (date.today()+timedelta(days=7)))
		return resp

	return flask.render_template("login.html", wrong="1")


@app.route("/admin")
def admin() -> str:
	#verify user
	result = verify(flask.request.cookies.get("token"))
	if(not result is None):
		return result
		
	#main function
	return flask.render_template("admin.html")
		

@app.route("/db")
def ShowDB() -> str:
	#verify user
	result = verify(flask.request.cookies.get("token"))
	if(not result is None):
		return result
		
	#main function
	return flask.render_template("db.html")


@app.route("/db/edit", methods = ["POST", "GET"])
def EditDB() -> str:
	#verify user
	result = verify(flask.request.cookies.get("token"))
	if(not result is None):
		return result

	#for GET method
	if(flask.request.method == "GET"):
		return flask.render_template("db_edit.html")
		
	#for POST method
	key: str = flask.request.form["key"]
	value: str = flask.request.form["value"]
	method: str = flask.request.form["method"]
	
	res: dict = mydb.edit.cmd(method, key, value)
	return flask.render_template("db_edit.html", pop_type=res["status"], pop_title=res["title"], pop_msg=res["msg"])


@app.route("/spr", methods = ["POST", "GET"])
def supporter() -> str:
	#verify user
	result = verify(flask.request.cookies.get("token"))
	if(not result is None):
		return result

	#for GET method
	if(flask.request.method == "GET"):
		return flask.render_template("supporter.html")
	
	#for POST method
	id: str = flask.request.form["id"]
	name: str = flask.request.form["name"]
	url: str = flask.request.form["url"]
	uid: str = flask.request.form["uid"]
	latest_date = flask.request.form["latest_date"]
	latest_id = flask.request.form["latest_id"]

	if(not mydb.is_leagal(id)):
		return flask.render_template("supporter.html", pop_title="School ID is invalid", pop_msg="The School ID contains illeagal characters")

	if(schools.is_valid(id)):
		return flask.render_template("supporter.html", pop_title="School ID is invalid", pop_msg="The School ID already exists")
	
	log(f"School_add: \n id={id} \n url={url} \n uid={uid} \n latest_date={latest_date} \n latest_id={latest_id} \n")
	
	schools.add(id, url, uid, name)
	mydb.info.set(id, "date", latest_date)
	
	if(latest_id):
		mydb.info.set(id, "id", latest_id)
	else:
		mydb.info.set(id, "id", "0")
		
	return flask.render_template("supporter.html", pop_title="Successed", pop_msg="Successed!", pop_type="ok")


@app.route("/api/sch")
def API_School() -> flask.Response:
	res: dict = {}
	
	for id in schools.info:
		res.update({id : schools.info[id]["name"]})
		
	return flask.jsonify(res)


@app.route("/api/school_info.txt")
def API_School_Orig() -> flask.Response:
	return flask.send_file(r"assets/school_info.txt")


@app.route("/api/db")
def API_DB() -> flask.Response:
	res: dict = {}
	
	#verify user
	token: str = flask.request.cookies.get("token")
	
	#token empty
	if(not token):
		res = {"state":"token_is_empty"}
		
	#token wrong
	elif(token != os.environ["db_token"]):
		res = {"state":"token_is_invaild"}
		
	#token vaild (pass)
	else:
		for key in db.keys_iter():
			res.update({key : db.get(key)})

	return flask.jsonify(res)


@app.route("/api/icon.png")
def icon():
	return flask.send_file(f"assets/icon.png")
	

#the following functions are for testing porpuse
def run() -> None:
	app.run(host = "0.0.0.0", port = 8080)


def alive() -> None:
	t = threading.Thread(target = run)
	t.start()