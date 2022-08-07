import os
import time
from datetime import datetime, timezone, timedelta
from src import myemail, ischool, database as db
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
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
	"Chrome/100.0.4896.60 Safari/537.36 "
}


def today() -> datetime.date:
	""" Get the current date in GMT+8 """

	return datetime.now(timezone(timedelta(hours=8))).date()


def push_email(sch_id: str, news: list) -> None:
	""" Send emails to the subscribers of the school

	:param sch_id: id of school
	:param news: list of basic.Msg objects
	"""

	is_empty: bool = len(news) == 0

	if is_empty:
		log(f"No new announcements for {sch_id}\n")

	else:
		for n in news:
			log(n.detail() + "\n")

	# if there is at least one subscriber in the list
	if db.user.list_keys(sch_id):
		subject: str = f"{db.schools.get_name(sch_id)}學校公告 ({today().strftime('%m/%d')})".replace("-", "/")
		content: str = ""

		if is_empty:
			content = f"尚無新公告<br><br>"

		else:
			for n in news:
				content += f"{n.html()}<br><br>"

		recipients: list = []

		if test_mail:
			recipients.append(os.environ["email_admin"])

		else:
			# prefix format: schid_email_address@example.com
			prefix_len: int = len(sch_id) + 7

			for re in db.user.list_keys(sch_id):
				# re[prefix_len:] is for removing the prefix (schid_email_)
				recipients.append(re[prefix_len:])

		myemail.send(recipients, subject, content, sch_id)

	else:
		log(f"The recipient list of {sch_id} is empty", True)

	log("Done! Waiting for next round!")


def show_result(news: list) -> None:
	""" Show every news details in a list of basic.Msg objects

	:param news: list of basic.Msg objects
	"""

	if len(news) == 0:
		log("No new announcements")

	else:
		for re in news:
			log(re.detail())


def run() -> None:
	""" Run news-gathering for every school and send news emails to the subscribers """

	for sch_id in db.schools.info.keys():
		try:
			info: db.schools.Sch = db.schools.info[sch_id]
			news: list = ischool.get_news(sch_id, info.url, info.uid)
			push_email(sch_id, news)

		except Exception as e:
			log(f"{sch_id} Runtime Error: {e}", True)


def debug(sch_ids: list = None) -> None:
	""" Run news-gathering for given list of school ids

	:param sch_ids: list of school ids to run (optional, run every school's by default)
	"""

	ischool_info: list = ["date", "id"]

	if not sch_ids:
		sch_ids = db.schools.info.keys()

	for sch_id in sch_ids:
		info: dict = db.schools.info[sch_id]
		db.memory.remember_school(sch_id, ischool_info)
		show_result(ischool.get_news(sch_id, info["url"], info["uid"]))
		db.memory.recall_school(sch_id, ischool_info)
