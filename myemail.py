import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
import website
from unilog import log


#Retuen a boolean telling if the process ran successfully
#"to" parameter must be an list rather than a single string
def send(to: list, subject: str, content_base: str, unsub_sch: str = "") -> bool:
	content_all: str = content_base
	
	try:
		with smtplib.SMTP(host="smtp.office365.com", port=587) as smtp:
			smtp.ehlo()
			smtp.starttls()
			smtp.login(os.environ["smtp_account"], os.environ["smtp_password"])
			
			list_len: int = len(to)
			count: int = 1

			from_addr: str = formataddr(("SchoolNotify", os.environ["smtp_account"]), "utf-8")
			
			try:
				for r in to:
					msg = MIMEMultipart()
					msg["from"] = from_addr
					msg["to"] = r
					msg["subject"] = subject
			
					if(unsub_sch != ""):
						content_all = content_base + f'點擊 <a href="{website.unsub_link(r, unsub_sch)}">這裡</a> 來退訂此服務'
			
					msg.attach(MIMEText(content_all, "html"))
					smtp.send_message(msg)
					log(f"email sent: {r} ({count}/{list_len})")
					count += 1
					
			except Exception as ex:
				log(f"Email Sending Error: {r}\n{ex}\n")
			
			log(f"{len(to)} Emails Sent: {subject}", True)
			
	except Exception as e:
		log(f"SMTP Error: {e}")
		return False
	
	return True