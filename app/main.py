
#from builtins import object

#from pymavlink.dialects.v10 import ardupilotmega as mavlink1
#from pymavlink.dialects.v20 import ardupilotmega as mavlink2

#from pymavlink import mavutil
from CatchVehicleLocalGPSParam import _VehicleGpsLocal
from SendVehicleGPSParam import _VehicleGpsLocalSend
from CatchUsblParam import _VehicleUsblParamCatch

from loguru import logger
import time
import argparse
import math


#PYTHON JEST CLIENTEM PO STRONIE BLUEOS TRZEBA KONFIGURACAĆ ENDPOINT JAKO SERWER UDP
#adres serwera domyślnie 192.168.10.140 port 14562
#OKAZUJE SIĘ ZE TYLKO SERWER JEST W STANIE ODBIERAC DANE MAVLINK MOZE TO KWESTIA
#UDPIN LUB OUT ???
#wysyła wiagomosci GPS_INPUT po mavlinku, w pojezdzie trzena ustawić parametr
#GPS_TYPE NA MAV, specyfikacja GPS_INPUT nie pozwala na sprecyzwanie nr systemu i komponetu
#wiec ramki najprawdopodobniej odbierane sa przez wszystkich,
class UsblExtension:

	def __init__(self, args) -> None:
		self.SurfVehicleLocalPositionCatch  = _VehicleGpsLocal(ip = args.Surf_host, port = args.Surf_port, 
										VehicleSysID = args.VehicleSys, VehicleCompID = args.VehicleComp)
		self.SubVehicleGpsUsblPositionSending = _VehicleGpsLocalSend(ip = args.Sub_host, port = args.Sub_port)
		self.UsblSerialPositionCatch = _VehicleUsblParamCatch(port = args.UartPort, baud = args.UartBaud)
		self.last_position_update = 0
		#self.update_period = 1 #USBL wysyła pingi co sek. wiec nie ma sensu częściej aktualizować pozycje
		self.update_period = 1 #USBL wysyła pingi co sek. wiec nie ma sensu częściej aktualizować pozycje
		#testowo symulacja ruchu - docelowo usunąć
		self.step = 0
		logger.info("inicjacja klasy UsblExtension")


	def run(self):
		#try:
		if True:
			while True:
				if time.time()>self.last_position_update + self.update_period:
					self.last_position_update = time.time()
					logger.info("Jestem w run kalsy UsblExtension")
					self.SurfVehicleLocalPositionCatch.catchGpsLocalPos() #update lokalnych zmiennych  pozycji GPS z pojazdu nawodnego
					self.UsblSerialPositionCatch.catchUsblLocalPos()	#update lokalnych zmiennych pozycji USBL z pojazdu podwodnego

					gpsLocalSurfPosition = self.SurfVehicleLocalPositionCatch.retLastGpsLocalList() #odczyt pozycji GPS
					#odczyt pozycji GPS pojazdu nawodnego
					Latitude_RX = gpsLocalSurfPosition.lat
					Longitude_RX = gpsLocalSurfPosition.lon
					#odcyt pozycji USBL pojazdu podwodnego
					Azimuth = self.UsblSerialPositionCatch.retUsblParam(
							self.UsblSerialPositionCatch.UsblParamIdx.tb) #AB pozorny namiar (azymut) do nadajnika w stopniach matematycznych
					Elevation = self.UsblSerialPositionCatch.retUsblParam(
							self.UsblSerialPositionCatch.UsblParamIdx.te)
					SlantRange = self.UsblSerialPositionCatch.retUsblParam(
							self.UsblSerialPositionCatch.UsblParamIdx.sr)
					#obliczenia: Wyliczenie współrzędnych pojazdu podwodnego w oparciu o dane z GPS i USBL
					MapRadius = math.cos(math.radians(Elevation)) * SlantRange
					CE = 40074000 		#obwód ziemi w m
					LatMperDeg = CE/360	#ilość m na stopień szerokości geograficznej
					LonMperDeg = LatMperDeg * math.cos(math.radians(Latitude_RX/10000000))
					Latitude_TX = Latitude_RX + (math.sin(math.radians(Azimuth)) * (MapRadius*10000000)/LatMperDeg)
					Longitude_TX  = Longitude_RX  + (math.cos(math.radians(Azimuth)) * (MapRadius*10000000)/LonMperDeg)
					Latitude_TX = int(Latitude_TX)
					Longitude_TX = int(Longitude_TX)
					print ("Azimuth  : ", Azimuth)
					print ("Elevation  : ", Elevation)
					print ("SlantRange: ",  SlantRange)
					print ("MapRadius: ",  MapRadius)
					print ("LatMperDeg: ", LatMperDeg)
					print ("LonMperDeg: ",  LonMperDeg)
					print (" Latitude_TX: ",  Latitude_TX)
					print (" Longitude_TX ",   Longitude_TX)
					#TUTAJ ODCZYTAĆ POZYCJIE Z USBLa I JĄ ODPOWIEDNIO PRZELICZYĆ NA WSPÓŁŻĘDNE
					#I WYSŁAĆ DO SUBa + 5000 wpisane tylko dla testów
					self.step = self.step + 1000
					self.SubVehicleGpsUsblPositionSending.sendGpsLocalPos(Latitude_TX, Longitude_TX)
		#except:
			#logger.warning("Unable to send GPS+USBL position")




if __name__ == "__main__":

	logger.info("Starting BlueOS extension for USBL.")

	parser = argparse.ArgumentParser(description="BlueOS extension for USBL.")

	parser.add_argument('--Surf_host', action="store", type=str, default="localhost",
				help="Adres IP hosta lub localhost który współpracuje z sprzętowym GPSem, w BLUEOS Endpoint skonfigurowany jako klient UDP")

	parser.add_argument('--Surf_port', action="store", type=int, default=14560,
				help="Nr portu dla serwera UDP - serwer realizowany przez python")

	parser.add_argument('--VehicleSys', action="store", type=int, default=1,
				help="ID sytemtemu z którym współpracuje sprzętowy GPS")

	parser.add_argument('--VehicleComp', action="store", type=int, default=1,
				help="ID komponentu współpracującego ze sprzętowym GPS")

	parser.add_argument('--Sub_host', action="store", type=str, default="192.168.10.140",
				help="Adres IP hosta do którego zostanie wysłana pozycja uwzględniająca dane z GPS i USBL"+
				"python pracuje jako klient na pojeżdzie docelowym należy skonfigurować endpointa jako serwer UDP")

	parser.add_argument('--Sub_port', action="store", type=int, default=14562,
				help="Nr portu dla nasłuchu serwera UDP - serwer realizowany przez pojazd")

	parser.add_argument('--UartPort', action="store", type=str, default="/dev/ttyS0",
				help="Adres IP hosta do którego zostanie wysłana pozycja uwzględniająca dane z GPS i USBL"+
				"python pracuje jako klient na pojeżdzie docelowym należy skonfigurować endpointa jako serwer UDP")

	parser.add_argument('--UartBaud', action="store", type=int, default=115200,
				help="Nr portu dla nasłuchu serwera UDP - serwer realizowany przez pojazd")


	args = parser.parse_args()
	logger.info("Jestem przed utworzeniem klasy UsblExtension")
	service = UsblExtension(args)
	service.run()
#SurfGps = _VehicleGpsLocalSend()
#SurfVehicleLocalPosition = _VehicleGpsLocal("localhost", 14560, 1, 1) 
#last_position_update = 0
#update_period = 1 #USBL wysyła pingi co sek. wiec nie ma sensu częściej aktualizować pozycje
#LAT = 496847330
#LON = 217435198 
#while True:
#	if time.time()>last_position_update + update_period:
#		last_position_update = time.time()
#		SurfGps.sendGpsLocalPos(LAT,LON)
#		LAT = LAT + 100



