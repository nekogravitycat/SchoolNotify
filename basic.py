import os
import time
import pyotp
from datetime import datetime, timezone, timedelta
import myemail
import mydb
import ischool
import schools
from unilog import log

test_mail: bool = False


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
	"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
}


def today() -> datetime.date:
	return datetime.now(timezone(timedelta(hours=8))).date()


def sys_msg() -> str:
	try:
		if(os.stat("sys_msg.txt").st_size == 0):
			return ""

		content: str = ""
		with open("sys_msg.txt", "r+") as f:
			content = f.read().replace("\n", "<br>")
			f.truncate(0)
			return f"～～系統公告～～<br>{content}<br><br>"
			
	except Exception as e:
		log(f"SYS_MSG Runtime Error: {e}", True)
		return ""


def push_email(school: str, result: list):
	is_empty: bool = len(result) == 0

	if(is_empty):
		log(f"No new announcemts for {school}\n")

	else:
		for r in result:
			log(r.detail() + "\n")

	if(len(mydb.token.list(school)) > 0):
		subject: str = f"{school} 學校公告 ({today().strftime('%m/%d')})".replace("-", "/")
		content: str = ""
		
		if(is_empty):
			content = f"尚無新公告<br><br>"

		else:
			for r in result:
				content += f"{r.html()}<br><br>"

		content += sys_msg()
		recipients: list = []

		if(test_mail):
			recipients.append(os.environ["email_admin"])
			
		else:
			perfix_len: int = len(school) + 7
			
			for re in mydb.token.list(school):
				recipients.append(re[perfix_len:])

		myemail.send(recipients, subject, content, school)

	else:
		log(f"The recipient list of {school} is empty", True)

	log("Done! Waiting for next round!")


def ShowResult(result: list):
	if(len(result) == 0):
		log("No new announcements")
	else:
		for re in result:
			log(re.detail())


ischool_info: list = ["date", "id"]


def run():
	for id in schools.info.keys():
		try:
			info: dict = schools.info[id]
			news: list = ischool.get_news(id, info["url"], info["uid"])
			push_email(id, news)
		except Exception as e:
			log(f"{id} Runtime Error: {e}", True)


def debug(school_ids = []):
	if(not school_ids):
		school_ids = schools.info.keys()
	for id in school_ids:
		info: dict = schools.info[id]
		mydb.memory.remember(id, ischool_info)
		ShowResult(ischool.get_news(id, info["url"], info["uid"]))
		mydb.memory.recall(id, ischool_info)
	

def verify_totp(code: str) -> bool:
	t = pyotp.TOTP(os.environ["totp"])
	return t.verify(code)