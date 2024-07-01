
from builtins import object

from pymavlink.dialects.v10 import ardupilotmega as mavlink1
from pymavlink.dialects.v20 import ardupilotmega as mavlink2

from pymavlink import mavutil

from loguru import logger
import time


#PYTHON JEST CLIENTEM PO STRONIE BLUEOS TRZEBA KONFIGURACAĆ ENDPOINT JAKO SERWER UDP
#adres serwera domyślnie 192.168.10.140 port 14562
#OKAZUJE SIĘ ZE TYLKO SERWER JEST W STANIE ODBIERAC DANE MAVLINK MOZE TO KWESTIA
#UDPIN LUB OUT ???
#wysyła wiagomosci GPS_INPUT po mavlinku, w pojezdzie trzena ustawić parametr
#GPS_TYPE NA MAV, specyfikacja GPS_INPUT nie pozwala na sprecyzwanie nr systemu i komponetu
#wiec ramki najprawdopodobniej odbierane sa przez wszystkich,
class _VehicleGpsLocalSend:

	def __init__(self, ip: str = "192.168.10.140", port: int = 14562):
		self.ip = ip
		self.port = port

		self.master = mavutil.mavlink_connection('udpout:'+self.ip+':'+str(self.port))
		if not self.master:
			logger.warning("Connection error: no connect")

	def sendGpsLocalPos(self, Lat: int = 0, Lon: int = 0):
		try:
			self.master.mav.gps_input_send(
			0,  # Timestamp (micros since boot or Unix epoch)
			0,  # ID of the GPS for multiple GPS inputs
			# Flags indicating which fields to ignore (see GPS_INPUT_IGNORE_FLAGS enum).
			# All other fields must be provided.
			(mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_HORIZ |
			mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_VERT |
			mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_SPEED_ACCURACY),
			0,  # GPS time (milliseconds from start of GPS week)
			0,  # GPS week number
			3,  # 0-1: no fix, 2: 2D fix, 3: 3D fix. 4: 3D with DGPS. 5: 3D with RTK
			Lat,  # Latitude (WGS84), in degrees * 1E7
			Lon,  # Longitude (WGS84), in degrees * 1E7
			0,  # Altitude (AMSL, not WGS84), in m (positive for up)
			1,  # GPS HDOP horizontal dilution of position in m
			1,  # GPS VDOP vertical dilution of position in m
			0,  # GPS velocity in m/s in NORTH direction in earth-fixed NED frame
			0,  # GPS velocity in m/s in EAST direction in earth-fixed NED frame
			0,  # GPS velocity in m/s in DOWN direction in earth-fixed NED frame
			0,  # GPS speed accuracy in m/s
			0,  # GPS horizontal accuracy in m
			0,  # GPS vertical accuracy in m
			7   # Number of satellites visible.
			)
			logger.info("Update new position in vehicle")
			print ("Lat : ", Lat/10000000)
			print ("Lon : ", Lon/10000000)
		except:
			logger.warning("Unable to send GPS+USBL position")

#TEST
#SurfGps = _VehicleGpsLocalSend()
#last_position_update = 0
#update_period = 1 #USBL wysyła pingi co sek. wiec nie ma sensu częściej aktualizować pozycje
#LAT = 496847330
#LON = 217435198 
#while True:
#	if time.time()>last_position_update + update_period:
#		last_position_update = time.time()
#		SurfGps.sendGpsLocalPos(LAT,LON)
#		LAT = LAT + 100



