from src.unilog import log

timestamp: str = "A"
table: dict = {}


class AskRecord:
	def __init__(self, school: str, email: str, timestamp: str, token: str):
		self.email = email
		self.school = school
		self.timestamp = timestamp
		self.token = token

	def info(self) -> str:
		return f"{self.email};{self.school};{self.timestamp};{self.token}"


def add(uid: str, record: AskRecord):
	table.update({uid: record})


def get(uid: str) -> AskRecord:
	return table.get(uid)


def list_asks():
	return table.keys()


def delete(uid: str) -> None:
	if uid not in table:
		log(f"database.ask: key '{uid}' not exists")
		return

	del table[uid]


def exists(uid: str) -> bool:
	return uid in table


def exists_school_email(school: str, email: str) -> bool:
	for uid in table:
		if table.get(uid).school == school and table.get(uid).email == email:
			return True

	return False
