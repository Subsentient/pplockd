import time

def SetCPUPower(CoreID, Online):
	with open(f'/sys/devices/system/cpu/cpu{CoreID}/online', 'w') as Desc:
		Desc.write(f'{int(Online)}')

def SetCPUPowersave(CoreID, UsePowersave):
	with open(f'/sys/devices/system/cpu/cpu{CoreID}/cpufreq/scaling_governor', 'w') as Desc:
		Desc.write('powersave' if UsePowersave else 'ondemand')

def ActivateSleep():
	with open('/sys/power/state', 'w') as Desc:
		Desc.write('mem')
	
	time.sleep(0.25) #Give it a moment, though in my experience it's instant
	

