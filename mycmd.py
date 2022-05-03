from unilog import log
import basic
import schools


def debug_sch(id: str):
	if(not schools.is_valid(id)):
		return f"error: invaild school id '{id}'"
	basic.debug([id])
	return "done!"


def run(line: str, token: str):
	log(f"received cmd:\n'{line}'\ntoken:'{token}'")
	#verifying user
	if(not basic.verify_totp(token)):
		log(f"error: token '{token}' is invaild")
		return "error: token is invaild"
	
	split = line.split()
	
	if(len(split) == 0):
		return "error: empty input"
		
	cmd = split.pop(0)
	args: list = split
	
	if(cmd == "debug-sch"):
		return show_sch(args[0])
		
	elif(cmd == "help"):
		return "1. debug-sch [id]: run a school without sending mails"
	
	else:
		log(f"error: unknown command '{cmd}'")
		return f"error: unknown command '{cmd}'"