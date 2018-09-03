#!/usr/bin/env python3

from datetime import datetime, timedelta
import sys
from wifi_analyser import find_devices as find_devices
import signal

def update_device(mac_addr, scanned_addr, connection_status, wifi_status, time0, max_delay, longest_delay, false_counts):
	if mac_addr in scanned_addr:
		wifi_status = True
		time1 = datetime.now()
		if time1 - time0 > longest_delay and connection_status:
			longest_delay = time1 - time0

		time0 = time1

		connection_status = True

		false_counts = 0
	else:
		wifi_status = False
		false_counts += 1
		if false_counts == 1:
			time0 = datetime.now()
		elif datetime.now() - time0 > max_delay:
			false_counts = 0
			connection_status = False

	return [connection_status, wifi_status, time0, longest_delay, false_counts]

def check_sys_argv():

        default_mac_addr = ""
        default_visible_output = False
        default_ask_each_time = True
        default_max_delay = 15

        with open("./conf.txt") as configs:
            for config in configs:
                if config.startswith("#"):
                    continue

                keyword, value = config.split("=")

                if keyword == "mac_addr":
                    default_mac_addr = value
                if keyword == "DEFAULT_visible_output":
                    default_visible_output = value
                if keyword == "DEFAULT_ask_each_scan":
                    default_ask_each_time = value
                if keyword == "DEFAULT_max_delay":
                    default_max_delay = value

	if len(sys.argv) > 1:
		max_delay = timedelta(minutes=int(sys.argv[1]))
	else:
		max_delay = timedelta(minutes=default_max_delay)

	if len(sys.argv) > 2:
		visible_output = bool(sys.argv[2])
	else:
		visible_output = default_visible_output

	if len(sys.argv) > 3:
		ask_each_scan = bool(sys.argv[3])
	else:
		ask_each_scan = default_ask_each_scan

        if len(sys.argv) > 3:
                mac_addr = str(sys.argv[4])
        else:
                mac_addr = default_mac_addr

	return [max_delay, visible_output, ask_each_scan, mac_addr]

def run_logger():
	scanned_addr = find_devices()

	[connection_status, wifi_status, time0, longest_delay, false_counts] = update_device(mac_addr, scanned_addr, connection_status, wifi_status, time0, max_delay, longest_delay, false_counts)

	if visible_output:
		GPIO.output(connection_pin, connection_status)
		GPIO.output(active_pin, wifi_status)

	print("iPhone Connected: ", connection_status)
	print("iPhone wifi active: ", wifi_status)
	print("Longest delay yet: ", longest_delay)
	print("Current delay: ", datetime.now() - time0, "\n")

	if ask_each_scan == True:
		keep_on = input("Keep on watching? (Y/n):")
        else: keep_on = "y"

        if keep_on = "y": return True
        else: return False

def exit_gracefully(signum, frame):
        signal.signal(signal.SIGINT, original_siginit)

        try:
                if raw_imput("Do you really wish to quit [Y/n]: ").lower().startswith("y"):
                        if visible_output:
                            GPIO.cleanup()
                
                    sys.exit(1)

        except KeyboardInterrupt:
                print("Ok, quitting...")
                if visible_output:
                    GPIO.cleanup()

                sys.exit(1)


# GPIO Variables
connection_pin = 21
active_pin = 18

# Phone status variables
connection_status = False
wifi_status = False
false_counts = 0
time0 = datetime.now()
longest_delay = timedelta(seconds=0)

[max_delay, visible_output, ask_each_scan, mac_addr] = check_sys_argv()

# While loop variable
keep_on = "y"

# Import RPi.GPIO library if visible output is required (LED, relay, etc.)
if visible_output:
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(connection_pin, GPIO.OUT)
	GPIO.setup(active_pin, GPIO.OUT)


############################
### BEGINING OF PROGRAMM ###
############################

print("Max delay = ", max_delay)

if __name__ == "__main__":
    original_siginit = signal.getsignal(signal.SIGINIT)
    signal.signal(signal.SIGINIT, exit_gracefully)
    keep_on = run_logger()
    if keep_on == False:
        if visible_output:
            GPIO.cleanup()
            sys.exit(1)
