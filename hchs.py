import time
import requests
import bs4
import re
import basic
import mydb

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
    "uid" : "WID_0_2_0516b5aba93b58b0547367faafb2f1dbe2ebba4c",
    "tf" : "1", #"tf" means "the fuck?"
    "auth_type" : "user"
  }

  responce: requests.Response = requests.post(url = "http://www.hchs.hc.edu.tw/ischool/widget/site_news/news_query_json.php", data = send_data)

  result: list = []

  id_pinned: list = re.findall(r'"newsId":"([0-9]*)","top":([01])', responce.text)

  for i in id_pinned:
    is_pinned: bool = (i[1] == 1)
    result.append(news_id(i[0], is_pinned))

  return result


def get_news() -> list:
  print(f"hchs runned at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} UTC+0\n")

  next: bool = True
  page: int = 0
  result: list = []

  vaild_news: list = []

  try:
    while(next):
      news: list = get_newsid(page)

      for n in news:
        if(n.id == mydb.info.get("hchs", "id") and not n.is_pinned):
          break

        link: str =  f"http://www.hchs.hc.edu.tw/ischool/public/news_view/show.php?nid={n.id}"
        #HCHS website has no HTTPS YET >:(

        response: requests.Response = requests.get(link, headers = basic.header)
        response.encoding = response.apparent_encoding

        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        soup.encoding = response.encoding

        title: str = soup.title.string
        date: time.struct_time = time.strptime(soup.find(id = "info_time").text.strip(), "%Y-%m-%d %H:%M:%S")
        latest_date: time.struct_time = time.strptime(mydb.info.get("hchs", "date"), "%Y-%m-%d")

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
          mydb.info.set("hchs", "date", time.strftime("%Y-%m-%d", vn.date))
          mydb.info.set("hchs", "id", vn.id)
          break

    return result
  
  except Exception as e:
    print("hchs failed")
    print(repr(e) + "\n")
    return None