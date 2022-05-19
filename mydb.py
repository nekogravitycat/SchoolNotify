import re
from myredis import db

def is_leagal(key_name: str) -> re.Match:
	return re.match(r"^[\w-]+$", key_name)


#users' token (password)
class token:
	def get(school: str, email: str) -> str:
		return db.get(f"{school}_email_{email}")

	def set(school: str, email:str, token: str) -> None:
		db.set(f"{school}_email_{email}", token)

	def list(school: str) -> tuple:
		return db.prefix(f"{school}_email")

	def exist(school: str, email: str) -> bool:
		return (f"{school}_email_{email}" in token.list(school))

	def delete(school: str, email: str) -> None:
		db.delete(f"{school}_email_{email}")


#latest infomation from schools
class info:
	def get(school: str, info: str) -> str:
		return db.get(f"{school}_latest_{info}")

	def set(school: str, info: str, context: str) -> None:
		db.set(f"{school}_latest_{info}", context)


#subscribtion requests
class ask:
	def get(school: str, email: str) -> str:
		return db.get(f"ask_{school}_{email}")
		#return db.get(f"ask{token}")

	def set(school: str, email: str, token: str) -> None:
		db.set(f"ask_{school}_{email}", token)
		#db.set(f"ask_{token}", f"{school};{email}")

	def list(school: str = "") -> tuple:
		if(school == ""):
			return db.prefix("ask")
		else:
			return db.prefix(f"ask_{school}")

	def exist(school: str, email: str) -> bool:
		return (f"ask_{school}_{email}" in ask.list(school))

	def delete(school: str, email: str):
		db.delete(f"ask_{school}_{email}")


class timestamp:
	def get() -> str:
		return db.get("timestamp")

	def set(stamp: str) -> None:
		db.set("timestamp", stamp)


temp: dict = {}

class memory:
	def remember(school: str, info_list: list) -> None:
		for i in info_list:
			temp[i] = info.get(school, i)

	def recall(school: str, info_list: list) -> None:
		for i in info_list:
			info.set(school, i, temp[i])
			

class edit:
	def cmd(method: str, key: str, value: str = "") -> dict:
		res: dict = {
			"status" : "error",
			"title" : "Cannot perfrom the method",
			"msg" : "Operation successed!"
		}
		
		method_vaild: bool = (method == "delete") or ((method in ["edit", "add"]) and value)
		
		if(not key or not method_vaild):
			res["msg"] = "Method is invaild"
			return res

		if(method == "edit"):
			if(key not in db.keys_iter()):
				res["msg"] = "Key does not exist"
				return res
				
			db.set(key, value)
			
		elif(method == "add"):
			if(key in db.keys_iter()):
				res["msg"] = "Key already exists"
				return res
				
			if(not re.match(r"^[\w-]+$", key)):
				res["msg"] = "Key name is illeagle"
				return res
				
			db.set(key, value)

		elif(method == "delete"):
			if(key not in db.keys_iter()):
				res["msg"] = "Key does not exist"
				return res
				
			db.delete(key)
			
		res["status"] = "ok"
		res["title"] = "Successed!"
		return res