
import serial
from enum import IntEnum
from loguru import logger
import time


class _VehicleUsblParamCatch:

	class UsblParamIdx(IntEnum):
		ab = 0
		ac = 1
		ae = 2
		sr = 3
		tb = 4
		cb = 5
		te = 6
		er = 7
		ep = 8
		ey = 9
		ch = 10
		db = 11
		ah = 12
		ag = 13
		ls = 14
		im = 15
		oc = 16
		idx = 17
		idq = 18
		hh = 19
		max = 20

	def __init__(self, port: str = "/dev/ttyS0", baud: int = 115200):
		self.port = port
		self.baud = baud

		self.serialPort = serial.Serial(
    			port=self.port, baudrate=self.baud, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
						)
		if not self.serialPort:
			logger.warning("Serial port" + self.port + " open error")

		self.UsblParamList = []
	
	def IsNumeric(self, txt: str = ""):
		try:
			number = float(txt)
			return True
		except ValueError:
			return False

	def retUsblParam(self, idx: int = 0):
		if not self.UsblParamList:
			return 0
		else:
			return self.UsblParamList[idx]

	def catchUsblLocalPos(self):
		serialString = ""
		try:
			serialString = self.serialPort.readline()
			serialString = serialString.decode("Ascii")
			#print (serialString)
			serialString = serialString.strip()		#usuniecie białych znaków ze stringa
			serialString = serialString.replace('*',',')
			serialListString = serialString.split(",")	#przekształcenie stringa w liste stringów
			#print (serialListString)
			if serialListString[0] == "$USRTH":		#sprawdzenie czy pierwszy element listy jest identyfikatorem ramki USBLa
				logger.info("Frame received from USBL")
				print ("RECV: ", serialListString)
				del serialListString[0]			#usnuniecie elementu o idx=0 - $USRTH
				serialListLenght = len(serialListString)	#ilość elemantów listy
				self.UsblParamList.clear()			#wyczyszczenie całej listy
				for i in range(0, serialListLenght):
					if i < self.UsblParamIdx.max:
						if self.IsNumeric(serialListString[i]):
							self.UsblParamList.append(float(serialListString[i])) #dodanie elemantu do listy jako typ float
						else:
							if i == self.UsblParamIdx.hh:	#jesli to CRC - konwertujemy na liczbę dziesiętną
								serialListString[i] = '0x'+serialListString[i]
								self.UsblParamList.append(int(serialListString[i], 0))
							else:	#w przeciwnym wypadku zostawiamy jako string
								self.UsblParamList.append(serialListString[i])		#dodanie elementu do listy jako string
					else:
						logger.warning("Data frame too long was received")
				#print ("USBL_PARAM:")
				#print (self.UsblParamList)
		except:
			logger.warning("Error reading data from the port")

#TEST
#USBLdata = _VehicleUsblParamCatch()
#last_position_update = 0
#update_period = 1 #USBL wysyła pingi co sek. wiec nie ma sensu częściej aktualizować pozycje
#LAT = 496847330
#LON = 217435198 

#while True:
#	if time.time()>last_position_update + update_period:
#		last_position_update = time.time()
#		USBLdata.catchUsblLocalPos()
#		print ("AB from USBL" ,USBLdata.retUsblParam(USBLdata.UsblParamIdx.ab))
#		LAT = LAT + 100



