import subprocess
from datetime import datetime, timedelta
import sys

def find_devices():
	scanned_addr = []

	try:
		scan_output =  str(subprocess.check_output(["sudo", "arp-scan", "--interface=wlan0", "--localnet"]))
		scan_output = scan_output.split("\\n")

		for i in range(0, len(scan_output)):
			if "192.168.0." in scan_output[i]:
				split_output = scan_output[i].split("\\t")
				scanned_addr.append(split_output[1])

	except subprocess.CalledProcessError as e:
		print("arp-scan failled, trying again...")

	return scanned_addr

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

if visible_output:
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(connection_pin, GPIO.OUT)
	GPIO.setup(active_pin, GPIO.OUT)

keep_on = "y"

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

