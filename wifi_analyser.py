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
