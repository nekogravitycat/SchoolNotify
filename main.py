#crummy.com/software/BeautifulSoup/bs4/doc/

import os
from replit import db
import time
import requests
from bs4 import BeautifulSoup
import email.message
import smtplib

#db["latest_date"] = "2021-08-10" #for testing
result = [] #storing Announcement()s


class Announcement:
  def __init__(self, link, title, date):
    self.link = link #str
    self.title = title #str
    self.date = date #time.struct_time

  def detail(self):
    return f"{str(self.link)}\n{str(self.title)}\n{str(self.date_str())}"

  def html(self):
    return f'<a href="{str(self.link)}">{str(self.title)}</a> {str(self.date_str())}'

  def date_str(self):
    return time.strftime("%Y-%m-%d", self.date)


next = True
page = 1

while next:
  header_ = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
  } #pretend to be a browser
  response = requests.get(f"http://www.{os.environ['host']}/files/501-1000-1001-{page}.php?Lang=zh-tw", headers = header_)

  response.encoding = response.apparent_encoding

  soup = BeautifulSoup(response.text, "html.parser")
  soup.encoding = response.encoding

  row = soup.find_all("tr", class_ = ["row_01", "row_02"])

  for r in row:
    #hyperlink of the article
    division = r.select_one("div")
    anchor = division.select_one("a")

    link = anchor["href"]

    #title, source (unwanted), and date
    table = r.select("td")
    table_list = []

    for td in table:
      table_list.append(td)

    title = table_list[0].text.strip()
    #source = table_list[1].text.strip() #unwanted
    date = time.strptime(table_list[2].text.strip(), "%Y-%m-%d")
    if date > time.strptime(db["latest_date"], "%Y-%m-%d"):
      result.append(Announcement(link, title, date))
    else:
      next = False
      break
  
  page += 1


from_date = db['latest_date']
is_empty = len(result) == 0

if is_empty:
  print("No any new announcemt\n")

else:
  db["latest_date"] = result[0].date_str()

  for r in result:
    print(r.detail() + "\n")

print(f"From: {from_date}")
print(f"Latest date: {db['latest_date']}\n")


send_email = True

if send_email:
  content = ""
  
  if is_empty:
    content = f"No any new announcemt<br><br>"

  else:
    for r in result:
      content += r.html()
      content += "<br><br>" #<br> = new line in html

  content += f"form: {from_date}<br>latest: {db['latest_date']}"

  server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
  server.login(os.environ["account"], os.environ["password"])

  for r in os.environ["recipients"].split(";"): #split recipients with ;
    msg = email.message.EmailMessage()
    msg["From"] = os.environ["account"]
    msg["To"] = r
    msg["Subject"] = f"School Announcements ({from_date[5:]} ~ {db['latest_date'][5:]})".replace("-", "/")

    #msg.set_content("") #for plain text
    msg.add_alternative(content, subtype = "html") #for html

    server.send_message(msg)
  
  server.close()


print("done!")
