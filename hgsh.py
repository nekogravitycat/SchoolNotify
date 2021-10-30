import time
import requests
import bs4
import basic
import mydb


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

  responce: requests.Response = requests.post(url = "https://www.hgsh.hc.edu.tw/ischool/widget/site_news/news_query_json.php", data = send_data)

  block: str = str(responce.content).split("newsId")
  newsid: list = []

  for i in range(1, len(block)):
    newsid.append(block[i][3:8].replace('"', ""))
  
  return newsid


def get_news() -> list:
  print(f"hgsh runned at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} UTC+0\n")

  next: bool = True
  page: int = 0
  result: list = []

  try:
    while(next):
      newsid: list = get_newsid(page)

      for id in newsid:
        if(id == mydb.info.get("hgsh", "id")):
          break

        link: str =  f"https://www.hgsh.hc.edu.tw/ischool/public/news_view/show.php?nid={id}"

        response: requests.Response = requests.get(link, headers = basic.header)
        response.encoding = response.apparent_encoding

        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        soup.encoding = response.encoding

        title: str = soup.title.string
        date: time.struct_time = time.strptime(soup.find(id = "info_time").text.strip(), "%Y-%m-%d %H:%M:%S")
        latest_date: time.struct_time = time.strptime(mydb.info.get("hgsh", "date"), "%Y-%m-%d")

        if(date >= latest_date):
          result.append(basic.msg(link, title, date))

        else:
          next = False

      page += 1

    if(len(result) > 0):
      mydb.info.set("hgsh", "date", time.strftime("%Y-%m-%d", result[0].date))
      mydb.info.set("hgsh", "id", newsid[0])

    return result
  
  except Exception as e:
    print("hgsh failed")
    print(repr(e) + "\n")
    return None