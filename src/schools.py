info: dict = {}


def read_schools() -> None:
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


def is_valid(sch_id: str) -> bool:
	return sch_id in info.keys()


def add(sch_id: str, url: str, uid: str, name: str) -> None:
	with open("school_info.txt", "a") as f:
		f.write(f"{sch_id};{url};{uid};{name}\n")

	info.clear()
	read_schools()


def get_name(sch_id: str) -> str:
	if sch_id not in info:
		return "*此學校不存在*"

	return info[sch_id]["name"]


read_schools()
