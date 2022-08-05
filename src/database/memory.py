import info

temp: dict = {}


def remember_school(school: str, info_list: list) -> None:
	for i in info_list:
		temp[i] = info.get_key(school, i)


def recall_school(school: str, info_list: list) -> None:
	for i in info_list:
		info.set_key(school, i, temp[i])
