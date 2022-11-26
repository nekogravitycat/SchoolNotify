from datetime import datetime, timezone, timedelta


def log(data: str) -> None:
	print(data)

	now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

	with open("log.txt", "a") as f:
		f.write(f"[{now}] {data}\n")
