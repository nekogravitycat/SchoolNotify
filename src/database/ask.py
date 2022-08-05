from src.database import myredis


def get_key(school: str, email: str) -> str:
	return myredis.get_key(f"ask_{school}_{email}")


def set_key(school: str, email: str, token: str) -> None:
	myredis.set_key(f"ask_{school}_{email}", token)


def list_keys(school: str = "") -> list:
	if school == "":
		return myredis.list_prefix("ask")
	else:
		return myredis.list_prefix(f"ask_{school}")


def is_exist(school: str, email: str) -> bool:
	return f"ask_{school}_{email}" in list_keys(school)


def delete_key(school: str, email: str):
	myredis.delete_key(f"ask_{school}_{email}")
