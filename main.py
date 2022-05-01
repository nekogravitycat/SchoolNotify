import time
import schedule
import basic
from unilog import log

debug: bool = False
run_immediate: bool = False


def ScheduleRun():
	#replit uses UTC+0, so schedule the tasks 8 hours earlier, using 24-hour clock
	scheduler: schedule.Scheduler = schedule.Scheduler()
	time_to_send: str = "10:00"

	scheduler.every().monday.at(time_to_send).do(basic.run)
	scheduler.every().thursday.at(time_to_send).do(basic.run)

	log("tasks scheduled")

	while(True):
		scheduler.run_pending()
		time.sleep(1)


def main():
	if(run_immediate):
		if(debug):
			basic.debug()
		else:
			basic.run()
	
	ScheduleRun()


if(__name__ == "__main__"):
	main()