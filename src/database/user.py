from src.database import json_io
from src.unilog import log

io = json_io.TableIO(r"/app/data/subscriber_list.json")


def add(school: str, email: str, token: str) -> None:
	if io.table.get(school) is None:
		io.table.update({school: {}})

	io.table.get(school)[email] = token
	io.dump()


def delete(school: str, email: str) -> None:
	if io.table.get(school).get(email) is None:
		log(f"database.user: key '{school}-{email}' not exists")
		return

	del io.table.get(school)[email]
	io.dump()


def get_token(school: str, email: str) -> str:
	return io.table.get(school).get(email)


def emails(school: str) -> list:
	result = []
	for u in io.table.get(school):
		result.append(u)

	return result


def exists(school: str, email: str) -> bool:
	return io.table.get(school).get(email) is not None
