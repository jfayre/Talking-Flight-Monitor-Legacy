# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str
from builtins import object
import os
import paths
import widgetUtils
import config
import application
from dialogs import configuration
# from wxUI import commonMessageDialogs
from pubsub import pub
import logging
import config_utils
log = logging.getLogger("Settings")
from collections import OrderedDict

class settingsController(object):
    def __init__(self):
        super(settingsController, self).__init__()
        self.dialog = configuration.configurationDialog()
        self.create_config()

    def create_config(self):
        # general tab
        self.dialog.create_general()
        self.dialog.set_value("general", "geonames_username", config.app['config']['geonames_username'])
        self.dialog.set_value("general", "use_sapi", config.app['config']['use_sapi'])
        self.dialog.set_value("general", "voice_rate", config.app['config']['voice_rate'])
        self.dialog.set_value("general", "flight_following", config.app['config']['flight_following'])
        self.dialog.set_value("general", "read_instrumentation", config.app['config']['read_instrumentation'])
        self.dialog.set_value("general", "read_simconnect", config.app['config']['read_simconnect'])
        self.dialog.set_value("general", "read_gpws", config.app['config']['read_gpws'])
        self.dialog.set_value("general", "read_ils", config.app['config']['read_ils'])
        self.dialog.set_value("general", "read_groundspeed", config.app['config']['read_groundspeed'])
        self.dialog.set_value("general", "use_metric", config.app['config']['use_metric'])
        # timings tab
        self.dialog.create_timing()
        self.dialog.set_value("timing", "flight_following_interval", str(config.app['timing']['flight_following_interval']))
        self.dialog.set_value("timing", "manual_interval", str(config.app['timing']['manual_interval']))
        self.dialog.set_value("timing", "ils_interval", str(config.app['timing']['ils_interval']))
        # hotkeys tab
        self.dialog.create_hotkeys()
        self.dialog.set_value("hotkeys", "command_key", config.app['hotkeys']['command_key'])
        self.dialog.set_value("hotkeys", "asl_key", config.app['hotkeys']['asl_key'])
        self.dialog.set_value("hotkeys", "agl_key", config.app['hotkeys']['agl_key'])
        self.dialog.set_value("hotkeys", "city_key", config.app['hotkeys']['city_key'])
        self.dialog.set_value("hotkeys", "heading_key", config.app['hotkeys']['heading_key'])
        self.dialog.set_value("hotkeys", "waypoint_key", config.app['hotkeys']['waypoint_key'])
        self.dialog.set_value("hotkeys", "tas_key", config.app['hotkeys']['tas_key'])
        self.dialog.set_value("hotkeys", "ias_key", config.app['hotkeys']['ias_key'])
        self.dialog.set_value("hotkeys", "mach_key", config.app['hotkeys']['mach_key'])
        self.dialog.set_value("hotkeys", "message_key", config.app['hotkeys']['message_key'])
        self.dialog.set_value("hotkeys", "dest_key", config.app['hotkeys']['dest_key'])
        self.dialog.set_value("hotkeys", "attitude_key", config.app['hotkeys']['attitude_key'])
        self.dialog.set_value("hotkeys", "manual_key", config.app['hotkeys']['manual_key'])
        self.dialog.set_value("hotkeys", "director_key", config.app['hotkeys']['director_key'])
        self.dialog.set_value("hotkeys", "vspeed_key", config.app['hotkeys']['vspeed_key'])
        self.dialog.set_value("hotkeys", "airtemp_key", config.app['hotkeys']['airtemp_key'])
        self.dialog.set_value("hotkeys", "trim_key", config.app['hotkeys']['trim_key'])
        self.dialog.set_value("hotkeys", "mute_simconnect_key", config.app['hotkeys']['mute_simconnect_key'])
        self.dialog.set_value("hotkeys", "toggle_gpws_key", config.app['hotkeys']['toggle_gpws_key'])
        self.dialog.set_value("hotkeys", "toggle_ils_key", config.app['hotkeys']['toggle_ils_key'])
        self.dialog.set_value("hotkeys", "toggle_flaps_key", config.app['hotkeys']['toggle_flaps_key'])
        self.dialog.set_value("hotkeys", "autopilot_key", config.app['hotkeys']['autopilot_key'])
        self.dialog.set_value("hotkeys", "wind_key", config.app['hotkeys']['wind_key'])
        self.dialog.set_value("hotkeys", "runway_guidance_key", config.app['hotkeys']['runway_guidance_key'])
        self.dialog.set_value("hotkeys", "fuel_report_key", config.app['hotkeys']['fuel_report_key'])
        self.dialog.set_value("hotkeys", "fuel_flow_key", config.app['hotkeys']['fuel_flow_key'])
        self.dialog.set_value("hotkeys", "tank1_key", config.app['hotkeys']['tank1_key'])
        self.dialog.set_value("hotkeys", "tank2_key", config.app['hotkeys']['tank2_key'])
        self.dialog.set_value("hotkeys", "tank3_key", config.app['hotkeys']['tank3_key'])
        self.dialog.set_value("hotkeys", "tank4_key", config.app['hotkeys']['tank4_key'])
        self.dialog.set_value("hotkeys", "tank5_key", config.app['hotkeys']['tank5_key'])
        self.dialog.set_value("hotkeys", "tank6_key", config.app['hotkeys']['tank6_key'])
        self.dialog.set_value("hotkeys", "tank7_key", config.app['hotkeys']['tank7_key'])
        self.dialog.set_value("hotkeys", "tank8_key", config.app['hotkeys']['tank8_key'])
        self.dialog.set_value("hotkeys", "tank9_key", config.app['hotkeys']['tank9_key'])
        self.dialog.set_value("hotkeys", "tank10_key", config.app['hotkeys']['tank10_key'])
        self.dialog.set_value("hotkeys", "tcas_air_key", config.app['hotkeys']['tcas_air_key'])
        self.dialog.set_value("hotkeys", "tcas_ground_key", config.app['hotkeys']['tcas_ground_key'])
        self.dialog.set_value("hotkeys", "eng1_key", config.app['hotkeys']['eng1_key'])
        self.dialog.set_value("hotkeys", "eng2_key", config.app['hotkeys']['eng2_key'])
        self.dialog.set_value("hotkeys", "eng3_key", config.app['hotkeys']['eng3_key'])
        self.dialog.set_value("hotkeys", "eng4_key", config.app['hotkeys']['eng4_key'])


        self.dialog.realize()
        self.response = self.dialog.get_response()
        



    def save_configuration(self):
        for key in config.app['config'].keys():
            config.app['config'][key] = self.dialog.get_value("general", key)
        for key in config.app['timing'].keys():
            config.app['timing'][key] = self.dialog.get_value("timing", key)
        for key in config.app['hotkeys'].keys():
            if "a2a" in key:
                continue
            else:
                config.app['hotkeys'][key] = self.dialog.get_value("hotkeys", key)
        
        config.app.write()
