from datetime import datetime, timezone, timedelta


def log(data: str, write_log: bool = False) -> None:
	""" Print a string to console, write to log file if "write_log" is True

	:param data: string to print
	:param write_log: Whether to write to log file (optional, False by default)
	"""

	print(data)

	if write_log:
		now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

		with open("log.txt", "a") as f:
			f.write(f"[{now}] {data}\n")
