import sys
import os
import pyuipc
import config
import threading
import queue
import time
import requests
import copy
from aviationFormula.aviationFormula import calcBearing
from babel import Locale
from babel.dates import get_timezone, get_timezone_name
from math import degrees, floor
import pyglet
import numpy as np
from pubsub import pub
## Main Class of tfm.
class TFM(threading.Thread):
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
            'PitotHeat': (0x029c, 'b'), # pitot heat switch
            'Lights1': (0x0d0c, 'b'), # lights
            'Lights': (0x0d0d, 'b'), # lights
            'WindSpeed': (0x0e90, 'H'), # Ambient wind speed in knots
            'WindDirection': (0x0e92, 'H'), # Ambient wind direction (at aircraft), *360/65536 to get degrees True.
            'WindGust': (0x0e94, 'H'), # At aircraft altitude: wind gusting value: max speed in knots, or 0 if no gusts
            'RadioAltimeter': (0x31e4, 'u'), # Radio altitude in metres * 65536













    }

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
    ## Setup the tfm object.
    def __init__(self,queue):
        global keyboard_handler
        threading.Thread.__init__(self)
        self.q = queue
    def run(self):
        # Init logging.
        # self.logger = VaLogger(os.path.join(self.rootDir,'voiceAtis','logs'))
        # First log message.
        # self.logger.info('TFM started')
        self.read_config()
        # Establish pyuipc connection
        while True:
            try:
                self.pyuipcConnection = pyuipc.open(0)
                self.pyuipcOffsets = pyuipc.prepare_data(list(self.InstrOffsets.values()))
                self.pyuipcSIMC = pyuipc.prepare_data(list (self.SimCOffsets.values()))
                self.pyuipcAttitude = pyuipc.prepare_data(list (self.AttitudeOffsets.values()))
                # self.logger.info('FSUIPC connection established.')
                break
            except NameError:
                self.pyuipcConnection = None
                break
            except Exception as e:
                logging.error('error initializing fsuipc: ' + str(e))
                time.sleep(20)
        
        # variables to track states of various aircraft instruments
        self.oldTz = 'none' ## variable for storing timezone name
        self.airborne = False
        self.oldWP = None

        self.oldSimCChanged = None
        self.oldGear = 16383
        self.oldRCMsg = None
        self.GSDetected = False
        self.LocDetected = False
        self.HasGS = False
        self.HasLoc = False
        self.oldHPA = 0
        self.groundSpeed =False
        self.Eng1FuelFlow = False
        self.Eng2FuelFlow = False
        self.Eng3FuelFlow = False
        self.Eng4FuelFlow = False
        self.Eng1N1 = False
        self.Eng1N2 = False
        self.Eng2N1 = False
        self.Eng2N2 = False
        self.Eng3N1 = False
        self.Eng3N2 = False
        self.Eng4N1 = False
        self.Eng4N2 = False
        self.APUStarting = False
        self.APUShutdown = False
        self.APURunning = False
        self.APUGenerator = False
        self.APUOff = True
        
        # grab a SAPI interface so we can use it periodically
        # self.sapi5 = sapi5.SAPI5()



        # variables for GPWS announcements.
        self.calloutsHigh = [2500, 1000, 500, 400, 300, 200, 100]
        self.calloutsLow = [50, 40, 30, 20, 10]
        # dictionary to track if callouts have been announced
        self.calloutState = {
            2500: False,
            1000: False,
            500: False,
            400: False,
            300: False,
            200: False,
            100: False,
            50: False,
            40: False,
            30: False,
            20: False,
            10: False}
        # variables to track all altitude callouts
        self.altFlag = {}
        for i in range(1000, 65000, 1000):
            self.altFlag[i] = False

        self.trimEnabled = True
        self.MuteSimC = False
        self.CachedMessage = {}
        self.flapsEnabled = True

        # set up tone arrays and player objects for sonification.
        # arrays for holding tone frequency values
        self.DownTones = {}
        self.UpTones = {}
        # envelopes for tone playback
        self.decay = pyglet.media.synthesis.LinearDecayEnvelope()
        self.flat = pyglet.media.synthesis.FlatEnvelope (0.3)

        # grab 200 equal values across a range of numbers for aircraft pitch. Negative number is pitch up.
        self.PitchUpVals = np.around(np.linspace(-0.1, -20, 200), 1)
        self.PitchDownVals = np.around(np.linspace(0.1, 20, 200), 1)
        self.PitchUpFreqs = np.linspace(2, 4, 200)
        self.PitchDownFreqs = np.linspace(1.5, 0.5, 200)
        self.BankFreqs = np.linspace(1, 4, 90)
        self.BankTones = {}
        countDown = 0
        countUp = 0
        for i in np.arange (1.0, 90.0, 1):
            self.BankTones[i] = self.BankFreqs[countUp]
            countUp += 1


        countDown = 0
        countUp = 0

        for i in self.PitchDownVals:
            self.DownTones[i]  = self.PitchDownFreqs[countDown]
            countDown += 1

        for i in self.PitchUpVals:
            self.UpTones[i] = self.PitchUpFreqs[countUp]
            countUp += 1


            

        # track state of various modes
        self.sonifyEnabled = False
        self.manualEnabled = False
        self.directorEnabled = False
        self.APEnabled = False
        # instantiate sound player objects for attitude and flight director modes
        self.PitchUpPlayer = pyglet.media.Player        ()
        self.PitchDownPlayer = pyglet.media.Player()
        self.BankPlayer = pyglet.media.Player()
        # enable looping
        self.PitchUpPlayer.loop = True
        self.PitchDownPlayer.loop = True
        self.BankPlayer.loop = True
        # synthesis media sources for sonification modes
        self.PitchUpSource = pyglet.media.StaticSource (pyglet.media.synthesis.Triangle(duration=10, frequency=440, envelope=self.flat))
        self.PitchDownSource = pyglet.media.StaticSource (pyglet.media.synthesis.Sine(duration=10, frequency=440, envelope = self.flat))
        self.BankSource = pyglet.media.StaticSource (pyglet.media.synthesis.Triangle(duration=0.3, frequency=200, envelope=self.decay))
        # queue the sources onto the players
        self.PitchUpPlayer.queue (self.PitchUpSource)
        self.PitchDownPlayer.queue (self.PitchDownSource)
        self.BankPlayer.queue (self.BankSource)
        self.BankPlayer.min_distance = 10
        
        if self.FFEnabled:
            self.AnnounceInfo(triggered=0, dt=0)
        
        # initially read simulator data so we can populate instrument dictionaries
        self.getPyuipcData()
        
        self.oldInstr = copy.deepcopy(self.instr)
        

        
        # Infinite loop.
        try:
            # Start closest city loop if enabled.
            if self.FFEnabled:
                pyglet.clock.schedule_interval(self.AnnounceInfo, self.FFInterval * 60)
            # Periodically poll for instrument updates. If not enabled, just poll sim data to keep hotkey functions happy
            if self.InstrEnabled:
                pyglet.clock.schedule_interval(self.readInstruments, 1.0)
            else: 
                pyglet.clock.schedule_interval (self.getPyuipcData, 1.0)
            # start simConnect message reading loop
            if self.SimCEnabled:
                pyglet.clock.schedule_interval(self.readSimConnectMessages, 0.5)
            if self.calloutsEnabled:
                pyglet.clock.schedule_interval (self.readCallouts, 0.2)
            # read engine temperatures while engine is starting. Does nothing before and after startup.
            pyglet.clock.schedule_interval(self.readEngTemps, 3)


                
        except KeyboardInterrupt:
            # Actions at Keyboard Interrupt.
            pyuipc.close()
            sys.exit()

        except Exception as e:
            logging.exception('Error during main loop:' + str(e))

    def read_config(self):
            

            self.geonames_username = config.app['config']['geonames_username']
            if self.geonames_username == 'your_username':
                # output = sapi5.SAPI5()
                # output.speak('Error: edit the tfm.ini file and add your Geo names username. exiting!')
                # time.sleep(8)
                # sys.exit(1)
                self.username()

            self.FFInterval = float(config.app['config']['flight_following_interval'])
            self.ManualInterval = float(config.app['config']['manual_interval'])
            self.ILSInterval = float(config.app['config']['ils_interval'])
            self.distance_units = config.app['config']['distance_units']
            self.voice_rate = int(config.app['config']['voice_rate'])
            if config.app['config']['flight_following']:
                self.FFEnabled = True
            else:
                self.FFEnabled = False
                self.q.put('Flight Following  announcements disabled.')
            if config.app['config']['read_instrumentation']:
                self.InstrEnabled = True
            else:
                self.InstrEnabled = False
                self.q.put('instrumentation disabled.')
            if config.app['config']['read_simconnect']:
                self.SimCEnabled = True
            else:
                self.SimCEnabled = False
                self.q.put("Sim Connect messages disabled.")
            if config.app['config']['read_gpws']:
                self.calloutsEnabled = True
            else:
                self.calloutsEnabled = False
            if config.app['config']['read_ils']:
                self.readILSEnabled = True
            else:
                self.readILSEnabled = False
            if config.app['config']['read_groundspeed']:
                self.groundspeedEnabled = True
            else:
                self.groundspeedEnabled = False
            

    def username(self):
        dlg = wx.TextEntryDialog(None, "Please enter your Geonames user name in order to use flight following features.", "GeoNames username")
        dlg.ShowModal()
        config.app['config']['geonames_username'] = dlg.GetValue()
        config.app.write()
        self.geonames_username= config.app['config']['geonames_username']
        

    def manualFlight(self, dt, triggered = 0):
        try:
            pitch = round(self.attitude['Pitch'], 1)
            bank = round(self.attitude['Bank'])
            if bank > 0:
                self.q.put (F'Left {bank}')
            elif bank < 0:
                self.q.put (F'right {abs(bank)}')
            if pitch > 0:
                self.q.put (F'down {pitch}')
            elif pitch < 0:
                self.q.put (F'Up {abs(pitch)}')
        except Exception as e:
            logging.exception (F'Error in manual flight. Pitch: {pitch}, Bank: {bank}' + str(e))
    def set_speed(self, speed):
        # set the autopilot airspeed
        offset, type = self.InstrOffsets['ApAirspeed']
        data = [(offset, type, int(speed))]
        pyuipc.write(data)
    def set_heading(self, heading):
        # set the auto pilot heading
        offset, type = self.InstrOffsets['ApHeading']
        # convert the supplied heading into the proper FSUIPC format (degrees*65536/360)
        heading = int(heading)
        heading = int(heading * 65536 / 360)
        data = [(offset, type, heading)]
        pyuipc.write(data)
    def set_altitude(self, altitude):
        offset, type = self.InstrOffsets['ApAltitude']
        # convert the supplied altitude into the proper FSUIPC format.
        #  FSUIPC needs the altitude as metres*65536
        altitude =int(altitude)
        altitude = int(altitude / 3.28084 * 65536)
        data = [(offset, type, altitude)]
        pyuipc.write(data)
    def set_mach(self, mach):
        # set mach speed
        offset, type = self.InstrOffsets['ApMach']
        # convert the supplied mach value into the proper FSUIPC format.
        #  FSUIPC needs the mach multiplied by 65536
        mach = float(mach) * 65536
        mach = int(mach)
        
        data = [(offset, type, mach)]
        pyuipc.write(data)
    def set_vspeed(self, vspeed):
        # set the autopilot vertical speed
        offset, type = self.InstrOffsets['ApVerticalSpeed']
        data = [(offset, type, int(vspeed))]
        pyuipc.write(data)

    def set_transponder(self, transponder):
        # set the transponder
        offset, type = self.InstrOffsets['Transponder']
        data = [(offset, type, int(transponder, 16))]
        pyuipc.write(data)
    def set_com1(self, com1):
        # set com 1 frequency
        offset, type = self.InstrOffsets['Com1Freq']
        freq = float(com1) * 100
        freq = int(freq) - 10000
        freq = F"{freq}"
        data = [(offset, type, int(freq, 16))]
        pyuipc.write(data)
    def set_qnh(self, qnh):
        offset, type = self.InstrOffsets['Altimeter']
        qnh = int(qnh) * 16
        data = [(offset, type, qnh)]
        pyuipc.write(data)
    def set_inches(self, inches):
        # we need to convert altimeter value to qnh, since that is what the fsuipc expects
        offset, type = self.InstrOffsets['Altimeter']
        qnh = float(inches) * 33.864
        qnh = round(qnh, 1) * 16
        qnh = int(qnh)
        data = [(offset, type, qnh)]
        pyuipc.write(data)



    def sonifyFlightDirector(self, dt):
        try:
            pitch = round(self.instr['ApFlightDirectorPitch'], 1)
            bank = round(self.instr['ApFlightDirectorBank'], 0)
            if pitch > 0 and pitch < 20:
                self.PitchUpPlayer.pause ()
                self.PitchDownPlayer.play()
                self.PitchDownPlayer.pitch = self.DownTones[pitch]
            elif pitch < 0 and pitch > -20:
                self.PitchDownPlayer.pause ()
                self.PitchUpPlayer.play() 
                self.PitchUpPlayer.pitch = self.UpTones[pitch]
            elif pitch == 0:
                self.PitchUpPlayer.pause()
                self.PitchDownPlayer.pause()
            if bank < 0 and bank > -90:
                self.BankPlayer.position = (5, 0, 0)
                self.BankPlayer.play()
                self.BankPlayer.pitch = self.BankTones[abs(bank)]

            if bank > 0 and bank < 90:
                self.BankPlayer.position = (-5, 0, 0)
                self.BankPlayer.play()
                self.BankPlayer.pitch = self.BankTones[bank]


            if bank == 0:
                self.BankPlayer.pause()
        except Exception as e:
            logging.exception (F'Error in flight director. Pitch: {pitch}, Bank: {bank}' + str(e))



        
    def sonifyPitch(self, dt):
        try:
            self.getPyuipcData(3)
            pitch = round(self.attitude['Pitch'], 1)
            bank = round(self.attitude['Bank'])
            if pitch > 0 and pitch < 20:
                self.PitchUpPlayer.pause ()
                self.PitchDownPlayer.play()
                self.PitchDownPlayer.pitch = self.DownTones[pitch]
            elif pitch < 0 and pitch > -20:
                self.PitchDownPlayer.pause ()
                self.PitchUpPlayer.play() 
                self.PitchUpPlayer.pitch = self.UpTones[pitch]
            elif pitch == 0:
                self.PitchUpPlayer.pause()
                self.PitchDownPlayer.pause()
            if bank < 0 and bank > -90:
                self.BankPlayer.position = (5, 0, 0)
                self.BankPlayer.play()
                self.BankPlayer.pitch = self.BankTones[abs(bank)]
            if bank > 0 and bank < 90:
                self.BankPlayer.position = (-5, 0, 0)
                self.BankPlayer.play()
                self.BankPlayer.pitch = self.BankTones[bank]

            if bank == 0:
                self.BankPlayer.pause()
            pyglet.clock.tick()
            pyglet.app.platform_event_loop.dispatch_posted_events()
        except Exception as e:
            logging.exception (F'Error in attitude. Pitch: {pitch}, Bank: {bank}' + str(e))



    def readAltitude(self):
        self.q.put(F'{self.instr["Altitude"]} feet A S L')
        pub.sendMessage('reset', arg1=True)
    def readGroundAltitude(self):
        AGLAltitude = self.instr['Altitude'] - self.instr['GroundAltitude']
        self.q.put(F"{round(AGLAltitude)} feet A G L")
        pub.sendMessage('reset', arg1=True)

    def readFlightFollowing(self):
        pub.sendMessage('reset', arg1=True)
        self.AnnounceInfo()
    def readHeading(self):
        self.q.put(F'Heading: {round(self.headingCorrected)}')
        pub.sendMessage('reset', arg1=True)
    def readTAS(self):
        self.q.put (F'{self.instr["AirspeedTrue"]} knots true')
        pub.sendMessage('reset', arg1=True)
    def readIAS(self):
        self.q.put (F'{self.instr["AirspeedIndicated"]} knots indicated')
        pub.sendMessage('reset', arg1=True)
    def readMach(self):
        self.q.put (F'Mach {self.instr["AirspeedMach"]:0.2f}')
        pub.sendMessage('reset', arg1=True)
    def readVSpeed(self):
        self.q.put (F"{self.instr['VerticalSpeed']:.0f} feet per minute")
        pub.sendMessage('reset', arg1=True)
    def readDest(self):
        self.q.put(F'Time enroute {self.instr["DestETE"]}. {self.instr["DestETA"]}')
        pub.sendMessage('reset', arg1=True)
    def readTemp(self):
        self.q.put (F'{self.tempC:.0f} degrees Celcius, {self.tempF} degrees Fahrenheit')
        pub.sendMessage('reset', arg1=True)
    def readWind(self):
        windSpeed = self.instr['WindSpeed']
        windDirection = round(self.instr['WindDirection'])
        windGust = self.instr['WindGust']
        self.q.put(F'Wind: {windDirection} at {windSpeed} knotts. Gusts at {windGust} knotts.')
        pub.sendMessage('reset', arg1=True)

    def toggleTrim(self):
        if self.trimEnabled:
            self.q.put ('trim announcement disabled')
            self.trimEnabled = False
        else:
            self.trimEnabled = True
            self.q.put ('trim announcement enabled')
        pub.sendMessage('reset', arg1=True)

    def toggleGPWS(self):
        if self.calloutsEnabled:
            self.q.put ('GPWS callouts disabled')
            self.calloutsEnabled = False
        else:
            self.calloutsEnabled = True
            self.q.put ("GPWS callouts enabled")
        pub.sendMessage('reset', arg1=True)

    def toggleMuteSimconnect(self):
        if self.MuteSimC:
            self.q.put ('Sim Connect messages unmuted')
            self.MuteSimC = False
        else:
            self.MuteSimC = True
            self.q.put ('Sim Connect messages muted')
        pub.sendMessage('reset', arg1=True)
    def toggleFlaps(self):
        if self.flapsEnabled:
            self.q.put ("flaps disabled")
            self.flapsEnabled = False
        else:
            self.q.put ("Flaps enabled")
            self.flapsEnabled = True
        pub.sendMessage('reset', arg1=True)
    def toggleILS(self):
        if self.readILSEnabled:
            self.q.put ('I L S info disabled')
            self.readILSEnabled = False
        else:
            self.q.put ('I L S info enabled')
            self.readILSEnabled = True
        pub.sendMessage('reset', arg1=True)
    def toggleDirectorMode(self):
        if self.directorEnabled:
            pyglet.clock.unschedule(self.sonifyFlightDirector)
            self.directorEnabled = False
            self.PitchUpPlayer.pause()
            self.PitchDownPlayer.pause()
            self.BankPlayer.pause ()
            self.q.put ('flight director mode disabled.')
        else:
            pyglet.clock.schedule_interval(self.sonifyFlightDirector, 0.2)
            self.directorEnabled = True
            self.q.put ('flight director mode enabled')
        pub.sendMessage('reset', arg1=True)

    def toggleAutoPilot(self):
        if not self.APEnabled:
            self.q.put (F'Autopilot control enabled')
            self.APEnabled = True
        else:
            self.q.put (F'autopilot control disabled')
            self.APEnabled = False
        pub.sendMessage('reset', arg1=True)
    def toggleManualMode(self):
        if self.manualEnabled:
            pyglet.clock.unschedule(self.manualFlight)
            self.manualEnabled = False
            self.q.put ('manual flight  mode disabled.')
        else:
            pyglet.clock.schedule_interval(self.manualFlight, self.ManualInterval)
            self.manualEnabled = True
            self.q.put ('manual flight mode enabled')
        pub.sendMessage('reset', arg1=True)

    def toggleAttitudeMode(self):
        if self.sonifyEnabled:
            pyglet.clock.unschedule(self.sonifyPitch)
            self.PitchUpPlayer.pause()
            self.PitchDownPlayer.pause()
            self.BankPlayer.pause ()
            self.sonifyEnabled = False
            self.q.put ('attitude mode disabled.')
        else:
            pyglet.clock.schedule_interval(self.sonifyPitch, 0.05)
            self.sonifyEnabled = True
            self.q.put ('attitude mode enabled')
        pub.sendMessage('reset', arg1=True)





    def readCallouts (self, dt=0):
        if self.calloutsEnabled:
            vspeed = self.instr['VerticalSpeed']
            callout = 0
            if vspeed < -50:
                for i in self.calloutsHigh:
                    if self.RadioAltitude <= i + 5 and self.RadioAltitude >= i - 5 and self.calloutState[i] == False:
                        source = pyglet.media.load (F'sounds\\{str(i)}.wav')
                        source.play()
                        self.calloutState[i] = True
                        
                for i in self.calloutsLow:
                    if self.RadioAltitude <= i + 3 and self.RadioAltitude >= i - 3 and self.calloutState[i] == False:
                        source = pyglet.media.load (F'sounds\\{str(i)}.wav')
                        source.play()
                        self.calloutState[i] = True
                        
            
    ## read various instrumentation automatically
    def readInstruments(self, dt):
        flapsTransit = False
        # Get data from simulator
        self.getPyuipcData()

        # detect if aircraft is on ground or airborne.
        if not self.instr['OnGround'] and not self.airborne:
            self.q.put ("Positive rate.")
            pyglet.clock.unschedule(self.readGroundSpeed)
            self.groundSpeed = False
            self.airborne = True
        # landing gear
        if self.instr['Gear'] != self.oldInstr['Gear']:
            if self.instr['Gear'] == 0:
                self.q.put ('Gear up.')
            elif self.instr['Gear'] == 16383:
                self.q.put ('Gear down.')
            self.oldInstr['Gear'] = self.instr['Gear']

        # if flaps position has changed, flaps are in motion. We need to wait until they have stopped moving to read the value.
        if self.flapsEnabled:
            if self.instr['Flaps'] != self.oldInstr['Flaps']:
                flapsTransit = True
                while flapsTransit:
                    self.getPyuipcData()
                    if self.instr['Flaps'] != self.oldInstr['Flaps']:
                        self.oldInstr['Flaps'] = self.instr['Flaps']
                        time.sleep (0.2)
                    else:
                        flapsTransit = False
                self.q.put (F'Flaps {self.instr["Flaps"]:.0f}')
                self.oldInstr['Flaps'] = self.instr['Flaps']
            # announce radio frequency changes
        if self.instr['Com1Freq'] != self.oldInstr['Com1Freq']:
            self.q.put (F"com 1, {self.instr['Com1Freq']}")
        if self.instr['Com2Freq'] != self.oldInstr['Com2Freq']:
            self.q.put (F"com 2, {self.instr['Com1Freq']}")

        # spoilers
        if self.oldInstr['Spoilers'] != self.instr['Spoilers']:
            if self.instr['Spoilers'] == 4800:
                self.q.put ("spoilers armed.")
            elif self.instr['Spoilers'] == 16384:
                self.q.put(f'Spoilers deployed')
            elif self.instr['Spoilers'] == 0:
                if self.oldSpoilers == 4800:
                    self.q.put(F'arm spoilers off')
                else:
                    self.q.put(F'Spoilers retracted')
        if self.oldInstr['ApAltitude'] != self.instr['ApAltitude']:
            self.q.put(F"Altitude set to {round(self.instr['ApAltitude'])}")
        if self.APEnabled:
            if self.oldInstr['ApHeading'] != self.instr['ApHeading']:
                self.q.put (F"{self.instr['ApHeading']} degrees")
            if self.oldInstr['ApAirspeed'] != self.instr['ApAirspeed']:
                self.q.put (F"{self.instr['ApAirspeed']}")
            if self.oldInstr['ApMach'] != self.instr['ApMach']:
                self.q.put (F"mach {self.instr['ApMach']:.2f}")
            if self.oldInstr['ApVerticalSpeed'] != self.instr['ApVerticalSpeed']:
                self.q.put (F"{self.instr['ApVerticalSpeed']} feet per minute")



        # transponder
        if self.instr['Transponder'] != self.oldInstr['Transponder']:
            self.q.put(F'Squawk {self.instr["Transponder"]:x}')
        # next waypoint
        if self.instr['NextWPId'] != self.oldInstr['NextWPId']:
            time.sleep(3)
            self.getPyuipcData()
            self.readWaypoint(0)
            self.oldInstr['NextWPId'] = self.instr['NextWPId']
        # read autobrakes
        if self.instr['AutoBrake'] != self.oldInstr['AutoBrake']:
            if self.instr['AutoBrake'] == 0:
                brake = 'R T O'
            elif self.instr['AutoBrake'] == 1:
                brake = 'off'
            elif self.instr['AutoBrake'] == 2:
                brake = 'position 1'
            elif self.instr['AutoBrake'] == 3:
                brake = 'position 2'
            elif self.instr['AutoBrake'] == 4:
                brake = 'position 3'
            elif self.instr['AutoBrake'] == 5:
                brake = 'maximum'
            self.q.put (F'Auto brake {brake}')
        if self.instr['ElevatorTrim'] != self.oldInstr['ElevatorTrim'] and self.instr['ApMaster'] != 1 and self.trimEnabled:
            if self.instr['ElevatorTrim'] < 0:
                self.q.put (F"Trim down {abs(round (self.instr['ElevatorTrim'], 2))}")
            else:
                self.q.put (F"Trim up {round (self.instr['ElevatorTrim'], 2)}")


        if self.AltHPA != self.oldHPA:
            self.q.put (F'Altimeter: {self.AltHPA}, {self.AltInches / 100} inches')
            self.oldHPA = self.AltHPA
        # read nav1 ILS info if enabled
        if self.readILSEnabled:
            if self.instr['Nav1Signal'] == 256 and self.LocDetected == False and self.instr['Nav1Type']:
                self.sapi5.speak (F'localiser is alive')
                self.LocDetected = True
                pyglet.clock.schedule_interval (self.readILS, self.ILSInterval)
            if self.instr['Nav1GS'] and self.GSDetected == False:
                self.sapi5.speak (F'Glide slope is alive.')
                self.GSDetected = True
                
            
            
            if self.instr['Nav1Type'] and self.HasLoc == False:
                self.sapi5.speak (F'Nav 1 has localiser')
                self.HasLoc = True
            if self.instr['Nav1GSAvailable'] and self.HasGS == False:
                self.sapi5.speak (F'Nav 1 has glide slope')
                self.HasGS = True
        else:
            pyglet.clock.unschedule(self.readILS)
        self.readToggle('PitotHeat', 'Pitot Heat', 'on', 'off')
        self.readToggle('ParkingBrake', 'Parking brake', 'on', 'off')
        self.readToggle('AutoFeather', 'Auto Feather', 'Active', 'off')
        # autopilot mode switches
        self.readToggle ('ApMaster', 'Auto pilot master', 'active', 'off')
        # auto throttle
        self.readToggle ('AutoThrottleArm', 'Auto Throttle', 'Armed', 'off')
        # yaw damper
        self.readToggle('ApYawDamper', 'Yaw Damper', 'active', 'off')
        # Toga
        self.readToggle('Toga', 'take off power', 'active', 'off')
        self.readToggle('ApAltitudeLock', 'altitude lock', 'active', 'off')
        self.readToggle('ApHeadingLock', 'Heading lock', 'active', 'off')
        self.readToggle('ApNavLock', 'nav lock', 'active', 'off')
        self.readToggle('ApFlightDirector', 'Flight Director', 'Active', 'off')
        self.readToggle ('ApNavGPS', 'Nav gps switch', 'set to GPS', 'set to nav')
        self.readToggle('ApAttitudeHold', 'Attitude hold', 'active', 'off')
        self.readToggle('ApWingLeveler', 'Wing leveler', 'active', 'off')
        self.readToggle ('ApAutoRudder', 'Auto rudder', 'active', 'off')
        self.readToggle('ApApproachHold', "approach mode", "active", "off")
        self.readToggle('ApSpeedHold', 'Airspeed hold', 'active', 'off')
        self.readToggle('ApMachHold', 'Mach hold', 'Active', 'off')
        self.readToggle('PropSync', 'Propeller Sync', 'active', 'off')
        self.readToggle ('BatteryMaster', 'Battery Master', 'active', 'off')
        self.readToggle('Door1', 'Door 1', 'open', 'closed')
        self.readToggle('Door2', 'Door 2', 'open', 'closed')
        self.readToggle('Door3', 'Door 3', 'open', 'closed')
        self.readToggle('Door4', 'Door 4', 'open', 'closed')
        self.readToggle('Eng1Starter', 'Number 1 starter', 'engaged', 'off')
        self.readToggle('Eng2Starter', 'Number 2 starter', 'engaged', 'off')
        self.readToggle('Eng3Starter', 'Number 3 starter', 'engaged', 'off')
        self.readToggle('Eng4Starter', 'Number 4 starter', 'engaged', 'off')
        self.readToggle('Eng1Combustion', 'Number 1 ignition', 'on', 'off')
        self.readToggle('Eng2Combustion', 'Number 2 ignition', 'on', 'off')
        self.readToggle('Eng3Combustion', 'Number 3 ignition', 'on', 'off')
        self.readToggle('Eng4Combustion', 'Number 4 ignition', 'on', 'off')
        self.readToggle('Eng1Generator', 'Number 1 generator', 'active', 'off')
        self.readToggle('Eng2Generator', 'Number 2 generator', 'active', 'off')
        self.readToggle('Eng3Generator', 'Number 3 generator', 'active', 'off')
        self.readToggle('Eng4Generator', 'Number 4 generator', 'active', 'off')
        self.readToggle('BeaconLights', 'Beacon light', 'on', 'off')
        self.readToggle('LandingLights', 'Landing Lights', 'on', 'off')
        self.readToggle('TaxiLights', 'Taxi Lights', 'on', 'off')
        self.readToggle('NavigationLights', 'Nav lights', 'on', 'off')
        self.readToggle('StrobeLights', 'strobe lights', 'on', 'off')
        self.readToggle('InstrumentLights', 'Instrument lights', 'on', 'off')
        self.readToggle('APUGenerator', 'A P U Generator', 'active', 'off')
        self.readToggle('AvionicsMaster', 'Avionics master', 'active', 'off')

        if self.groundspeedEnabled:
            if self.instr['GroundSpeed'] > 0 and self.instr['OnGround'] and self.groundSpeed == False:
                pyglet.clock.schedule_interval(self.readGroundSpeed, 3)
                self.groundSpeed = True
            elif self.instr['GroundSpeed'] == 0 and self.groundSpeed:
                pyglet.clock.unschedule(self.readGroundSpeed)

        # read APU status
        if self.instr['APUPercentage'] > 4 and self.APUStarting == False and self.APURunning == False and self.APUShutdown == False and self.APUOff == True:
            self.q.put('A P U starting')
            self.APUStarting = True
            self.APUOff = False
        if self.instr['APUPercentage'] < 100 and self.APURunning:
            self.q.put ('Shutting down A P U')
            self.APURunning = False
            self.APUShutdown = True
        if self.instr['APUPercentage'] == 100 and self.APUStarting:
            self.APUStarting = False
            self.APURunning = True
            self.q.put("apu at 100 percent")
        if self.instr['APUPercentage'] == 0 and self.APUOff == False:
            self.q.put('A P U shut down')
            self.APURunning = False
            self.APUStarting = False
            self.APUShutdown = False
            self.APUOff = True


        if self.instr['APUGenerator'] and self.APUGenerator == False:
            self.q.put (F"{round(self.instr['APUVoltage'])} volts")
            self.APUGenerator = True
        if self.instr['APUGenerator'] == False:
            self.APUGenerator = False


        # read engine status on startup.
        if self.instr['Eng1FuelFlow'] > 10 and self.instr['Eng1Starter'] and self.Eng1FuelFlow == False:
            self.q.put ('Number 1 fuel flow')
            self.Eng1FuelFlow = True
        if self.instr['Eng2FuelFlow'] > 10 and self.instr['Eng2Starter'] and self.Eng2FuelFlow == False:
            self.q.put ('Number 2 fuel flow')
            self.Eng2FuelFlow = True
        if self.instr['Eng3FuelFlow'] > 10 and self.instr['Eng3Starter'] and self.Eng3FuelFlow == False:
            self.q.put ('Number 3 fuel flow')
            self.Eng3FuelFlow = True
        if self.instr['Eng4FuelFlow'] > 10 and self.instr['Eng4Starter'] and self.Eng4FuelFlow == False:
            self.q.put ('Number 4 fuel flow')
            self.Eng4FuelFlow = True
        if self.instr['Eng1N2'] > 5 and self.Eng1N2 == False and self.instr['Eng1Starter']:
            self.q.put ('number 1, 5 percent N2')
            self.Eng1N2 = True
        if self.instr['Eng1N1'] > 5 and self.Eng1N1 == False  and self.instr['Eng1Starter']:
            self.q.put ('number 1, 5 percent N1')
            self.Eng1N1 = True
        if self.instr['Eng2N2'] > 5 and self.Eng2N2 == False  and self.instr['Eng2Starter']:
            self.q.put ('number 2, 5 percent N2')
            self.Eng2N2 = True
        if self.instr['Eng2N1'] > 5 and self.Eng2N1 == False  and self.instr['Eng2Starter']:
            self.q.put ('number 2, 5 percent N1')
            self.Eng2N1 = True
        if self.instr['Eng3N2'] > 5 and self.Eng3N2 == False  and self.instr['Eng3Starter']:
            self.q.put ('number 3, 5 percent N2')
            self.Eng3N2 = True
        if self.instr['Eng3N1'] > 5 and self.Eng3N1 == False  and self.instr['Eng3Starter']:
            self.q.put ('number 3, 5 percent N1')
            self.Eng3N1 = True
        if self.instr['Eng4N2'] > 5 and self.Eng4N2 == False  and self.instr['Eng4Starter']:
            self.q.put ('number 4, 5 percent N2')
            self.Eng4N2 = True
        if self.instr['Eng4N1'] > 5 and self.Eng4N1 == False  and self.instr['Eng4Starter']:
            self.q.put ('number 4, 5 percent N1')
            self.Eng4N1 = True





        # read altitude every 1000 feet
        for i in range (1000, 65000, 1000):
            if self.instr['Altitude'] >= i - 10 and self.instr['Altitude'] <= i + 10 and self.altFlag[i] == False:
                self.q.put (F"{i} feet")
                self.altFlag[i] = True
            elif self.instr['Altitude'] >= i + 100:
                self.altFlag[i] = False
        # maintain state of instruments so we can check on the next run.
        self.oldInstr = copy.deepcopy(self.instr)

    def readEngTemps(self, dt = 0):
        if self.distance_units == '1':
            Eng1Temp = round(9.0/5.0 * self.instr['Eng1ITT'] + 32)
            Eng2Temp = round(9.0/5.0 * self.instr['Eng2ITT'] + 32)
            Eng3Temp = round(9.0/5.0 * self.instr['Eng3ITT'] + 32)
            Eng4Temp = round(9.0/5.0 * self.instr['Eng4ITT'] + 32)
        else:
            Eng1Temp = self.instr['Eng1ITT']
            Eng2Temp = self.instr['Eng2ITT']
            Eng3Temp = self.instr['Eng3ITT']
            Eng4Temp = self.instr['Eng4ITT']
        if self.instr['Eng1Starter'] and self.instr['Eng1Combustion']:
            self.q.put (F"number 1 temp, {Eng1Temp}")
        elif self.instr['Eng2Starter'] and self.instr['Eng2Combustion']:
            self.q.put (F"number 2 temp, {Eng2Temp}")
        elif self.instr['Eng3Starter'] and self.instr['Eng3Combustion']:
            self.q.put (F"number 3 temp, {Eng3Temp}")
        elif self.instr['Eng4Starter'] and self.instr['Eng4Combustion']:
            self.q.put (F"number 4 temp, {Eng4Temp}")
        
    def readGroundSpeed(self, dt=0):
        self.sapi5.speak (F"{self.instr['GroundSpeed']} knotts")

    def readILS(self, dt=0):
        GSNeedle = self.instr['Nav1GSNeedle']
        LocNeedle = self.instr['Nav1LocNeedle']
        if GSNeedle > 0 and GSNeedle < 119:
            GSPercent = GSNeedle / 119 * 100.0
            self.q.put (f'up {GSPercent:.0f} percent G S I')
        elif GSNeedle < 0 and GSNeedle > -119:
            GSPercent = abs(GSNeedle) / 119 * 100.0
            self.q.put (f'down {GSPercent:.0f} percent G S I')
        if LocNeedle > 0 and LocNeedle < 127:
            LocPercent = GSNeedle / 127 * 100.0
            self.q.put (F'{LocPercent:.0f} percent right')    
        elif LocNeedle < 0 and LocNeedle > -127:
            LocPercent = abs(GSNeedle) / 127 * 100.0
            self.q.put (F'{LocPercent:.0f} percent left')    



    def readToggle(self, instrument, name, onMessage, offMessage):
        ## There are several aircraft functions that are simply on/off toggles. 
        ## This function allows reading those without a bunch of duplicate code.
        try:
            if self.oldInstr[instrument] != self.instr[instrument]:
                if self.instr[instrument]:
                    self.q.put (F'{name} {onMessage}.')
                else:
                    self.q.put (F'{name} {offMessage}')
                self.oldInstr[instrument] = self.instr[instrument]
        except Exception as e:
            logging.exception(F"error in instrument toggle. Instrument was {instrument}")

    def secondsToText(self, secs):
        ## convert number of seconds into human readable format. Thanks to Stack Overflow for this!
        days = secs//86400
        hours = (secs - days*86400)//3600
        minutes = (secs - days*86400 - hours*3600)//60
        seconds = secs - days*86400 - hours*3600 - minutes*60
        result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
        ("{0} hour{1}, ".format(hours, "s" if hours!=1 else "") if hours else "") + \
        ("{0} minute{1}, ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
        ("{0} second{1}, ".format(seconds, "s" if seconds!=1 else "") if seconds else "")
        return result
    def readWaypoint(self, triggered=False):
        try:
            WPId = self.instr['NextWPId'].decode ('UTF-8')
            if self.distance_units == '0':
                distance = self.instr['NextWPDistance'] / 1000
                self.q.put (F'Next waypoint: {WPId}, distance: {distance:.1f} kilometers')    
            else:
                distance = (self.instr['NextWPDistance'] / 1000)/ 1.609
                self.q.put(F'Next waypoint: {WPId}, distance: {distance:.1f} miles')    
            self.q.put (F'baring: {self.instr["NextWPBaring"]:.0f}')
            # read estimated time enroute to next waypoint
            strTime = self.secondsToText(self.instr['NextWPETE'])
            self.q.put(strTime)
            # if we were triggered with a hotkey, read the ETA to the next waypoint.
            if triggered:
                self.q.put(F'ETA: {self.instr["NextWPETA"]}')
                reset_hotkeys()
            reset_hotkeys()
        except Exception as e:
            logging.exception ("error reading waypoint info")



        

    def readSimConnectMessages(self, dt,triggered = False):
        ## reads any SimConnect messages that don't require special processing.
        ## right now, rc4 is the only message type that needs special processing.
        SimCMessageRaw = ""
        try:
            RCMessage = False
            index = 0
            if self.SimCEnabled:
                # If the change is due to an old message clearing, just return without doing anything.
                if self.SimCData['SimCLength'] == 0:
                    return
                if self.oldSimCChanged != self.SimCData['SimCChanged'] or triggered:
                    # if this is an rc message, handle that.
                    if self.SimCData['SimCType'] == 768:
                        self.readRC4(triggered=triggered)
                    else:
                        i = 1
                        SimCMessageRaw = self.SimCMessage[:self.SimCData['SimCLength']]
                        SimCMessage = SimCMessageRaw.split('\x00')
                        for index, message in enumerate(SimCMessage):
                            if index < 2 and message != "":
                                self.q.put(f'{message}')
                                self.CachedMessage[index] = message
                            elif message != "":
                                self.q.put(f'{i}: {message}')
                                self.CachedMessage[index] = f'{i}: {message}'
                                i += 1


                    if not RCMessage:
                        self.CachedMessage[index] = 'EOM'
                    self.oldSimCChanged = self.SimCData['SimCChanged']
                if triggered == 1:
                    reset_hotkeys()
            # else:
                    # reset_hotkeys()
        except KeyError:
            pass
        except Exception as e:
            logging.exception (F'error reading SimConnect message. {SimCMessageRaw}')


    def readCachedSimConnectMessages(self):

        for i, message in self.CachedMessage.items():
            if message == 'EOM':
                break
            else:
                self.q.put (message)
        reset_hotkeys()
    
    def readRC4(self, triggered = False):
        msgUpdated = False
        msgRaw = self.SimCMessage[:self.SimCData['SimCLength']]
        msg = msgRaw.splitlines()
        # logging.error(F'{msg}')
        # breakpoint()
        if self.oldRCMsg != msg[1] and msg[1][:3] != 'Rwy' and msg[1][:1] != '<':
            msgUpdated = True
        if triggered:
            msgUpdated = True
        for index, message in enumerate(msg):
            if index == 0 or message == "" or '<' in message or '/' in message:
                continue
            if message != "" and msgUpdated == True:
                self.q.put (message.replace('\x00', ''))
                self.CachedMessage[index] = message
        self.CachedMessage[index] = 'EOM'
        self.oldRCMsg = msg[1]


    ## Announce Talking Flight Monitor (TFM) info
    def AnnounceInfo(self, dt=0, triggered = 0):
        # Get data from simulator
        self.getPyuipcData()
        # Lookup nearest cities to aircraft position using the Geonames database.
        self.airport="test"
        try:
            response = requests.get('http://api.geonames.org/findNearbyPlaceNameJSON?style=long&lat={}&lng={}&username={}&cities=cities5000&radius=200'.format(self.instr['Lat'],self.instr['Long'], self.geonames_username))
            response.raise_for_status() # throw an exception if we get an error from Geonames.
            data =response.json()
            if len(data['geonames']) >= 1:
                bearing = calcBearing (self.instr['Lat'], self.instr['Long'], float(data["geonames"][0]["lat"]), float(data["geonames"][0]["lng"]))
                bearing = (degrees(bearing) +360) % 360
                if self.distance_units == '1':
                    distance = float(data["geonames"][0]["distance"]) / 1.609
                    units = 'miles'
                else:
                    distance = float(data["geonames"][0]["distance"])
                    units = 'kilometers'
                self.q.put ('Closest city: {} {}. {:.1f} {}. Bearing: {:.0f}'.format(data["geonames"][0]["name"],data["geonames"][0]["adminName1"],distance,units,bearing))
            else:
                distance = 0
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logging.error('latitude:{}, longitude:{}'.format(self.instr['Lat'], self.instr['Long']))
            logging.exception('error getting nearest city: ' + str(e))
            self.q.put ('cannot find nearest city. Geonames connection error. Check error log.')
        except requests.exceptions.HTTPError as e:
            logging.error('latitude:{}, longitude:{}'.format(self.instr['Lat'], self.instr['Long']))
            logging.exception('error getting nearest city. Error while connecting to Geonames.' + str(e))
            self.q.put ('cannot find nearest city. Geonames may be busy. Check error log.')
            
        ## Check if we are flying over water.
        ## If so, announce body of water.
        ## We will continue to announce over water until the maximum radius of the search is reached.
        try:
            response = requests.get('http://api.geonames.org/oceanJSON?lat={}&lng={}&username={}'.format(self.instr['Lat'],self.instr['Long'], self.geonames_username))
            data = response.json()
            if 'ocean' in data and distance >= 1:
                self.q.put ('currently over {}'.format(data['ocean']['name']))
                self.oceanic = True
        except Exception as e:
            logging.error('Error determining oceanic information: ' + str(e))
            logging.exception(str(e))
            
        ## Read time zone information
        try:
            response = requests.get('http://api.geonames.org/timezoneJSON?lat={}&lng={}&username={}'.format(self.instr['Lat'],self.instr['Long'], self.geonames_username))
            data = response.json()
            
            if 'timezoneId' in data:
                tz = get_timezone(data['timezoneId'])
                tzName = get_timezone_name(tz, locale=Locale.parse('en_US'))
                if tzName != self.oldTz:
                    self.q.put ('{}.'.format(tzName))
                    self.oldTz = tzName
        except Exception as e:
            logging.error('Error determining timezone: ' + str(e))
            logging.exception(str(e))


    
    ## Read data from the simulator
    def getPyuipcData(self, type=0, dt=0):
    # read types: 0 - all, 1 - instrumentation, 2 - SimConnect, 3 - attitude    
        if type == 0 or type == 1:
            self.instr = dict(zip(self.InstrOffsets.keys(), pyuipc.read(self.pyuipcOffsets)))
            # prepare instrumentation variables
            hexCode = hex(self.instr['Com1Freq'])[2:]
            self.instr['Com1Freq'] = float('1{}.{}'.format(hexCode[0:2],hexCode[2:]))
            hexCode = hex(self.instr['Com2Freq'])[2:]
            self.instr['Com2Freq'] = float('1{}.{}'.format(hexCode[0:2],hexCode[2:]))
            # lat lon
            self.instr['Lat'] = self.instr['Lat'] * (90.0/(10001750.0 * 65536.0 * 65536.0))
            self.instr['Long'] = self.instr['Long'] * (360.0/(65536.0 * 65536.0 * 65536.0 * 65536.0))
            self.instr['Flaps'] = self.instr['Flaps'] / 256
            self.instr['OnGround'] = bool(self.instr['OnGround'])
            self.instr['ParkingBrake'] = bool(self.instr['ParkingBrake'])
            # self.ASLAltitude = round(results[8] * 3.28084)
            self.instr['Altitude'] = round(self.instr['Altitude'])
            self.instr['GroundAltitude'] = self.instr['GroundAltitude'] / 256 * 3.28084
            self.instr['ApHeading'] = round(self.instr['ApHeading']/65536*360)
            self.instr['ApAltitude'] = self.instr['ApAltitude'] / 65536 * 3.28084
            self.instr['ApMach'] = self.instr['ApMach'] / 65536
            # self.headingTrue = floor(((self.instr['Heading'] * 360) / (65536 * 65536)) + 0.5)
            self.headingTrue = self.instr['Heading'] * 360 / (65536 * 65536)
            self.headingCorrected = self.instr['CompassHeading']
            self.instr['AirspeedTrue'] = round(self.instr['AirspeedTrue'] / 128)
            self.instr['AirspeedIndicated'] = round(self.instr['AirspeedIndicated'] / 128)
            self.instr['AirspeedMach'] = self.instr['AirspeedMach'] / 20480
            self.instr['GroundSpeed'] = round((self.instr['GroundSpeed'] * 3600) / (65536 * 1852))
            self.instr['NextWPETA'] = time.strftime('%H:%M', time.localtime(self.instr['NextWPETA']))
            self.instr['NextWPBaring'] = degrees(self.instr['NextWPBaring'])
            self.instr['DestETE'] =self.secondsToText(self.instr['DestETE'])
            self.instr['DestETA'] = time.strftime('%H:%M', time.localtime(self.instr['DestETA']))
            self.instr['ElevatorTrim'] = degrees(self.instr['ElevatorTrim'])
            self.instr['VerticalSpeed'] = round ((self.instr['VerticalSpeed'] * 3.28084) * -1, 0)
            self.tempC = round(self.instr['AirTemp'] / 256, 0)
            self.tempF = round(9.0/5.0 * self.tempC + 32)
            self.AGLAltitude = self.instr['Altitude'] - self.instr['GroundAltitude']
            self.RadioAltitude = self.instr['RadioAltimeter']  / 65536 * 3.28084
            self.instr['APUPercentage'] = round(self.instr['APUPercentage'])
            self.Nav1Bits = list(map(int, '{0:08b}'.format(self.instr['Nav1Flags'])))
            self.instr['Nav1Type'] = self.Nav1Bits[0]
            self.instr['Nav1GSAvailable'] = self.Nav1Bits[6]
            self.DoorBits = list(map(int, '{0:08b}'.format(self.instr['Doors'])))
            self.instr['Door1'] = self.DoorBits[7]
            self.instr['Door2'] = self.DoorBits[6]
            self.instr['Door3'] = self.DoorBits[5]
            self.instr['Door4'] = self.DoorBits[4]
            self.lights = list(map(int, '{0:08b}'.format(self.instr['Lights'])))
            self.lights1 = list(map(int, '{0:08b}'.format(self.instr['Lights1'])))
            # breakpoint()
            self.instr['CabinLights'] = self.lights[0]
            self.instr['LogoLights'] = self.lights[1]
            self.instr['WingLights'] = self.lights1[0]
            self.instr['RecognitionLights'] = self.lights1[1]
            self.instr['InstrumentLights'] = self.lights1[2]
            self.instr['StrobeLights'] = self.lights1[3]
            self.instr['TaxiLights'] = self.lights1[4]
            self.instr['LandingLights'] = self.lights1[5]
            self.instr['BeaconLights'] = self.lights1[6]
            self.instr['NavigationLights'] = self.lights1[7]
            self.AltQNH = self.instr['Altimeter'] / 16
            self.AltHPA = floor(self.AltQNH + 0.5)
            self.AltInches = floor(((100 * self.AltQNH * 29.92) / 1013.2) + 0.5)
            self.instr['Eng1ITT'] = round(self.instr['Eng1ITT'] / 16384)
            self.instr['Eng2ITT'] = round(self.instr['Eng2ITT'] / 16384)
            self.instr['Eng3ITT'] = round(self.instr['Eng3ITT'] / 16384)
            self.instr['Eng4ITT'] = round(self.instr['Eng4ITT'] / 16384)
            self.instr['WindDirection'] = self.instr['WindDirection'] *360/65536






        if type == 0 or type == 2:
            # prepare simConnect message data
            try:
                if self.SimCEnabled:
                    self.SimCData = dict(zip(self.SimCOffsets.keys(), pyuipc.read(self.pyuipcSIMC)))
                    self.SimCMessage = self.SimCData['SimCData'].decode ('UTF-8', 'ignore')
            except Exception as e:
                logging.exception ('error reading simconnect message data')
        if type == 0 or type == 3:
            # Read attitude
            self.attitude = dict(zip(self.AttitudeOffsets.keys(), pyuipc.read(self.pyuipcAttitude)))
            self.attitude['Pitch'] = self.attitude['Pitch'] * 360 / (65536 * 65536)
            self.attitude['Bank'] = self.attitude['Bank'] * 360 / (65536 * 65536)
