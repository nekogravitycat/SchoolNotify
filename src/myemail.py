import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
from src import basic
from src.unilog import log


def send(recipients: list, subject: str, content_base: str, unsub_sch: str = "") -> None:
	""" Send emails to recipients in the list, contain unsubscribing link if "unsub_sch" is provided

	:param recipients: list of recipients
	:param subject: subject of mail
	:param content_base: content_base of mail
	:param unsub_sch: school to unsubscribe (optional, attach unsubscribing link if provided)
	"""

	content_all: str = content_base

	try:
		with smtplib.SMTP(host="smtp.office365.com", port=587) as smtp:
			smtp.ehlo()
			smtp.starttls()
			smtp.login(os.environ.get("smtp_account"), os.environ.get("smtp_password"))

			list_len: int = len(recipients)
			count: int = 1

			from_addr: str = formataddr(("SchoolNotify", os.environ.get("smtp_account")), "utf-8")

			try:
				for r in recipients:
					msg = MIMEMultipart()
					msg["from"] = from_addr
					msg["to"] = r
					msg["subject"] = subject

					if unsub_sch:
						content_all = f'{content_base}點擊 <a href="{basic.unsub_link(r, unsub_sch)}">這裡</a> 來退訂此服務'

					msg.attach(MIMEText(content_all, "html"))
					smtp.send_message(msg)
					print(f"({count}/{list_len}) email sent: {r} {subject}")
					count += 1

			except Exception as ex:
				log(f"Email Sending Error: {r}\n{ex}\n")

	except Exception as e:
		log(f"SMTP Error: {e}")
