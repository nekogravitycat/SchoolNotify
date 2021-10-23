from replit import db
import time
import requests
import bs4
import basic


class msg(basic.msg):
  def __init__(self, newsid: str):
    self.newsid = newsid


def newsIdGrabber(pageNum: int = 0, maxRows: int = 15) -> list:
  send_data: dict = {
    "field" : "time",
    "order" : "DESC",
    "pageNum" : str(pageNum),
    "maxRows" : str(maxRows),
    "keyword" : "",
    "uid" : "WID_0_2_21b2de5a55209704d947481c9d16786c85145eca",
    "tf" : "1", #"tf" means "the fuck?"
    "auth_type" : "user"
  }

  responce: requests.Response = requests.post("https://www.hgsh.hc.edu.tw/ischool/widget/site_news/news_query_json.php", data = send_data)

  block: str = str(responce.content).split("newsId")
  newsid: list = []

  for i in range(1, len(block)):
    newsid.append(block[i][3:8].replace('"', ""))
  
  for s in newsid:
    print(s)

  return newsid


def get_news() -> list:
  #WIP
  pass