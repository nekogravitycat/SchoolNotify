import os
import time
from datetime import datetime, timezone, timedelta
from src import myemail, mydb, ischool, schools
from src.unilog import log

test_mail: bool = False


class Msg:
	def __init__(self, link: str, title: str, date: time.struct_time) -> None:
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
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 "
	"Safari/537.36 "
}


def today() -> datetime.date:
	return datetime.now(timezone(timedelta(hours=8))).date()


def push_email(school: str, result: list) -> None:
	is_empty: bool = len(result) == 0

	if is_empty:
		log(f"No new announcements for {school}\n")

	else:
		for r in result:
			log(r.detail() + "\n")

	if len(mydb.Token.list(school)) > 0:
		subject: str = f"{school} 學校公告 ({today().strftime('%m/%d')})".replace("-", "/")
		content: str = ""

		if is_empty:
			content = f"尚無新公告<br><br>"

		else:
			for r in result:
				content += f"{r.html()}<br><br>"

		recipients: list = []

		if test_mail:
			recipients.append(os.environ["email_admin"])

		else:
			prefix_len: int = len(school) + 7

			for re in mydb.Token.list(school):
				recipients.append(re[prefix_len:])

		myemail.send(recipients, subject, content, school)

	else:
		log(f"The recipient list of {school} is empty", True)

	log("Done! Waiting for next round!")


def show_result(result: list) -> None:
	if len(result) == 0:
		log("No new announcements")

	else:
		for re in result:
			log(re.detail())


ischool_info: list = ["date", "id"]


def run() -> None:
	for ID in schools.info.keys():
		try:
			info: dict = schools.info[ID]
			news: list = ischool.get_news(ID, info["url"], info["uid"])
			push_email(ID, news)

		except Exception as e:
			log(f"{ID} Runtime Error: {e}", True)


def debug(school_ids: None | list = None) -> None:
	if not school_ids:
		school_ids = schools.info.keys()

	for ID in school_ids:
		info: dict = schools.info[ID]
		mydb.memory.remember(ID, ischool_info)
		show_result(ischool.get_news(ID, info["url"], info["uid"]))
		mydb.memory.recall(ID, ischool_info)
