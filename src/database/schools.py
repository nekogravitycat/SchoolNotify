import json

info: dict = {}


class Sch:
	def __init__(self, name: str, url: str, uid: str):
		self.name = name
		self.url = url
		self.uid = uid

	def to_dict(self) -> dict:
		""" Make a dictionary containing name, url, and uid """

		return {
			"name": self.name,
			"url": self.url,
			"uid": self.uid
		}


def read_schools() -> None:
	""" Read school info from "school_info.json" and store them into "info" dict variable """

	with open(r"assets/school_info.json", "r", encoding="utf8") as f:
		data: dict = json.load(f)
		for sch_id in data:
			sch_info: Sch = Sch(
				name=data[sch_id]["name"],
				url=data[sch_id]["url"],
				uid=data[sch_id]["uid"]
			)
			info.update({sch_id: sch_info})


def exists(sch_id: str) -> bool:
	""" Check if the given school id exists in the database

	:param sch_id: school id to check
	:return: True if exists, False if not
	"""

	return sch_id in info.keys()


def add_school(sch_id: str, sch_info: Sch) -> None:
	""" Write school info into "school_info.txt"

	:param sch_id: id of school
	:param sch_info: Sch object of school info
	"""

	if exists(sch_id):
		print(f"database.schools.add_school() error: school {sch_id} already exists")
		return

	with open(r"assets/school_info.json", "r", encoding="utf-8") as f:
		data: dict = json.load(f)

	to_insert: dict = {sch_id: sch_info.to_dict()}
	data |= to_insert

	with open(r"assets/school_info.json", "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)

	info.clear()
	read_schools()


def get_name(sch_id: str) -> str:
	""" Get the name of school

	:param sch_id: id of school
	:return: name of school, "*此學校不存在*" if doesn't exist
	"""

	return "*此學校不存在*" if sch_id not in info else info[sch_id].name


read_schools()
