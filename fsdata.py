#  - b: a 1-byte unsigned value, to be converted into a Python int
#  - c: a 1-byte signed value, to be converted into a Python int
#  - h: a 2-byte signed value, to be converted into a Python int
#  - H: a 2-byte unsigned value, to be converted into a Python int
#  - d: a 4-byte signed value, to be converted into a Python int
#  - u: a 4-byte unsigned value, to be converted into a Python long
#  - l: an 8-byte signed value, to be converted into a Python long
#  - L: an 8-byte unsigned value, to be converted into a Python long
#  - f: an 8-byte floating point value, to be converted into a Python double
# main offsets for reading instrumentation.

InstrOffsets = {'Com1Freq': (0x034E,'H'),	# com1freq
        'Com2Freq': (0x3118,'H'),	# com2freq
        'RadioActive': (0x3122,'b'),	# radioActive
        'Lat': (0x0560,'l'),	# ac Latitude
        'Long': (0x0568,'l'),	# ac Longitude
        'Flaps': (0x30f0,'h'),	# flaps angle
        'OnGround': (0x0366,'h'),	# on ground flag: 0 = airborne
        'ParkingBrake': (0x0bc8,'h'),	# parking Brake: 0 off, 32767 on
        'Gear': (0x0be8, 'u'), # Gear control: 0=Up, 16383=Down
        'Altitude': (0x3324,'d'),	#altitude in feet or meters
        'GroundAltitude': (0x0020,'u'),	# ground altitude x 256
        'SpoilersArm': (0x0bcc,'u'),	# spoilers armed: 0 - off, 1 - armed
        'Spoilers': (0x0bd0, 'u'), # Spoilers control, 0 off, 4800 arm, then 5620 (7%) to 16383 (100% fully deployed).
        'AvionicsMaster': (0x2e80, 'u'), # Avionics master switch
        'ApMaster': (0x07bc,'u'), # AP master switch
        'ApNavLock': (0x07c4,'u'), # AP Nav1 lock
        'ApHeadingLock': (0x07c8,'u'), # AP heading lock
        'ApHeading': (0x07cc,'H'), # Autopilot heading value, as degrees*65536/360
        'ApAltitudeLock': (0x07d0,'u'), # AP Altitude lock
        'ApAltitude': (0x07d4,'u'), # Autopilot altitude value, as metres*65536
        'ApSpeedHold': (0x07dc,'u'), # AP airspeed hold
        'ApMachHold': (0x07e4, 'u'), # autopilot mach hold
        'ApAirspeed': (0x07e2,'h'), # AP airspeed in knots
        'ApMach': (0x07e8, 'u'), # Autopilot mach value, as Mach*65536
        'ApVerticalSpeedHold': (0x07ec, 'u'), # autopilot vertical speed hold
        'ApVerticalSpeed': (0x07f2, 'h'), # autopilot vertical speed
        'ApNavGPS': (0x132c,'u'), # nav gps switch: 0 - nav, 1 - GPS
        'ApApproachHold': (0x0800, 'u'), # autopilot approach hold
        'ApFlightDirector': (0x2ee0,'u'), # Flight director: 0 - off, 1 - on
        'ApFlightDirectorPitch': (0x2ee8, 'f'), # flight director pitch
        'ApFlightDirectorBank': (0x2ef0, 'f'), # flight director bank value in degrees. Right negative, left positive
        'ApAttitudeHold': (0x07d8,'u'), # auto-pilot attitude hold switch
        'ApWingLeveler': (0x07c0, 'u'), # auto-pilot wing leveler switch
        'PropSync': (0x243c, 'u'), # propeller sync
        'ApAutoRudder': (0x0278, 'h'), # auto-rudder switch
        'BatteryMaster': (0x281c, 'u'), # battery master swtich
        'Heading': (0x0580,'u'), # Heading, *360/(65536*65536) for degrees TRUE.[Can be set in slew or pause states]
        'MagneticVariation': (0x02a0,'h'), # Magnetic variation (signed, –ve = West). For degrees *360/65536. Convert True headings to Magnetic by subtracting this value, Magnetic headings to True by adding this value.
        'Transponder': (0x0354,'H'), # transponder in BCD format
        'CompassHeading': (0x2b00, 'f'), # Gyro compass heading (magnetic), including any drift. 
        'NextWPDistance': (0x6048,'f'), # distance to next waypoint
        'NextWPId': (0x60a4,-6), # next waypoint string
        'NextWPETE': (0x60e4,'u'), # time enroute to next waypoint in seconds
        'AutoBrake': (0x2f80,'b'), # Panel autobrake switch: 0=RTO, 1=Off, 2=brake1, 3=brake2, 4=brake3, 5=max
        'AirspeedTrue': (0x02b8,'u'), # TAS: True Air Speed, as knots * 128
        'AirspeedIndicated': (0x02bc,'u'), # IAS: Indicated Air Speed, as knots * 128
        'GroundSpeed': (0x02b4, 'u'), # GS: Ground Speed, as 65536*metres/sec. Not updated in Slew mode!
        'ApYawDamper': (0x0808,'u'), # Yaw damper
        'Toga': (0x080c,'u'), # autothrottle TOGA
        'AutoThrottleArm': (0x0810,'u'), # Auto throttle arm
        'AutoFeather': (0x2438, 'u'), # Auto Feather switch
        'AirspeedMach': (0x11c6,'h'), # Mach speed *20480
        'NextWPETA': (0x60e8,'u'), # next waypoint ETA in seconds (localtime)
        'NextWPBaring': (0x6050,'f'), # magnetic baring to next waypoint in radions
        'DestAirportId': (0x6137,-5), # destination airport ID string
        'DestETE': (0x6198,'u'), # time enroute to destination in seconds
        'DestETA': (0x619c,'u'), # Destination ETA in seconds (localtime)
        'RouteDistance': (0x61a0,'f'), # route total distance in meters
        'FuelBurn': (0x61a8,'f'), # estimated fuel burn in gallons
        'FuelQuantity': (0x126c, 'u'), # Fuel: total quantity weight in pounds (32-bit integer)
        'ElevatorTrim': (0x2ea0, 'f'), # elevator trim deflection in radions
        'VerticalSpeed': (0x0842, 'h'), # 2 byte Vertical speed in metres per minute, but with –ve for UP, +ve for DOWN. Multiply by 3.28084 and reverse the sign for the normal fpm measure.
        'AirTemp': (0x0e8c, 'h'), # Outside air temp Outside Air Temperature (OAT), degrees C * 256 (“Ambient Temperature
        'Nav1GS': (0x0c4c, 'b'), # nav 1 GS alive flag
        'Nav1Flags': (0x0c4d, 'b'), # nav 1 code flags
        'Nav1Signal': (0x0c52, 'u'), # Nav 1 signal strength
        'Nav1LocNeedle': (0x0c48, 'c'), # nav 1 localiser needle: -127 left to 127 right
        'Nav1GSNeedle': (0x0c49, 'c'), # Nav1 glideslope needle: -119 up to 119 down
        'Altimeter': (0x0330, 'H'), # Altimeter pressure setting (“Kollsman” window). As millibars (hectoPascals) * 16
        'Doors': (0x3367, 'b'), # byte indicating open exits. One bit per door.
        'APUGenerator': (0x0b51, 'b'), # apu generator switch
        'APUGeneratorActive': (0x0b52, 'b'), # apu generator active flag
        'APUPercentage': (0x0b54, 'F'), # APU rpm percentage
        'APUVoltage': (0x0b5c, 'F'), # apu generator voltage
        'Eng1RPM': (0x2400, 'f'), # engine 1 rpm
        'Eng1Starter': (0x3b00, 'u'), # engine 1 starter
        'Eng2Starter': (0x3a40, 'u'), # engine 2 starter
        'Eng3Starter': (0x3980, 'u'), # engine 3 starter
        'Eng4Starter': (0x38c0, 'u'), # engine 4 starter
        'Eng1FuelFlow': (0x2060, 'f'), # Engine 1 fuel flow in pounds per hour
        'Eng2FuelFlow': (0x2160, 'f'), # Engine 2 fuel flow in pounds per hour
        'Eng3FuelFlow': (0x2260, 'f'), # Engine 3 fuel flow in pounds per hour
        'Eng4FuelFlow': (0x2360, 'f'), # Engine 1 fuel flow in pounds per hour
        'Eng1N1': (0x2010, 'f'), # Engine 1 n1 value
        'Eng4Generator': (0x393c, 'u'), # Engine 4 generator
        'Eng3Generator': (0x39fc, 'u'),  # Engine 3 generator
        'Eng2Generator': (0x3abc, 'u'), # Engine 2 Generator
        'Eng1Generator': (0x3b7c, 'u'),  # Engine 1 generator
        'Eng1N2': (0x2018, 'f'), # Engine 1 N2 value
        'Eng2N1': (0x2110, 'f'), # Engine 2 N1 value
        'Eng2N2': (0x2118, 'f'), # Engine 2 N2 value
        'Eng3N1': (0x2210, 'f'), # Engine 3 N1 value
        'Eng3N2': (0x2218, 'f'), # Engine 3 N2 value
        'Eng4N1': (0x2310, 'f'), # Engine 4 N1 value
        'Eng4N2': (0x2318, 'f'), # Engine 4 N2 value
        'Eng1Combustion': (0x0894, 'H'), # Engine 1 ignition flag
        'Eng2Combustion': (0x092c, 'H'), # Engine 2 ignition flag
        'Eng3Combustion': (0x09c4, 'H'), # Engine 3 ignition flag
        'Eng4Combustion': (0x0a5c, 'H'), # Engine 4 ignition flag
        'Eng1ITT': (0x08f0, 'u'), # Engine 1 Turbine temperature: degree C *16384 (Helos?) (Turbine engine ITT)
        'Eng2ITT': (0x0988, 'u'), # Engine 2 Turbine temperature: degree C *16384 (Helos?) (Turbine engine ITT)
        'Eng3ITT': (0x0a20, 'u'), # Engine 3 Turbine temperature: degree C *16384 (Helos?) (Turbine engine ITT)
        'Eng4ITT': (0x0ab8, 'u'), # Engine 4 Turbine temperature: degree C *16384 (Helos?) (Turbine engine ITT)
        'Eng1FuelValve': (0x3590, 'u'), # engine 1 fuel valve
        'Eng2FuelValve': (0x3594, 'u'), # engine 2 fuel valve
        'Eng3FuelValve': (0x3598, 'u'), # engine 3 fuel valve
        'Eng4FuelValve': (0x359c, 'u'), # engine 4 fuel valve


        'PitotHeat': (0x029c, 'b'), # pitot heat switch
        'Lights1': (0x0d0c, 'b'), # lights
        'Lights': (0x0d0d, 'b'), # lights
        'WindSpeed': (0x0e90, 'H'), # Ambient wind speed in knots
        'WindDirection': (0x0e92, 'H'), # Ambient wind direction (at aircraft), *360/65536 to get degrees True.
        'WindGust': (0x0e94, 'H'), # At aircraft altitude: wind gusting value: max speed in knots, or 0 if no gusts
        'RadioAltimeter': (0x31e4, 'u'), # Radio altitude in metres * 65536
        'AircraftName': (0x3d00, -255), # aircraft name
        'TextDisplay': (0x3380, -128), # FSUIPC text display
        'FuelPump': (0x3104, 'b'), # fuel pump
        'lvl_center': (0x0b74, 'u'),
        'cap_center': (0x0b78, 'u'),
        'lvl_center2': (0x1244, 'u'),
        'cap_center2': (0x1248, 'u'),
        'lvl_center3': (0x124c, 'u'),
        'cap_center3': (0x1250, 'u'),
        'lvl_main_left': (0x0b7c, 'u'),
        'cap_main_left': (0x0b80, 'u'),
        'lvl_aux_left': (0x0b84, 'u'),
        'cap_aux_left': (0x0b88, 'u'),
        'lvl_tip_left': (0x0b8c, 'u'),
        'cap_tip_left': (0x0b90, 'u'),
        'lvl_main_right': (0x0b94, 'u'),
        'cap_main_right': (0x0b98, 'u'),
        'lvl_aux_right': (0x0b9c, 'u'),
        'cap_aux_right': (0x0ba0, 'u'),
        'lvl_tip_right': (0x0ba4, 'u'),
        'cap_tip_right': (0x0ba8, 'u'),
        'fuel_weight': (0x0af4, 'H'),
        'num_engines': (0x0aec, 'H'),
        'eng1_fuel_flow': (0x0918, 'f'),
        'eng2_fuel_flow': (0x09b0, 'f'),
        'eng3_fuel_flow': (0x0a48, 'f'),
        'eng4_fuel_flow': (0x0ae0, 'f'),
        'EngineSelectFlags': (0x0888, 'b'), # engine select flags
        'GyroSuction': (0x0b18, 'f'), # gyro suction gauge
        'OilQuantity': (0x66c9, 'b'),















}
# offsets for A2A Bonanza
BonanzaOffsets = {
    "BatterySwitch": (0x66c0, 'b'), # a2a battery switch
    'TipTankLeftPump': (0x66c1, 'b'), # left tip tank pump
    'TipTankRightPump': (0x66c2, 'b'), # right tip tank pump
    'FuelSelector': (0x66c3, 'b'), # a2a fuel selector
    'TipTanksAvailable': (0x66c4, 'b'), # tip tanks avaiable
    'window': (0x66c5, 'b'), # a2a windows
    'fan': (0x66c6, 'b'), # a2a cabin fan
    'CabinHeat': (0x66c7, 'b'),
    'defrost': (0x66c8, 'b'),

}
# offsets for A2A Cherokee
CherokeeOffsets = {
    "BatterySwitch": (0x66c0, 'b'), # a2a battery switch
    'FuelSelector': (0x66c1, 'b'), # a2a fuel selector
    'window': (0x66c2, 'b'), # a2a windows
    'CabinHeat': (0x66c3, 'b'),
    'defrost': (0x66c4, 'b'),
    'CarbHeat': (0x66c5, 'b'), 
}
a2a_payload = {}




# Offsets for SimConnect messages.
SimCOffsets = {'SimCChanged': (0xb000,'u'), # changed indicator (4 bytes)
    'SimCType': (0xb004,'u'), # type value (4 bytes)
    'SimCDuration': (0xb008,'u'), # display duration in secs (4 bytes)
    'SimCEvent': (0xb00c,'u'), # SimConnect event ID (4 bytes)
    'SimCLength': (0xb010,'u'), # length of data received (4 bytes)
    'SimCData': (0xb014,2028), # text data (<= 2028 bytes)
}
# attitude indication offsets, since we need fast access to these
AttitudeOffsets = {'Pitch': (0x0578,'d'), # Pitch, *360/(65536*65536) for degrees. 0=level, –ve=pitch up, +ve=pitch down[Can be set in slew or pause states]
    'Bank': (0x057c,'d'), # Bank, *360/(65536*65536) for degrees. 0=level, –ve=bank right, +ve=bank left[Can be set in slew or pause states]


}
