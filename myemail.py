import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import website
import re


def is_vaild(email: str) -> bool:
  email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
  return email_regex.match(email) != None


#Retuen a boolean telling if the process ran successfully
def send(to: list, subject: str, content_base:str, is_html: bool, unsub_school:str = "") -> bool: #"to" parameter must be an list rather than a single string
  content_all: str = content_base

  with smtplib.SMTP(host="smtp.office365.com", port="587") as smtp:
    try:
      smtp.ehlo()
      smtp.starttls()
      smtp.login(os.environ["smtp_account"], os.environ["smtp_password"])

      list_len: int = len(to)
      count: int = 1

      for r in to:
        msg = MIMEMultipart()
        msg["from"] = os.environ["smtp_account"]
        msg["to"] = r
        msg["subject"] = subject

        if(unsub_school != ""):
          content_all = content_base + f'點擊 <a href="{website.unsub_ask_link(r, unsub_school)}">{"這裡"}</a> 來退訂此服務'

        else:
          content_all = content_base

        if(is_html):
          #msg.add_alternative(content_all, subtype = "html") #for html
          msg.attach(MIMEText(content_all, "html"))

        else:
          #msg.set_content(content_all)
          msg.attach(MIMEText(content_all))

        smtp.send_message(msg)

        print(f"email sent: {count}/{list_len}")
        count += 1
    
      return True

    except Exception as e:
      print("Error message: ", e)
      return False