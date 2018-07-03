import Platform
import StreamClient

if Platform.platform_detect() == 1:
	if Platform.pi_version() != 3:
		print("If you are not using a Raspberry Pi 3, make sure you have a WiFi dongle installed")
	import StreamServer

elif Platform.platform_detect() == 0:
	import StreamClient
