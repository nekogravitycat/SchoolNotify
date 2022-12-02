from src.database import myredis


def get_key(school: str, email: str) -> str:
	return myredis.get_key(f"{school}_email_{email}")


def set_key(school: str, email: str, token: str) -> None:
	myredis.set_key(f"{school}_email_{email}", token)


def list_keys(school: str) -> list:
	return myredis.list_prefix(f"{school}_email")


def exists(school: str, email: str) -> bool:
	return myredis.exists(f"{school}_email_{email}")


def delete_key(school: str, email: str) -> None:
	myredis.delete_key(f"{school}_email_{email}")
