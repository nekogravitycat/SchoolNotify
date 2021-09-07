#crummy.com/software/BeautifulSoup/bs4/doc/

import os #for replit
import requests
from bs4 import BeautifulSoup

import email.message
import smtplib

page_to_crawl = 1
result = [] #storing Announcement()


class Announcement:
  def __init__(self, link, title, date):
    self.link = link
    self.title = title
    self.date = date

  def detail(self):
    return f"{str(self.link)}\n{str(self.title)}\n{str(self.date)}"

  def html(self):
    return f'<a href="{self.link}">{self.title}</a> {self.date}'


for i in range(1, page_to_crawl + 1):
  header_ = { "User-Agent" : os.environ['User-Agent'] }
  response = requests.get(f"http://www.{os.environ['host']}/files/501-1000-1001-{i}.php?Lang=zh-tw", headers = header_)

  response.encoding = response.apparent_encoding

  soup = BeautifulSoup(response.text, "html.parser")
  soup.encoding = response.encoding

  #row_01 & row_02 appears alternately, including all information we need
  #in a row there'll be three <td>, first one has the <div> which contains the hyperlink of the article and the title while other two contain the source and the date

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
    date = table_list[2].text.strip()

    result.append(Announcement(link, title, date))


for r in result:
  print(r.detail() + "\n")


send_email = False

if send_email:
  msg = email.message.EmailMessage()
  msg["From"] = os.environ["account"]
  msg["To"] = os.environ["email"]
  msg["Subject"] = "School Announcements Test"

  content = ""
  for r in result:
    content += r.html()
    content += "<br><br>"

  #msg.set_content("")
  msg.add_alternative(content, subtype = "html")

  server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
  server.login(os.environ["account"], os.environ["password"])
  server.send_message(msg)
  server.close()


print("done!")
