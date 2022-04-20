import time
import requests
import bs4
import re
import basic
import mydb
from unilog import log


def get_newsid(sch_url: str, sch_uid: str, pageNum: int = 0, maxRows: int = 15) -> list:
	send_data: dict = {
		"field" : "time",
		"order" : "DESC",
		"pageNum" : str(pageNum),
		"maxRows" : str(maxRows),
		"keyword" : "",
		"uid" : sch_uid,
		"tf" : "1", #"tf" means "the fuck?"
		"auth_type" : "user"
	}
	responce: requests.Response = requests.post(url = f"https://{sch_url}/ischool/widget/site_news/news_query_json.php", data=send_data)
	result: list = []
	id: list = re.findall(r'"newsId":"([0-9]*)"', responce.text)

	for i in id:	
		result.append(i)

	return result


def get_news(sch_id: str, sch_url: str, sch_uid: str) -> list:
	log(f"{sch_id} runned", True)

	next: bool = True
	page: int = 0
	result: list = []

	try:
		while(next):
			newsid: list = get_newsid(sch_url, sch_uid, page)

			for id in newsid:
				if(id == mydb.info.get(sch_id, "id")):
					break

				link: str =	f"https://{sch_url}/ischool/public/news_view/show.php?nid={id}"

				response: requests.Response = requests.get(link, headers = basic.header)
				response.encoding = response.apparent_encoding

				soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
				soup.encoding = response.encoding

				title: str = soup.title.string
				date: time.struct_time = time.strptime(soup.find(id = "info_time").text.strip(), "%Y-%m-%d %H:%M:%S")
				latest_date: time.struct_time = time.strptime(mydb.info.get(sch_id, "date"), "%Y-%m-%d")

				if(date >= latest_date):
					result.append(basic.msg(link, title, date))

				else:
					next = False
					break

			page += 1

		if(len(result) > 0):
			mydb.info.set(sch_id, "date", time.strftime("%Y-%m-%d", result[0].date))
			mydb.info.set(sch_id, "id", newsid[0])

		return result
	
	except Exception as e:
		log(f"{sch_id} failed: {repr(e)}", True)
		return None
