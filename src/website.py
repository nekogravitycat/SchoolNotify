"""
All routes start with gravitycat.tw/admin/ are protected by Cloudflare Access
"""

import os
import flask
import threading
import string
import random
from src import myemail, basic, database as db
from src.unilog import log

app: flask.Flask = flask.Flask("")
app.config["JSON_AS_ASCII"] = False


def main():
	log("website start!")


def show(title: str, content: str, icon: str = "") -> str:
	""" Show a message using message page template

	:param title: message title
	:param content: message content
	:param icon: icon of message (optional)
	:return: message page
	"""

	return flask.render_template("message.html", title=title, content=content.replace("\n", "<br>"), icon=icon)


def sub_page_error(title: str, msg: str) -> str:
	""" Show error message when something went wrong during subscribing process

	:param title: error title
	:param msg: error message
	:return: subscription page containing error message
	"""

	return flask.render_template("sub.html", pop_type="error", pop_title=title, pop_msg=msg)


def clear_ask(timestamp: str) -> None:
	""" Clear subscribe request with the given timestamp

	:param timestamp: timestamp to find and clear
	"""

	for uid in list(db.ask.list_asks()):
		if db.ask.get(uid).timestamp == timestamp:
			log(f"request cleared: {db.ask.get(uid).info()}")
			db.ask.delete(uid)


@app.route("/", methods=["POST", "GET"])
def home() -> str:
	# for GET method
	if flask.request.method == "GET":
		return flask.render_template("sub.html")

	# for POST method
	email: str = flask.request.form["email"]
	school: str = flask.request.form["school"]

	log(f"Ask to sub: {flask.request.headers.get('X-Forwarded-For')}, {email}, {school}")

	if not email or not school:
		log("Bad flask.request: no email or school")
		return sub_page_error("不完整的資訊", "請確認輸入的網址中包含完整的資訊")

	if not db.schools.exists(school):
		log("Invalid school id")
		return sub_page_error("無效的學校代碼", "請重新確認填寫的學校代碼是否正確")

	if db.user.exists(school, email):
		log("Already subscribed")
		return sub_page_error("已訂閱", "您已訂閱至此服務")

	if db.ask.exists_school_email(school, email):
		log("Already sent email")
		return sub_page_error("請進行身分驗證", "一封驗證電子郵件先前已送出，請至收件夾查收或是等 15 分鐘以再次發送")

	# generates a 6-characters-long token and 12-characters-long uid
	token: str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
	uid: str = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
	hyperlink: str = basic.verify_link(uid)

	content: str = f"點擊以下連結以完成電子郵件認證<br><a href={hyperlink}>{hyperlink}</a><br><br>連結有效期限為 5 分鐘。若您並未要求此動作，請忽略這封郵件"

	email_thread = threading.Thread(target=myemail.send, args=([email], r"請驗證您的電子郵件", content))
	email_thread.start()

	record = db.ask.AskRecord(
		school=school,
		email=email,
		timestamp=db.ask.now_timestamp,
		token=token
	)
	db.ask.add(uid, record)
	log(f"Passed: {record.info()}")
	return flask.render_template(
		"sub.html",
		email=email,
		school=school,
		again="1",
		pop_type="ok",
		pop_title="請進行身分驗證",
		pop_msg="一封驗證電子郵件已送出，請查收",
	)


@app.route("/verify")
def verify() -> str:
	uid: str = flask.request.args.get("uid", default="", type=str)

	log(f"Verify: {flask.request.headers.get('X-Forwarded-For')}, {uid}")

	if not uid:
		log("Bad flask.request")
		return show("身分驗證：無效的請求", "請確認輸入的網址中包含完整的資訊")

	if not db.ask.exists(uid):
		log("Invalid email or token")
		return show("身分驗證：無效的資料", "無效的資料（或是驗證連結已失效，需再次請求訂閱）")

	record = db.ask.get(uid)
	db.user.add(record.school, record.email, record.token)
	db.ask.delete(uid)

	log(f"Successfully subscribed: {record.info()}")
	return show("成功訂閱！", "您已成功訂閱至此服務，感謝您的使用！", "circle-check")


@app.route("/unsub", methods=["POST", "GET"])
def unsub() -> str:
	# for GET method
	if flask.request.method == "GET":
		school: str = flask.request.args.get("school", default="", type=str)
		return flask.render_template("unsub.html", school=db.schools.get_name(school))

	# for POST method
	email: str = flask.request.form["email"]
	school: str = flask.request.form["school"]
	token: str = flask.request.form["token"]

	log(f"Unsub: {flask.request.headers.get('X-Forwarded-For')}, {email}, {school}, {token}")

	if not email or not school or not token:
		log("Bad request")
		return flask.render_template("unsub.html", state="bad_request")

	if not db.user.exists(school, email):
		log("Invalid email or token")
		return flask.render_template("unsub.html", state="already_unsub")

	if token != db.user.get_token(school, email):
		return flask.render_template("unsub.html", state="invalid_token")

	db.user.delete(school, email)
	log("Successfully unsubscribed")
	return flask.render_template("unsub.html", state="succeed")


@app.route("/uptime")
def uptime() -> str:
	# verify the bot
	token: str = flask.request.args.get("bot", default="", type=str)
	if token != os.environ.get("uptimerobot_token"):
		return show(
			"You found me!",
			"Hello, visitor! This page is built for a service called UptimeRobot. The bot will visit here every 5 mins, "
			"triggering some special functions!",
			"circle-check",
		)

	# main function
	if db.ask.now_timestamp == "A":
		clear_ask("B")
		db.ask.now_timestamp = "B"

	elif db.ask.now_timestamp == "B":
		clear_ask("C")
		db.ask.now_timestamp = "C"

	elif db.ask.now_timestamp == "C":
		clear_ask("A")
		db.ask.now_timestamp = "A"

	return "Hello, uptimerobot!"


@app.route("/api/sch")
def api_school() -> flask.Response:
	return flask.jsonify({sch_id: db.schools.info[sch_id].name for sch_id in db.schools.info})


@app.route("/api/icon.png")
def icon_file() -> flask.Response:
	return flask.send_file(r"assets/icon.png")


@app.route("/admin")
def admin() -> str | flask.Response:
	log(f"access /admin: {flask.request.headers.get('X-Forwarded-For')}")
	return flask.render_template("admin.html")


@app.route("/admin/spr", methods=["POST", "GET"])
def supporter() -> str | flask.Response:
	log(f"access /admin/spr: {flask.request.headers.get('X-Forwarded-For')}")
	# for GET method
	if flask.request.method == "GET":
		return flask.render_template("supporter.html")

	# for POST method
	sch_id: str = flask.request.form["id"]
	name: str = flask.request.form["name"]
	url: str = flask.request.form["url"]
	uid: str = flask.request.form["uid"]
	latest_date = flask.request.form["latest_date"]
	latest_id = flask.request.form["latest_id"]

	if not db.schools.is_legal_name(sch_id):
		return flask.render_template(
			"supporter.html",
			pop_title="School ID is invalid",
			pop_msg="The School ID contains illegal characters",
		)

	if db.schools.exists(sch_id):
		return flask.render_template(
			"supporter.html",
			pop_title="School ID is invalid",
			pop_msg="The School ID already exists",
		)

	log(f"School_add: \n id={sch_id} \n url={url} \n uid={uid} \n latest_date={latest_date} \n latest_id={latest_id} \n")

	sch_info = db.schools.Sch(name=name, url=url, uid=uid)
	db.schools.add_school(sch_id, sch_info)

	db.info.set_info(sch_id, "date", latest_date)

	if latest_id:
		db.info.set_info(sch_id, "id", latest_id)
		
	else:
		db.info.set_info(sch_id, "id", "0")

	return flask.render_template("supporter.html", pop_title="Succeed", pop_msg="Succeed!", pop_type="ok")


@app.route("/github")
def github_redirect():
	return flask.redirect(r"https://github.com/nekogravitycat/SchoolNotify")


main()
