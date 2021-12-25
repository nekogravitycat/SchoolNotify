import os
import requests


def log(data: str):
  print(data)
  try:
    url = "https://UniLog.nekogravitycat.repl.co/log"
    data = {
      "cat": "sn",
      "data": data,
      "token": os.environ["unilog_token"]
    }
    requests.post(url, json=data)
  except:
    pass