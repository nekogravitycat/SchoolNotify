import time
import requests
import bs4
import re
from src import basic, database as db
from src.unilog import log


def get_newsid(sch_url: str, sch_uid: str, page_num, max_rows: int = 15) -> list:
	""" Get a list of news_ids in a selected range

	:param sch_url: domain name of school
	:param sch_uid: uid of school
	:param page_num: current page number
	:param max_rows: max row number to show (optional, 15 by default)
	:return: a list of news_ids
	"""

	send_data: dict = {
		# data required to be sent to the ischool api
		"field": "time",
		"order": "DESC",
		"pageNum": str(page_num),
		"maxRows": str(max_rows),
		"keyword": "",
		"uid": sch_uid,
		"tf": "1",  # "tf" means "the fuck?"
		"auth_type": "user",
	}
	response: requests.Response = requests.post(
		url=f"https://{sch_url}/ischool/widget/site_news/news_query_json.php",
		data=send_data,
	)
	return re.findall(r'"newsId":"([0-9]*)"', response.text)


def get_news(sch_id: str, sch_url: str, sch_uid: str) -> list | None:
	""" Get a list of basic.Msg objects containing the latest news info

	:param sch_id: id of school
	:param sch_url: domain name of school
	:param sch_uid: uid of school
	:return: list of basic.Msg objects
	"""

	log(f"{sch_id} run", True)

	next_: bool = True
	page: int = 0
	result: list = []

	try:
		newsid: list = get_newsid(sch_url, sch_uid, page)
		while next_:

			for ID in newsid:
				# break the loop if the news was already got by us
				if ID == db.info.get_key(sch_id, "id"):
					break

				# the link to the news detail page
				link: str = (
					f"https://{sch_url}/ischool/public/news_view/show.php?nid={ID}"
				)

				# get the detail page
				response: requests.Response = requests.get(link, headers=basic.header)
				response.encoding = response.apparent_encoding

				# parse the detail page
				soup: bs4.BeautifulSoup = bs4.BeautifulSoup(
					response.text, "html.parser"
				)
				soup.encoding = response.encoding

				# get the information
				title: str = soup.title.string
				date: time.struct_time = time.strptime(
					soup.find(id="info_time").text.strip(), "%Y-%m-%d %H:%M:%S"
				)
				latest_date: time.struct_time = time.strptime(
					db.info.get_key(sch_id, "date"), "%Y-%m-%d"
				)

				# prevent it from getting outdated news
				if date >= latest_date:
					result.append(basic.Msg(link, title, date))

				# if all the latest news are gotten, break the loop
				else:
					next_ = False
					break

			# if the latest news are more than a page, increase the page number by 1
			page += 1

		# if the result is not empty, update the latest info
		if len(result) > 0:
			db.info.set_key(sch_id, "date", time.strftime("%Y-%m-%d", result[0].date))
			db.info.set_key(sch_id, "id", newsid[0])

		return result

	except Exception as e:
		log(f"{sch_id} failed: {repr(e)}", True)
		return None
