import os

local_test: bool = False
env_file: str = "myenv.txt"

#set environment variable if not exists
def set_env():
	#detect the existence env var
	if(os.environ.get("db_token")):
		return
	print("Environment varibles not exist, setting it from myenv.txt")
	#set env var
	with open(env_file, "r") as f:
		while(True):
			line = f.readline()
			if(not line):
				break
			#format: key=value
			kv = line.split("=")
			os.environ[kv[0]] = kv[1]
			print(f"set: {kv[0]}={kv[1]}")
			
set_env()