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

def sub_link(email: str, school: str) -> str:
  return f"{base}/sub?email={email}&school={school}"

def verify_link(email: str, school:str, token:str) -> str:
  return f"{base}/verify?email={email}&school={school}&token={token}"

def unsub_ask_link(email: str, school: str, token:str = "") -> str:
  if token == "":
    token = mydb.token.get(school, email)
  return f"{base}/unsub-ask?email={email}&school={school}&token={token}"


@app.route("/")
def home():
  return flask.render_template("sub.html")


@app.route("/sub")
def sub():
  email: str = flask.request.args.get("email", default = "", type = str)
  school: str = flask.request.args.get("school", default = "", type = str)

  log(f"Ask to sub: {email}, {school}")
  if(email == "" or school == ""):
    log("Bad flask.request: no email or school")
    
    return show("請提供電子郵件和學校", "不完整的資訊")

  if(not myemail.is_vaild(email)):
    log("Invaild email address")
    return show("無效的電子郵件", "無效的電子郵件")

  if(mydb.token.exist(school, email)):
    log("Already subscribed")
    return show("您已訂閱至此服務", "已訂閱")

  if(mydb.ask.exist(school, email)):
    log("Already sent email")
    return show("一封驗證電子郵件先前已送出，請至收件夾查收或是等 15 分鐘以再次發送", "請進行身分驗證")

  token: str = "".join(random.choices(string.ascii_uppercase + string.digits, k = 6)) #generates a six-characters-long token
  hyperlink: str = verify_link(email, school, token)

  content: str = f"點擊以下連結以完成電子郵件認證<br><a href={hyperlink}>{hyperlink}</a><br><br>連結有效期限為 5 分鐘"

  email_thread = threading.Thread(target=myemail.send, args=([email], r"請驗證您的電子郵件", content, True))
  email_thread.start()
  mydb.ask.set(school, email, mydb.timestamp.get() + ";" + token)
  log(f"Passed: {school}, {token}")
  return show(f"一封驗證電子郵件已送出至 {email}，請查收", "請進行身分驗證")


@app.route("/verify")
def ver():
  email: str = flask.request.args.get("email", default = "", type = str)
  school: str = flask.request.args.get("school", default = "", type = str)
  token: str = flask.request.args.get("token", default = "", type = str)

  log(f"Verify: {email}, {school}, {token}")
  
  if(email == "" or school == "" or token == ""):
    log("Bad flask.request")
    return show("無效的請求", "無效的請求")

  if(mydb.token.exist(school, email)):
    log("Already subscribed")
    return show("您已訂閱至此服務", "已訂閱")

  if((not mydb.ask.exist(school, email)) or (token != mydb.ask.get(school, email).split(";")[1])):
    log("Invalid email or token")
    return show("無效的電子郵件或令牌（或是驗證連結已失效，需再次請求訂閱）", "無效的資料")

  mydb.token.set(school, email, token)
  mydb.ask.delete(school, email)
  
  log("Successfully subscribed")
  return show("成功訂閱！", "成功訂閱！")


@app.route("/unsub-ask")
def unsub_ask():
  return flask.render_template("unsub.html")


@app.route("/unsub")
def unsub():
  email: str = flask.request.args.get("email", default = "", type = str)
  school: str = flask.request.args.get("school", default = "", type = str)
  token: str = flask.request.args.get("token", default = "", type = str)

  log(f"Unsub: {email}, {school}, {token}")

  if(email == "" or school == "" or token == ""):
    log("Bad request")
    return show("無效的請求", "無效的請求")

  if((not mydb.token.exist(school, email)) or token != mydb.token.get(school, email)):
    log("Invaild email or token")
    return show("無效的電子郵件或令牌", "無效的資料")

  mydb.token.delete(school, email)
  log("Successfully unsubscribed")
  return show("成功取消訂閱！", "成功取消訂閱！")


@app.route("/uptimebot")
def uptime():
  if(flask.request.args.get("token", default = "", type = str) != os.environ["uptimerobot_token"]):
    return show("Hello, visitor!", "You found me!")

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
    log(f"request cleared: {cleared}")


@app.route("/login", methods = ["POST", "GET"])
def login():
  if(flask.request.method == "POST"):
    token = flask.request.form["token"]

    if(token != ""):
      resp = flask.make_response(flask.redirect("/db"))
      sha: str = hashlib.sha256(token.encode()).hexdigest()
      resp.set_cookie("token", sha)
      return resp
  
  else:
    token: str = flask.request.cookies.get("token")

    if(token == os.environ["db_token"]):
      return flask.redirect("/db")

    else:
      return flask.render_template("login.html")


@app.route("/db")
def ShowDB():
  token: str = flask.request.cookies.get("token")

  if(token == "" or token is None):
    return flask.redirect("/login")

  elif(token != os.environ["db_token"]):
    return flask.redirect("/login?try-again=1") 

  else:
    ls: str = ""
    
    for k in db.keys():
      ls += f"{k} : {db[k]}<br>"

    return ls


@app.route("/db/sys")
def ShowRunDB():
  ls:str = ""

  for k in sorted(db.keys()):
    if("latest" in k):
      ls += f"{k} : {db[k]}<br>"

  return ls


@app.route("/db/edit", methods = ["POST", "GET"])
def EditDB():
  token: str = flask.request.cookies.get("token")
  if(token == "" or token is None):
    return flask.redirect("/login")
  elif(token != os.environ["db_token"]):
    return flask.redirect("/login?try-again=1")

  if(flask.request.method == "GET"):
    return flask.render_template("db.html")
    
  key: str = flask.request.form["key"]
  value: str = flask.request.form["value"]
  action: str = flask.request.form["action"]

  action_vaild: bool = False
  if(action == "delete"):
    action_vaild = True
  elif(action in ["edit", "add"] and value != "" and not value is None):
    action_vaild = True
    
  if((key == "") or (key is None) or not action_vaild):
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

  else:
    if(key not in db.keys()):
      return flask.render_template("db.html", msg="Key does not exist")
    del db[key]
    
  return flask.render_template("db.html", msg="Successed!")


def show(msg: str, title: str = "") -> str:
  msg.replace("\n", "<br>")
  if(title != ""):
    title.replace("\n", "<br>")
    return flask.render_template("message.html", title=title, msg=msg)
  else:
    return flask.render_template("message.html", msg=msg)


def run():
  app.run(host = '0.0.0.0', port = 8080)


def alive():
  t = threading.Thread(target = run)
  t.start()