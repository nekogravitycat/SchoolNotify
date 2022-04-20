info: dict = {}


def read_schools():
	with open("school_info.txt") as f:
		for line in f.readlines():
			#format: id;url;uid
			item: list = line.split(";")
			temp: dict = {
				"url" : item[1].strip(),
				"uid" : item[2].strip()
			}
			info.update({item[0] : temp})


def is_valid(id: str) -> bool:
	return (id in info.keys())


read_schools()