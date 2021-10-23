from replit import db
import time
import requests
import bs4
import basic


def get_newsid(pageNum: int = 0, maxRows: int = 15) -> list:
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
  
  """
  for s in newsid:
    print(s)
  """
  return newsid


def get_news() -> list:
  print(f"hchs runned at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} UTC+0\n")

  result: list = []

  for id in get_newsid():
    if(id == db["hgsh_latest_id"]):
      break

    link: str =  f"https://www.hgsh.hc.edu.tw/ischool/public/news_view/show.php?nid={id}"

    response: requests.Response = requests.get(link, headers = basic.header)
    response.encoding = response.apparent_encoding

    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
    soup.encoding = response.encoding

    title: str = soup.title.string
    date: time.struct_time = time.strptime(soup.find(id = "info_time").text.strip(), "%Y-%m-%d %H:%M:%S")
    latest_date: time.struct_time = time.strptime(db["hgsh_latest_date"], "%Y-%m-%d")

    if(date >= latest_date):
      result.append(basic.msg(link, title, date))

  return result