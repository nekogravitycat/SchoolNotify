import os
import json
from src.unilog import log


class TableIO:
	table: dict = {}

	def __init__(self, table_path: str):
		self.table_path = table_path
		self.load()

	def load(self) -> None:
		if not os.path.exists(self.table_path):
			try:
				with open(self.table_path, "w+") as f:
					f.write(json.dumps({}))
			except Exception as ex:
				log(f"json_io.TableIO.load_table() write new file {self.table_path} error: {ex}")

		with open(self.table_path, "r") as f:
			self.table = json.loads(f.read())

	def dump(self) -> None:
		with open(self.table_path, "w+") as f:
			f.write(json.dumps(self.table, indent=2))
