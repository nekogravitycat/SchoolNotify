import os
import time
import email.message
import smtplib
import website


def send(to: list, subject: str, content_base:str, is_html: bool, append_unsub: bool = False) -> bool:
  try_times: int = 3 #times to try when smtp is failed
  ex: Exception

  content_all:str = content_base

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

        if append_unsub:
          content_all = content_base + f'Click <a href="{website.unsub_ask_link(r)}">{"here"}</a> to unsubscribe'

        else:
          content_all = content_base

        if is_html:
          msg.add_alternative(content_all, subtype = "html") #for html

        else:
          msg.set_content(content_all)

        server.send_message(msg)

        print(f"email sent: {count}/{list_len}")
        count += 1
      
      server.close()
      print()

      return True

    except Exception as e:
      try_times -= 1
      print(f"smtp failed: {try_times} retry times remaining, wait 1 sec to try again")
      print(repr(e) + "\n")
      time.sleep(1) #sleep for 1 second to try again
  
  if try_times < 0:
    #don't call ErrorReport() here or it'll create an infinite loop
    print("smtp failed: tried to many times\n")
    return False