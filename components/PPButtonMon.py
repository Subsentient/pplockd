import threading, struct, queue
from PPTypes import *

FormatString = '@nnHHi'
FormatSize = struct.calcsize(FormatString)

class KernelInputEventStruct:
	Fields = ('tv_sec', 'tv_usec', 'type', 'code', 'value')

	def __init__(self, Input):
		Blob = struct.unpack(FormatString, Input)
		assert len(self.Fields) == len(Blob)
		
		for Inc, Field in enumerate(self.Fields):
			setattr(self, Field, Blob[Inc])
		
	@property	
	def MSTime(self):
		return ((self.tv_sec * 1_000_000) + self.tv_usec) // 1000

class ButtonMonitor:
	Instance = None
	
	def __init__(self):
		self.__PowerThread = threading.Thread(target=self.__PowerThreadFunc)
		self.__VolThread = threading.Thread(target=self.__VolThreadFunc)
		self.__ShouldDie = False
		self.__DieLock = threading.Lock()
		self.__ButtonStates = { ButtonType(S) : ButtonState(S) for S in (ButtonType.POWER, ButtonType.VOLDOWN, ButtonType.VOLUP) }
		self.__ButtonEvent = queue.Queue()
		self.__PowerThread.start()
		self.__VolThread.start()
		
		type(self).Instance = self
		
	@property
	def ShouldDie(self):
		with self.__DieLock:
			return bool(self.__ShouldDie)

	@ShouldDie.setter
	def ShouldDie(self, Value):
		with self.__DieLock:
			self.__ShouldDie = Value

	def WaitForChange(self, Timeout = None):
		try:
			return self.__ButtonEvent.get(timeout=Timeout)
		except queue.Empty:
			return None
	
	def __del__(self):
		return #Might be blocking on a read(), just forget about it and let Python deal with it.
		
		self.__ShouldDie = True
		self.__PowerThread.join()
		self.__VolThread.join()

	def __VolThreadFunc(self):
		with open('/dev/input/event1', 'rb') as Desc:
			while not self.ShouldDie:
				Blob = Desc.read(FormatSize)
				
				S = KernelInputEventStruct(Blob)
	
				if not S.type or not S.code: continue #Filter useless data
	
				print(f'Volume button event {S.__dict__}')
	
				with self.__ButtonStates[ButtonType(S.code)] as Button:
					Button.IsPressed = bool(S.value)
					Button.LastChangeTime = Button.ChangeTime
					Button.ChangeTime = S.MSTime
				
				self.__ButtonEvent.put(self.GetButtonStates())
	
		
	def __PowerThreadFunc(self):
		with open('/dev/input/event0', 'rb') as Desc:
			while not self.ShouldDie:
				Blob = Desc.read(FormatSize)
					
				S = KernelInputEventStruct(Blob)
	
				if not S.code: continue #Filter useless data
	
				print(f'Power button event {S.__dict__}')
			
				with self.__ButtonStates[ButtonType.POWER] as Button:
					Button.IsPressed = bool(S.value)
					Button.LastChangeTime = Button.ChangeTime
					Button.ChangeTime = S.MSTime

				self.__ButtonEvent.put(self.GetButtonStates())

	def GetButtonStates(self):
		return { S : self.__ButtonStates[S].Clone() for S in self.__ButtonStates }

