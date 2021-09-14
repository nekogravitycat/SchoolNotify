#crummy.com/software/BeautifulSoup/bs4/doc
#schedule.readthedocs.io/en/stable
#uptimerobot.com

import os
from replit import db
import time
import schedule
import requests
import bs4
import email.message
import smtplib
import website

website.alive() #for uptimerobot

#db["latest_date"] = "2021-09-13" #for testing
#db["latest_title"] = "Test title" #for testing


class Announcement:
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


def Job():
  print(f"runned at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} UTC+0\n")
  
  next: bool = True
  page: int = 1
  result: list = [] #storing a list of Announcement()

  while next:
    try_times: int = 3 #times to try when request is failed
    ex: Exception

    while try_times >= 0:
      try:
        response: requests.Response = requests.get(f"http://{os.environ['school']}/files/501-1000-1001-{page}.php?Lang=zh-tw", headers = header_)

        response.encoding = response.apparent_encoding

        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        soup.encoding = response.encoding

        row: bs4.element.ResultSet = soup.find_all("tr", class_ = ["row_01", "row_02"])

        for r in row:
          #hyperlink of the article
          division: bs4.element.Tag = r.select_one("div")
          anchor: bs4.element.Tag = division.select_one("a")

          link: str = anchor["href"]

          #title, source (unwanted), and date
          table: bs4.element.ResultSet = r.select("td")
          table_list: list = []

          for td in table:
            table_list.append(td)

          title: str = table_list[0].text.strip()
          #source = table_list[1].text.strip() #unwanted
          date: time.struct_time = time.strptime(table_list[2].text.strip(), "%Y-%m-%d")

          if date >= time.strptime(db["latest_date"], "%Y-%m-%d") and title != db["latest_title"]:
            result.append(Announcement(link, title, date))
            
          else:
            next = False
            break

      except Exception as e:
        ex = e
        try_times -= 1
        print(f"request failed: {try_times} retry times remaining, wait 1 min to try again")
        print(repr(e) + "\n")
        time.sleep(60) #sleep for 1 minute to try again

      else:
        break

    if try_times < 0:
      ErrorReport(repr(ex))
      print("request failed: tried to many times\n")
      return

    page += 1


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


  send_email: bool = True

  if send_email:
    subject: str = f"School Announcements ({from_date[5:]} ~ {db['latest_date'][5:]})".replace("-", "/")
    content: str = ""
    
    if is_empty:
      content = f"No new announcemts<br><br>"

    else:
      for r in result:
        content += r.html()
        content += "<br><br>" #<br> = new line in html

    content += f"form: {from_date}<br>latest: {db['latest_date']}"
    EmailSend(os.environ["recipients"].split(";"), subject, content, True)

  print("done! waiting for next round!\n")


def ErrorReport(e: str):
  subject: str = "School Notify: An Error Occurred"
  content: str = f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} UTC+0\n\nExpectionn:\n{e}"
  EmailSend(os.environ["email_admin"], subject, content, False)


def EmailSend(to: list, subject: str, content:str, is_html: bool):
  try_times: int = 3 #times to try when smtp is failed
  ex: Exception

  while try_times >= 0:
    try:
      server: smtplib.SMTP_SSL = smtplib.SMTP_SSL(os.environ["smtp_server"], 465)
      server.login(os.environ["smtp_account"], os.environ["smtp_password"])

      list_len: int = len(to)
      count: int = 1

      for r in to:
        msg: email.message.EmailMessage = email.message.EmailMessage()
        msg["From"] = os.environ["smtp_account"]
        msg["To"] = r
        msg["Subject"] = subject

        if is_html:
          msg.add_alternative(content, subtype = "html") #for html

        else:
          msg.set_content(content)

        server.send_message(msg)

        print(f"email sent: {count}/{list_len}")
        count += 1
      
      server.close()
      print()

    except Exception as e:
      try_times -= 1
      print(f"smtp failed: {try_times} retry times remaining, wait 1 min to try again")
      print(repr(e) + "\n")
      time.sleep(60) #sleep for 1 minute to try again

    else:
      break
  
  if try_times < 0:
    #don't call ErrorReport() here or it'll create an infinite loop
    print("smtp failed: tried to many times\n")
    return


def ScheduleRun():
  #replit uses UTC+0, so schedule the tasks 8 hours earlier, using 24-hour clock
  scheduler: schedule.Scheduler = schedule.Scheduler()

  time_to_send: str = "10:00"

  scheduler.every().monday.at(time_to_send).do(Job)
  #scheduler.every().tuesday.at(time_to_send).do(Job)
  #scheduler.every().wednesday.at(time_to_send).do(Job)
  scheduler.every().thursday.at(time_to_send).do(Job)
  #scheduler.every().friday.at(time_to_send).do(Job)

  print("tasks scheduled")

  while True:
    scheduler.run_pending()
    time.sleep(1)

ScheduleRun()
#Job() #for testing, remember to set "send_email" into False