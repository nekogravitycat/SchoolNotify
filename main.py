import time
import schedule
import website
import basic
import mydb
import hchs
import hgsh


website.alive() #for uptimerobot

send_email: bool = True
run_immediate: bool = False

#for testing
#mydb.info.set("hchs", "date", "2021-11-03")
#mydb.info.set("hchs", "id", "142")
#mydb.info.set("hgsh", "date", "2021-11-04")
#mydb.info.set("hgsh", "id", "10371")


def ShowResult(result: list):
  if(len(result) == 0):
    print("No new announcements")

  else:
    for re in result:
      print(re.detail())
      print()


def Job():
  if(send_email):
    basic.push_email("hchs", hchs.get_news())
    basic.push_email("hgsh", hgsh.get_news())
    
  else:
    ischool_info: list = ["date", "id"]

    basic.memory.remember("hchs", ischool_info)
    ShowResult(hchs.get_news())
    basic.memory.recall("hchs", ischool_info)

    basic.memory.remember("hgsh", ischool_info)
    ShowResult(hgsh.get_news())
    basic.memory.recall("hgsh", ischool_info)


def ScheduleRun():
  #replit uses UTC+0, so schedule the tasks 8 hours earlier, using 24-hour clock
  scheduler: schedule.Scheduler = schedule.Scheduler()

  time_to_send: str = "10:00"

  scheduler.every().monday.at(time_to_send).do(Job)
  scheduler.every().thursday.at(time_to_send).do(Job)

  print("tasks scheduled")

  while True:
    scheduler.run_pending()
    time.sleep(1)


if(run_immediate):
  Job()


ScheduleRun()