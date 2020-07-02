
import KernelControl, XorgControl
from PPTypes import PPLockState
import time

def PerformSoftLock():
	State = PPLockState.Instance

	XorgControl.SetTouchscreenPower(False)
	
	for CoreID in range(1, 4):
		KernelControl.SetCPUPower(CoreID, False)
		
	KernelControl.SetCPUPowersave(0, True)

	State.SoftLocked = True
	State.LastSoftLock = int(time.time())
	
	print('Soft locked PinePhone')
	
def PerformHardLock():
	if not PPLockState.Instance.SoftLocked: #Don't do it all over again for no good reason
		PerformSoftLock()

	PPLockState.Instance.HardLocked = True
	PPLockState.Instance.LastHardLock = int(time.time())

	print('Performing hard lock')

	KernelControl.ActivateSleep()

	print('Woken from hard lock')

	PPLockState.Instance.LastHardLockWake = int(time.time())
	
def PerformUnlock():
	State = PPLockState.Instance

	State.HardLocked = False
	State.SoftLocked = False

	for CoreID in range(4):
		KernelControl.SetCPUPower(CoreID, True)
		KernelControl.SetCPUPowersave(CoreID, False)

	XorgControl.SetTouchscreenPower(True)

	print('Unlocked PinePhone')


def PerformRotate():
	if PPLockState.Instance.RightRotated:
		XorgControl.SetNormalRotation()
		print('Rotated to portrait orientation')
	else:
		XorgControl.SetRightRotation()
		print('Rotated to landscape orientation')
	
	PPLockState.Instance.RightRotated = not PPLockState.Instance.RightRotated
	
