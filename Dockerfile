#FROM python:3.9
FROM python:3.9.6-buster

# set a directory for the app
WORKDIR /home/pi/docker_app/USBL

# skopiuj zawartość katalogu app do WORKDIR/app/
COPY app/. app/.

# Use pip as the build frontend

COPY requirements.txt app/

#RUN python -m pip install --upgrade pip 
RUN python -m pip install -r app/requirements.txt

# For gps reading local position:
EXPOSE 14560/udp

# For sending MAVLINK GPS_INPUT to sub vehicle:
#EXPOSE 14562/udp

# Enable udev for detection of dynamically plugged devices
#ENV UDEV=on

LABEL version="v1.0.0"

# Reference:
# 
# 
LABEL permissions='\
{\
	"NetworkMode": "host",\
	"Env": [\
		"SURF_HOST=localhost",\
		"SURF_PORT=14560",\
		"VEHICLE_SYS=1",\
		"VEHICLE_COMP=1"\
		"SUB_HOST=192.168.10.140"\
		"SUB_PORT=14562"\
		"UART_PORT=/dev/ttyS0"\
		"UART_Baud=115200"\
	],\
  	"HostConfig": {\
		"Privileged": true,\
		"Binds":[\
			"/dev:/dev"\
		]\
  	},\
}'
LABEL authors='[\
    {\
        "name": "Slawomir Gradowicz",\
        "email": "sgradowicz@avimot.pl"\
    }\
]'
LABEL company='{\
        "about": "",\
        "name": "Marine Tech S.A.",\
        "email": ""\
    }'
LABEL type="device-integration"
LABEL tags='[\
    "positioning",\
    "navigation",\
    "short-baseline"\
]'
LABEL readme='https://raw.githubusercontent.com/clydemcqueen/wl_ugps_external_extension/{tag}/README.md'
LABEL links='{\
    "website": "https://github.com/calka75/usbl_positions",\
    "support": "https://github.com/calka75/usbl_positions"\
}'
LABEL requirements="core >= 1.1"

#CMD run -t -i --device=/dev/ttyS0
CMD ["python", "/app/main.py --Surf_host $SURF_HOST --Surf_port $SURF_PORT --VehicleSys $VEHICLE_SYS --VehicleComp $VEHICLE_COMP --Sub_host $SUB_HOST --Sub_port $SUB_PORT --UartPort $UART_PORT --UartBaud $UART_Baud "]
#ENTRYPOINT cd /app && python main.py --Surf_host $SURF_HOST --Surf_port $SURF_PORT --VehicleSys $VEHICLE_SYS --VehicleComp $VEHICLE_COMP --Sub_host $SUB_HOST --Sub_port $SUB_PORT --UartPort $UART_PORT --UartBaud $UART_Baud
#--ugps_host $UGPS_HOST --send_rate $SEND_RATE
