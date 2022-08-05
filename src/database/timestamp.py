import myredis


def get_key() -> str:
	return myredis.get_key("timestamp")


def set_key(stamp: str) -> None:
	myredis.set_key("timestamp", stamp)
