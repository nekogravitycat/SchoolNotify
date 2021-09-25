import string
import random


def random_str(digits: int) -> str:
  return "".join(random.choices(string.ascii_uppercase + string.digits, k = digits))


key: str = random_str(10)
key_next = random_str(10)


def roll():
  global key, key_next

  key = key_next
  key_next = random_str(10)