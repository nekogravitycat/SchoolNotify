import os
import requests


def log(data: str):
  print(data)
  try:
    url = "https://log.nekogc.com/log"
    data = {
      "cat": "sn",
      "data": data,
      "token": os.environ["unilog_token"]
    }
    requests.post(url, json=data)
  except:
    print("UniLog failed")