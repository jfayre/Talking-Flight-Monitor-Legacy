
# -*- coding: iso-8859-15 -*-
#==============================================================================
# Talking Flight Monitor - an accessibility application for Microsoft Flight Simulator and Lockheed Martin Prepar3d.
# Copyright (C) 2020 by Jason Fayre
# based on the VoiceATIS addon by   Oliver Clemens
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.	 See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.	 If not, see <https://www.gnu.org/licenses/>.
#==============================================================================



import logging
# Import built-ins
import os
import sys
import time
import warnings
import winsound
from configparser import ConfigParser

from win32event import CreateMutex
from win32api import GetLastError
from winerror import ERROR_ALREADY_EXISTS
from math import degrees, floor
import keyboard
import requests

from aviationFormula.aviationFormula import calcBearing
from babel import Locale
from babel.dates import get_timezone, get_timezone_name
import pyglet
from accessible_output2.outputs import sapi5
from accessible_output2.outputs import auto
import numpy as np
from timeit import default_timer as timer
# Import own packages.
from        VaLogger import VaLogger

# initialize the log settings
logging.basicConfig(filename = 'error.log', level = logging.INFO)
# Set encoding
#reload(sys)
#sys.setdefaultencoding('iso-8859-15')  # @UndefinedVariable
# detect if another copy is running
handle = CreateMutex(None, 1, 'FlightFollowing')
if GetLastError(  ) == ERROR_ALREADY_EXISTS:
    output = sapi5.SAPI5()
    output.speak('Error! A version of Flight Following is already running. Exiting!')
    time.sleep(5)
    sys.exit(1)
                
# Import pyuipc package (except failure with debug mode). 


try:
    import pyuipc
    pyuipcImported = True
    debug = False
except ImportError:
        pyuipcImported = False
        debug = True

## Main Class of FlightFollowing.
# Run constructor to run the program.
class FlightFollowing:
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
               'Eng1Starter': (0x3b00, 'u'), # engine 1 starter
               'Eng2Starter': (0x3a40, 'u'), # engine 2 starter
               'Eng3Starter': (0x3980, 'u'), # engine 3 starter
               'Eng4Starter': (0x38c0, 'u'), # engine 4 starter
               'Eng1FuelFlow': (0x2060, 'f'), # Engine 1 fuel flow in pounds per hour
               'Eng2FuelFlow': (0x2160, 'f'), # Engine 2 fuel flow in pounds per hour
               'Eng3FuelFlow': (0x2260, 'f'), # Engine 3 fuel flow in pounds per hour
               'Eng4FuelFlow': (0x2360, 'f'), # Engine 1 fuel flow in pounds per hour
               'Eng1N1': (0x2010, 'f'), # Engine 1 n1 value
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
               'APUGenerator': (0x0b51, 'b'), # apu generator switch
               'APUGeneratorActive': (0x0b52, 'b'), # apu generator active flag
               'APUPercentage': (0x0b54, 'F'), # APU rpm percentage
               'APUVoltage': (0x0b5c, 'F'), # apu generator voltage
               'Lights1': (0x0d0c, 'b'), # lights
               'Lights': (0x0d0d, 'b'), # lights













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
    ## Setup the FlightFollowing object.
    def __init__(self,**optional):
        # Get file path.
        self.rootDir = os.path.abspath(os.path.dirname(sys.argv[0]))
        # window = pyglet.window.Window()        
        # @window.event
        # def on_draw():
            # window.clear()

        # Init logging.
        self.logger = VaLogger(os.path.join(self.rootDir,'voiceAtis','logs'))
        # initialize two config parser objects. One for defaults and one for config file.
        self.default_config = ConfigParser(allow_no_value=True)
        self.config = ConfigParser(allow_no_value=True)
        self.default_config['config'] = {'# Flight Following requires a username from the Geonames service':None,
                'geonames_username': 'your_username',
                '# voice rate for SAPI output':None,
                'voice_rate': '5',
                '# speech output: 0 - screen reader, 1 - SAPI5':None,
                'speech_output': '0',
                '# Read closest city info. ':None,
                'flight_following': '1',
                '# Automatically read aircraft instrumentation. If using Ideal Flight, you may want to turn this off.':None,
                'read_instrumentation':'1',
                '# Read SimConnect messages. Not compatible with FSX and requires latest FSUIPC.':None,
                'read_simconnect':'1',
                '# GPWS callouts.': None,
                'read_gpws': '1',
                'read_ils': '1',
                'read_groundspeed': '0',
                '# time interval for reading of nearest city, in minutes':None,
                'flight_following_interval': '10',
                '# Time interval between manual flight announcements, in seconds': None,
                'manual_interval': '5',
                '# Interval between ILS messages': None,
                'ils_interval': '5',
                '# Distance units: 0 - Kilometers, 1 - Miles':None,
                'distance_units': '0'}
        self.default_config['hotkeys'] = {'# command key: This key must be pressed before the other commands listed below':None,
                'command_key': ']',
                'agl_key': 'g',
                'asl_key': 'a',
                'heading_key': 'h',
                'ias_key': 's',
                'tas_key': 't',
                'mach_key': 'm',
                'vspeed_key': 'v',
                'airtemp_key': 'o',
                'trim_key': 'shift+t',
                'mute_simconnect_key': 'Shift+r',
                'city_key': 'c',
                'waypoint_key': 'w',
                'dest_key': 'd',
                'attitude_key': '[',
                'manual_key': 'Ctrl+m',
                'autopilot_key': 'shift+a',
                'director_key': 'Ctrl+f',
                'toggle_gpws_key': 'shift+g',
                'toggle_ils_key': 'shift+i',
                'toggle_flaps_key': 'Shift+f',
                'message_key': 'r'}

        # First log message.
        self.logger.info('Flight Following started')
        # check for config file. Create it if it doesn't exist.
        exists = os.path.isfile(self.rootDir + "/flightfollowing.ini")
        if exists:
            self.logger.info("config file exists.")
            self.read_config()
        else:
            self.logger.info ("no config file found. It will be created.")
            self.write_config()
            
        # Establish pyuipc connection
        while True:
            try:
                self.pyuipcConnection = pyuipc.open(0)
                self.pyuipcOffsets = pyuipc.prepare_data(list(self.InstrOffsets.values()))
                self.pyuipcSIMC = pyuipc.prepare_data(list (self.SimCOffsets.values()))
                self.pyuipcAttitude = pyuipc.prepare_data(list (self.AttitudeOffsets.values()))
                self.logger.info('FSUIPC connection established.')
                break
            except NameError:
                self.pyuipcConnection = None
                self.logger.warning('Using voiceAtis without FSUIPC.')
                break
            except Exception as e:
                logging.error('error initializing fsuipc: ' + str(e))
                self.logger.warning('FSUIPC: No simulator detected. Start your simulator first! Retrying in 20 seconds.')
                time.sleep(20)
        
        ## add global hotkey definitions
        self.commandKey = keyboard.add_hotkey(self.config['hotkeys']['command_key'], self.commandMode, args=(), suppress=True, timeout=2)
        # variables to track states of various aircraft instruments
        self.oldTz = 'none' ## variable for storing timezone name
        self.old_flaps = 0
        self.airborne = False
        self.oldBrake = True
        self.oldCom1 = None
        self.oldSpoilers = 0
        self.oldApHeading = None
        self.oldApAltitude = None
        self.oldApHeading = None
        self.oldApSpeed = None
        self.oldApMach = None
        self.oldAPVSpeed = None

        self.oldTransponder = None
        self.oldWP = None
        self.oldSimCChanged = None
        self.oldAutoBrake = None
        self.oldGear = 16383
        self.oldElevatorTrim = None
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
        self.sapi5 = sapi5.SAPI5()



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
        self.PitchUpPlayer = pyglet.media.Player()
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
        
        self.oldInstr = self.instr

        
        # Infinite loop.
        try:
            # Start closest city loop if enabled.
            if self.FFEnabled:
                pyglet.clock.schedule_interval(self.AnnounceInfo, self.FFInterval * 60)
            # Periodically poll for instrument updates. If not enabled, just poll sim data to keep hotkey functions happy
            if self.InstrEnabled:
                pyglet.clock.schedule_interval(self.readInstruments, 0.2)
            else: 
                pyglet.clock.schedule_interval (self.getPyuipcData, 0.2)
            # start simConnect message reading loop
            if self.SimCEnabled:
                pyglet.clock.schedule_interval(self.readSimConnectMessages, 0.5)
            if self.calloutsEnabled:
                pyglet.clock.schedule_interval (self.readCallouts, 0.2)
            # read engine temperatures while engine is starting. Does nothing before and after startup.
            pyglet.clock.schedule_interval(self.readEngTemps, 3)


                
        except KeyboardInterrupt:
            # Actions at Keyboard Interrupt.
            self.logger.info('Loop interrupted by user.')
            if pyuipcImported:
                pyuipc.close()
            sys.exit()

        except Exception as e:
            logging.exception('Error during main loop:' + str(e))

    def read_config(self):
            cfgfile = self.config.read(self.rootDir + "/flightfollowing.ini")
            self.geonames_username = self.config.get('config','geonames_username')
            if self.geonames_username == 'your_username':
                output = sapi5.SAPI5()
                output.speak('Error: edit the flightfollowing.ini file and add your Geo names username. exiting!')
                time.sleep(8)
                sys.exit(1)

            self.FFInterval = float(self.config.get('config','flight_following_interval'))
            self.ManualInterval = float(self.config.get('config','manual_interval'))
            self.ILSInterval = float(self.config.get('config','ils_interval'))
            self.distance_units = self.config.get('config','distance_units')
            self.voice_rate = int(self.config.get('config','voice_rate'))
            if self.config['config']['speech_output'] == '1':
                self.output = sapi5.SAPI5()
                self.output.set_rate(self.voice_rate)
            else:
                self.output = auto.Auto()
            if self.config['config'].getboolean('flight_following'):
                self.FFEnabled = True
            else:
                self.FFEnabled = False
                self.output.speak('Flight Following functions disabled.')
            if self.config['config'].getboolean('read_instrumentation'):
                self.InstrEnabled = True
            else:
                self.InstrEnabled = False
                self.output.speak('instrumentation disabled.')
            if self.config['config'].getboolean('read_simconnect'):
                self.SimCEnabled = True
            else:
                self.SimCEnabled = False
                self.output.speak("Sim Connect messages disabled.")
            if self.config['config'].getboolean ('read_gpws'):
                self.calloutsEnabled = True
            else:
                self.calloutsEnabled = False
            if self.config['config'].getboolean ('read_ils'):
                self.readILSEnabled = True
            else:
                self.readILSEnabled = False
            if self.config['config'].getboolean ('read_groundspeed'):
                self.groundspeedEnabled = True
            else:
                self.groundspeedEnabled = False
            

    def write_config(self):
        with open(self.rootDir + "/flightfollowing.ini", 'w') as configfile:
            self.default_config.write(configfile)
        output = sapi5.SAPI5()
        output.speak('Configuration file created. Open the FlightFollowing.ini file and add your geonames username. Exiting.')
        time.sleep(8)
        sys.exit()

    def manualFlight(self, dt, triggered = 0):
        try:
            pitch = round(self.attitude['Pitch'], 1)
            bank = round(self.attitude['Bank'])
            if bank > 0:
                self.output.speak (F'Left {bank}')
            elif bank < 0:
                self.output.speak (F'right {abs(bank)}')
            if pitch > 0:
                self.output.speak (F'down {pitch}')
            elif pitch < 0:
                self.output.speak (F'Up {abs(pitch)}')
        except Exception as e:
            logging.exception (F'Error in manual flight. Pitch: {pitch}, Bank: {bank}' + str(e))

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
        except Exception as e:
            logging.exception (F'Error in attitude. Pitch: {pitch}, Bank: {bank}' + str(e))




    ## handle hotkeys for reading instruments on demand
    def keyHandler(self, instrument):
        try:
            if instrument == 'asl':
                self.output.speak(F'{self.instr["Altitude"]} feet A S L')
                
                
            elif instrument == 'agl':
                AGLAltitude = self.instr['Altitude'] - self.instr['GroundAltitude']
                self.output.speak(F"{round(AGLAltitude)} feet A G L")
            elif instrument == 'heading':
                self.output.speak(F'Heading: {self.headingCorrected}')
            elif instrument == 'wp':
                self.readWaypoint(triggered=True)
            elif instrument == 'tas':
                self.output.speak (F'{self.instr["AirspeedTrue"]} knots true')
            elif instrument == 'ias':
                self.output.speak (F'{self.instr["AirspeedIndicated"]} knots indicated')
            elif instrument == 'mach':
                self.output.speak (F'Mach {self.instr["AirspeedMach"]:0.2f}')
            elif instrument == 'vspeed':
                self.output.speak (F"{self.instr['VerticalSpeed']:.0f} feet per minute")
            elif instrument =='dest':
                self.output.speak(F'Time enroute {self.instr["DestETE"]}. {self.instr["DestETA"]}')
            elif instrument == 'airtemp':
                self.output.speak (F'{self.tempC:.0f} degrees Celcius, {self.tempF} degrees Fahrenheit')
            elif instrument == 'toggletrim':
                if self.trimEnabled:
                    self.output.speak ('trim announcement disabled')
                    self.trimEnabled = False
                else:
                    self.trimEnabled = True
                    self.output.speak ('trim announcement enabled')
            elif instrument == 'togglegpws':
                if self.calloutsEnabled:
                    self.output.speak ('GPWS callouts disabled')
                    self.calloutsEnabled = False
                else:
                    self.calloutsEnabled = True
                    self.output.speak ("GPWS callouts enabled")
            elif instrument == 'togglesimc':
                if self.MuteSimC:
                    self.output.speak ('Sim Connect messages unmuted')
                    self.MuteSimC = False
                else:
                    self.MuteSimC = True
                    self.output.speak ('Sim Connect messages muted')

            elif instrument =="toggleflaps":
                if self.flapsEnabled:
                    self.output.speak ("flaps disabled")
                    self.flapsEnabled = False
                else:
                    self.output.speak ("Flaps enabled")
                    self.flapsEnabled = True
            elif instrument =='toggleils':
                if self.readILSEnabled:
                    self.output.speak ('I L S info disabled')
                    self.readILSEnabled = False
                else:
                    self.output.speak ('I L S info enabled')
                    self.readILSEnabled = True
            elif instrument == 'director':
                if self.directorEnabled:
                    pyglet.clock.unschedule(self.sonifyFlightDirector)
                    self.directorEnabled = False
                    self.PitchUpPlayer.pause()
                    self.PitchDownPlayer.pause()
                    self.BankPlayer.pause ()
                    self.output.speak ('flight director mode disabled.')
                else:
                    pyglet.clock.schedule_interval(self.sonifyFlightDirector, 0.2)
                    self.directorEnabled = True
                    self.output.speak ('flight director mode enabled')

            elif instrument == 'toggleap':
                if self.APEnabled == False:
                    self.output.speak (F'Autopilot control enabled')
                    self.APEnabled = True
                else:
                    self.output.speak (F'autopilot control disabled')
                    self.APEnabled = False

            elif instrument == 'manual':
                if self.manualEnabled:
                    pyglet.clock.unschedule(self.manualFlight)
                    self.manualEnabled = False
                    self.output.speak ('manual flight  mode disabled.')
                else:
                    pyglet.clock.schedule_interval(self.manualFlight, self.ManualInterval)
                    self.manualEnabled = True
                    self.output.speak ('manual flight mode enabled')

            elif instrument == 'attitude':
                if self.sonifyEnabled:
                    pyglet.clock.unschedule(self.sonifyPitch)
                    
                    self.PitchUpPlayer.pause()
                    self.PitchDownPlayer.pause()
                    self.BankPlayer.pause ()
                    self.sonifyEnabled = False
                    self.output.speak ('attitude mode disabled.')
                else:
                    pyglet.clock.schedule_interval(self.sonifyPitch, 0.2)
                    self.sonifyEnabled = True
                    self.output.speak ('attitude mode enabled')
            self.reset_hotkeys()
        except Exception as e:
            logging.exception(F'error in hotkey handler. Instrument was {instrument} ' + str(e))
                





    ## Layered key support for reading various instrumentation
    def commandMode(self):
        try:
            self.output.speak ('command?', interrupt=True)
            self.aslKey= keyboard.add_hotkey (self.config['hotkeys']['asl_key'], self.keyHandler, args=(['asl']), suppress=True, timeout=2)
            self.aglKey = keyboard.add_hotkey (self.config['hotkeys']['agl_key'], self.keyHandler, args=(['agl']), suppress=True, timeout=2)
            self.cityKey = keyboard.add_hotkey(self.config['hotkeys']['city_key'], self.AnnounceInfo, args=([0, 1]))
            self.headingKey = keyboard.add_hotkey (self.config['hotkeys']['heading_key'], self.keyHandler, args=(['heading']), suppress=True, timeout=2)
            self.WPKey = keyboard.add_hotkey (self.config['hotkeys']['waypoint_key'], self.keyHandler, args=(['wp']), suppress=True, timeout=2)
            self.tasKey = keyboard.add_hotkey (self.config['hotkeys']['tas_key'], self.keyHandler, args=(['tas']), suppress=True, timeout=2)
            self.iasKey = keyboard.add_hotkey (self.config['hotkeys']['ias_key'], self.keyHandler, args=(['ias']), suppress=True, timeout=2)
            self.machKey = keyboard.add_hotkey (self.config['hotkeys']['mach_key'], self.keyHandler, args=(['mach']), suppress=True, timeout=2)
            self.messageKey = keyboard.add_hotkey(self.config['hotkeys']['message_key'], self.readCachedSimConnectMessages, args=(), suppress=True, timeout=2)
            self.destKey = keyboard.add_hotkey (self.config['hotkeys']['dest_key'], self.keyHandler, args=(['dest']), suppress=True, timeout=2)
            self.attitudeKey = keyboard.add_hotkey (self.config['hotkeys']['attitude_key'], self.keyHandler, args=(['attitude']), suppress=True, timeout=2)
            self.manualKey = keyboard.add_hotkey (self.config['hotkeys']['manual_key'], self.keyHandler, args=(['manual']), suppress=True, timeout=2)
            self.directorKey = keyboard.add_hotkey (self.config['hotkeys']['director_key'], self.keyHandler, args=(['director']), suppress=True, timeout=2)
            self.vspeedKey = keyboard.add_hotkey (self.config['hotkeys']['vspeed_key'], self.keyHandler, args=(['vspeed']), suppress=True, timeout=2)
            self.airtempKey = keyboard.add_hotkey (self.config['hotkeys']['airtemp_key'], self.keyHandler, args=(['airtemp']), suppress=True, timeout=2)
            self.trimKey = keyboard.add_hotkey (self.config['hotkeys']['trim_key'], self.keyHandler, args=(['toggletrim']), suppress=True, timeout=2)
            self.MuteSimCKey = keyboard.add_hotkey (self.config['hotkeys']['mute_simconnect_key'], self.keyHandler, args=(['togglesimc']), suppress=True, timeout=2)
            self.CalloutsKey = keyboard.add_hotkey (self.config['hotkeys']['toggle_gpws_key'], self.keyHandler, args=(['togglegpws']), suppress=True, timeout=2)
            self.ILSKey = keyboard.add_hotkey (self.config['hotkeys']['toggle_ils_key'], self.keyHandler, args=(['toggleils']), suppress=True, timeout=2)
            self.flapsKey = keyboard.add_hotkey (self.config['hotkeys']['toggle_flaps_key'], self.keyHandler, args=(['toggleflaps']), suppress=True, timeout=2)
            self.apKey = keyboard.add_hotkey (self.config['hotkeys']['autopilot_key'], self.keyHandler, args=(['toggleap']), suppress=True, timeout=2)
            # winsound.Beep(500, 100)
        except Exception as e:
            logging.exception ("error in command mode.")
    def reset_hotkeys(self):
        keyboard.remove_all_hotkeys()
        self.commandKey = keyboard.add_hotkey(self.config['hotkeys']['command_key'], self.commandMode, args=(), suppress=True, timeout=2)

    def readCallouts (self, dt=0):
        if self.calloutsEnabled:
            vspeed = self.instr['VerticalSpeed']
            callout = 0
            if vspeed < -50:
                for i in self.calloutsHigh:
                    if self.AGLAltitude <= i + 5 and self.AGLAltitude >= i - 5 and self.calloutState[i] == False:
                        source = pyglet.media.load (F'sounds\\{str(i)}.wav')
                        source.play()
                        self.calloutState[i] = True
                        
                for i in self.calloutsLow:
                    if self.AGLAltitude <= i + 3 and self.AGLAltitude >= i - 3 and self.calloutState[i] == False:
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
            self.output.speak ("Positive rate.")
            pyglet.clock.unschedule(self.readGroundSpeed)
            self.groundSpeed = False
            self.airborne = True
        # landing gear
        if self.instr['Gear'] != self.oldGear:
            if self.instr['Gear'] == 0:
                self.output.speak ('Gear up.')
            elif self.instr['Gear'] == 16383:
                self.output.speak ('Gear down.')
            self.oldGear = self.instr['Gear']

        # if flaps position has changed, flaps are in motion. We need to wait until they have stopped moving to read the value.
        if self.flapsEnabled:
            if self.instr['Flaps'] != self.old_flaps:
                flapsTransit = True
                while flapsTransit:
                    self.getPyuipcData()
                    if self.instr['Flaps'] != self.old_flaps:
                        self.old_flaps = self.instr['Flaps']
                        time.sleep (0.2)
                    else:
                        flapsTransit = False
                self.output.speak (F'Flaps {self.instr["Flaps"]:.0f}')
                self.old_flaps = self.instr['Flaps']
            # announce radio frequency changes
        if self.instr['Com1Freq'] != self.oldCom1:
            self.output.speak (F"com 1, {self.instr['Com1Freq']}")
            self.oldCom1 = self.instr['Com1Freq']
        # spoilers
        if self.instr['SpoilersArm'] == 1 and self.oldSpoilers != self.instr['SpoilersArm']:
            self.output.speak ("spoilers armed.")
            self.oldSpoilers = self.instr['SpoilersArm']
        if self.oldApAltitude != self.instr['ApAltitude']:
            self.output.speak(F"Altitude set to {round(self.instr['ApAltitude'])}")
            self.oldApAltitude = self.instr['ApAltitude']
        if self.APEnabled:
            if self.oldApHeading != self.instr['ApHeading']:
                self.output.speak (F"{self.instr['ApHeading']} degrees")
                self.oldApHeading = self.instr['ApHeading']
            if self.oldApSpeed != self.instr['ApAirspeed']:
                self.output.speak (F"{self.instr['ApAirspeed']}")
                self.oldApSpeed = self.instr['ApAirspeed']
            if self.oldApMach != self.instr['ApMach']:
                self.output.speak (F"mach {self.instr['ApMach']:.2f}")
                self.oldApMach = self.instr['ApMach']
            if self.oldAPVSpeed != self.instr['ApVerticalSpeed']:
                self.output.speak (F"{self.instr['ApVerticalSpeed']} feet per minute")
                self.oldAPVSpeed = self.instr['ApVerticalSpeed']



        # transponder
        if self.instr['Transponder'] != self.oldTransponder:
            self.output.speak(F'Squawk {self.instr["Transponder"]:x}')
            self.oldTransponder = self.instr['Transponder']
        # next waypoint
        if self.instr['NextWPId'] != self.oldWP:
            time.sleep(3)
            self.getPyuipcData()
            self.readWaypoint(0)
            self.oldWP = self.instr['NextWPId']
        # read autobrakes
        if self.instr['AutoBrake'] != self.oldAutoBrake:
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
            self.output.speak (F'Auto brake {brake}')
            self.oldAutoBrake = self.instr['AutoBrake']
        if self.instr['ElevatorTrim'] != self.oldElevatorTrim and self.instr['ApMaster'] != 1 and self.trimEnabled:
            if self.instr['ElevatorTrim'] < 0:
                self.output.speak (F"Trim down {abs(round (self.instr['ElevatorTrim'], 2))}")
            else:
                self.output.speak (F"Trim up {round (self.instr['ElevatorTrim'], 2)}")

            self.oldElevatorTrim = self.instr['ElevatorTrim']

        if self.AltHPA != self.oldHPA:
            self.output.speak (F'Altimeter: {self.AltHPA}, {self.AltInches / 100} inches')
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
        self.readToggle('APUGenerator', 'A P U Generator', 'active', 'off')
        self.readToggle('BeaconLights', 'Beacon light', 'on', 'off')
        self.readToggle('LandingLights', 'Landing Lights', 'on', 'off')
        self.readToggle('TaxiLights', 'Taxi Lights', 'on', 'off')
        self.readToggle('NavigationLights', 'Nav lights', 'on', 'off')
        self.readToggle('StrobeLights', 'strobe lights', 'on', 'off')
        self.readToggle('InstrumentLights', 'Instrument lights', 'on', 'off')
        if self.groundspeedEnabled:
            if self.instr['GroundSpeed'] > 0 and self.instr['OnGround'] and self.groundSpeed == False:
                pyglet.clock.schedule_interval(self.readGroundSpeed, 3)
                self.groundSpeed = True
            elif self.instr['GroundSpeed'] == 0 and self.groundSpeed:
                pyglet.clock.unschedule(self.readGroundSpeed)

        
        # read engine status on startup.
        if self.instr['Eng1FuelFlow'] > 10 and self.instr['Eng1Starter'] and self.Eng1FuelFlow == False:
            self.output.speak ('Number 1 fuel flow')
            self.Eng1FuelFlow = True
        if self.instr['Eng2FuelFlow'] > 10 and self.instr['Eng2Starter'] and self.Eng2FuelFlow == False:
            self.output.speak ('Number 2 fuel flow')
            self.Eng2FuelFlow = True
        if self.instr['Eng3FuelFlow'] > 10 and self.instr['Eng3Starter'] and self.Eng3FuelFlow == False:
            self.output.speak ('Number 3 fuel flow')
            self.Eng3FuelFlow = True
        if self.instr['Eng4FuelFlow'] > 10 and self.instr['Eng4Starter'] and self.Eng4FuelFlow == False:
            self.output.speak ('Number 4 fuel flow')
            self.Eng4FuelFlow = True
        if self.instr['Eng1N2'] > 5 and self.Eng1N2 == False and self.instr['Eng1Starter']:
            self.output.speak ('number 1, 5 percent N2')
            self.Eng1N2 = True
        if self.instr['Eng1N1'] > 5 and self.Eng1N1 == False  and self.instr['Eng1Starter']:
            self.output.speak ('number 1, 5 percent N1')
            self.Eng1N1 = True
        if self.instr['Eng2N2'] > 5 and self.Eng2N2 == False  and self.instr['Eng2Starter']:
            self.output.speak ('number 2, 5 percent N2')
            self.Eng2N2 = True
        if self.instr['Eng2N1'] > 5 and self.Eng2N1 == False  and self.instr['Eng2Starter']:
            self.output.speak ('number 2, 5 percent N1')
            self.Eng2N1 = True
        if self.instr['Eng3N2'] > 5 and self.Eng3N2 == False  and self.instr['Eng3Starter']:
            self.output.speak ('number 3, 5 percent N2')
            self.Eng3N2 = True
        if self.instr['Eng3N1'] > 5 and self.Eng3N1 == False  and self.instr['Eng3Starter']:
            self.output.speak ('number 3, 5 percent N1')
            self.Eng3N1 = True
        if self.instr['Eng4N2'] > 5 and self.Eng4N2 == False  and self.instr['Eng4Starter']:
            self.output.speak ('number 4, 5 percent N2')
            self.Eng4N2 = True
        if self.instr['Eng4N1'] > 5 and self.Eng4N1 == False  and self.instr['Eng4Starter']:
            self.output.speak ('number 4, 5 percent N1')
            self.Eng4N1 = True





        # read APU status
        if self.instr['APUPercentage'] > 0 and self.APUStarting == False and self.APURunning == False and self.APUShutdown == False:
            self.output.speak('A P U starting')
            self.APUStarting = True
            self.APUOff = False
        if self.instr['APUPercentage'] < 100 and self.APURunning:
            self.output.speak ('Shutting down A P U')
            self.APURunning = False
            self.APUShutdown = True
        if self.instr['APUPercentage'] == 100 and self.APUStarting:
            self.APUStarting = False
            self.APURunning = True
            self.output.speak("apu at 100 percent")
        if self.instr['APUPercentage'] == 0 and self.APUOff == False:
            self.output.speak('A P U shut down')
            self.APURunning = False
            self.APUStarting = False
            self.APUShutdown = False
            self.APUOff = true


        if self.instr['APUGenerator'] and self.APUGenerator == False:
            self.output.speak (F"{round(self.instr['APUVoltage'])} volts")
            self.APUGenerator = True
        if self.instr['APUGenerator'] == False:
            self.APUGenerator = False




        # read altitude every 1000 feet
        for i in range (1000, 65000, 1000):
            if self.instr['Altitude'] >= i - 10 and self.instr['Altitude'] <= i + 10 and self.altFlag[i] == False:
                self.output.speak (F"{i} feet")
                self.altFlag[i] = True
            elif self.instr['Altitude'] >= i + 100:
                self.altFlag[i] = False

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
            self.output.speak (F"number 1 temp, {Eng1Temp}")
        elif self.instr['Eng2Starter'] and self.instr['Eng2Combustion']:
            self.output.speak (F"number 2 temp, {Eng2Temp}")
        elif self.instr['Eng3Starter'] and self.instr['Eng3Combustion']:
            self.output.speak (F"number 3 temp, {Eng3Temp}")
        elif self.instr['Eng4Starter'] and self.instr['Eng4Combustion']:
            self.output.speak (F"number 4 temp, {Eng4Temp}")
        
    def readGroundSpeed(self, dt=0):
        self.sapi5.speak (F"{self.instr['GroundSpeed']} knotts")

    def readILS(self, dt=0):
        GSNeedle = self.instr['Nav1GSNeedle']
        LocNeedle = self.instr['Nav1LocNeedle']
        if GSNeedle > 0 and GSNeedle < 119:
            GSPercent = GSNeedle / 119 * 100.0
            self.output.speak (f'up {GSPercent:.0f} percent G S I')
        elif GSNeedle < 0 and GSNeedle > -119:
            GSPercent = abs(GSNeedle) / 119 * 100.0
            self.output.speak (f'down {GSPercent:.0f} percent G S I')
        if LocNeedle > 0 and LocNeedle < 127:
            LocPercent = GSNeedle / 127 * 100.0
            self.output.speak (F'{LocPercent:.0f} percent right')    
        elif LocNeedle < 0 and LocNeedle > -127:
            LocPercent = abs(GSNeedle) / 127 * 100.0
            self.output.speak (F'{LocPercent:.0f} percent left')    



    def readToggle(self, instrument, name, onMessage, offMessage):
        ## There are several aircraft functions that are simply on/off toggles. 
        ## This function allows reading those without a bunch of duplicate code.
        try:
            if self.oldInstr[instrument] != self.instr[instrument]:
                if self.instr[instrument]:
                    self.output.speak (F'{name} {onMessage}.')
                else:
                    self.output.speak (F'{name} {offMessage}')
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
                self.output.speak (F'Next waypoint: {WPId}, distance: {distance:.1f} kilometers')    
            else:
                distance = (self.instr['NextWPDistance'] / 1000)/ 1.609
                self.output.speak(F'Next waypoint: {WPId}, distance: {distance:.1f} miles')    
            self.output.speak (F'baring: {self.instr["NextWPBaring"]:.0f}')
            # read estimated time enroute to next waypoint
            strTime = self.secondsToText(self.instr['NextWPETE'])
            self.output.speak(strTime)
            # if we were triggered with a hotkey, read the ETA to the next waypoint.
            if triggered:
                self.output.speak(F'ETA: {self.instr["NextWPETA"]}')
                self.reset_hotkeys()
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
                                self.output.speak(f'{message}')
                                self.CachedMessage[index] = message
                            elif message != "":
                                self.output.speak(f'{i}: {message}')
                                self.CachedMessage[index] = f'{i}: {message}'
                                i += 1


                    if not RCMessage:
                        self.CachedMessage[index] = 'EOM'
                    self.oldSimCChanged = self.SimCData['SimCChanged']
                if triggered == 1:
                    self.reset_hotkeys()
            # else:
                    # self.reset_hotkeys()
        except KeyError:
            pass
        except Exception as e:
            logging.exception (F'error reading SimConnect message. {SimCMessageRaw}')


    def readCachedSimConnectMessages(self):

        for i, message in self.CachedMessage.items():
            if message == 'EOM':
                break
            else:
                self.output.speak (message)
        self.reset_hotkeys()
    
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
                self.output.speak (message.replace('\x00', ''))
                self.CachedMessage[index] = message
        self.CachedMessage[index] = 'EOM'
        self.oldRCMsg = msg[1]


    ## Announce flight following info
    def AnnounceInfo(self, dt, triggered = 0):
        # If invoked by hotkey, reset hotkey deffinitions.
        if triggered == 1:
            self.reset_hotkeys()
            triggered = '0'
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
                self.output.speak ('Closest city: {} {}. {:.1f} {}. Bearing: {:.0f}'.format(data["geonames"][0]["name"],data["geonames"][0]["adminName1"],distance,units,bearing))
            else:
                distance = 0
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logging.error('latitude:{}, longitude:{}'.format(self.instr['Lat'], self.instr['Long']))
            logging.exception('error getting nearest city: ' + str(e))
            self.output.speak ('cannot find nearest city. Geonames connection error. Check error log.')
        except requests.exceptions.HTTPError as e:
            logging.error('latitude:{}, longitude:{}'.format(self.instr['Lat'], self.instr['Long']))
            logging.exception('error getting nearest city. Error while connecting to Geonames.' + str(e))
            self.output.speak ('cannot find nearest city. Geonames may be busy. Check error log.')
            
        ## Check if we are flying over water.
        ## If so, announce body of water.
        ## We will continue to announce over water until the maximum radius of the search is reached.
        try:
            response = requests.get('http://api.geonames.org/oceanJSON?lat={}&lng={}&username={}'.format(self.instr['Lat'],self.instr['Long'], self.geonames_username))
            data = response.json()
            if 'ocean' in data and distance >= 1:
                self.output.speak ('currently over {}'.format(data['ocean']['name']))
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
                    self.output.speak ('{}.'.format(tzName))
                    self.oldTz = tzName
        except Exception as e:
            logging.error('Error determining timezone: ' + str(e))
            logging.exception(str(e))


    
    ## Read data from the simulator
    def getPyuipcData(self, dt=0):
        
        if pyuipcImported:
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
            self.headingTrue = floor(((self.instr['Heading'] * 360) / (65536 * 65536)) + 0.5)
            self.headingCorrected = self.instr['Heading'] - (self.instr['MagneticVariation'] * 65536)
            self.headingCorrected = floor(self.headingCorrected * 360 / (65536 * 65536) + 0.5)
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
            self.instr['APUPercentage'] = round(self.instr['APUPercentage'])






            # prepare simConnect message data
            try:
                if self.SimCEnabled:
                    self.SimCData = dict(zip(self.SimCOffsets.keys(), pyuipc.read(self.pyuipcSIMC)))
                    self.SimCMessage = self.SimCData['SimCData'].decode ('UTF-8', 'ignore')

                # Read attitude
                self.attitude = dict(zip(self.AttitudeOffsets.keys(), pyuipc.read(self.pyuipcAttitude)))
                self.attitude['Pitch'] = self.attitude['Pitch'] * 360 / (65536 * 65536)
                self.attitude['Bank'] = self.attitude['Bank'] * 360 / (65536 * 65536)
            except Exception as e:
                logging.exception ('error reading simconnect message data')

        else:
            self.logger.error ('FSUIPC not found! Exiting')
            exit()

if __name__ == '__main__':
    FlightFollowing = FlightFollowing()
    pyglet.app.run()
    pass
