from unilog import log
import basic
import schools

def show_sch(id: str):
	if(not schools.is_valid(id)):
		return f"error: invaild school id '{id}'"
	basic.debug([id])
	return "done!"

def run(line: str):
	split = line.split()
	
	if(len(split) == 0):
		return "error: empty input"
		
	cmd  = split.pop(0)
	args: list = split
	
	if(cmd == "show-sch"):
		return show_sch(args[0])
	else:
		return f'error: unknown command {cmd}'
	
	return "ok, cmd function is still under construction, nothing has runned"
