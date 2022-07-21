import time
import requests
import bs4
import re
from src import basic, mydb
from src.unilog import log


#get a list of newids in a selected range
def get_newsid(sch_url: str, sch_uid: str, pageNum: int = 0, maxRows: int = 15) -> list:
	#these are the data required to be sent to the ischool api
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
	return re.findall(r'"newsId":"([0-9]*)"', responce.text)


#get a list of detail info from a given newsids list
def get_news(sch_id: str, sch_url: str, sch_uid: str) -> list:
	log(f"{sch_id} runned", True)

	next: bool = True
	page: int = 0
	result: list = []

	try:
		while(next):
			newsid: list = get_newsid(sch_url, sch_uid, page)

			for id in newsid:
				#break the loop if the news was already got by us
				if(id == mydb.info.get(sch_id, "id")):
					break

				#the link to the news detail page
				link: str =	f"https://{sch_url}/ischool/public/news_view/show.php?nid={id}"

				#get the detail page
				response: requests.Response = requests.get(link, headers = basic.header)
				response.encoding = response.apparent_encoding
				
				#parse the detail page
				soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
				soup.encoding = response.encoding

				#get the information
				title: str = soup.title.string
				date: time.struct_time = time.strptime(soup.find(id = "info_time").text.strip(), "%Y-%m-%d %H:%M:%S")
				latest_date: time.struct_time = time.strptime(mydb.info.get(sch_id, "date"), "%Y-%m-%d")

				#prevent it from getting outdated news
				if(date >= latest_date):
					result.append(basic.msg(link, title, date))

				#if all the latest news are gotten, break the loop
				else:
					next = False
					break

			#if the latest news are more than a page, increase the page number by 1
			page += 1

		#if the result is not empty, update the latest info
		if(len(result) > 0):
			mydb.info.set(sch_id, "date", time.strftime("%Y-%m-%d", result[0].date))
			mydb.info.set(sch_id, "id", newsid[0])

		return result
	
	except Exception as e:
		log(f"{sch_id} failed: {repr(e)}", True)
		return None
