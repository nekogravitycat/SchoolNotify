from flask import Flask, request, render_template
from threading import Thread
from replit import db
import myemail
import rollingcode

app = Flask("")
timestamp: str = "A"


def sub_link(email: str) -> str:
  return f"https://SchoolNotify.nekogravitycat.repl.co/sub?email={email}"


def verify_link(email: str, password:str) -> str:
  return f"https://SchoolNotify.nekogravitycat.repl.co/verify?email={email}&key={password}"


def unsub_ask_link(email: str, password:str = "") -> str:
  if password == "":
    password = db[f"email_{email}"]
    
  return f"https://SchoolNotify.nekogravitycat.repl.co/unsub-ask?email={email}&key={password}"


@app.route("/")
def home():
  return render_template("sub.html")


@app.route("/sub")
def sub():
  email: str = request.args.get("email", default = "", type = str)

  if email == "":
   return "Email arg cannot be empty"

  if f"email_{email}" in db.prefix("email"):
    return "You've already subscribed to this service"

  if f"ask_{email}" in db.prefix("ask"):
    return "The verification email has been sent before, go check your inbox or wait for 15mins to send again"

  password: str = rollingcode.random_str(6)
  print(f"Ask to sub: {email}, Pass: {password}")

  hyperlink: str = verify_link(email, password)

  content: str = f"Click the following link to complete email verification:<br><a href={hyperlink}>{hyperlink}</a>"

  if myemail.send([email], r"Please verify your email", content, True) == True:
    db[f"ask_{email}"] = timestamp + ";" + password
    return f"A verification email has been sent to {email}, go check it!"
  
  else:
    return "Failed to send email, please try again later."


@app.route("/verify")
def ver():
  email: str = request.args.get("email", default = "", type = str)
  password: str = request.args.get("key", default = "", type = str)

  print(f"Verify: {email}, {password}")
  
  if email == "" or password == "":
    print("Bad request")
    return "Bad request"

  if f"email_{email}" in db.prefix("email"):
    return "You've already subscribed to this service"
  
  if f"ask_{email}" not in db.prefix("ask"):
    print("Email not found")
    return "Email not found"

  if password != db[f"ask_{email}"].split(";")[1]:
    print("Wrong password")
    return "Wrong password"

  db[f"email_{email}"] = password
  del db[f"ask_{email}"]
  print("Successfully subscribed!\n")
  return "Successfully subscribed!"


@app.route("/unsub-ask")
def unsub_ask():
  return render_template("unsub.html")


@app.route("/unsub")
def unsub():
  email: str = request.values.get("email")
  password: str = request.values.get("key")

  print(f"Unsub: {email}, {password}")

  if email == "" or password == "":
    print("Bad request")
    return "Bad request"
  
  if f"email_{email}" not in db.prefix("email"):
    print("Email not found")
    return "Email not found"

  if password != db[f"email_{email}"]:
    print("Wrong password")
    return "Wrong password"

  del db[f"email_{email}"]
  print("Successfully unsubscribed!\n")
  return "Successfully unsubscribed!"


@app.route("/uptimebot")
def uptime():
  global timestamp

  if timestamp == "A":
    ClearAsk("B")
    timestamp = "B"

  elif timestamp == "B":
    ClearAsk("C")
    timestamp = "C"

  elif timestamp == "C":
    ClearAsk("A")
    timestamp = "A"

  print(f"Current timestamp = {timestamp}\n")
  return "Hello, uptimerobot!"


def ClearAsk(target: str):
  print("Request cleared:")
  for a in db.prefix("ask"):
    if db[a].split(";")[0] == target:
      print(a[4:])
      del db[a]
  print()


key: str = rollingcode.random_str(10)
key_next = rollingcode.random_str(10)


#Provide the passcode showen in the console after loading the page for first time
@app.route("/db")
def ShowDB():
  print(rollingcode.key_next)
  
  password: str = request.args.get("key", default = "", type = str)
  verified: bool = password == rollingcode.key

  rollingcode.roll()

  if verified:
    ls: str = ""
    for k in db.keys():
      ls += f"{k} : {db[k]}<br>"
    return ls
  
  else:
    return "Wrong password"


def run():
  app.run(host = '0.0.0.0', port = 8080)


def alive():
  t = Thread(target = run)
  t.start()