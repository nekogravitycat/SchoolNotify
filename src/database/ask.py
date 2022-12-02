import myredis


def get_key(school: str, email: str) -> str:
	return myredis.get_key(f"ask_{school}_{email}")


def set_key(school: str, email: str, token: str) -> None:
	myredis.set_key(f"ask_{school}_{email}", token)


def list_keys(school: str = "") -> list:
	return myredis.list_prefix(f"ask_{school}") if school else myredis.list_prefix("ask")


def exists(school: str, email: str) -> bool:
	return myredis.exists(f"ask_{school}_{email}")


def delete_key(school: str, email: str):
	myredis.delete_key(f"ask_{school}_{email}")
