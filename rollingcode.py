import string
import random


def random_str(digits: int) -> str:
  return "".join(random.choices(string.ascii_uppercase + string.digits, k = digits))


code: str = random_str(10)
code_next = random_str(10)


def roll():
  global code, code_next

  code = code_next
  code_next = random_str(10)