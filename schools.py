info: dict = {}


def read_schools() -> None:
	with open("school_info.txt") as f:
		for line in f.readlines():
			#format: id;url;uid
			item: list = line.split(";")
			temp: dict = {
				#id (item[0]) as key name
				"url" : item[1].strip(),
				"uid" : item[2].strip(),
				"name" : item[3].strip()
			}
			info.update({item[0] : temp})


def is_valid(id: str) -> bool:
	return (id in info.keys())


def add(id: str, url: str, uid: str) -> None:
	with open("school_info.txt", "a") as f:
		f.write(f"{id};{url};{uid}\n")
	info.clear()
	read_schools()


def get_name(id: str) -> str:
	return info[id].name


read_schools()