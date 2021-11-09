import os
import time
from datetime import datetime, timezone, timedelta
import myemail
import mydb


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


header: dict = {
  "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
} #pretend to be a browser


def today() -> datetime.date:
  return datetime.now(timezone(timedelta(hours=8))).date()


def push_email(school: str, result: list):
  is_empty: bool = len(result) == 0

  if(is_empty):
    print("No new announcemts\n")

  else:
    for r in result:
      print(r.detail() + "\n")

  if(len(mydb.token.list(school)) > 0):
    subject: str = f"{school} 學校公告 ({today().strftime('%m/%d')})".replace("-", "/")
    content: str = ""
    
    if(is_empty):
      content = f"尚無新公告<br><br>"

    else:
      for r in result:
        content += r.html()
        content += "<br><br>" #<br> = new line in html

    recipients: list = []

    for re in mydb.token.list(school):
      recipients.append(re[11:])

    myemail.send(recipients, subject, content, True, school)

  else:
    print("Recipient list is empty\n")

  print("done! waiting for next round!\n")


def ErrorReport(e: str):
  subject: str = "School Notify: An Error Occurred"
  content: str = f"Time: {today()}\n\nExpectionn:\n{e}"
  myemail.send(os.environ["email_admin"], subject, content, False)


temp: dict = {}

class memory:
  def remember(school: str, info: list):
    for i in info:
      temp[i] = mydb.info.get(school, i)

  def recall(school: str, info: list):
    for i in info:
      mydb.info.set(school, i, temp[i])