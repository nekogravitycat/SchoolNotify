import redis
import os

r = redis.Redis(
	host=os.environ.get("redis_url"),
	port=12860,
	password=os.environ.get("redis_password"),
	decode_responses=True,
)


def set_key(key: str, value: str) -> None:
	r.set(key, value)


def get_key(key: str) -> str:
	return r.get(key)


def delete_key(key: str) -> None:
	r.delete(key)


def exists(key: str) -> bool:
	return r.exists(key) > 0


def keys():
	return r.scan_iter()


def list_prefix(pre: str) -> list:
	return list(r.scan_iter(f"{pre}*"))
