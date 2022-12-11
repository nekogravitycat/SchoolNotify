import json
import os
from src.unilog import log

table_file = "/app/data/data.json"
table = {}


def load_table() -> None:
	if not os.path.exists(table_file):
		try:
			with open(table_file, "w+") as f:
				f.write(json.dumps({"dummy": "meow"}))
		except Exception as ex:
			log(f"myredis.load_table() write new file {table_file} error: {ex}")

	with open(table_file, "r") as f:
		global table
		table = json.loads(f.read())


def dump_table() -> None:
	with open(table_file, "w+") as f:
		f.write(json.dumps(table))


def set_key(key: str, value: str) -> None:
	table[key] = value
	dump_table()


def get_key(key: str) -> str:
	return table.get(key)


def delete_key(key: str) -> None:
	del table[key]
	dump_table()


def exists(key: str) -> bool:
	return key in table


def keys():
	return table.keys()


def list_prefix(pre: str) -> list:
	result: list = []

	for key in table.keys():
		if key.startswith(pre):
			result.append(key)

	return result


load_table()
