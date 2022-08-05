import redis
import os

r = redis.Redis(
	host=os.environ["redis_url"],
	port=12860,
	password=os.environ["redis_password"],
	decode_responses=True,
)


def set_key(key: str, value: str) -> None:
	r.set(key, value)


def get_key(key: str) -> str:
	return r.get(key)


def delete_key(key: str) -> None:
	r.delete(key)


def keys():
	return r.scan_iter()


def list_prefix(pre: str) -> list:
	matches: list = []

	for key in r.scan_iter(f"{pre}*"):
		matches.append(key)

	return matches
