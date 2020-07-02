import threading
from enum import IntEnum, auto

class ButtonType(IntEnum):
	INVALID = 0
	POWER = 1
	VOLDOWN = 114
	VOLUP = 115
	MAX = auto()

class ButtonState:
	def __init__(self, Type):
		self.IsPressed = False
		self.ChangeTime = 0
		self.LastChangeTime = 0
		self.__Type = Type
		self.Lock = threading.Lock()
		self.Event = threading.Semaphore()

	def __enter__(self):
		self.Lock.acquire()
		return self

	def __exit__(self, *Discarded):
		self.Lock.release()

	def __repr__(self):
		with self.Lock:
			return f'<ButtonState for {self.Type}, IsPressed: {self.IsPressed}, ChangeTime: {self.ChangeTime}, LastChangeTime: {self.LastChangeTime}>'

	def Wait(self, IsPressed):
		while True:
			with self.Lock:
				if self.IsPressed == IsPressed:
					return
			
			self.Event.acquire()
			
	def Clone(self):
		B = ButtonState(self.Type)

		with self.Lock:
			B.IsPressed = self.IsPressed
			B.ChangeTime = self.ChangeTime
			B.LastChangeTime = self.LastChangeTime

		return B

	@property
	def Type(self):
		return ButtonType(self.__Type)

class PPLockState:
	Instance = None
	
	def __init__(self):
		if self.Instance:
			raise RuntimeError('Class already instantiated')

		self.SoftLocked = False #Screen is off, touch is disabled, cores are in powersave
		self.HardLocked = False #We're in suspend/standby, waiting for a wake event
		self.RightRotated = False #Screen is rotated to the right
		self.LastHardLockWake = 0
		self.LastSoftLock = 0
		self.LastHardLock = 0
		type(self).Instance = self
