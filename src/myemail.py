import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
from src import website
from src.unilog import log


def send(recipients: list, subject: str, content_base: str, unsub_sch: str = "") -> bool:
	""" Send emails to recipients in the list, contain unsubscribing link if "unsub_sch" is provided

	:param recipients: list of recipients
	:param subject: subject of mail
	:param content_base: content_base of mail
	:param unsub_sch: school to unsubscribe (optional, attach unsubscribing link if provided)
	:return: True if ran successfully, False if not
	"""

	content_all: str = content_base

	try:
		with smtplib.SMTP(host="smtp.office365.com", port=587) as smtp:
			smtp.ehlo()
			smtp.starttls()
			smtp.login(os.environ["smtp_account"], os.environ["smtp_password"])

			list_len: int = len(recipients)
			count: int = 1

			from_addr: str = formataddr(("SchoolNotify", os.environ["smtp_account"]), "utf-8")

			try:
				for r in recipients:
					msg = MIMEMultipart()
					msg["from"] = from_addr
					msg["to"] = r
					msg["subject"] = subject

					if unsub_sch:
						content_all = f'{content_base}點擊 <a href="{website.unsub_link(r, unsub_sch)}">這裡</a> 來退訂此服務'

					msg.attach(MIMEText(content_all, "html"))
					smtp.send_message(msg)
					log(f"email sent: {r} ({count}/{list_len})")
					count += 1

			except Exception as ex:
				log(f"Email Sending Error: {r}\n{ex}\n")

			log(f"{count}/{len(recipients)} Emails Sent: {subject}", True)

	except Exception as e:
		log(f"SMTP Error: {e}")
		return False

	return True
