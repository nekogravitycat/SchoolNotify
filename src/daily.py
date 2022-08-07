from src import basic
from src.unilog import log


def schedule_run() -> None:
	""" Run news-gathering if it's Monday or Thursday """

	weekday: int = basic.today().weekday()
	log(f"schedule_run: weekday={weekday}")
	# monday = 0, thursday = 3
	if weekday in {0, 3}:
		basic.run()


if __name__ == "__main__":
	schedule_run()
