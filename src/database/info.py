from src.database import json_io

io = json_io.TableIO(r"/app/data/school_info.json")


def get_info(school: str, info: str) -> str:
	return io.table.get(school).get(info)


def set_info(school: str, info: str, context: str) -> None:
	if io.table.get(school) is None:
		io.table.update({school: {}})

	io.table.get(school)[info] = context
	io.dump()
