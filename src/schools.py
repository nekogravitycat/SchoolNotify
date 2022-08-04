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


def is_valid(ID: str) -> bool:
    return ID in info.keys()


def add(ID: str, url: str, uid: str, name: str) -> None:
    with open("school_info.txt", "a") as f:
        f.write(f"{ID};{url};{uid};{name}\n")

    info.clear()
    read_schools()


def get_name(ID: str) -> str:
    if ID not in info:
        return "*此學校不存在*"

    return info[ID]["name"]


read_schools()
