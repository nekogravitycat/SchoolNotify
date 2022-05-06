import myenv
import time
import schedule
import basic
from unilog import log
import os


def ScheduleRun() -> None:
	#heroku uses UTC+0, so schedule the tasks 8 hours earlier, using 24-hour clock
	scheduler: schedule.Scheduler = schedule.Scheduler()
	time_to_send: str = "10:00"

	scheduler.every().monday.at(time_to_send).do(basic.run)
	scheduler.every().thursday.at(time_to_send).do(basic.run)

	log("tasks scheduled")

	while(True):
		scheduler.run_pending()
		time.sleep(1)


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
	main()