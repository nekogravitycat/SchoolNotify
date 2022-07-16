from src import myenv, basic #environment setup
from src.unilog import log
import os


def ScheduleRun() -> None:
	weekday: int = basic.today().weekday()
	#monday = 0, thursday = 3
	if(weekday == 0 or weekday == 3):
		basic.run()


def main() -> None:
	if(os.environ.get("run_flask_wsgi")):
		import website
		website.alive()
	
	if(os.environ.get("run_immediate")):
		if(os.environ.get("debug")):
			basic.debug()
		else:
			basic.run()
			
	if(os.environ.get("production")):
		ScheduleRun()
	else:
		log("running on debug platform mode")


if(__name__ == "__main__"):
	myenv.set_env()
	main()