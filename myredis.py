import redis
import os

r = redis.Redis(
	host=os.environ["redis_url"],
	port=12860,
	password=os.environ["redis_password"],
	decode_responses=True
)

class db:
	def set(key, value):
		r.set(key, value)

	def get(key):
		return r.get(key)
	
	def delete(key):
		r.delete(key)
		
	def keys(return_list: bool = False):
		if(return_list):
			return r.keys()
		return r.scan_iter()

	def keys_iter():
		return r.scan_iter()
		
	def prefix(prefix):
		matches = []
		for key in r.scan_iter(f"{prefix}*"):
			matches.append(key)
		return matches