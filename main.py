#crummy.com/software/BeautifulSoup/bs4/doc/

import os #for replit
import requests
from bs4 import BeautifulSoup

page_to_crawl = 1

for i in range(1, page_to_crawl + 1):
  response = requests.get(f"http://www.{os.environ['host']}/files/501-1000-1001-{i}.php?Lang=zh-tw")

  response.encoding = response.apparent_encoding

  soup = BeautifulSoup(response.text, "html.parser")
  soup.encoding = response.encoding

  #row_01 & row_02 appears alternately, including all information we need

  #in a row there'll be three <td>, first one has the <div> which contains the hyperlink of the article and the title while other two contain the source and the date

  row = soup.find_all("tr", class_ = ["row_01", "row_02"])

  for r in row:
    #hyperlink of the article
    division  = r.select("div")

    for div in division :
      anchor = div.select("a")

      for a in anchor:
        print(a["href"])

    #title, source, and date
    table = r.select("td")

    for td in table:
      print(td.text.strip())
      
    print()

print("done!")
