from replit import db


def get_token(school: str, email: str) -> str:
  db[f"{school}_email_{email}"]


def set_token(school: str, email:str, token: str):
  db[f"{school}_email_{email}"] = token


def list_token(school: str) -> tuple:
  return db.prefix(f"{school}_email")


def exist_token(school: str, email: str) -> bool:
  return (f"{school}_email_{email}" in list_token(school))


def del_token(school: str, email: str):
  del db[f"{school}_email_{email}"]


def get_info(school: str, info: str) -> str:
  return db[f"{school}_latest_{info}"]


def set_info(school: str, info: str, context: str):
  db[f"{school}_latest_{info}"] = context


def get_ask(school: str, email: str) -> str:
  return db[f"ask_{school}_{email}"]


def set_ask(school: str, email: str, token: str):
  db[f"ask_{school}_{email}"] = token


def list_ask(school: str = "") -> tuple:
  if(school == ""):
    return db.prefix("ask")
  
  else:
    return db.prefix(f"ask_{school}")


def exist_ask(school: str, email: str) -> bool:
  return (f"ask_{school}_{email}" in list_ask(school))


def del_ask(school: str, email: str):
  del db[f"ask_{school}_{email}"]


def get_timestamp() -> str:
  return db["timestamp"]


def set_timestamp(stamp: str):
  db["timestamp"] = stamp