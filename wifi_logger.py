#!/usr/bin/env python3

from datetime import datetime, timedelta
import sys
from wifi_analyser import find_devices as find_devices

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
	if len(sys.argv) > 1:
		max_delay = timedelta(minutes=int(sys.argv[1]))
	else:
		max_delay = timedelta(minutes=15)

	if len(sys.argv) > 2:
		visible_output = bool(sys.argv[2])
	else:
		visible_output = True

	if len(sys.argv) > 3:
		ask_each_scan = bool(sys.argv[3])
	else:
		ask_each_scan = False

	return [max_delay, visible_output, ask_each_scan]

connection_pin = 21
active_pin = 18

my_macAddr = "70:ec:e4:6b:4b:ee" # mac address de mon iPhone

connection_status = False
wifi_status = False
false_counts = 0

time0 = datetime.now()
[max_delay, visible_output, ask_each_scan] = check_sys_argv()
longest_delay = timedelta(seconds=0)
keep_on = "y"

if visible_output:
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(connection_pin, GPIO.OUT)
	GPIO.setup(active_pin, GPIO.OUT)

print("Max delay = ", max_delay)

while keep_on == "y":

	scanned_addr = find_devices()

	[connection_status, wifi_status, time0, longest_delay, false_counts] = update_device(my_macAddr, scanned_addr, connection_status, wifi_status, time0, max_delay, longest_delay, false_counts)

	if visible_output:
		GPIO.output(connection_pin, connection_status)
		GPIO.output(active_pin, wifi_status)

	print("iPhone Connected: ", connection_status)
	print("iPhone wifi active: ", wifi_status)
	print("Longest delay yet: ", longest_delay)
	print("Current delay: ", datetime.now() - time0, "\n")

	if ask_each_scan == True:
		keep_on = input("Keep on watching? (Y/n):")

if visible_output:
	GPIO.cleanup()

