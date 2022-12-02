from src.database import myredis


def get_key(school: str, info: str) -> str:
	return myredis.get_key(f"{school}_latest_{info}")


def set_key(school: str, info: str, context: str) -> None:
	myredis.set_key(f"{school}_latest_{info}", context)
