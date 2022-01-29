import time
import schedule
import website
import basic
import mydb
import isch_allpin
import isch_pin
from unilog import log

website.alive() #for uptimerobot

send_email: bool = True
run_immediate: bool = False

sch_pin_list: list = [
  ["hchs", "www.hchs.hc.edu.tw", "WID_0_2_0516b5aba93b58b0547367faafb2f1dbe2ebba4c"],
  ["whsh", "web.whsh.tc.edu.tw", "WID_0_2_518cd2a7e52b7f65fc750eded8b99ffcc2a7daca"]
]
sch_allpin_list: list = [
  ["hgsh", "www.hgsh.hc.edu.tw", "WID_0_2_21b2de5a55209704d947481c9d16786c85145eca"],
  ["tcivs", "w3.tcivs.tc.edu.tw", "WID_0_2_a18324d5b18f53971c1d32b13dcfe427c6c77ed4"],
  ["dali", "www.dali.tc.edu.tw", "WID_0_2_377afa59cce9f22276e3f66e9d896cb97110c95d"]
]
ischool_info: list = ["date", "id"]

def ShowResult(result: list):
  if(len(result) == 0):
    print("No new announcements")

  else:
    for re in result:
      print(re.detail())
      print()


def Job():
  if(send_email):
    for sch in sch_pin_list:
      basic.push_email(sch[0], isch_pin.get_news(sch[0], sch[1], sch[2]))
    
    for sch in sch_allpin_list:
      basic.push_email(sch[0], isch_allpin.get_news(sch[0], sch[1], sch[2]))
    
  else:
    for sch in sch_pin_list:
      mydb.memory.remember(sch[0], ischool_info)
      ShowResult(isch_pin.get_news(sch[0], sch[1], sch[2]))
      mydb.memory.recall(sch[0], ischool_info)

    for sch in sch_allpin_list:
      mydb.memory.remember(sch[0], ischool_info)
      ShowResult(isch_allpin.get_news(sch[0], sch[1], sch[2]))
      mydb.memory.recall(sch[0], ischool_info)


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


if(run_immediate):
  Job()


ScheduleRun()