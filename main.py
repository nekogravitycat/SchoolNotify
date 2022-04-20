import time
import schedule
import website
import basic
import mydb
import ischool
import schools
from unilog import log

send_email: bool = True
run_immediate: bool = False


def ShowResult(result: list):
	if(len(result) == 0):
		log("No new announcements")
	else:
		for re in result:
			log(re.detail())


def Job():
	ischool_info: list = ["date", "id"]
	#for debugging
	if(not send_email):
		for id in schools.info.keys():
			info: dict = schools.info[id]
			mydb.memory.remember(id, ischool_info)
			ShowResult(ischool.get_news(id, info["url"], info["uid"]))
			mydb.memory.recall(id, ischool_info)
		return
	#main function
	for id in schools.info.keys():
		try:
			info: dict = schools.info[id]
			news: list = ischool.get_news(id, info["url"], info["uid"])
			basic.push_email(id, news)
		except Exception as e:
			log(f"{id} Runtime Error: {e}", True)


def ScheduleRun():
	#replit uses UTC+0, so schedule the tasks 8 hours earlier, using 24-hour clock
	scheduler: schedule.Scheduler = schedule.Scheduler()
	time_to_send: str = "10:00"

	scheduler.every().monday.at(time_to_send).do(Job)
	scheduler.every().thursday.at(time_to_send).do(Job)

	log("tasks scheduled")

	while(True):
		scheduler.run_pending()
		time.sleep(1)


website.alive()

if(run_immediate):
	Job()
	
ScheduleRun()
