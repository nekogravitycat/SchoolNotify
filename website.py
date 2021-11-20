import os
import flask
import threading
import hashlib
import string
import random
from replit import db
import myemail
import mydb


app = flask.Flask("")


base: str = "https://SchoolNotify.nekogravitycat.repl.co"

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

  print(f"Ask to sub: {email}, {school}")

  if(email == "" or school == ""):
    print("Bad flask.request: no email or school")
    flask.abort(400, "請提供電子郵件和學校\nNo email adderss or school provided")

  if(not myemail.is_vaild(email)):
    print("Invaild email address")
    flask.abort(400, "無效的電子郵件\nInvaild email address")

  if(mydb.token.exist(school, email)):
    print("Already subscribed")
    return "您已訂閱至此服務\nYou've already subscribed to this service"

  if(mydb.ask.exist(school, email)):
    print("Already sent email")
    return "一封驗證電子郵件先前已送出，請至收件夾查收或是等 15 分鐘以再次發送\nThe verification email has been sent before, go check your inbox or wait for 15 minutes to send again"

  token: str = "".join(random.choices(string.ascii_uppercase + string.digits, k = 6)) #generates a six-characters-long token
  hyperlink: str = verify_link(email, school, token)

  content: str = f"點擊以下連結以完成電子郵件認證<br>Click the following link to complete email verification:<br><a href={hyperlink}>{hyperlink}</a><br><br>連結有效期限為 5 分鐘<br>The link will be vaild for 5 minutes"

  if(myemail.send([email], r"Please verify your email", content, True)):
    mydb.ask.set(school, email, mydb.timestamp.get() + ";" + token)
    print(f"Passed: {school}, {token}")
    return f"一封驗證電子郵件已送出至 {email}\nA verification email has been sent to {email}"
  
  else:
    print(f"Passed: {token}, failed to send email")
    return "目前無法發送電子郵件，請稍後再試\nFailed to send email, please try again later"


@app.route("/verify")
def ver():
  email: str = flask.request.args.get("email", default = "", type = str)
  school: str = flask.request.args.get("school", default = "", type = str)
  token: str = flask.request.args.get("token", default = "", type = str)

  print(f"Verify: {email}, {school}, {token}")
  
  if(email == "" or school == "" or token == ""):
    print("Bad flask.request")
    flask.abort(400, "無效的請求\nBad flask.request")

  if(mydb.token.exist(school, email)):
    print("Already subscribed")
    return "您已訂閱至此服務\nWhoohoo! You've already subscribed to this service"

  if((not mydb.ask.exist(school, email)) or (token != mydb.ask.get(school, email).split(";")[1])):
    print("Invalid email or token")
    flask.abort(403, "無效的電子郵件或令牌（或是驗證連結已失效，需再次請求訂閱）\nInvalid email or token (or the verification link has expired and needs to ask for subscribe again)")

  mydb.token.set(school, email, token)
  mydb.ask.delete(school, email)
  
  print("Successfully subscribed!\n")
  return "成功訂閱！\nSuccessfully subscribed!"


@app.route("/unsub-ask")
def unsub_ask():
  return flask.render_template("unsub.html")


@app.route("/unsub")
def unsub():
  email: str = flask.request.args.get("email", default = "", type = str)
  school: str = flask.request.args.get("school", default = "", type = str)
  token: str = flask.request.args.get("token", default = "", type = str)

  print(f"Unsub: {email}, {school}, {token}")

  if(email == "" or school == "" or token == ""):
    print("Bad flask.request")
    flask.abort(400, "無效的請求\nBad flask.request")

  if((not mydb.token.exist(school, email)) or token != mydb.token.get(school, email)):
    print("Invaild email or token")
    flask.abort(403, "無效的電子郵件或令牌\nInvalid email or token")

  mydb.token.delete(school, email)
  print("Successfully unsubscribed!\n")
  return "成功取消訂閱！\nSuccessfully unsubscribed!"


@app.route("/uptimebot")
def uptime():
  if(flask.request.args.get("token", default = "", type = str) != os.environ["uptimerobot_token"]):
    return "Hello, visitor!"

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
    print(f"flask.request cleared:\n{cleared}")


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

  if(token == ""):
    return flask.redirect("/login")

  elif(token != os.environ["db_token"]):
    return flask.redirect("/login?try-again=1") 

  else:
    ls: str = ""
    
    for k in db.keys():
      ls += f"{k} : {db[k]}<br>"

    return ls


def run():
  app.run(host = '0.0.0.0', port = 8080)


def alive():
  t = threading.Thread(target = run)
  t.start()