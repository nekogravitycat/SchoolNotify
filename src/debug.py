from src import basic, daily


def main():
	action: str = input("Action to execute: ")

	if not action or action == "help":
		print("Available actions: run, debug, schedule_run")
		return

	if input(f'Are you sure you want to execute the action "{action}"? [y/n]:') != "y":
		return

	if action == "run":
		basic.run()

	elif action == "debug":
		basic.debug()

	elif action == "schedule_run":
		daily.schedule_run()

	else:
		print(f'Action "{action}" is invalid')

	print(f'debug: Action "{action}" done!')


if __name__ == "__main__":
	main()
