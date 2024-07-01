
from builtins import object

from pymavlink.dialects.v10 import ardupilotmega as mavlink1
from pymavlink.dialects.v20 import ardupilotmega as mavlink2

from pymavlink import mavutil

from loguru import logger
import time

#PYTHON JEST SERWEREM PO STRONIE BLUEOS TRZEBA KONFIGURACAĆ ENDPOINT JAKO CLIENT
#OKAZUJE SIĘ ZE TYLKO SERWER JEST W STANIE ODBIERAC DANE MAVLINK MOZE TO KWESTIA
#UDPIN LUB OUT ???
#przechwytuje wiagomosci GLOBAL_POSITION_INT na mavlinku z systemu o podanym ID/
#i komponetu o podanym ID, dla 0 - z całego systemu
class _VehicleGpsLocal:

	def __init__(self, ip: str = "localhost", port: int = 14560, VehicleSysID: int = 1, VehicleCompID: int  = 1):
		self.ip = ip
		self.port = port
						#server
		self.master = mavutil.mavlink_connection('udpin:'+self.ip+':'+str(self.port))
		if not self.master:
			logger.warning("Connection error: no connect")
			return
		self.master.Accept_IDsystem = VehicleSysID		#akceptujemy tylko ramki z systemu o podanym ID 
		self.master.Accept_IDcomponent = VehicleCompID		#akceptyjemy tylko tamki z componetu o podanym ID 
		self.timeBootMS = 0
		self.lat = 0
		self.lon = 0
		self.alt = 0
		self.relative_alt = 0
		self.vx = 0
		self.vy = 0
		self.vz = 0
		self.hdg = 0

	def catchGpsLocalPos(self):
		try:
			msg = self.master.recv_match(type='GLOBAL_POSITION_INT',blocking=True)
			if not msg:
				logger.warning("Not exist message")
				return
			if msg.get_type() == "BAD_DATA":
				logger.warning("Last message: BAD_DATA")
				if mavutil.all_printable(msg.data):
					sys.stdout.write(msg.data)
					sys.stdout.flush()
			else:
				#Message is valid
				# Use the attribute
				IDsystemFromMsg = msg.get_srcSystem()
				IDcomponentFromMsg = msg.get_srcComponent()
				print ("SrcSystem from msg: ", IDsystemFromMsg)
				print ("SrcCOmponent from msg: ", IDcomponentFromMsg)
				print ("MSG: ", msg)
				if IDsystemFromMsg == self.master.Accept_IDsystem and IDcomponentFromMsg == self.master.Accept_IDcomponent:
					logger.info('GLOBAL_POSITION_INT - new message received:')
					self.lastMsg = msg
					self.timeBootMS = msg.time_boot_ms
					self.lat = msg.lat
					self.lon = msg.lon
					self.alt = msg.alt
					self.relative_alt = msg.relative_alt
					self.vx = msg.vx
					self.vy = msg.vy
					self.vz = msg.vz
					self.hdg = msg.hdg

		except:
			 logger.warning('GLOBAL_POSITION_INT - not message receive')

	def printGpsLocalPos(self):
		print("Time Boot [ms]: ", self.timeBootMS)
		print("LAT: ", self.lat)
		print("LON: ", self.lon)
		print("ALT: ", self.alt)
		print("RELATIVE_ALT: ", self.relative_alt)
		print("VX: ", self.vx)
		print("VY: ", self.vy)
		print("VZ: ", self.vz)
		print("HDG: ", self.hdg)

	def retLastGpsLocalList(self):
		return self.lastMsg


#TEST
#SurfGps = _VehicleGpsLocal()
#last_position_update = 0
#update_period = 1 #USBL wysyła pingi co sek. wiec nie ma sensu częściej aktualizować pozycje

#while True:
#	if time.time()>last_position_update + update_period:
#		last_position_update = time.time()
#		SurfGps.catchGpsLocalPos()
#		SurfGps.printGpsLocalPos()


