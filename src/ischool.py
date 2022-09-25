import time
import requests
import bs4
import re
from src import basic, database as db
from src.unilog import log

header: dict = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
	"Chrome/100.0.4896.60 Safari/537.36 "
}


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
	link: str = f"https://{sch_url}/ischool/widget/site_news/news_query_json.php"
	log(f"get_newsid(): request url: {link}")
	response: requests.Response = requests.post(
		url=f"https://{sch_url}/ischool/widget/site_news/news_query_json.php",
		data=send_data,
		headers=header
	)
	log(f"get_newsid(): response from {response.url}: {response}")
	return re.findall(r'"newsId":"([0-9]*)"', response.text)


def get_news(sch_id: str, sch_url: str, sch_uid: str) -> list | None:
	""" Get a list of basic.Msg objects containing the latest news info

	:param sch_id: id of school
	:param sch_url: domain name of school
	:param sch_uid: uid of school
	:return: list of basic.Msg objects
	"""

	log(f"ischool.get_news() run: id={sch_id}, url={sch_url}, uid={sch_uid}", True)

	next_: bool = True
	page: int = 0
	result: list = []

	try:
		news_ids: list = get_newsid(sch_url, sch_uid, page)
		log(f"get_news(): get {len(news_ids)} ids: {news_ids}")

		while next_:

			for news_id in news_ids:
				# break the loop if the news was already got by us
				if news_id == db.info.get_key(sch_id, "id"):
					log(f"get_news(): news_id ({news_id} already got)")
					next_ = False
					break

				# the link to the news detail page
				link: str = f"https://{sch_url}/ischool/public/news_view/show.php?nid={news_id}"
				log(f"get_news(): request url: {link}")
				# get the detail page
				response: requests.Response = requests.get(link, headers=header)
				response.encoding = response.apparent_encoding
				log(f"get_news(): response from {response.url}: {response}")

				# parse the detail page
				soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
				soup.encoding = response.encoding

				# get the information
				title: str = soup.title.string
				date: time.struct_time = time.strptime(soup.find(id="info_time").text.strip(), "%Y-%m-%d %H:%M:%S")
				latest_date: time.struct_time = time.strptime(db.info.get_key(sch_id, "date"), "%Y-%m-%d")

				# prevent it from getting outdated news
				if date >= latest_date:
					result.append(basic.Msg(link, title, date))

				# if all the latest news are gotten, break the loop
				else:
					next_ = False
					break

			# if the latest news are more than a page, increase the page number by 1
			page += 1

			# just to prevent "unused variable" warning
			print(f"ischool: get_news(), next_={next_}; just to prevent 'unused variable' warning")
			# break to prevent infinite loop (optional)
			break

		# if the result is not empty, update the latest info
		if result:
			db.info.set_key(sch_id, "date", time.strftime("%Y-%m-%d", result[0].date))
			db.info.set_key(sch_id, "id", news_ids[0])

		return result

	except Exception as e:
		log(f"{sch_id} failed: {repr(e)}", True)
		return None
