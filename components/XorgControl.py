import subprocess, re, os, sys, pwd, multiprocessing
import PPConfig

def RunAsXorgUser(Username, Func, Args = tuple()):
	Recv, Send = multiprocessing.Pipe()
	
	PID = os.fork()

	if PID > 0: #Parent process
		os.waitpid(PID, 0)

		return Recv.recv()

	User = pwd.getpwnam(Username)

	os.setgid(User.pw_gid)
	os.setuid(User.pw_uid)

	os.putenv('DISPLAY', ':0')
	
	Send.send(Func(*Args))

	os._exit(0) #Child terminates after it's done

	
def _IsMonitorOnImpl():
	Stringy = subprocess.run(['xset', '-q'], capture_output=True).stdout.decode('utf-8')

	return bool(re.match('.*Monitor is On.*', Stringy))
	
def IsMonitorOn():
	return RunAsXorgUser(PPConfig.XorgUser, _IsMonitorOnImpl)

def _FindTSIDImpl():
	Stringy = subprocess.run('xinput', capture_output=True).stdout.decode('utf-8')

	Strings = Stringy.splitlines()

	FoundString = None

	Rx = re.compile('.*Goodix Capacitive TouchScreen.*id\=(\d+).*')

	for Line in Strings:
		R = Rx.search(Line)

		if not R:
			continue

		try:
			if R.group(1).isnumeric():
				return R.group(1)
				
		except:
			continue

def FindTSID():
	return RunAsXorgUser(PPConfig.XorgUser, _FindTSIDImpl)


def __SetTouchscreenPowerImpl(Online):
	PowerString = 'on' if Online else 'off'
	TimeoutString = '0' if Online else str(PPConfig.SoftLockResleepSecs)
	TouchString = '-enable' if Online else '-disable'

	Cmds = (f'xset dpms force {PowerString}',
			f'xset dpms {TimeoutString}',
			f'xinput {TouchString} {FindTSID()}')

	for Cmd in Cmds:
		os.system(Cmd)

def SetTouchscreenPower(Online):
	return RunAsXorgUser(PPConfig.XorgUser, __SetTouchscreenPowerImpl, (Online,))
	
def _SetRightRotationImpl():
	Cmds = ('xrandr --output DSI-1 --rotate right',
			f'xinput set-prop {FindTSID()} "Coordinate Transformation Matrix" 0 1 0 -1 0 1 0 0 1')

	for Cmd in Cmds:
		os.system(Cmd)

def SetRightRotation():
	return RunAsXorgUser(PPConfig.XorgUser, _SetRightRotationImpl)

def _SetNormalRotationImpl():
	Cmds = ('xrandr --output DSI-1 --rotate normal',
			f'xinput set-prop {FindTSID()} "Coordinate Transformation Matrix" 1 0 0 0 1 0 0 0 1')

	for Cmd in Cmds:
		os.system(Cmd)


def SetNormalRotation():
	return RunAsXorgUser(PPConfig.XorgUser, _SetNormalRotationImpl)
