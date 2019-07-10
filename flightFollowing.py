#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#==============================================================================
# Voice Flight Following - Periodically announce cities along your flight path
# Copyright (C) 2019 by Jason Fayre
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

from __future__ import division

# Import built-ins
import os
import sys
import re
import time
import gzip
# import threading
from contextlib import closing
from math import *
import warnings
import json
import requests
from configparser import SafeConfigParser
import keyboard
from babel import Locale
from babel.dates import get_timezone_name, get_timezone
import pyttsx3
import logging
# initialize the log settings
logging.basicConfig(filename = 'error.log', level = logging.INFO)
# Set encoding
#reload(sys)
#sys.setdefaultencoding('iso-8859-15')  # @UndefinedVariable

# Import pip packages (except failure with debug mode).
try:
	import pyuipc
	pyuipcImported = True
	debug = False
except ImportError:
		pyuipcImported = False
		debug = True


from aviationFormula.aviationFormula import calcBearing
# from aviationFormula import gcDistanceNm

# Import own packages.
from VaLogger import VaLogger
# from voiceAtisUtil import parseVoiceInt, parseVoiceString, CHAR_TABLE

## Main Class of FlightFollowing.
# Run constructor to run the program.
class FlightFollowing(object):
	OFFSETS = [(0x034E,'H'),	# com1freq
			   (0x3118,'H'),	# com2freq
			   (0x3122,'b'),	# radioActive
			   (0x0560,'l'),	# ac Latitude
			   (0x0568,'l'),	# ac Longitude
			   (0x30f0,'h'),	# flaps angle
			  ]
	## Setup the FlightFollowing object.
	# Also starts the voice generation loop.
	def __init__(self,**optional):
		#TODO: Remove the debug code when tested properly.
		
		# Process optional arguments.
		self.debug = optional.get('Debug',debug)
		
		# Get file path.
		self.rootDir = os.path.abspath(os.path.dirname(sys.argv[0]))
		
		# Init logging.
		self.logger = VaLogger(os.path.join(self.rootDir,'voiceAtis','logs'))
		# init config parser
		self.config = SafeConfigParser()
		# First log message.
		self.logger.info('Flight Following started')
		# check for config file. Create it if it doesn't exist.
		exists = os.path.isfile(self.rootDir + "/flightfollowing.ini")
		if exists:
			self.logger.info("config file exists.")
			cfgfile = self.config.read(self.rootDir + "/flightfollowing.ini")
			self.geonames_username = self.config.get('config','geonames_username')
			self.interval = float(self.config.get('config','interval'))
			self.distance_units = self.config.get('config','distance_units')
			self.voice_rate = self.config.get('config','voice_rate')
			
			
		else:
			self.logger.info ("no config file found. It will be created.")
			cfgfile = open (self.rootDir + "/flightfollowing.ini",'w')
			self.config.add_section ('config')
			self.config.set ('config','geonames_username','your_user_name')
			self.config.set ('config','voice_rate','150')
			self.config.set ('config','interval','180')
			self.config.set ('config','distance_units','0')
			
			self.config.write(cfgfile)
			cfgfile.close()
			
		# Establish pyuipc connection
		while True:
			try:
				self.pyuipcConnection = pyuipc.open(0)
				self.pyuipcOffsets = pyuipc.prepare_data(self.OFFSETS)
				self.logger.info('FSUIPC connection established.')
				break
			except NameError:
				self.pyuipcConnection = None
				self.logger.warning('Using voiceAtis without FSUIPC.')
				break
			except:
				self.logger.warning('FSUIPC: No simulator detected. Start your simulator first! Retrying in 20 seconds.')
				time.sleep(20)
		
		# Show debug Info
		#TODO: Remove for release.
		if self.debug:
			self.logger.info('Debug mode on.')
			self.logger.setLevel(ConsoleLevel='debug')
		## add global hotkey definition
		keyboard.add_hotkey('ctrl+alt+c', self.AnnounceInfo)
		self.oldTz = 'none' ## variable for storing timezone name
		# start a thread to read various info such as flaps		
		# t = threading.Thread(target=self.readInstruments, args=())
		# t.start()
		
		# Infinite loop.
		try:
			while True:
				self.AnnounceInfo()
				time.sleep(self.interval)
				pass
				
		except KeyboardInterrupt:
			# Actions at Keyboard Interrupt.
			self.logger.info('Loop interrupted by user.')
			if pyuipcImported:
				self.pyuipc.close()
			
	
	## read various instrumentation automatically such as flaps
	def readInstruments(self):
		old_flaps = 0
		while True:
			# Get data from simulator
			self.getPyuipcData()
			if self.flaps != old_flaps:
				self.atisVoice = 'Flaps {}'.format(self.flaps)
				self.readVoice()
				old_flaps = self.flaps
			time.sleep (10)
		

	## Announce flight following info
	def AnnounceInfo(self):
		# Get data from simulator
		self.getPyuipcData()
		# Lookup nearest cities to aircraft position using the Geonames database.
		self.airport="test"
		try:
			response = requests.get('http://api.geonames.org/findNearbyPlaceNameJSON?style=long&lat={}&lng={}&username={}&cities=cities5000&radius=200'.format(self.lat,self.lon, self.geonames_username))
			r.raise_for_status() # throw an exception if we get an error from Geonames.
			data =response.json()
			if len(data['geonames']) >= 1:
				bearing = calcBearing (self.lat, self.lon, float(data["geonames"][0]["lat"]), float(data["geonames"][0]["lng"]))
				bearing = (degrees(bearing) +360) % 360
				if self.distance_units == '1':
					distance = float(data["geonames"][0]["distance"]) / 1.609
					units = 'miles'
				else:
					distance = float(data["geonames"][0]["distance"])
					units = 'kilometers'
				self.atisVoice='Closest city: {} {}. {:.1f} {}. Bearing: {:.0f}'.format(data["geonames"][0]["name"],data["geonames"][0]["adminName1"],distance,units,bearing)
				self.airport="test"
				# Read the string.
				self.readVoice()
			else:
				distance = 0
		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
			logging.error('latitude:{}, longitude:{}'.format(self.lat, self.lon))
			logging.exception('error getting nearest city: ' + str(e))
			self.atisVoice='cannot find nearest city. Geonames connection error. Check error log.'
			self.readVoice()
		except requests.exceptions.HTTPError as e:
			logging.error('latitude:{}, longitude:{}'.format(self.lat, self.lon))
			logging.exception('error getting nearest city. Error while connecting to Geonames.' + str(e))
			self.atisVoice='cannot find nearest city. Geonames may be busy. Check error log.'
			self.readVoice()
			
		## Check if we are flying over water.
		## If so, announce body of water.
		## We will continue to announce over water until the maximum radius of the search is reached.
		try:
			response = requests.get('http://api.geonames.org/oceanJSON?lat={}&lng={}&username={}'.format(self.lat,self.lon, self.geonames_username))
			data = response.json()
			if 'ocean' in data and distance >= 1:
				self.atisVoice = 'currently over {}'.format(data['ocean']['name'])
				self.oceanic = True
				self.readVoice()
		except Exception as e:
			logging.error('Error determining oceanic information: ' + str(e))
			logging.exception(str(e))
			sys.exit()
			
		## Read time zone information
		try:
			response = requests.get('http://api.geonames.org/timezoneJSON?lat={}&lng={}&username={}'.format(self.lat,self.lon, self.geonames_username))
			data = response.json()
			
			if 'timezoneId' in data:
				tz = get_timezone(data['timezoneId'])
				tzName = get_timezone_name(tz, locale=Locale.parse('en_US'))
				if tzName != self.oldTz:
					self.atisVoice = '{}.'.format(tzName)
					self.oldTz = tzName
					self.readVoice()
		except Exception as e:
			logging.error('Error determining timezone: ' + str(e))
			logging.exception(str(e))
			sys.exit()


	## Reads the flight following string using voice generation.
	def readVoice(self):
		# Init currently Reading with None.
		# self.currentlyReading = None
		
		self.logger.debug('Voice Text is: {}'.format(self.atisVoice))
		pyttsxImported = True
		if pyttsxImported:
			# Set properties currently reading
			# Init voice engine.
			self.engine = pyttsx3.init()
			# Set properties.
			voices = self.engine.getProperty('voices')
			for vo in voices:
				if 'english' in vo.name.lower():
					self.engine.setProperty('voice', vo.id)
					self.logger.debug('Using voice: {}'.format(vo.name))
					break
			
			self.engine.setProperty('rate', self.voice_rate)
			# Say complete ATIS
			self.engine.say(self.atisVoice)
			self.logger.info('Start reading.')
			self.engine.runAndWait()
			self.logger.info('Reading finished.')
			self.engine = None
			
		else:
			self.logger.warning('Speech engine not initalized, no reading. Sleeping for {} seconds...'.format(self.SLEEP_TIME))
			time.sleep(self.SLEEP_TIME)
	
	## Read data from the simulator
	def getPyuipcData(self):
		
		if pyuipcImported:
			results = pyuipc.read(self.pyuipcOffsets)
			# lat lon
			self.lat = results[3] * (90.0/(10001750.0 * 65536.0 * 65536.0))
			self.lon = results[4] * (360.0/(65536.0 * 65536.0 * 65536.0 * 65536.0))
			self.flaps = results[5]/ 256
		
		else:
			self.com1frequency = self.COM1_FREQUENCY_DEBUG
			self.com2frequency = self.COM2_FREQUENCY_DEBUG
			self.com1active = True
			self.com2active = True
			self.lat = self.LAT_DEBUG
			self.lon = self.LON_DEBUG

if __name__ == '__main__':
	FlightFollowing = FlightFollowing()
	pass