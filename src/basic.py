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


def today() -> datetime.date:
	""" Get the current date in GMT+8 """

	return datetime.now(timezone(timedelta(hours=8))).date()


def push_email(sch_id: str, news: list) -> None:
	""" Send emails to the subscribers of the school

	:param sch_id: id of school
	:param news: list of basic.Msg objects
	"""

	is_empty: bool = not news

	if is_empty:
		log(f"No new announcements for {sch_id}, skip email sending\n")
		log("push_email() done(skipped)!")
		return

	for n in news:
		print(n.detail() + "\n")

	# if there is at least one subscriber in the list
	if db.user.list_keys(sch_id):
		subject: str = f"{db.schools.get_name(sch_id)}學校公告 ({today().strftime('%m/%d')})".replace("-", "/")
		content: str = ""

		if is_empty:
			content = "尚無新公告<br><br>"

		else:
			for n in news:
				content += f"{n.html()}<br><br>"

		recipients: list = []

		if test_mail:
			recipients.append(os.environ.get("email_admin"))

		else:
			# prefix format: schid_email_address@example.com
			prefix_len: int = len(sch_id) + 7

			# re[prefix_len:] is for removing the prefix (schid_email_)
			recipients.extend(re[prefix_len:] for re in db.user.list_keys(sch_id))

		myemail.send(recipients, subject, content, sch_id)

	else:
		log(f"The recipient list of {sch_id} is empty")

	log("push_email() done!")


def show_result(news: list) -> None:
	""" Show every news details in a list of basic.Msg objects

	:param news: list of basic.Msg objects
	"""

	if not news:
		print("No new announcements")

	else:
		for re in news:
			print(re.detail())


def run() -> None:
	""" Run news-gathering for every school and send news emails to the subscribers """

	for sch_id in db.schools.info.keys():
		try:
			info: db.schools.Sch = db.schools.info[sch_id]
			news: list = ischool.get_news(sch_id, info.url, info.uid)
			push_email(sch_id, news)

		except Exception as e:
			log(f"{sch_id} Runtime Error: {e}")


def debug(sch_ids: list = None) -> None:
	""" Run news-gathering for given list of school ids

	:param sch_ids: list of school ids to run (optional, run every school's by default)
	"""

	ischool_info: list = ["date", "id"]

	if not sch_ids:
		sch_ids = db.schools.info.keys()

	for sch_id in sch_ids:
		info: db.schools.Sch = db.schools.info[sch_id]
		db.memory.remember_school(sch_id, ischool_info)
		show_result(ischool.get_news(sch_id, info.url, info.uid))
		db.memory.recall_school(sch_id, ischool_info)


base: str = "https://sn.gravitycat.tw"


def verify_link(email: str, school: str, token: str) -> str:
	""" Generate a verification link for user

	:param email: user's email
	:param school: user's school
	:param token: user's token
	:return: verification link
	"""

	return f"{base}/verify?email={email}&school={school}&token={token}"


def unsub_link(email: str, school: str, token: str = "") -> str:
	""" Generate an unsubscribe link for user

		:param email: user's email
		:param school: user's school
		:param token: user's token (optional, will fetch from database by default)
		:return: unsubscribe link
		"""

	if not token:
		token = db.user.get_key(school, email)

	return f"{base}/unsub?email={email}&school={school}&token={token}"
