#User editable config file. Change triggers here as you see fit.

import PPButtonMon, PPActions
from PPTypes import *
import time

XorgUser = 'ben' #User account Xorg is running on
SoftLockResleepSecs = 5 #Shut the display off again after this amount of time if awoken by an event and NOT the user
HardLockResleepSecs = 30 #After 30 seconds of a wakeup event, if the user hasn't unlocked us, go back to sleep

def CheckForSoftLock(ButtonStates): #Soft press power
	if any([ButtonStates[S].IsPressed for S in (ButtonType.VOLDOWN, ButtonType.VOLUP)]):
		return False #Probably a hard lock

	PowButton = ButtonStates[ButtonType.POWER]
	
	if not PowButton.IsPressed or PowButton.ChangeTime and PowButton.ChangeTime + 2000 < int(time.time_ns() // 1_000_000):
		return False
	
	#Wait for them to let go.
	PPButtonMon.ButtonMonitor.Instance.WaitForButtonState(ButtonType.POWER, False)
	
	if all((PowButton.ChangeTime, PowButton.LastChangeTime)) and PowButton.ChangeTime - PowButton.LastChangeTime <= 75: #Obviously a bug in the kernel driver, nobody's that fast 
		return False
		
	if PPLockState.Instance.HardLocked or PPLockState.Instance.SoftLocked:
		PPActions.PerformUnlock()
	else:
		PPActions.PerformSoftLock()

	return True

def CheckForHardLock(ButtonStates): #Vol down + power at same time
	if PPLockState.Instance.HardLocked:
		return False #Don't re-lock if we're already locked.
	
	Relevant = (ButtonType.VOLDOWN, ButtonType.POWER)
	
	if not all([ButtonStates[S].IsPressed for S in Relevant]):
		return False
	
	for R in Relevant: #Wait for them to let go
		PPButtonMon.ButtonMonitor.Instance.WaitForButtonState(R, False)

	
	PPActions.PerformHardLock()
	return True
	
def CheckForRotate(ButtonStates):
	if PPLockState.Instance.SoftLocked or PPLockState.Instance.HardLocked:
		return False #Don't allow us to do this by accident when it's in our pocket
		
	if not all([not ButtonStates[S].IsPressed for S in ButtonStates]):
		return False #Can't have a button held down to trigger this
	
	VolDown = ButtonStates[ButtonType.VOLDOWN]
	VolUp = ButtonStates[ButtonType.VOLUP]
	
	if not VolDown.ChangeTime or not VolUp.ChangeTime:
		return False
		
	Distance = VolDown.ChangeTime - VolUp.ChangeTime
	
	PushTime = max((VolDown.ChangeTime, VolUp.ChangeTime))
	
	print(f'PUSH TIME {PushTime}')
	if Distance < 0:
		return False
	
	if Distance > 1500 or PushTime + 1000 < (time.time_ns() // 1_000_000): #No longer than 1.5secs distance, and not more than a second ago.
		print(f'Got rejection by {(time.time_ns()//1_000_000) - PushTime + 1000} milliseconds')
		return False
	
	PPActions.PerformRotate()
	
	return True

EventTriggerFuncs = (CheckForHardLock, CheckForSoftLock, CheckForRotate)
