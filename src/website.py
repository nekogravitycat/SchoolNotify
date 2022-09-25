"""
All routes start with nekogc.com/admin/ are protected by Cloudflare Access
"""

import os
import flask
import threading
import string
import random
from src import myemail, database as db
from src.unilog import log

app: flask.Flask = flask.Flask("")
app.config["JSON_AS_ASCII"] = False

base: str = "https://sn.nekogc.com"


def main():
	log("website start!")
	db.schools.read_schools()


def verify_link(email: str, school: str, token: str) -> str:
	""" Generate a verification link for user

	:param email: user's email
	:param school: user's school
	:param token: user's token
	:return: verification link
	"""

	return f"{base}/verify?email={email}&school={school}&token={token}"


def unsub_link(email: str, school: str, token: str = "") -> str:
	""" Generate an unsubscribe link for user

		:param email: user's email
		:param school: user's school
		:param token: user's token (optional, will fetch from database by default)
		:return: unsubscribe link
		"""

	if not token:
		token = db.user.get_key(school, email)

	return f"{base}/unsub?email={email}&school={school}&token={token}"


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

	cleared: str = ""

	for a in db.ask.list_keys():
		if db.myredis.get_key(a).split(";")[0] == timestamp:
			cleared += f"{a}\n"
			db.myredis.delete_key(a)

	if len(cleared) > 0:
		log(f"request cleared:\n{cleared}")


@app.route("/", methods=["POST", "GET"])
def home() -> str:
	# for GET method
	if flask.request.method == "GET":
		return flask.render_template("sub.html")

	# for POST method
	email: str = flask.request.form["email"]
	school: str = flask.request.form["school"]

	log(f"Ask to sub: {email}, {school}")

	if not email or not school:
		log("Bad flask.request: no email or school")
		return sub_page_error("不完整的資訊", "請確認輸入的網址中包含完整的資訊")

	if not db.schools.exists(school):
		log("Invalid school id")
		return sub_page_error("無效的學校代碼", "請重新確認填寫的學校代碼是否正確")

	if db.user.exists(school, email):
		log("Already subscribed")
		return sub_page_error("已訂閱", "您已訂閱至此服務")

	if db.ask.exists(school, email):
		log("Already sent email")
		return sub_page_error("請進行身分驗證", "一封驗證電子郵件先前已送出，請至收件夾查收或是等 15 分鐘以再次發送")

	# generates a six-characters-long token
	token: str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
	hyperlink: str = verify_link(email, school, token)

	content: str = f"點擊以下連結以完成電子郵件認證<br><a href={hyperlink}>{hyperlink}</a><br><br>連結有效期限為 5 分鐘。若您並未要求此動作，請忽略這封郵件"

	email_thread = threading.Thread(target=myemail.send, args=([email], r"請驗證您的電子郵件", content))
	email_thread.start()

	db.ask.set_key(school, email, f"{db.timestamp.get_key()};{token}")
	log(f"Passed: {school}, {token}")
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
	email: str = flask.request.args.get("email", default="", type=str)
	school: str = flask.request.args.get("school", default="", type=str)
	token: str = flask.request.args.get("token", default="", type=str)

	log(f"Verify: {email}, {school}, {token}")

	if not email or not school or not token:
		log("Bad flask.request")
		return show("身分驗證：無效的請求", "請確認輸入的網址中包含完整的資訊")

	if db.user.exists(school, email):
		log("Already subscribed")
		return show("成功訂閱！", "您已成功訂閱至此服務，感謝您的使用！", "circle-check")

	if (not db.ask.exists(school, email)) or (token != db.ask.get_key(school, email).split(";")[1]):
		log("Invalid email or token")
		return show("身分驗證：無效的資料", "無效的電子郵件或令牌（或是驗證連結已失效，需再次請求訂閱）")

	db.user.set_key(school, email, token)
	db.ask.delete_key(school, email)

	log("Successfully subscribed")
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

	log(f"Unsub: {email}, {school}, {token}")

	if not email or not school or not token:
		log("Bad request")
		return flask.render_template("unsub.html", state="bad_request")

	if not db.user.exists(school, email):
		log("Invalid email or token")
		return flask.render_template("unsub.html", state="already_unsub")

	if token != db.user.get_key(school, email):
		return flask.render_template("unsub.html", state="invalid_token")

	db.user.delete_key(school, email)
	log("Successfully unsubscribed")
	return flask.render_template("unsub.html", state="succeed")


@app.route("/uptime")
def uptime() -> str:
	# verify the bot
	token: str = flask.request.args.get("bot", default="", type=str)
	if token != os.environ["uptimerobot_token"]:
		return show(
			"You found me!",
			"Hello, visitor! This page is built for a service called UptimeRobot. The bot will visit here every 5 mins, "
			"triggering some special functions!",
			"circle-check",
		)

	# main function
	timestamp: str = db.timestamp.get_key()

	if timestamp == "A":
		clear_ask("B")
		db.timestamp.set_key("B")

	elif timestamp == "B":
		clear_ask("C")
		db.timestamp.set_key("C")

	elif timestamp == "C":
		clear_ask("A")
		db.timestamp.set_key("A")

	return "Hello, uptimerobot!"


@app.route("/api/sch")
def api_school() -> flask.Response:
	res: dict = {sch_id: db.schools.info[sch_id].name for sch_id in db.schools.info}
	return flask.jsonify(res)


@app.route("/api/school_info.json")
def school_info_file() -> flask.Response:
	return flask.send_file(r"assets/school_info.json")


@app.route("/api/icon.png")
def icon_file() -> flask.Response:
	return flask.send_file(r"assets/icon.png")


@app.route("/admin")
def admin() -> str | flask.Response:
	# main function
	return flask.render_template("admin.html")


@app.route("/admin/db")
def show_db() -> str | flask.Response:
	# main function
	return flask.render_template("db.html")


@app.route("/admin/db/edit", methods=["POST", "GET"])
def edit_db() -> str | flask.Response:
	# for GET method
	if flask.request.method == "GET":
		return flask.render_template("db_edit.html")

	# for POST method
	key: str = flask.request.form["key"]
	value: str = flask.request.form["value"]
	method: str = flask.request.form["method"]

	res: dict = db.operate.edit_key(method, key, value)
	return flask.render_template(
		"db_edit.html",
		pop_type=res["status"],
		pop_title=res["title"],
		pop_msg=res["msg"],
	)


@app.route("/admin/spr", methods=["POST", "GET"])
def supporter() -> str | flask.Response:
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

	if not db.operate.is_legal_name(sch_id):
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

	db.info.set_key(sch_id, "date", latest_date)

	if latest_id:
		db.info.set_key(sch_id, "id", latest_id)
		
	else:
		db.info.set_key(sch_id, "id", "0")

	return flask.render_template("supporter.html", pop_title="Succeed", pop_msg="Succeed!", pop_type="ok")


@app.route("/admin/api/db")
def api_db() -> flask.Response:
	res: dict = {key: db.myredis.get_key(key) for key in db.myredis.keys()}

	return flask.jsonify(res)


@app.route("/admin/log.txt")
def logs_file() -> str | flask.Response:
	return flask.send_file(r"logs.txt") if os.path.exists(r"logs.txt") else "No logs yet."


@app.route("/github")
def github_redirect():
	return flask.redirect(r"https://github.com/nekogravitycat/SchoolNotify")


main()
