from replit import db


class token:
  def get(school: str, email: str) -> str:
    return db[f"{school}_email_{email}"]

  def set(school: str, email:str, token: str):
    db[f"{school}_email_{email}"] = token

  def list(school: str) -> tuple:
    return db.prefix(f"{school}_email")

  def exist(school: str, email: str) -> bool:
    return (f"{school}_email_{email}" in token.list(school))

  def delete(school: str, email: str):
    del db[f"{school}_email_{email}"]


class info:
  def get(school: str, info: str) -> str:
    return db[f"{school}_latest_{info}"]

  def set(school: str, info: str, context: str):
    db[f"{school}_latest_{info}"] = context


class ask:
  def get(school: str, email: str) -> str:
    return db[f"ask_{school}_{email}"]

  def set(school: str, email: str, token: str):
    db[f"ask_{school}_{email}"] = token

  def list(school: str = "") -> tuple:
    if(school == ""):
      return db.prefix("ask")
    
    else:
      return db.prefix(f"ask_{school}")

  def exist(school: str, email: str) -> bool:
    return (f"ask_{school}_{email}" in ask.ask(school))

  def delete(school: str, email: str):
    del db[f"ask_{school}_{email}"]


class timestamp:
  def get() -> str:
    return db["timestamp"]

  def set(stamp: str):
    db["timestamp"] = stamp