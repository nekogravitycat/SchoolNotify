from replit import db
import time
import requests
import bs4
import basic


def get_news() -> list:
  print(f"hchs runned at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} UTC+0\n")
  
  next: bool = True
  page: int = 1
  result: list = [] #storing a list of Announcement()

  while next:
    try_times: int = 3 #times to try when request is failed
    ex: Exception

    while try_times >= 0:
      try:
        response: requests.Response = requests.get(f"http://www.hchs.hc.edu.tw/files/501-1000-1001-{page}.php?Lang=zh-tw", headers = basic.header)

        response.encoding = response.apparent_encoding

        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        soup.encoding = response.encoding

        row: bs4.element.ResultSet = soup.find_all("tr", class_ = ["row_01", "row_02"]) 

        for r in row:
          #hyperlink of the article
          division: bs4.element.Tag = r.select_one("div")
          anchor: bs4.element.Tag = division.select_one("a")

          link: str = anchor["href"]

          #title, source (unwanted), and date
          table: bs4.element.ResultSet = r.select("td")
          table_list: list = []

          for td in table:
            table_list.append(td)

          title: str = table_list[0].text.strip()
          #source = table_list[1].text.strip() #unwanted
          date: time.struct_time = time.strptime(table_list[2].text.strip(), "%Y-%m-%d")
          latest_date: time.struct_time = time.strptime(db["hchs_latest_date"], "%Y-%m-%d")

          if(date > latest_date or (date >= latest_date and title != db["hchs_latest_title"])):
            result.append(basic.msg(link, title, date))
            
          else:
            next = False
            break

      except Exception as e:
        ex = e
        try_times -= 1
        print(f"hchs request failed: {try_times} retry times remaining, wait 1 sec to try again")
        print(repr(e) + "\n")
        time.sleep(1) #sleep for 1 sec to try again

      else:
        break

    if(try_times < 0):
      basic.ErrorReport(repr(ex))
      print("hchs request failed: tried to many times\n")
      return

    page += 1
    
  return result