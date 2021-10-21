import os
from replit import db
import time
import myemail


class msg:
  def __init__(self, link: str, title: str, date: time.struct_time):
    self.link: str = link
    self.title: str = title
    self.date: time.struct_time = date

  def detail(self) -> str:
    return f"{self.link}\n{self.title}\n{self.date_str()}"

  def html(self) -> str:
    return f'<a href="{self.link}">{self.title}</a> {self.date_str()}'

  def date_str(self) -> str:
    return time.strftime("%Y-%m-%d", self.date)

  
header_: dict = {
  "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
} #pretend to be a browser


def push_email(school: str, result: list):
  from_date: str = db['latest_date']
  is_empty: bool = len(result) == 0

  if is_empty:
    print("No new announcemts\n")

  else:
    db["latest_date"] = result[0].date_str()
    db["latest_title"] = result[0].title

    for r in result:
      print(r.detail() + "\n")

  print(f"From: {from_date}")
  print(f"Latest date: {db['latest_date']}\n")

  if len(db.prefix("email")) > 0:
    subject: str = f"School Announcements ({from_date[5:]} ~ {db['latest_date'][5:]})".replace("-", "/")
    content: str = ""
    
    if is_empty:
      content = f"No new announcemts<br><br>"

    else:
      for r in result:
        content += r.html()
        content += "<br><br>" #<br> = new line in html

    recipients: list = []

    for re in db.prefix("email"):
      recipients.append(re[6:])

    myemail.send(recipients, subject, content, True, True)

  elif len(db.prefix("email")) == 0:
    print("Recipient list is empty\n")

  print("done! waiting for next round!\n")


def ErrorReport(e: str):
  subject: str = "School Notify: An Error Occurred"
  content: str = f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} UTC+0\n\nExpectionn:\n{e}"
  myemail.send(os.environ["email_admin"], subject, content, False)