from unilog import log
import basic

def show_sch(school: str):
	return

def run(line: str):
	split = line.split()
	
	if(len(split) == 0):
		return "error: empty input"
		
	cmd  = split.pop(0)
	args: list = split
	
	if(cmd == "show-sch"):
		show_sch(args[0])
	else:
		return f'error: unknown command {cmd}'
	
	return "ok, cmd function is still under construction, nothing has runned"
