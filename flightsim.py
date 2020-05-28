import copy
import logging
import os
import queue
import sys
import threading
import time
from dataclasses import dataclass

from math import degrees, floor

import numpy as np
import pyglet
import requests
import wx
from aviationFormula.aviationFormula import calcBearing
from babel import Locale
from babel.dates import get_timezone, get_timezone_name
from pubsub import pub
import fsdata
import application
import config
import pyuipc
from logger import logger

log = logging.getLogger("tfm")
        
## Data class for fuel tanks
## We don't strictly need to use a dataclass here, it was a bit of an experiment
@dataclass
class tank:
    present: bool = False
    key: int = 0
    name: str = ""
    capacity: int = 0
    percent: float = 0.0
    weight: float = 0.0
    quantity: float = 0.0


## Main Class of tfm.
class TFM(threading.Thread):
    ## Setup the tfm object.
    def __init__(self,queue, sapi_queue):
        # global keyboard_handler
        threading.Thread.__init__(self)
        self.q = queue
        self.sapi_q = sapi_queue

    def run(self):
        # Init log.
        # self.logger = VaLogger(os.path.join(self.rootDir,'voiceAtis','logs'))
        # First log message.
        pub.sendMessage('update', msg=F'TFM {application.version} started')
        self.read_config()
        # Establish pyuipc connection
        while  True:
            try:
                log.debug("opening FSUIPC connection")
                self.pyuipcConnection = pyuipc.open(0)
                log.debug("preparing main offsets")
                self.pyuipcOffsets = pyuipc.prepare_data(list(fsdata.InstrOffsets.values()))
                log.debug("preparing simconnect offsets")
                self.pyuipcSIMC = pyuipc.prepare_data(list (fsdata.SimCOffsets.values()))
                log.debug("preparing attitude mode offsets")
                self.pyuipcAttitude = pyuipc.prepare_data(list (fsdata.AttitudeOffsets.values()))
                self.pyuipcBonanza = pyuipc.prepare_data(list (fsdata.BonanzaOffsets.values()))
                self.pyuipcCherokee = pyuipc.prepare_data(list (fsdata.CherokeeOffsets.values()))
                # self.pyuipcC182 = pyuipc.prepare_data(list (fsdata.C182Offsets.values()))
                self.pyuipcRadioAlt = pyuipc.prepare_data ([(0x31e4, 'u')])
                
                break
            except NameError:
                self.pyuipcConnection = None
                break
            except Exception as e:
                log.error('error initializing fsuipc: ' + str(e))
                time.sleep(20)
        
        # variables to track states of various aircraft instruments
        self.oldAircraftName = None
        self.old_a2a_bat = None
        self.old_a2a_ttl = None
        self.old_a2a_ttr = None
        self.old_a2a_tt = None
        self.old_a2a_fsel = None
        self.old_a2a_window = None
        self.old_a2a_fan = None
        self.tfh = None
        self.adjust_heat = False
        self.defrost_level = None
        self.adjust_defrost = False

        self.oldTz = 'none' ## variable for storing timezone name
        self.airborne = False
        self.oldWP = None
        self.runway_guidance = False
        self.triggered = False
        self.oldSimCChanged = None
        self.oldSimCData = None
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
        
        self.oldInstr = copy.deepcopy(fsdata.instr)
        # Start closest city loop if enabled.
        pub.subscribe(self.set_triggered, "triggered")
        pub.subscribe (self.tip_tank_left_toggle, "ttl")
        if 'A2A Beechcraft' in fsdata.instr['AircraftName'].decode():
            log.debug("starting A2A Bonanza features")
            # pyglet.clock.schedule_interval(self.read_a2a_info, 1)
            # pyglet.clock.schedule_once(self.test_var, 4)


        if self.FFEnabled:
            log.debug("scheduling flight following function")
            pyglet.clock.schedule_interval(self.AnnounceInfo, self.FFInterval * 60)
        # Periodically poll for instrument updates. If not enabled, just poll sim data to keep hotkey functions happy
        if fsdata.instrEnabled:
            log.debug('scheduling instrumentation')
            pyglet.clock.schedule_interval(self.readInstruments, 1)
        else:
            pyglet.clock.schedule_interval(self.getPyuipcData, 1)
        # # start simConnect message reading loop
        if self.SimCEnabled:
            log.debug("scheduling simconnect messages")
            pyglet.clock.schedule_interval(self.readSimConnectMessages, 1)
        if self.calloutsEnabled:
            log.debug("scheduling GPWS callouts")
            pyglet.clock.schedule_interval (self.readCallouts, 0.2)
        # Infinite loop.
        log.debug("starting infinite loop")
        while True:
            try:
                # we need to tick the clock for pyglet scheduling functions to work
                pyglet.clock.tick()
                # dispatch any pending events so audio looping works
                pyglet.app.platform_event_loop.dispatch_posted_events()
                time.sleep(0.1)
            except Exception as e:
                log.exception("error in main loop. This is bad!")
    def set_triggered(self, msg):
        if msg:
            self.triggered = True
        else:
            self.triggered = False
    def output(self, msg):
        # put a speech message in the queue and output to the text control
        log.debug("queuing: " + msg)
        pub.sendMessage("update", msg=msg)
        self.q.put(msg)
    def speak(self, msg):
        # only speak a message, don't update the text control
        log.debug("queuing: " + msg)
        self.q.put(msg)
    def read_config(self):
        try:
            self.geonames_username = config.app['config']['geonames_username']
            self.FFInterval = float(config.app['timing']['flight_following_interval'])
            self.ManualInterval = float(config.app['timing']['manual_interval'])
            self.ILSInterval = float(config.app['timing']['ils_interval'])
            self.use_metric = config.app['config']['use_metric']
            self.voice_rate = int(config.app['config']['voice_rate'])
            if config.app['config']['flight_following']:
                self.FFEnabled = True
            else:
                self.FFEnabled = False
                self.output('Flight Following  announcements disabled.')
            if config.app['config']['read_instrumentation']:
                fsdata.instrEnabled = True
            else:
                fsdata.instrEnabled = False
                self.output('instrumentation disabled.')
            if config.app['config']['read_simconnect']:
                self.SimCEnabled = True
            else:
                self.SimCEnabled = False
                self.output("Sim Connect messages disabled.")
            if config.app['config']['read_gpws']:
                self.calloutsEnabled = True
            else:
                self.calloutsEnabled = False
                log.debug("callouts disabled")
            if config.app['config']['read_ils']:
                self.readILSEnabled = True
            else:
                self.readILSEnabled = False
                log.debug("ILS messages disabled")
            if config.app['config']['read_groundspeed']:
                self.groundspeedEnabled = True
            else:
                self.groundspeedEnabled = False
                log.debug ("ground speed announcements disabled")
        except Exception as e:
            log.exception("error setting up configuration variables")

        

    def manualFlight(self, dt, triggered = 0):
        try:
            pitch = round(self.attitude['Pitch'], 1)
            bank = round(self.attitude['Bank'])
            if bank > 0:
                self.speak (F'Left {bank}')
            elif bank < 0:
                self.speak (F'right {abs(bank)}')
            if pitch > 0:
                self.speak (F'down {pitch}')
            elif pitch < 0:
                self.speak (F'Up {abs(pitch)}')
        except Exception as e:
            log.exception (F'Error in manual flight. Pitch: {pitch}, Bank: {bank}' + str(e))
    def set_speed(self, speed):
        # set the autopilot airspeed
        offset, type = fsdata.instrOffsets['ApAirspeed']
        data = [(offset, type, int(speed))]
        pyuipc.write(data)
    def set_heading(self, heading):
        # set the auto pilot heading
        offset, type = fsdata.instrOffsets['ApHeading']
        # convert the supplied heading into the proper FSUIPC format (degrees*65536/360)
        heading = int(heading)
        heading = int(heading * 65536 / 360)
        data = [(offset, type, heading)]
        pyuipc.write(data)
    def set_altitude(self, altitude):
        offset, type = fsdata.instrOffsets['ApAltitude']
        # convert the supplied altitude into the proper FSUIPC format.
        #  FSUIPC needs the altitude as metres*65536
        altitude =int(altitude)
        altitude = int(altitude / 3.28084 * 65536)
        data = [(offset, type, altitude)]
        pyuipc.write(data)
    def set_mach(self, mach):
        # set mach speed
        offset, type = fsdata.instrOffsets['ApMach']
        # convert the supplied mach value into the proper FSUIPC format.
        #  FSUIPC needs the mach multiplied by 65536
        mach = float(mach) * 65536
        mach = int(mach)
        
        data = [(offset, type, mach)]
        pyuipc.write(data)
    def set_vspeed(self, vspeed):
        # set the autopilot vertical speed
        offset, type = fsdata.instrOffsets['ApVerticalSpeed']
        data = [(offset, type, int(vspeed))]
        pyuipc.write(data)

    def set_transponder(self, transponder):
        # set the transponder
        offset, type = fsdata.instrOffsets['Transponder']
        data = [(offset, type, int(transponder, 16))]
        pyuipc.write(data)
    def set_com1(self, com1):
        # set com 1 frequency
        offset, type = fsdata.instrOffsets['Com1Freq']
        freq = float(com1) * 100
        freq = int(freq) - 10000
        freq = F"{freq}"
        data = [(offset, type, int(freq, 16))]
        pyuipc.write(data)
    def set_com2(self, com2):
        # set com 1 frequency
        offset, type = fsdata.instrOffsets['Com2Freq']
        freq = float(com2) * 100
        freq = int(freq) - 10000
        freq = F"{freq}"
        data = [(offset, type, int(freq, 16))]
        pyuipc.write(data)

    
    def set_qnh(self, qnh):
        offset, type = fsdata.instrOffsets['Altimeter']
        qnh = int(qnh) * 16
        data = [(offset, type, qnh)]
        pyuipc.write(data)
    def set_inches(self, inches):
        # we need to convert altimeter value to qnh, since that is what the fsuipc expects
        offset, type = fsdata.instrOffsets['Altimeter']
        qnh = float(inches) * 33.864
        qnh = round(qnh, 1) * 16
        qnh = int(qnh)
        data = [(offset, type, qnh)]
        pyuipc.write(data)



    def sonifyFlightDirector(self, dt):
        try:
            pitch = round(fsdata.instr['ApFlightDirectorPitch'], 1)
            bank = round(fsdata.instr['ApFlightDirectorBank'], 0)
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
            log.exception (F'Error in flight director. Pitch: {pitch}, Bank: {bank}' + str(e))



        
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
            log.exception (F'Error in attitude. Pitch: {pitch}, Bank: {bank}' + str(e))

    def runway_guidance_mode(self):
        try:
            if self.runway_guidance:
                self.runway_guidance = False
                pyglet.clock.unschedule(self.play_heading_tones)
                self.BankPlayer.pause()
                self.output ("Runway guidance disabled")
                pub.sendMessage('reset', arg1=True)
                return
            else:
                self.runway_guidance = True
                self.hdg = round(self.headingCorrected)
                self.output("Runway guidance enabled")
                self.output(F" current heading: {self.hdg} degrees")
                self.hdg_right = self.hdg + 45
                self.hdg_left = self.hdg - 45
                self.hdg_freqs = np.linspace(1, 4, 45)
                self.hdg_left_tones = {}
                self.hdg_right_tones = {}
                count = 0
                for i in np.arange (self.hdg, self.hdg_right, 1):
                    if i > 360:
                        i = i - 360
                    self.hdg_right_tones[i] = self.hdg_freqs[count]
                    count += 1
                count = 0
                for i in np.arange (self.hdg, self.hdg_left, -1):
                    if i < 0:
                        i = i + 360
                    self.hdg_left_tones[i] = self.hdg_freqs[count]
                    count += 1
                pyglet.clock.schedule_interval(self.play_heading_tones, 0.2)
                pub.sendMessage('reset', arg1=True)
        except Exception as e:
            log.exception("error calculating heading lock")


    def play_heading_tones(self, dt=0):
        try:
            self.headingCorrected = round(self.headingCorrected)
            if self.headingCorrected > self.hdg and  self.headingCorrected < self.hdg_right:
                self.BankPlayer.position = (5, 0, 0)
                self.BankPlayer.play()
                self.BankPlayer.pitch = self.hdg_right_tones[abs(self.headingCorrected)]
            if self.headingCorrected < self.hdg and self.headingCorrected > self.hdg_left:
                self.BankPlayer.position = (-5, 0, 0)
                self.BankPlayer.play()
                self.BankPlayer.pitch = self.hdg_left_tones[abs(self.headingCorrected)]

            if self.hdg == self.headingCorrected:
                self.BankPlayer.pause()
        except Exception as e:
            log.exception("error playing heading tones")
    def read_rpm(self):
        rpm = round(self.read_long_var(0x66f1, "Eng1_RPM"))
        self.output (F'{rpm} RPM')
        pub.sendMessage('reset', arg1=True)


    def readAltitude(self):
        self.getPyuipcData(1)
        self.output(F'{fsdata.instr["Altitude"]} feet A S L')
        pub.sendMessage('reset', arg1=True)
    def readGroundAltitude(self):
        self.getPyuipcData(1)
        AGLAltitude = fsdata.instr['Altitude'] - fsdata.instr['GroundAltitude']
        self.output(F"{round(AGLAltitude)} feet A G L")
        pub.sendMessage('reset', arg1=True)

    def readFlightFollowing(self):
        pub.sendMessage('reset', arg1=True)
        self.AnnounceInfo()
    def readHeading(self):
        self.getPyuipcData(1)
        self.output(F'Heading: {round(self.headingCorrected)}')
        pub.sendMessage('reset', arg1=True)
    def readTAS(self):
        self.getPyuipcData(1)
        self.output (F'{fsdata.instr["AirspeedTrue"]} knots true')
        pub.sendMessage('reset', arg1=True)
    def readIAS(self):
        self.getPyuipcData(1)
        self.output (F'{fsdata.instr["AirspeedIndicated"]} knots indicated')
        pub.sendMessage('reset', arg1=True)
    def readMach(self):
        self.getPyuipcData(1)
        self.output (F'Mach {fsdata.instr["AirspeedMach"]:0.2f}')
        pub.sendMessage('reset', arg1=True)
    def readVSpeed(self):
        self.getPyuipcData(1)
        self.output (F"{fsdata.instr['VerticalSpeed']:.0f} feet per minute")
        pub.sendMessage('reset', arg1=True)
    def readDest(self):
        self.getPyuipcData(1)
        self.output(F'Time enroute {fsdata.instr["DestETE"]}. {fsdata.instr["DestETA"]}')
        pub.sendMessage('reset', arg1=True)
    def readTemp(self):
        self.getPyuipcData(1)
        self.output (F'{self.tempC:.0f} degrees Celcius, {self.tempF} degrees Fahrenheit')
        pub.sendMessage('reset', arg1=True)
    def readWind(self):
        self.getPyuipcData(1)
        windSpeed = fsdata.instr['WindSpeed']
        windDirection = round(fsdata.instr['WindDirection'])
        windGust = fsdata.instr['WindGust']
        self.output(F'Wind: {windDirection} at {windSpeed} knotts. Gusts at {windGust} knotts.')
        pub.sendMessage('reset', arg1=True)

    def toggleTrim(self):
        if self.trimEnabled:
            self.output ('trim announcement disabled')
            self.trimEnabled = False
        else:
            self.trimEnabled = True
            self.output ('trim announcement enabled')
        pub.sendMessage('reset', arg1=True)

    def toggleGPWS(self):
        if self.calloutsEnabled:
            self.output ('GPWS callouts disabled')
            self.calloutsEnabled = False
        else:
            self.calloutsEnabled = True
            self.output ("GPWS callouts enabled")
        pub.sendMessage('reset', arg1=True)

    def toggleMuteSimconnect(self):
        if self.MuteSimC:
            self.output ('Sim Connect messages unmuted')
            self.MuteSimC = False
        else:
            self.MuteSimC = True
            self.output ('Sim Connect messages muted')
        pub.sendMessage('reset', arg1=True)
    def toggleFlaps(self):
        if self.flapsEnabled:
            self.output ("flaps disabled")
            self.flapsEnabled = False
        else:
            self.output ("Flaps enabled")
            self.flapsEnabled = True
        pub.sendMessage('reset', arg1=True)
    def toggleILS(self):
        if self.readILSEnabled:
            self.output ('I L S info disabled')
            self.readILSEnabled = False
        else:
            self.output ('I L S info enabled')
            self.readILSEnabled = True
        pub.sendMessage('reset', arg1=True)
    def toggleDirectorMode(self):
        if self.directorEnabled:
            pyglet.clock.unschedule(self.sonifyFlightDirector)
            self.directorEnabled = False
            self.PitchUpPlayer.pause()
            self.PitchDownPlayer.pause()
            self.BankPlayer.pause ()
            self.output ('flight director mode disabled.')
        else:
            pyglet.clock.schedule_interval(self.sonifyFlightDirector, 0.2)
            self.directorEnabled = True
            self.output ('flight director mode enabled')
        pub.sendMessage('reset', arg1=True)

    def toggleAutoPilot(self):
        if not self.APEnabled:
            self.output (F'Autopilot control enabled')
            self.APEnabled = True
        else:
            self.output (F'autopilot control disabled')
            self.APEnabled = False
        pub.sendMessage('reset', arg1=True)
    def toggleManualMode(self):
        if self.manualEnabled:
            pyglet.clock.unschedule(self.manualFlight)
            self.manualEnabled = False
            self.output ('manual flight  mode disabled.')
        else:
            pyglet.clock.schedule_interval(self.manualFlight, self.ManualInterval)
            self.manualEnabled = True
            self.output ('manual flight mode enabled')
        pub.sendMessage('reset', arg1=True)
    
    def setup_fuel_tanks(self):
        log.debug('checking available fuel tanks')    
        self.tanks = {}
        key = 1
        if fsdata.instr['cap_center'] != 0:
            log.debug ('found center tank')
            self.tanks[key] = tank(name='center')
            self.tanks[key].capacity = fsdata.instr['cap_center']
            key += 1
        if fsdata.instr['cap_center2'] != 0:
            log.debug ("found center 2")
            self.tanks[key] = tank(name='center2')
            self.tanks[key].capacity = fsdata.instr['cap_center2']
            key += 1
        if fsdata.instr['cap_center3'] != 0:
            log.debug ("found center 3")
            self.tanks[key] = tank(name='center3')
            self.tanks[key].capacity = fsdata.instr['cap_center3']
            key += 1
        if fsdata.instr['cap_main_left'] != 0:
            log.debug ('found main left')
            self.tanks[key] = tank(name='main left')
            self.tanks[key].capacity = fsdata.instr['cap_main_left']
            key += 1
        if fsdata.instr['cap_main_right'] != 0:
            log.debug ('found main right')
            self.tanks[key] = tank(name='main right')
            self.tanks[key].capacity = fsdata.instr['cap_main_right']
            key += 1
        if fsdata.instr['cap_aux_left'] != 0:
            log.debug ("found aux left")
            self.tanks[key] = tank(name='aux left')
            self.tanks[key].capacity = fsdata.instr['cap_aux_left']
            key += 1
        if fsdata.instr['cap_aux_right'] != 0:
            log.debug ('found aux right')
            self.tanks[key] = tank(name='aux right')
            self.tanks[key].capacity = fsdata.instr['cap_aux_right']
            key += 1
        if fsdata.instr['cap_tip_left'] != 0:
            log.debug ('found left tip')
            self.tanks[key] = tank(name='tip left')
            self.tanks[key].capacity = fsdata.instr['cap_center']
            key += 1
        if fsdata.instr['cap_tip_right'] != 0:
            log.debug ('found right tip')
            self.tanks[key] = tank(name='tip right')
            self.tanks[key].capacity = fsdata.instr['cap_tip_right']
            key += 1
        # breakpoint()



    def fuel_report(self):
        total_fuel_weight = 0
        total_fuel_quantity = 0
        if fsdata.instr['cap_center'] != 0:
            lvl_center = fsdata.instr['lvl_center'] / (128 * 65536)
            weight_center = (fsdata.instr['cap_center'] * lvl_center) * (fsdata.instr['fuel_weight'] / 256)
            quantity_center = fsdata.instr['cap_center'] * lvl_center
            total_fuel_quantity += quantity_center
            total_fuel_weight += weight_center
        if fsdata.instr['cap_center2'] != 0:
            lvl_center2 = fsdata.instr['lvl_center2'] / (128 * 65536)
            weight_center2 = (fsdata.instr['cap_center2'] * lvl_center2) * (fsdata.instr['fuel_weight'] / 256)
            quantity_center2 = fsdata.instr['cap_center'] * lvl_center
            total_fuel_quantity += quantity_center2
            total_fuel_weight += weight_center2
        if fsdata.instr['cap_center3'] != 0:
            lvl_center3 = fsdata.instr['lvl_center3'] / (128 * 65536)
            weight_center3 = (fsdata.instr['cap_center3'] * lvl_center3) * (fsdata.instr['fuel_weight'] / 256)
            quantity_center3 = fsdata.instr['cap_center3'] * lvl_center3
            total_fuel_quantity += quantity_center3
            total_fuel_weight += weight_center3
        
        if fsdata.instr['cap_main_left'] != 0:
            lvl_main_left = fsdata.instr['lvl_main_left'] / (128 * 65536)
            weight_main_left = (fsdata.instr['cap_main_left'] * lvl_main_left) * (fsdata.instr['fuel_weight'] / 256)
            quantity_main_left = fsdata.instr['cap_main_left'] * lvl_main_left
            total_fuel_quantity += quantity_main_left
            total_fuel_weight += weight_main_left
        if fsdata.instr['cap_main_right'] != 0:
            lvl_main_right = fsdata.instr['lvl_main_right'] / (128 * 65536)
            weight_main_right = (fsdata.instr['cap_main_right'] * lvl_main_right) * (fsdata.instr['fuel_weight'] / 256)
            quantity_main_right = fsdata.instr['cap_main_right'] * lvl_main_right
            total_fuel_quantity += quantity_main_right
            total_fuel_weight += weight_main_right
        if fsdata.instr['cap_aux_left'] != 0:
            lvl_aux_left = fsdata.instr['lvl_aux_left'] / (128 * 65536)
            weight_aux_left = (fsdata.instr['cap_aux_left'] * lvl_aux_left) * (fsdata.instr['fuel_weight'] / 256)
            quantity_aux_left = fsdata.instr['cap_aux_left'] * lvl_aux_left
            total_fuel_quantity += quantity_aux_left
            total_fuel_weight += weight_aux_left
        if fsdata.instr['cap_aux_right'] != 0:
            lvl_aux_right = fsdata.instr['lvl_aux_right'] / (128 * 65536)
            weight_aux_right = (fsdata.instr['cap_aux_right'] * lvl_aux_right) * (fsdata.instr['fuel_weight'] / 256)
            quantity_aux_right = fsdata.instr['cap_aux_right'] * lvl_aux_right
            total_fuel_quantity += quantity_aux_right
            total_fuel_weight += weight_aux_right
        if fsdata.instr['cap_tip_left'] != 0:
            lvl_tip_left = fsdata.instr['lvl_tip_left'] / (128 * 65536)
            weight_tip_left = (fsdata.instr['cap_tip_left'] * lvl_tip_left) * (fsdata.instr['fuel_weight'] / 256)
            quantity_tip_left = fsdata.instr['cap_tip_left'] * lvl_tip_left
            total_fuel_quantity += quantity_tip_left
            total_fuel_weight += weight_tip_left
        if fsdata.instr['cap_tip_right'] != 0:
            lvl_tip_right = fsdata.instr['lvl_tip_right'] / (128 * 65536)
            weight_tip_right = (fsdata.instr['cap_tip_right'] * lvl_tip_right) * (fsdata.instr['fuel_weight'] / 256)
            quantity_tip_right = fsdata.instr['cap_tip_right'] * lvl_tip_right
            total_fuel_quantity += quantity_tip_right
            total_fuel_weight += weight_tip_right
        self.output (F'total fuel: {round(total_fuel_weight)} pounds. ')
        self.output (F'{round(total_fuel_quantity)} gallons. ')
        total_fuel_flow = fsdata.instr['eng1_fuel_flow'] + fsdata.instr['eng2_fuel_flow'] + fsdata.instr['eng3_fuel_flow'] + fsdata.instr['eng4_fuel_flow']
        self.output (F'Total fuel flow: {round(total_fuel_flow)} P P H')
        pub.sendMessage('reset', arg1=True)
    def fuel_flow_report (self):
        num_engines = fsdata.instr['num_engines']
        self.output ("Fuel flow: ")
        self.output (F'Engine 1: {round(fsdata.instr["eng1_fuel_flow"])}.')
        if num_engines >= 2:
            self.output (F'Engine 2: {round(fsdata.instr["eng2_fuel_flow"])}.')
        if num_engines >= 3:
            self.output (F'Engine 3: {round(fsdata.instr["eng3_fuel_flow"])}.')
        if num_engines >= 4:
            self.output (F'Engine 4: {round(fsdata.instr["eng4_fuel_flow"])}.')
        pub.sendMessage('reset', arg1=True)
    def read_fuel_tank(self, key):
        if self.tanks[key].name == 'center':
            percentage = fsdata.instr['lvl_center'] / (128 * 65536)
            weight = round((fsdata.instr['cap_center'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_center'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        elif self.tanks[key].name == 'center2':
            percentage = fsdata.instr['lvl_center2'] / (128 * 65536)
            weight = round((fsdata.instr['cap_center2'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_center2'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        elif self.tanks[key].name == 'center3':
            percentage = fsdata.instr['lvl_center3'] / (128 * 65536)
            weight = round((fsdata.instr['cap_center3'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_center3'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        elif self.tanks[key].name == 'main left':
            percentage = fsdata.instr['lvl_main_left'] / (128 * 65536)
            weight = round((fsdata.instr['cap_main_left'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_main_left'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        elif self.tanks[key].name == 'main right':
            percentage = fsdata.instr['lvl_main_right'] / (128 * 65536)
            weight = round((fsdata.instr['cap_main_right'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_main_right'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        elif self.tanks[key].name == 'aux left':
            percentage = fsdata.instr['lvl_aux_left'] / (128 * 65536)
            weight = round((fsdata.instr['cap_aux_left'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_aux_left'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        elif self.tanks[key].name == 'aux right':
            percentage = fsdata.instr['lvl_aux_right'] / (128 * 65536)
            weight = round((fsdata.instr['cap_aux_right'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_aux_right'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        elif self.tanks[key].name == 'tip left':
            percentage = fsdata.instr['lvl_tip_left'] / (128 * 65536)
            weight = round((fsdata.instr['cap_tip_left'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_tip_left'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        elif self.tanks[key].name == 'tip right':
            percentage = fsdata.instr['lvl_tip_right'] / (128 * 65536)
            weight = round((fsdata.instr['cap_tip_right'] * percentage) * (fsdata.instr['fuel_weight'] / 256))
            quantity = round(fsdata.instr['cap_tip_right'] * percentage)
            self.output (F'{round(percentage * 100)} percent. {weight} pounds. {quantity} gallons')
        

    def fuel_t1(self):
        try:
            self.output (F'{self.tanks[1].name}: ')
            self.read_fuel_tank(1)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)
    def fuel_t2(self):
        try:
            self.output (F'{self.tanks[2].name}: ')
            self.read_fuel_tank(2)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)
    def fuel_t3(self):
        try:
            self.output (F'{self.tanks[3].name}: ')
            self.read_fuel_tank(3)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)
    def fuel_t4(self):
        try:
            self.output (F'{self.tanks[4].name}: ')
            self.read_fuel_tank(4)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)
    def fuel_t5(self):
        try:
            self.output (F'{self.tanks[5].name}: ')
            self.read_fuel_tank(5)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)
    def fuel_t6(self):
        try:
            self.output (F'{self.tanks[6].name}: ')
            self.read_fuel_tank(6)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)
    def fuel_t7(self):
        try:
            self.output (F'{self.tanks[7].name}: ')
            self.read_fuel_tank(7)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)
    def fuel_t8(self):
        try:
            self.output (F'{self.tanks[8].name}: ')
            self.read_fuel_tank(8)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)
    def fuel_t9(self):
        try:
            self.output (F'{self.tanks[9].name}: ')
            self.read_fuel_tank(9)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)

    def fuel_t10(self):
        try:
            self.output (F'{self.tanks[10].name}: ')
            self.read_fuel_tank(10)
        except KeyError:
            self.output (F"not available. ")
        pub.sendMessage('reset', arg1=True)


    def test_var(self, dt=0):
        self.write_var('FSelBonanzaState', 0)

    def toggleAttitudeMode(self):
        if self.sonifyEnabled:
            pyglet.clock.unschedule(self.sonifyPitch)
            self.PitchUpPlayer.pause()
            self.PitchDownPlayer.pause()
            self.BankPlayer.pause ()
            self.sonifyEnabled = False
            self.output ('attitude mode disabled.')
        else:
            pyglet.clock.schedule_interval(self.sonifyPitch, 0.05)
            self.sonifyEnabled = True
            self.output ('attitude mode enabled')
        pub.sendMessage('reset', arg1=True)





    def readCallouts (self, dt=0):
        if self.calloutsEnabled:
            result = pyuipc.read (self.pyuipcRadioAlt)
            radio_alt = round(result[0] / 65536 * 3.28084)
            vspeed = fsdata.instr['VerticalSpeed']
            callout = 0
            if vspeed < -50:
                for i in self.calloutsHigh:
                    if radio_alt <= i + 5 and radio_alt >= i - 5 and self.calloutState[i] == False:
                        source = pyglet.media.load (F'sounds\\{str(i)}.wav')
                        source.play()
                        self.calloutState[i] = True
                        
                for i in self.calloutsLow:
                    if radio_alt <= i + 3 and radio_alt >= i - 3 and self.calloutState[i] == False:
                        source = pyglet.media.load (F'sounds\\{str(i)}.wav')
                        source.play()
                        self.calloutState[i] = True
                        
            
    ## read various instrumentation automatically
    def readInstruments(self, dt=0):
        flapsTransit = False
        # Get data from simulator
        self.getPyuipcData()

        # self.output (fsdata.instr['test'].decode())
        if fsdata.instr['TextDisplay'] != self.oldInstr['TextDisplay']:
            self.output (fsdata.instr['TextDisplay'].decode())
        # read aircraft name and set up fuel tank info
        if fsdata.instr['AircraftName'] != self.oldAircraftName:
            self.output (f"current aircraft: {fsdata.instr['AircraftName'].decode('UTF-8')}")
            self.oldAircraftName = fsdata.instr['AircraftName']
            self.setup_fuel_tanks()
        # detect if aircraft is on ground or airborne.
        if self.oldInstr['OnGround'] != fsdata.instr['OnGround']:
            if fsdata.instr['OnGround'] == False:
                self.output ("Positive rate.")
                log.debug("unscheduling groundspeed")
                pyglet.clock.unschedule(self.readGroundSpeed)
                self.groundSpeed = False
                self.airborne = True
                log.debug("unscheduling heading lock")
                pyglet.clock.unschedule(self.play_heading_tones)
                self.runway_guidance = False
        # landing gear
        if fsdata.instr['Gear'] != self.oldInstr['Gear']:
            if fsdata.instr['Gear'] == 0:
                self.output ('Gear up.')
            elif fsdata.instr['Gear'] == 16383:
                self.output ('Gear down.')
            self.oldInstr['Gear'] = fsdata.instr['Gear']

        # if flaps position has changed, flaps are in motion. We need to wait until they have stopped moving to read the value.
        if self.flapsEnabled:
            if fsdata.instr['Flaps'] != self.oldInstr['Flaps']:
                flapsTransit = True
                while flapsTransit:
                    self.getPyuipcData()
                    if fsdata.instr['Flaps'] != self.oldInstr['Flaps']:
                        self.oldInstr['Flaps'] = fsdata.instr['Flaps']
                        time.sleep (0.2)
                    else:
                        flapsTransit = False
                
                self.output (F'Flaps {fsdata.instr["Flaps"]:.0f}')
                self.oldInstr['Flaps'] = fsdata.instr['Flaps']
            # announce radio frequency changes
        if fsdata.instr['Com1Freq'] != self.oldInstr['Com1Freq']:
            self.output (F"com 1, {fsdata.instr['Com1Freq']}")
        if fsdata.instr['Com2Freq'] != self.oldInstr['Com2Freq']:
            self.output (F"com 2, {fsdata.instr['Com2Freq']}")

        # spoilers
        if self.oldInstr['Spoilers'] != fsdata.instr['Spoilers']:
            if fsdata.instr['Spoilers'] == 4800:
                self.output ("spoilers armed.")
            elif fsdata.instr['Spoilers'] == 16384:
                self.output(f'Spoilers deployed')
            elif fsdata.instr['Spoilers'] == 0:
                if self.oldInstr['Spoilers'] == 4800:
                    self.output(F'arm spoilers off')
                else:
                    self.output(F'Spoilers retracted')
        if self.oldInstr['ApAltitude'] != fsdata.instr['ApAltitude']:
            self.output(F"Altitude set to {round(fsdata.instr['ApAltitude'])}")
        if self.APEnabled:
            if self.oldInstr['ApHeading'] != fsdata.instr['ApHeading']:
                self.output (F"{fsdata.instr['ApHeading']} degrees")
            if self.oldInstr['ApAirspeed'] != fsdata.instr['ApAirspeed']:
                self.output (F"{fsdata.instr['ApAirspeed']}")
            if self.oldInstr['ApMach'] != fsdata.instr['ApMach']:
                self.output (F"mach {fsdata.instr['ApMach']:.2f}")
            if self.oldInstr['ApVerticalSpeed'] != fsdata.instr['ApVerticalSpeed']:
                self.output (F"{fsdata.instr['ApVerticalSpeed']} feet per minute")



        # transponder
        if fsdata.instr['Transponder'] != self.oldInstr['Transponder']:
            self.output(F'Squawk {fsdata.instr["Transponder"]:x}')
        # next waypoint
        if fsdata.instr['NextWPId'] != self.oldInstr['NextWPId']:
            time.sleep(3)
            self.getPyuipcData()
            self.readWaypoint(0)
            self.oldInstr['NextWPId'] = fsdata.instr['NextWPId']
        # read autobrakes
        if fsdata.instr['AutoBrake'] != self.oldInstr['AutoBrake']:
            if fsdata.instr['AutoBrake'] == 0:
                brake = 'R T O'
            elif fsdata.instr['AutoBrake'] == 1:
                brake = 'off'
            elif fsdata.instr['AutoBrake'] == 2:
                brake = 'position 1'
            elif fsdata.instr['AutoBrake'] == 3:
                brake = 'position 2'
            elif fsdata.instr['AutoBrake'] == 4:
                brake = 'position 3'
            elif fsdata.instr['AutoBrake'] == 5:
                brake = 'maximum'
            self.output (F'Auto brake {brake}')
        if fsdata.instr['ElevatorTrim'] != self.oldInstr['ElevatorTrim'] and fsdata.instr['ApMaster'] != 1 and self.trimEnabled:
            if fsdata.instr['ElevatorTrim'] < 0:
                self.output (F"Trim down {abs(round (fsdata.instr['ElevatorTrim'], 2))}")
            else:
                self.output (F"Trim up {round (fsdata.instr['ElevatorTrim'], 2)}")


        if self.AltHPA != self.oldHPA:
            self.output (F'Altimeter: {self.AltHPA}, {self.AltInches / 100} inches')
            self.oldHPA = self.AltHPA
        # read nav1 ILS info if enabled
        if self.readILSEnabled:
            if fsdata.instr['Nav1Signal'] == 256 and self.LocDetected == False and fsdata.instr['Nav1Type']:
                self.sapi_q.put (F'localiser is alive')
                self.LocDetected = True
                pyglet.clock.schedule_interval (self.readILS, self.ILSInterval)
            if fsdata.instr['Nav1GS'] and self.GSDetected == False:
                self.sapi_q.put (F'Glide slope is alive.')
                self.GSDetected = True
                
            
            
            if fsdata.instr['Nav1Type'] and self.HasLoc == False:
                self.sapi_q.put (F'Nav 1 has localiser')
                self.HasLoc = True
            if fsdata.instr['Nav1GSAvailable'] and self.HasGS == False:
                self.sapi_q.put (F'Nav 1 has glide slope')
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
        self.readToggle('Eng1FuelValve', 'number 1 fuel valve', 'open', 'closed')
        self.readToggle('Eng2FuelValve', 'number 2 fuel valve', 'open', 'closed')
        self.readToggle('Eng3FuelValve', 'number 3 fuel valve', 'open', 'closed')
        self.readToggle('Eng4FuelValve', 'number 4 fuel valve', 'open', 'closed')
        self.readToggle("FuelPump", "Fuel pump", "active", "off")
        self.readToggle("Eng1Select", "number 1", 'selected', 'unselected')
        if fsdata.instr['num_engines'] >= 2:
            self.readToggle("Eng2Select", "number 2", 'selected', 'unselected')
        if fsdata.instr['num_engines'] >= 3:
            self.readToggle("Eng3Select", "number 3", 'selected', 'unselected')
        if fsdata.instr['num_engines'] >= 4:
            self.readToggle("Eng4Select", "number 4", 'selected', 'unselected')

        if self.groundspeedEnabled:
            if fsdata.instr['GroundSpeed'] > 0 and fsdata.instr['OnGround'] and self.groundSpeed == False:
                log.debug("moving on ground. Scheduling groundspeed callouts")
                pyglet.clock.schedule_interval(self.readGroundSpeed, 3)
                self.groundSpeed = True
            elif fsdata.instr['GroundSpeed'] == 0 and self.groundSpeed:
                pyglet.clock.unschedule(self.readGroundSpeed)
                self.groundSpeed = False

        # read APU status
        if fsdata.instr['APUPercentage'] > 4 and self.APUStarting == False and self.APURunning == False and self.APUShutdown == False and self.APUOff == True:
            self.output('A P U starting')
            self.APUStarting = True
            self.APUOff = False
        if fsdata.instr['APUPercentage'] < 100 and self.APURunning:
            self.output ('Shutting down A P U')
            self.APURunning = False
            self.APUShutdown = True
        if fsdata.instr['APUPercentage'] == 100 and self.APUStarting:
            self.APUStarting = False
            self.APURunning = True
            self.output("apu at 100 percent")
        if fsdata.instr['APUPercentage'] == 0 and self.APUOff == False:
            self.output('A P U shut down')
            self.APURunning = False
            self.APUStarting = False
            self.APUShutdown = False
            self.APUOff = True


        if fsdata.instr['APUGenerator'] and self.APUGenerator == False:
            self.output (F"{round(fsdata.instr['APUVoltage'])} volts")
            self.APUGenerator = True
        if fsdata.instr['APUGenerator'] == False:
            self.APUGenerator = False


        # read engine status on startup.
        if fsdata.instr['Eng1FuelFlow'] > 10 and fsdata.instr['Eng1Starter'] and self.Eng1FuelFlow == False:
            self.output ('Number 1 fuel flow')
            self.Eng1FuelFlow = True
        if fsdata.instr['Eng2FuelFlow'] > 10 and fsdata.instr['Eng2Starter'] and self.Eng2FuelFlow == False:
            self.output ('Number 2 fuel flow')
            self.Eng2FuelFlow = True
        if fsdata.instr['Eng3FuelFlow'] > 10 and fsdata.instr['Eng3Starter'] and self.Eng3FuelFlow == False:
            self.output ('Number 3 fuel flow')
            self.Eng3FuelFlow = True
        if fsdata.instr['Eng4FuelFlow'] > 10 and fsdata.instr['Eng4Starter'] and self.Eng4FuelFlow == False:
            self.output ('Number 4 fuel flow')
            self.Eng4FuelFlow = True
        if fsdata.instr['Eng1N2'] > 5 and self.Eng1N2 == False and fsdata.instr['Eng1Starter']:
            self.output ('number 1, 5 percent N2')
            self.Eng1N2 = True
        if fsdata.instr['Eng1N1'] > 5 and self.Eng1N1 == False  and fsdata.instr['Eng1Starter']:
            self.output ('number 1, 5 percent N1')
            self.Eng1N1 = True
        if fsdata.instr['Eng2N2'] > 5 and self.Eng2N2 == False  and fsdata.instr['Eng2Starter']:
            self.output ('number 2, 5 percent N2')
            self.Eng2N2 = True
        if fsdata.instr['Eng2N1'] > 5 and self.Eng2N1 == False  and fsdata.instr['Eng2Starter']:
            self.output ('number 2, 5 percent N1')
            self.Eng2N1 = True
        if fsdata.instr['Eng3N2'] > 5 and self.Eng3N2 == False  and fsdata.instr['Eng3Starter']:
            self.output ('number 3, 5 percent N2')
            self.Eng3N2 = True
        if fsdata.instr['Eng3N1'] > 5 and self.Eng3N1 == False  and fsdata.instr['Eng3Starter']:
            self.output ('number 3, 5 percent N1')
            self.Eng3N1 = True
        if fsdata.instr['Eng4N2'] > 5 and self.Eng4N2 == False  and fsdata.instr['Eng4Starter']:
            self.output ('number 4, 5 percent N2')
            self.Eng4N2 = True
        if fsdata.instr['Eng4N1'] > 5 and self.Eng4N1 == False  and fsdata.instr['Eng4Starter']:
            self.output ('number 4, 5 percent N1')
            self.Eng4N1 = True





        # read altitude every 1000 feet
        for i in range (1000, 65000, 1000):
            if fsdata.instr['Altitude'] >= i - 10 and fsdata.instr['Altitude'] <= i + 10 and self.altFlag[i] == False:
                self.speak (F"{i} feet")
                self.altFlag[i] = True
            elif fsdata.instr['Altitude'] >= i + 100:
                self.altFlag[i] = False
        
        # read Bonanza instruments
        if 'Bonanza' in fsdata.instr['AircraftName'].decode():
            self.read_bonanza()
            self.read_cabin()
        # read cherokee instruments
        if 'Cherokee' in fsdata.instr['AircraftName'].decode():
            self.read_cherokee()
            self.read_cabin()
        # maintain state of instruments so we can check on the next run.
        self.oldInstr = copy.deepcopy(fsdata.instr)
    def read_bonanza(self):
        self.readToggle('BatterySwitch', "battery", "active", "off")
        self.readToggle('TipTankLeftPump', 'left tip tank pump', 'active', 'off')
        self.readToggle('TipTankRightPump', 'right tip tank pump', 'active', 'off')
        self.readToggle('TipTanksAvailable', 'tip tanks', 'installed', 'not installed')
        self.readToggle('window', 'window', 'open', 'closed')
        self.readToggle('fan', 'fan', 'active', 'off')
        # fuel selector
        fsel_state = {
            0: 'off',
            1: 'left',
            2: 'right',
        }
        if fsdata.instr['FuelSelector'] != self.old_a2a_fsel:
            fsel = fsdata.instr['FuelSelector']
            self.output (F"fuel selector {fsel_state[fsel]}")
            self.old_a2a_fsel = fsdata.instr['FuelSelector']

    def read_cherokee(self):
        self.readToggle('BatterySwitch', "battery", "active", "off")
        self.readToggle('window', 'window', 'open', 'closed')
        # fuel selector
        fsel_state = {
            0: 'off',
            1: 'left',
            2: 'right',
        }
        if fsdata.instr['FuelSelector'] != self.old_a2a_fsel:
            fsel = fsdata.instr['FuelSelector']
            self.output (F"fuel selector {fsel_state[fsel]}")
            self.old_a2a_fsel = fsdata.instr['FuelSelector']
    def read_cabin(self):
        # read cabin climate info such as heat and defrost
        if fsdata.instr['CabinHeat'] != self.oldInstr['CabinHeat']:
            self.output (F"cabin heat at {int(fsdata.instr['CabinHeat'])}")
            self.oldInstr['CabinHeat'] = fsdata.instr['CabinHeat']
    def readEngTemps(self):
        if self.use_metric == False:
            Eng1Temp = round(9.0/5.0 * fsdata.instr['Eng1ITT'] + 32)
            Eng2Temp = round(9.0/5.0 * fsdata.instr['Eng2ITT'] + 32)
            Eng3Temp = round(9.0/5.0 * fsdata.instr['Eng3ITT'] + 32)
            Eng4Temp = round(9.0/5.0 * fsdata.instr['Eng4ITT'] + 32)
        else:
            Eng1Temp = fsdata.instr['Eng1ITT']
            Eng2Temp = fsdata.instr['Eng2ITT']
            Eng3Temp = fsdata.instr['Eng3ITT']
            Eng4Temp = fsdata.instr['Eng4ITT']
        
    def readGroundSpeed(self, dt=0):
        self.sapi_q.put(F"{fsdata.instr['GroundSpeed']} knotts")

    def readILS(self, dt=0):
        GSNeedle = fsdata.instr['Nav1GSNeedle']
        LocNeedle = fsdata.instr['Nav1LocNeedle']
        if GSNeedle > 0 and GSNeedle < 119:
            GSPercent = GSNeedle / 119 * 100.0
            self.speak (f'up {GSPercent:.0f} percent G S I')
        elif GSNeedle < 0 and GSNeedle > -119:
            GSPercent = abs(GSNeedle) / 119 * 100.0
            self.speak (f'down {GSPercent:.0f} percent G S I')
        if LocNeedle > 0 and LocNeedle < 127:
            LocPercent = GSNeedle / 127 * 100.0
            self.speak (F'{LocPercent:.0f} percent right')    
        elif LocNeedle < 0 and LocNeedle > -127:
            LocPercent = abs(GSNeedle) / 127 * 100.0
            self.speak (F'{LocPercent:.0f} percent left')    


    
    def readToggle(self, instrument, name, onMessage, offMessage):
        ## There are several aircraft functions that are simply on/off toggles. 
        ## This function allows reading those without a bunch of duplicate code.
        try:
            if self.oldInstr[instrument] != fsdata.instr[instrument]:
                if fsdata.instr[instrument]:
                    self.output (F'{name} {onMessage}.')
                else:
                    self.output (F'{name} {offMessage}')
                self.oldInstr[instrument] = fsdata.instr[instrument]
        except Exception as e:
            log.exception(F"error in instrument toggle. Instrument was {instrument}")

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
        msg = ""
        try:
            WPId = fsdata.instr['NextWPId'].decode ('UTF-8')
            distance = fsdata.instr['NextWPDistance'] * 0.00053995
            msg = F'Next waypoint: {WPId}, distance: {distance:.1f} nautical miles. '
            msg = msg + F'baring: {fsdata.instr["NextWPBaring"]:.0f}\n'
            # read estimated time enroute to next waypoint
            strTime = self.secondsToText(fsdata.instr['NextWPETE'])
            msg = msg + strTime
            if self.triggered:
                self.speak(msg)
                self.triggered = False
            else:
                self.output(msg)
            pub.sendMessage('reset', arg1=True)
        except Exception as e:
            log.exception ("error reading waypoint info")



        

    def readSimConnectMessages(self, dt=0,triggered = False):
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
                if self.oldSimCChanged != self.SimCData['SimCChanged'] or self.oldSimCData != self.SimCData['SimCData']:
                    # if this is an rc message, handle that.
                    if self.SimCData['SimCType'] == 768:
                        self.readRC4(triggered=triggered)
                    else:
                        i = 1
                        SimCMessageRaw = self.SimCMessage[:self.SimCData['SimCLength']]
                        SimCMessage = SimCMessageRaw.split('\x00')
                        for index, message in enumerate(SimCMessage):
                            if "cache" in message:
                                continue
                            if index < 2 and message != "":
                                if not self.MuteSimC:
                                    self.output(f'{message}')
                                self.CachedMessage[index] = message
                            elif message != "":
                                if not self.MuteSimC:
                                    self.output(f'{i}: {message}')
                                self.CachedMessage[index] = f'{i}: {message}'
                                i += 1


                    if not RCMessage:
                        self.CachedMessage[index] = 'EOM'
                    self.oldSimCChanged = self.SimCData['SimCChanged']
                    self.oldSimCData = self.SimCData['SimCData']
                    
                if triggered == 1:
                    pub.sendMessage('reset', arg1=True)
            # else:
                    # pub.sendMessage('reset', arg1=True)
        except KeyError:
            pass
        except Exception as e:
            log.exception (F'error reading SimConnect message. {SimCMessageRaw}')


    def readCachedSimConnectMessages(self):

        for i, message in self.CachedMessage.items():
            if message == 'EOM':
                break
            else:
                self.output (message)
        pub.sendMessage('reset', arg1=True)
    
    def readRC4(self, triggered = False):
        msgUpdated = False
        msgRaw = self.SimCMessage[:self.SimCData['SimCLength']]
        msg = msgRaw.splitlines()
        if len(msg) == 1:
            return
        # log.error(F'{msg}')
        if self.oldRCMsg != msg[1] and msg[1][:3] != 'Rwy' and msg[1][:1] != '<':
            msgUpdated = True
        if triggered:
            msgUpdated = True
        for index, message in enumerate(msg):
            if index == 0 or message == "" or '<' in message or '/' in message:
                continue
            if message != "" and msgUpdated == True:
                if not self.MuteSimC:
                    self.output (message.replace('\x00', ''))
                self.CachedMessage[index] = message
        self.CachedMessage[index] = 'EOM'
        self.oldRCMsg = msg[1]


    ## Announce Talking Flight Monitor (TFM) info
    def AnnounceInfo(self, dt=0, triggered = 0):
        msg = ""
        # Get data from simulator
        self.getPyuipcData()
        # Lookup nearest cities to aircraft position using the Geonames database.
        self.airport="test"
        try:
            response = requests.get('http://api.geonames.org/findNearbyPlaceNameJSON?style=long&lat={}&lng={}&username={}&cities=cities5000&radius=200'.format(fsdata.instr['Lat'],fsdata.instr['Long'], self.geonames_username))
            response.raise_for_status() # throw an exception if we get an error from Geonames.
            data =response.json()
            if len(data['geonames']) >= 1:
                bearing = calcBearing (fsdata.instr['Lat'], fsdata.instr['Long'], float(data["geonames"][0]["lat"]), float(data["geonames"][0]["lng"]))
                bearing = (degrees(bearing) +360) % 360
                if self.use_metric == False:
                    distance = float(data["geonames"][0]["distance"]) / 1.609
                    units = 'miles'
                else:
                    distance = float(data["geonames"][0]["distance"])
                    units = 'kilometers'
                msg = 'Closest city: {} {}. {:.1f} {}. Bearing: {:.0f}. \n'.format(data["geonames"][0]["name"],data["geonames"][0]["adminName1"],distance,units,bearing)
            else:
                distance = 0
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            log.error('latitude:{}, longitude:{}'.format(fsdata.instr['Lat'], fsdata.instr['Long']))
            log.exception('error getting nearest city: ' + str(e))
            self.output ('cannot find nearest city. Geonames connection error. Check error log.')
        except requests.exceptions.HTTPError as e:
            log.error('latitude:{}, longitude:{}'.format(fsdata.instr['Lat'], fsdata.instr['Long']))
            log.exception('error getting nearest city. Error while connecting to Geonames.' + str(e))
            self.output ('cannot find nearest city. Geonames may be busy. Check error log.')
            
        ## Check if we are flying over water.
        ## If so, announce body of water.
        ## We will continue to announce over water until the maximum radius of the search is reached.
        try:
            response = requests.get('http://api.geonames.org/oceanJSON?lat={}&lng={}&username={}'.format(fsdata.instr['Lat'],fsdata.instr['Long'], self.geonames_username))
            data = response.json()
            if 'ocean' in data and distance >= 1:
                msg = msg + 'currently over {}\n'.format(data['ocean']['name'])
                self.oceanic = True
        except Exception as e:
            log.error('Error determining oceanic information: ' + str(e))
            log.exception(str(e))
            
        ## Read time zone information
        try:
            response = requests.get('http://api.geonames.org/timezoneJSON?lat={}&lng={}&username={}'.format(fsdata.instr['Lat'],fsdata.instr['Long'], self.geonames_username))
            data = response.json()
            
            if 'timezoneId' in data:
                tz = get_timezone(data['timezoneId'])
                tzName = get_timezone_name(tz, locale=Locale.parse('en_US'))
                if tzName != self.oldTz:
                    msg = msg + '{}.\n'.format(tzName)
                    self.oldTz = tzName
        except Exception as e:
            log.error('Error determining timezone: ' + str(e))
            log.exception(str(e))
        if self.triggered:
            self.output(msg)
            self.triggered = False
        else:
            self.output(msg)

    
    ## Read data from the simulator
    def getPyuipcData(self, type=0, dt=0):
        try:
            # read types: 0 - all, 1 - instrumentation, 2 - SimConnect, 3 - attitude    
            if type == 0 or type == 1:
                fsdata.instr = dict(zip(fsdata.InstrOffsets.keys(), pyuipc.read(self.pyuipcOffsets)))
                # prepare instrumentation variables
                hexCode = hex(fsdata.instr['Com1Freq'])[2:]
                fsdata.instr['Com1Freq'] = float('1{}.{}'.format(hexCode[0:2],hexCode[2:]))
                hexCode = hex(fsdata.instr['Com2Freq'])[2:]
                fsdata.instr['Com2Freq'] = float('1{}.{}'.format(hexCode[0:2],hexCode[2:]))
                # lat lon
                fsdata.instr['Lat'] = fsdata.instr['Lat'] * (90.0/(10001750.0 * 65536.0 * 65536.0))
                fsdata.instr['Long'] = fsdata.instr['Long'] * (360.0/(65536.0 * 65536.0 * 65536.0 * 65536.0))
                fsdata.instr['Flaps'] = fsdata.instr['Flaps'] / 256
                fsdata.instr['OnGround'] = bool(fsdata.instr['OnGround'])
                fsdata.instr['ParkingBrake'] = bool(fsdata.instr['ParkingBrake'])
                fsdata.instr['Altitude'] = round(fsdata.instr['Altitude'])
                fsdata.instr['GroundAltitude'] = fsdata.instr['GroundAltitude'] / 256 * 3.28084
                fsdata.instr['ApHeading'] = round(fsdata.instr['ApHeading']/65536*360)
                fsdata.instr['ApAltitude'] = fsdata.instr['ApAltitude'] / 65536 * 3.28084
                fsdata.instr['ApMach'] = fsdata.instr['ApMach'] / 65536
                # self.headingTrue = floor(((fsdata.instr['Heading'] * 360) / (65536 * 65536)) + 0.5)
                self.headingTrue = fsdata.instr['Heading'] * 360 / (65536 * 65536)
                self.headingCorrected = fsdata.instr['CompassHeading']
                fsdata.instr['AirspeedTrue'] = round(fsdata.instr['AirspeedTrue'] / 128)
                fsdata.instr['AirspeedIndicated'] = round(fsdata.instr['AirspeedIndicated'] / 128)
                fsdata.instr['AirspeedMach'] = fsdata.instr['AirspeedMach'] / 20480
                fsdata.instr['GroundSpeed'] = round((fsdata.instr['GroundSpeed'] * 3600) / (65536 * 1852))
                fsdata.instr['NextWPETA'] = time.strftime('%H:%M', time.localtime(fsdata.instr['NextWPETA']))
                fsdata.instr['NextWPBaring'] = degrees(fsdata.instr['NextWPBaring'])
                fsdata.instr['DestETE'] =self.secondsToText(fsdata.instr['DestETE'])
                fsdata.instr['DestETA'] = time.strftime('%H:%M', time.localtime(fsdata.instr['DestETA']))
                fsdata.instr['ElevatorTrim'] = degrees(fsdata.instr['ElevatorTrim'])
                fsdata.instr['VerticalSpeed'] = round ((fsdata.instr['VerticalSpeed'] * 3.28084) * -1, 0)
                self.tempC = round(fsdata.instr['AirTemp'] / 256, 0)
                self.tempF = round(9.0/5.0 * self.tempC + 32)
                self.AGLAltitude = fsdata.instr['Altitude'] - fsdata.instr['GroundAltitude']
                self.RadioAltitude = fsdata.instr['RadioAltimeter']  / 65536 * 3.28084
                fsdata.instr['APUPercentage'] = round(fsdata.instr['APUPercentage'])
                self.EngSelect = list(map(int, '{0:08b}'.format(fsdata.instr['EngineSelectFlags'])))
                fsdata.instr['Eng1Select'] = self.EngSelect[7]
                fsdata.instr['Eng2Select'] = self.EngSelect[6]
                fsdata.instr['Eng3Select'] = self.EngSelect[5]
                fsdata.instr['Eng4Select'] = self.EngSelect[4]
                self.Nav1Bits = list(map(int, '{0:08b}'.format(fsdata.instr['Nav1Flags'])))
                fsdata.instr['Nav1Type'] = self.Nav1Bits[0]
                fsdata.instr['Nav1GSAvailable'] = self.Nav1Bits[6]
                self.DoorBits = list(map(int, '{0:08b}'.format(fsdata.instr['Doors'])))
                fsdata.instr['Door1'] = self.DoorBits[7]
                fsdata.instr['Door2'] = self.DoorBits[6]
                fsdata.instr['Door3'] = self.DoorBits[5]
                fsdata.instr['Door4'] = self.DoorBits[4]
                self.lights = list(map(int, '{0:08b}'.format(fsdata.instr['Lights'])))
                self.lights1 = list(map(int, '{0:08b}'.format(fsdata.instr['Lights1'])))
                # breakpoint()
                fsdata.instr['CabinLights'] = self.lights[0]
                fsdata.instr['LogoLights'] = self.lights[1]
                fsdata.instr['WingLights'] = self.lights1[0]
                fsdata.instr['RecognitionLights'] = self.lights1[1]
                fsdata.instr['InstrumentLights'] = self.lights1[2]
                fsdata.instr['StrobeLights'] = self.lights1[3]
                fsdata.instr['TaxiLights'] = self.lights1[4]
                fsdata.instr['LandingLights'] = self.lights1[5]
                fsdata.instr['BeaconLights'] = self.lights1[6]
                fsdata.instr['NavigationLights'] = self.lights1[7]
                self.AltQNH = fsdata.instr['Altimeter'] / 16
                self.AltHPA = floor(self.AltQNH + 0.5)
                self.AltInches = floor(((100 * self.AltQNH * 29.92) / 1013.2) + 0.5)
                fsdata.instr['Eng1ITT'] = round(fsdata.instr['Eng1ITT'] / 16384)
                fsdata.instr['Eng2ITT'] = round(fsdata.instr['Eng2ITT'] / 16384)
                fsdata.instr['Eng3ITT'] = round(fsdata.instr['Eng3ITT'] / 16384)
                fsdata.instr['Eng4ITT'] = round(fsdata.instr['Eng4ITT'] / 16384)
                fsdata.instr['WindDirection'] = fsdata.instr['WindDirection'] *360/65536
                # prepare A2A aircraft data
                fsdata.bonanza = dict(zip(fsdata.BonanzaOffsets.keys(), pyuipc.read(self.pyuipcBonanza)))
                fsdata.cherokee = dict(zip(fsdata.CherokeeOffsets.keys(), pyuipc.read(self.pyuipcCherokee)))
                self.ac = fsdata.instr['AircraftName'].decode()
                if "Bonanza" in self.ac:
                    fsdata.instr.update(fsdata.bonanza)
                if 'Cherokee' in self.ac:
                    fsdata.instr.update(fsdata.cherokee)







            if type == 0 or type == 2:
                # prepare simConnect message data
                try:
                    if self.SimCEnabled:
                        self.SimCData = dict(zip(fsdata.SimCOffsets.keys(), pyuipc.read(self.pyuipcSIMC)))
                        self.SimCMessage = self.SimCData['SimCData'].decode ('UTF-8', 'ignore')
                except Exception as e:
                    log.exception ('error reading simconnect message data')
            if type == 0 or type == 3:
                # Read attitude
                self.attitude = dict(zip(fsdata.AttitudeOffsets.keys(), pyuipc.read(self.pyuipcAttitude)))
                self.attitude['Pitch'] = self.attitude['Pitch'] * 360 / (65536 * 65536)
                self.attitude['Bank'] = self.attitude['Bank'] * 360 / (65536 * 65536)
        except pyuipc.FSUIPCException as e:
            log.exception("error reading from simulator. This could be normal. Exiting.")
            pub.sendMessage("exit", msg="")
    ## a2a functions
    def read_binary_var(self, offset, var):
        # read a l:var from the simulator
        param = hex(offset + 0x70000)
        
        var_name = var
        var = ":" + var
        pyuipc.write([(0x0d6c, 'u', offset + 0x70000), (0x0d70, -40, var.encode())])
        result = pyuipc.read([(offset, 'F')])
        return result[0]

    def read_long_var(self, offset, var):
        # read a l:var from the simulator
        param = hex(offset + 0x10000)
        
        var_name = var
        var = ":" + var
        pyuipc.write([(0x0d6c, 'u', offset + 0x10000), (0x0d70, -40, var.encode())])
        result = pyuipc.read([(offset, 'F')])
    # self.a2   a_instr[var_name] = result[0]
        return result[0]

    def write_var(self, var, value):
        var = "::" + var
        pyuipc.write([(0x66f0, 'F', value)])
        pyuipc.write([(0x0d6c, 'u', 0x166f0),
            (0x0d70, -40, var.encode()),
            
        ])





    def macro(self, macro):
        # execute an FSUIPC macro 
        pyuipc.write([(0x0d70, -40, macro.encode())])

    def read_a2a_info (self, dt=0):
        if fsdata.instr['BatterySwitch'] != self.old_a2a_bat:
            if fsdata.instr['BatterySwitch']:
                self.output ("Battery on")
            else:
                self.output ("battery off")
            self.old_a2a_bat = fsdata.instr['BatterySwitch']
        if fsdata.instr['TipTankLeftPump'] != self.old_a2a_ttl:
            if fsdata.instr['TipTankLeftPump']:
                self.output ("left tip tank pump on")
            else:
                self.output ("left tip tank pump off")
            self.old_a2a_ttl = fsdata.instr['TipTankLeftPump']
        if fsdata.instr['TipTankRightPump'] != self.old_a2a_ttr:
            if fsdata.instr['TipTankRightPump']:
                self.output ("Right tip tank pump on")
            else:
                self.output ("Right tip tank pump off")
            self.old_a2a_ttr = fsdata.instr['TipTankRightPump']

        if fsdata.instr['TipTanksAvailable'] != self.old_a2a_tt:
            if fsdata.instr['TipTanksAvailable']:
                self.output(F"tip tanks available")
            else:
                self.output ("Tip tanks not available")
            self.old_a2a_tt = fsdata.instr['TipTanksAvailable']
        # fuel selector
        fsel_state = {
            0: 'off',
            1: 'left',
            2: 'right'
        }
        if fsdata.instr['FuelSelector'] != self.old_a2a_fsel:
            fsel = fsdata.instr['FuelSelector']
            self.output (F"fuel selector {fsel_state[fsel]}")
            self.old_a2a_fsel = fsdata.instr['FuelSelector']
        if fsdata.instr['window'] != self.old_a2a_window:
            if fsdata.instr['window'] == 1:
                self.output ("window open")
            else:
                self.output ("window closed")
            self.old_a2a_window = fsdata.instr['window']

    def read_a2a_toggle(self, instrument, name, onMessage, offMessage):
        ## There are several aircraft functions that are simply on/off toggles. 
        ## This function allows reading those without a bunch of duplicate code.
        try:
            if self.old_a2a_instr[instrument] != self.a2a_instr[instrument]:
                if self.a2a_instr[instrument]:
                    self.output (F'{name} {onMessage}.')
                else:
                    self.output (F'{name} {offMessage}')
                self.old_a2a_instr[instrument] = self.a2a_instr[instrument]
        except Exception as e:
            log.exception(F"error in A2A instrument toggle. Instrument was {instrument}")



    def fuel_quantity(self):
        tank_left = round(self.read_long_var(0x66e4, 'FuelLeftWingTank'), 1)
        tank_right = round(self.read_long_var(0x66e4, 'FuelRightWingTank'), 1)
        tip_tank_left = round(self.read_long_var(0x66e4, 'FuelLeftTipTank'), 1)
        tip_tank_right = round(self.read_long_var(0x66e4, 'FuelRightTipTank'), 1)
        self.output (F'left: {tank_left} gallons')
        self.output (F'right: {tank_right} gallons')
        if 'Bonanza' in fsdata.instr['AircraftName'].decode() and fsdata.instr['TipTanksAvailable']:
            self.output (F'left tip: {tip_tank_left} gallons')
            self.output (F'right tip: {tip_tank_right} gallons')
        pub.sendMessage('reset', arg1=True)

    def oil_quantity(self):
        oil = round(self.read_long_var(0x66e4, 'Eng1_OilQuantity'), 1)
        self.output (F'Oil quantity: {oil} gallons, {oil * 4} quarts. ')
        pub.sendMessage('reset', arg1=True)
    def cht (self):
        cht = round(self.read_long_var(0x66e8, 'Eng1_CHT'))
        self.output (F'CHT: {cht}')
        pub.sendMessage('reset', arg1=True)
    def egt (self):
        egt = round(self.read_long_var(0x66d0, 'Eng1_EGTGauge'))
        self.output (F'EGT: {egt}')
        pub.sendMessage('reset', arg1=True)
    def manifold (self):
        manifold = round(self.read_long_var(0x66d4,'Eng1_ManifoldPressure'), 1)
        self.output (F'Manifold pressure: {manifold}')
        pub.sendMessage('reset', arg1=True)
    def gph(self):
        gph = round(self.read_long_var(0x66d8, 'Eng1_gph'), 1)
        self.output (F'Fuel flow: {gph}')
        pub.sendMessage('reset', arg1=True)
    def oil_temp(self):
        oil_temp  = round(self.read_long_var(0x66dc, 'Eng1_OilTemp'), 1)
        self.output (F'oil temperature: {oil_temp}')
        pub.sendMessage('reset', arg1=True)
    def oil_pressure (self):
        oil_pressure = round(self.read_long_var(0x66e0, 'Eng1_OilPressureGauge'), 1)
        self.output (F'oil pressure: {oil_pressure}')
        pub.sendMessage('reset', arg1=True)
    def ammeter (self):
        ammeter = round(self.read_long_var(0x66ec, 'Ammeter1'), 2)
        self.output (F'Ammeter: {ammeter}')
        pub.sendMessage('reset', arg1=True)
    def voltmeter(self):
        voltmeter = round(self.read_long_var(0x66ec, 'Voltmeter') * 100) / 100
        self.output (F'Volt meter: {voltmeter}')
        pub.sendMessage('reset', arg1=True)
    def cabin_temp(self):
     temp = round(self.read_long_var(0x66ec, 'CabinTemp'))
     self.output (F'cabin temperature: {temp}')
     pub.sendMessage('reset', arg1=True)
    def toggle_tip_tank(self):
        # install or remove tip tanks on bonanza aircraft
        if fsdata.instr['TipTanksAvailable']:
            self.write_var("TipTank", 0.0)
        else:
            self.write_var("TipTank", 1.0)
        self.write_var("EquipmentChangeClickSound", 1.0)
        pub.sendMessage('reset', arg1=True)
    def tip_tank_left_on (self):
        self.write_var('TipTankLeftPumpSwitch', 1)
    def tip_tank_left_off (self):
        self.write_var('TipTankLeftPumpSwitch', 0)
        
    def tip_tank_left_toggle (self, msg=None):
        if fsdata.instr['TipTankLeftPump'] == 1 or msg == False:
            self.tip_tank_left_off()
        else:
            self.tip_tank_left_on()

        pub.sendMessage('reset', arg1=True)

    def tip_tank_right_on (self):
        self.write_var('TipTankRightPumpSwitch', 1)
    def tip_tank_right_off (self):
        self.write_var('TipTankRightPumpSwitch', 0)
    def tip_tank_right_toggle(self):
        if fsdata.instr['TipTankRightPump'] == 1:
            self.tip_tank_right_off()
        else:
            self.tip_tank_right_on()
        pub.sendMessage('reset', arg1=True)
    def fuel_selector(self):
        self.macro("bonanza:L:FSelBonanzaState")
        pub.sendMessage('reset', arg1=True)
# cabbin heat and ventilation
    def window_open(self):
        self.write_var('WindowLeft', 1.0)
    def window_close(self):
        self.write_var('WindowLeft', 0.0)
    def window_toggle(self):
        if fsdata.instr['window']:
            self.window_close()
        else:
            self.window_open()
        pub.sendMessage('reset', arg1=True)

        
    def fan_toggle(self):
        self.macro("bonanza:L:VentCabinFanSwitch")
        pub.sendMessage('reset', arg1=True)
    def fan_speed(self):
        spd = self.read_long_var(0x66c8, "VentCabinOverheadFreshAirControl")
        spd += 1
        if spd > 4:
            spd = 0
        spd = int(spd)
        self.write_var("VentCabinOverheadFreshAirControl", spd)


    def cabin_heat_inc(self):
        step = 10
        if self.adjust_heat == False:
            result = pyuipc.read([(0x66c7, 'b')])
            self.tfh = result[0]
            self.output (F'cabin heat: {self.tfh} percent')
            self.adjust_heat = True
            return
        self.tfh = self.tfh + step
        if self.tfh > 100:
            self.tfh = 100
        self.write_var('CabinTempControl', self.tfh)
        

    def cabin_heat_dec(self):
        step = 10
        if self.adjust_heat == False:
            result = pyuipc.read([(0x66c7, 'b')])
            self.tfh = result[0]
            self.output (F'cabin heat: {self.tfh} percent')
            self.adjust_heat = True
            return
        self.tfh = self.tfh - step
        if self.tfh < 0:
            self.tfh = 0
        self.write_var('CabinTempControl', self.tfh)
    def defrost_inc(self):
        step = 10
        if self.adjust_defrost == False:
            result = pyuipc.read([(0x66c8, 'b')])
            self.defrost_level = result[0]
            self.output (F'windshield defrost: {self.defrost_level} percent')
            self.adjust_defrost = True
            return
        self.defrost_level = self.defrost_level + step
        if self.defrost_level > 100:
            self.defrost_level = 100
        self.write_var('WindowDefrosterControlKnob', self.defrost_level)
        

    def defrost_dec(self):
        step = 10
        if self.adjust_defrost == False:
            result = pyuipc.read([(0x66c8, 'b')])
            self.defrost_level = result[0]
            self.output (F'windshield defrost: {self.defrost_level} percent')
            self.adjust_defrost = True
            return
        self.defrost_level = self.defrost_level - step
        if self.defrost_level < 0:
            self.defrost_level = 0
        self.write_var('WindowDefrosterControlKnob', self.defrost_level)
        
    
    def exit_command_mode(self):
        self.adjust_heat = False
        self.adjust_defrost = False
        self.output ("done")
        pub.sendMessage('reset', arg1=True)
        