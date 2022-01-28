import time
import requests
import bs4
import re
import basic
import mydb
from unilog import log


class news_id:
  def __init__(self, id: str, is_pinned: bool, date: time.struct_time = None):
    self.id = id
    self.is_pinned = is_pinned
    self.date = date


def get_newsid(pageNum: int = 0, maxRows: int = 15) -> list:
  send_data: dict = {
    "field" : "time",
    "order" : "DESC",
    "pageNum" : str(pageNum),
    "maxRows" : str(maxRows),
    "keyword" : "",
    "uid" : "WID_0_2_518cd2a7e52b7f65fc750eded8b99ffcc2a7daca",
    "tf" : "1", #"tf" means "the fuck?"
    "auth_type" : "user"
  }

  responce: requests.Response = requests.post(url = "https://web.whsh.tc.edu.tw/ischool/widget/site_news/news_query_json.php", data = send_data)

  result: list = []

  id_pinned: list = re.findall(r'"newsId":"([0-9]*)","top":([01])', responce.text)

  for i in id_pinned:
    is_pinned: bool = (i[1] == "1")
    result.append(news_id(i[0], is_pinned))

  return result


def get_news() -> list:
  log(f"whsh runned")

  next: bool = True
  page: int = 0
  result: list = []

  vaild_news: list = []

  try:
    while(next):
      news: list = get_newsid(page)

      for n in news:
        if(n.id == mydb.info.get("whsh", "id") and not n.is_pinned):
          break

        link: str = f"https://web.whsh.tc.edu.tw/ischool/public/news_view/show.php?nid={n.id}"

        response: requests.Response = requests.get(link, headers = basic.header)
        response.encoding = response.apparent_encoding

        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        soup.encoding = response.encoding

        title: str = soup.title.string
        date: time.struct_time = time.strptime(soup.find(id = "info_time").text.strip(), "%Y-%m-%d %H:%M:%S")
        latest_date: time.struct_time = time.strptime(mydb.info.get("whsh", "date"), "%Y-%m-%d")

        if(date >= latest_date or n.is_pinned):
          result.append(basic.msg(link, title, date))
          if(not n.is_pinned):
            vaild_news.append(news_id(n.id, n.is_pinned, date))

        else:
          next = False
          break

      page += 1

    if(len(vaild_news) > 0):
      for vn in vaild_news:
        if(not vn.is_pinned):
          mydb.info.set("whsh", "date", time.strftime("%Y-%m-%d", vn.date))
          mydb.info.set("whsh", "id", vn.id)
          break

    return result
  
  except Exception as e:
    log(f"whsh failed: {repr(e)}")
    return None