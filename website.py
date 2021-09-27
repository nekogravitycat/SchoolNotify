import os
from flask import Flask, request, render_template, abort
from threading import Thread
from replit import db
import myemail
import rollingcode

app = Flask("")


def sub_link(email: str) -> str:
  return f"https://SchoolNotify.nekogravitycat.repl.co/sub?email={email}"

def verify_link(email: str, token:str) -> str:
  return f"https://SchoolNotify.nekogravitycat.repl.co/verify?email={email}&token={token}"

def unsub_ask_link(email: str, token:str = "") -> str:
  if token == "":
    token = db[f"email_{email}"]
  return f"https://SchoolNotify.nekogravitycat.repl.co/unsub-ask?email={email}&token={token}"


@app.route("/")
def home():
  return render_template("sub.html")


@app.route("/sub")
def sub():
  email: str = request.args.get("email", default = "", type = str)

  print(f"Ask to sub: {email}")

  if email == "":
    print("Bad request")
    abort(400, "No email adderss provided")

  if not myemail.is_vaild(email):
    print("Invaild email address")
    abort(400, "Invaild email address")

  if f"email_{email}" in db.prefix("email"):
    print("Already subscribed")
    return "You've already subscribed to this service"

  if f"ask_{email}" in db.prefix("ask"):
    print("Already sent email")
    return "The verification email has been sent before, go check your inbox or wait for 15mins to send again"

  token: str = rollingcode.random_str(6)

  hyperlink: str = verify_link(email, token)

  content: str = f"Click the following link to complete email verification:<br><a href={hyperlink}>{hyperlink}</a>"

  if myemail.send([email], r"Please verify your email", content, True) == True:
    db[f"ask_{email}"] = db["timestamp"] + ";" + token
    print(f"Passed: {token}")
    return f"A verification email has been sent to {email}, go check it!"
  
  else:
    print(f"Passed: {token}, failed to send email")
    return "Failed to send email, please try again later."


@app.route("/verify")
def ver():
  email: str = request.args.get("email", default = "", type = str)
  token: str = request.args.get("token", default = "", type = str)

  print(f"Verify: {email}, {token}")
  
  if email == "" or token == "":
    print("Bad request")
    abort(400, "Bad request")

  if f"email_{email}" in db.prefix("email"):
    print("Already subscribed")
    return "You've already subscribed to this service"

  if (f"ask_{email}" not in db.prefix("ask")) or token != db[f"ask_{email}"].split(";")[1]:
    print("Wrong email or token")
    abort(403, "Wrong email or token")

  db[f"email_{email}"] = token
  del db[f"ask_{email}"]
  print("Successfully subscribed!\n")
  return "Successfully subscribed!"


@app.route("/unsub-ask")
def unsub_ask():
  return render_template("unsub.html")


@app.route("/unsub")
def unsub():
  email: str = request.args.get("email", default = "", type = str)
  token: str = request.args.get("token", default = "", type = str)

  print(f"Unsub: {email}, {token}")

  if email == "" or token == "":
    print("Bad request")
    abort(400, "Bad request")

  if (f"email_{email}" not in db.prefix("email")) or token != db[f"email_{email}"]:
    print("Wrong email or token")
    abort(403, "Wrong email or token")

  del db[f"email_{email}"]
  print("Successfully unsubscribed!\n")
  return "Successfully unsubscribed!"


@app.route("/uptimebot")
def uptime():
  if request.args.get("token", default = "", type = str) != os.environ["uptimerobot_token"]:
    return "Hello, visitor!"

  if db["timestamp"] == "A":
    ClearAsk("B")
    db["timestamp"] = "B"

  elif db["timestamp"] == "B":
    ClearAsk("C")
    db["timestamp"] = "C"

  elif db["timestamp"] == "C":
    ClearAsk("A")
    db["timestamp"] = "A"
    
  print("UpTimeRobot visited")
  return "Hello, uptimerobot!"


def ClearAsk(target: str):
  cleared: str = ""

  for a in db.prefix("ask"):
      if db[a].split(";")[0] == target:
        cleared += f"{a[4:]}\n"
        del db[a]

  if len(cleared) > 0:
    print(f"Request cleared:\n{cleared}")


#Provide the passcode showen in the console after loading the page for first time
@app.route("/db")
def ShowDB():
  print(f"db token: {rollingcode.code_next}")
  
  token: str = request.args.get("token", default = "", type = str)
  verified: bool = token == rollingcode.code

  rollingcode.roll()

  if verified:
    ls: str = ""
    for k in db.keys():
      ls += f"{k} : {db[k]}<br>"
    return ls
  
  else:
    abort(403, "Wrong token")


def run():
  app.run(host = '0.0.0.0', port = 8080)


def alive():
  t = Thread(target = run)
  t.start()