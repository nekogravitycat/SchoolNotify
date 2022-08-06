from src import basic  # environment setup


def schedule_run() -> None:
	""" Run news-gathering if it's Monday or Thursday """

	weekday: int = basic.today().weekday()
	# monday = 0, thursday = 3
	if weekday == 0 or weekday == 3:
		basic.run()


if __name__ == "__main__":
	schedule_run()
