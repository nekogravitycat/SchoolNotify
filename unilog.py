import os
import requests
from datetime import datetime, timezone, timedelta


def log(data: str, write_log: bool = False):
	print(data)
	
	if(write_log):
		now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
		with open("log.txt", "a") as f:
			f.write(f"[{now}] {data}\n")
			
	return

	#disable the unilog function
	try:
		url = "https://log.nekogc.com/log"
		data = {
			"cat": "sn",
			"data": data,
			"token": os.environ["unilog_token"]
		}
		requests.post(url, json=data)
		
	except:
		print("UniLog failed")