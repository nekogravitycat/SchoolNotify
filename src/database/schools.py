info: dict = {}


def read_schools() -> None:
	""" Read school info from "school_info.txt" """

	with open(r"assets/school_info.txt") as f:
		for line in f.readlines():
			# format: id;url;uid
			item: list = line.split(";")
			temp: dict = {
				# id (item[0]) as key name
				"url": item[1].strip(),
				"uid": item[2].strip(),
				"name": item[3].strip(),
			}
			info.update({item[0]: temp})


def exists(sch_id: str) -> bool:
	""" Check if the given school id exists in the database

	:param sch_id: school id to check
	:return: True if exists, False if not
	"""

	return sch_id in info.keys()


def add_school(sch_id: str, url: str, uid: str, name: str) -> None:
	""" Write school info into "school_info.txt"

	:param sch_id: id of school
	:param url: domain name of school
	:param uid: uid of school
	:param name: name of school
	"""

	with open("school_info.txt", "a") as f:
		f.write(f"{sch_id};{url};{uid};{name}\n")

	info.clear()
	read_schools()


def get_name(sch_id: str) -> str:
	""" Get the name of school

	:param sch_id: id of school
	:return: name of school, "*此學校不存在*" if doesn't exist
	"""

	if sch_id not in info:
		return "*此學校不存在*"

	return info[sch_id]["name"]
