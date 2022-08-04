import re
from src.myredis import Db


def is_legal(key_name: str) -> re.Match:
	return re.match(r"^[\w-]+$", key_name)


# users' token (password)
class Token:
	def get(school: str, email: str) -> str:
		return Db.get(f"{school}_email_{email}")

	def set(school: str, email: str, token: str) -> None:
		Db.set(f"{school}_email_{email}", token)

	def list(school: str) -> list:
		return Db.prefix(f"{school}_email")

	def exist(school: str, email: str) -> bool:
		return f"{school}_email_{email}" in Token.list(school)

	def delete(school: str, email: str) -> None:
		Db.delete(f"{school}_email_{email}")


# latest information from schools
class Info:
	def get(school: str, info: str) -> str:
		return Db.get(f"{school}_latest_{info}")

	def set(school: str, info: str, context: str) -> None:
		Db.set(f"{school}_latest_{info}", context)


# subscription requests
class ask:
	def get(school: str, email: str) -> str:
		return Db.get(f"ask_{school}_{email}")
		# return db.get(f"ask{token}")

	def set(school: str, email: str, token: str) -> None:
		Db.set(f"ask_{school}_{email}", token)
		# db.set(f"ask_{token}", f"{school};{email}")

	def list(school: str = "") -> list:
		if school == "":
			return Db.prefix("ask")
		else:
			return Db.prefix(f"ask_{school}")

	def exist(school: str, email: str) -> bool:
		return f"ask_{school}_{email}" in ask.list(school)

	def delete(school: str, email: str):
		Db.delete(f"ask_{school}_{email}")


class timestamp:
	def get() -> str:
		return Db.get("timestamp")

	def set(stamp: str) -> None:
		Db.set("timestamp", stamp)


temp: dict = {}


class memory:
	def remember(school: str, info_list: list) -> None:
		for i in info_list:
			temp[i] = Info.get(school, i)

	def recall(school: str, info_list: list) -> None:
		for i in info_list:
			Info.set(school, i, temp[i])


class edit:
	def cmd(method: str, key: str, value: str = "") -> dict:
		res: dict = {
			"status": "error",
			"title": "Cannot perform the method",
			"msg": "Operation successes!",
		}

		# check if the command is valid
		method_valid: bool = (method == "delete") or (
					(method in ["edit", "add"]) and value
		)

		if not key or not method_valid:
			res["msg"] = "Method is invalid"
			return res

		# run the command
		if method == "edit":
			if key not in Db.keys_iter():
				res["msg"] = "Key does not exist"
				return res

			Db.set(key, value)

		elif method == "add":
			if key in Db.keys_iter():
				res["msg"] = "Key already exists"
				return res

			if not re.match(r"^[\w-]+$", key):
				res["msg"] = "Key name is illegal"
				return res

			Db.set(key, value)

		elif method == "delete":
			if key not in Db.keys_iter():
				res["msg"] = "Key does not exist"
				return res

			Db.delete(key)

		res["status"] = "ok"
		res["title"] = "Success!"
		return res


class Temp:
	def __init__(self, data: dict) -> None:
		self.data = data

	def update(self) -> None:
		for key in Db.keys_iter():
			self.data[key] = Db.get(key)
