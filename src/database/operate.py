from src.database import myredis
import re


def is_legal_name(key_name: str) -> re.Match:
	return re.match(r"^[\w-]+$", key_name)


def edit_key(method: str, key: str, value: str = "") -> dict:
	res: dict = {
		"status": "error",
		"title": "Cannot perform the method",
		"msg": "Operation successes!",
	}

	# check if the command is valid
	method_valid: bool = (method == "delete") or (method in {"edit", "add"} and value)

	if not key or not method_valid:
		res["msg"] = "Method is invalid"
		return res

	# run the command
	if method == "edit":
		if not myredis.exists(key):
			res["msg"] = "Key does not exist"
			return res

		myredis.set_key(key, value)

	elif method == "add":
		if myredis.exists(key):
			res["msg"] = "Key already exists"
			return res

		if not re.match(r"^[\w-]+$", key):
			res["msg"] = "Key name is illegal"
			return res

		myredis.set_key(key, value)

	elif method == "delete":
		if not myredis.exists(key):
			res["msg"] = "Key does not exist"
			return res

		myredis.delete_key(key)

	res["status"] = "ok"
	res["title"] = "Success!"
	return res
