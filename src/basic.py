import os
import time
from datetime import datetime, timezone, timedelta
from src import myemail, ischool, database as db
from src.unilog import log


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


def push_email(sch_id: str, news: list, test_mail: bool = False) -> None:
	""" Send emails to the subscribers of the school

	:param sch_id: id of school
	:param news: list of basic.Msg objects
	:param test_mail: whether to send email only to the admin
	"""

	is_empty: bool = not news

	if is_empty:
		log(f"No new announcements for {sch_id}, skip email sending")
		return

	for n in news:
		print(n.detail() + "\n")

	recipients = db.user.emails(sch_id)

	# if there is at least one subscriber in the list
	if recipients:
		subject: str = f"{db.schools.get_name(sch_id)}學校公告 ({today().strftime('%m/%d')})".replace("-", "/")
		content: str = ""

		for n in news:
			content += f"{n.html()}<br><br>"

		if test_mail:
			recipients.clear()
			recipients.append(os.environ.get("email_admin"))

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
		if not db.user.emails(sch_id):
			log(f"There's no subscriber for {sch_id}, skipping")
			continue

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

	if sch_ids is None:
		sch_ids = db.schools.info.keys()

	print(f"sch_ids: {sch_ids}")

	for sch_id in sch_ids:
		info: db.schools.Sch = db.schools.info[sch_id]
		db.memory.remember_school(sch_id, ischool_info)
		news: list = ischool.get_news(sch_id, info.url, info.uid)
		show_result(news)
		push_email(sch_id, news, test_mail=True)
		db.memory.recall_school(sch_id, ischool_info)


base: str = "https://sn.gravitycat.tw"


def verify_link(uid: str) -> str:
	""" Generate a verification link for user

	:param uid: uid for the AskRecord
	:return: verification link
	"""

	return f"{base}/verify?uid={uid}"


def unsub_link(email: str, school: str, token: str = "") -> str:
	""" Generate an unsubscribe link for user

		:param email: user's email
		:param school: user's school
		:param token: user's token (optional, will fetch from database by default)
		:return: unsubscribe link
		"""

	if not token:
		token = db.user.get_token(school, email)

	return f"{base}/unsub?email={email}&school={school}&token={token}"
