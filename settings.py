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
        self.is_started = True

    def create_config(self):
        # general tab
        self.dialog.create_general()
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
        self.dialog.set_value("timing", "flight_following_interval", config.app['config']['flight_following_interval'])
        self.dialog.set_value("timing", "manual_interval", config.app['config']['manual_interval'])
        self.dialog.set_value("timing", "ils_interval", config.app['config']['ils_interval'])
        # hotkeys tab
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
        self.dialog.realize()
        self.response = self.dialog.get_response()
        



    def save_configuration(self):
        config.app["config"]["use_sapi"] = self.dialog.get_value("general", "use_sapi")
        config.app.write()
