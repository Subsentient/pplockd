import time, traceback

def SetCPUPower(CoreID, Online):
	with open(f'/sys/devices/system/cpu/cpu{CoreID}/online', 'w') as Desc:
		Desc.write(f'{int(Online)}')

def SetCPUPowersave(CoreID, UsePowersave):
	with open(f'/sys/devices/system/cpu/cpu{CoreID}/cpufreq/scaling_governor', 'w') as Desc:
		Desc.write('powersave' if UsePowersave else 'ondemand')

def ActivateSleep():
	try:
		with open('/sys/power/state', 'w') as Desc:
			Desc.write('mem')
	except OSError:
		print('Failed to sleep, path busy?')
		return False
	
	time.sleep(0.25) #Give it a moment, though in my experience it's instant

	return True

def SetSoftLockLED(Lit):
	try:
		with open('/sys/class/leds/green:indicator/brightness', 'w') as Desc:
			Desc.write(f'{int(Lit)}')
	except:
		traceback.print_exc()
		return False
	
	return True
	
def SetHardLockLED(Lit):
	try:
		with open('/sys/class/leds/blue:indicator/brightness', 'w') as Desc:
			Desc.write(f'{int(Lit)}')
	except:
		return False
	
	return True
