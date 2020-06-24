# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str
from builtins import object
import os
import paths
import widgetUtils
import config
import application
from dialogs import bonanza_controls
# from wxUI import commonMessageDialogs
from pubsub import pub
import logging
import config_utils
log = logging.getLogger("Fuel")
from collections import OrderedDict

class controlsControllerBonanza(object):
    def __init__(self):
        super(controlsControllerBonanza, self).__init__()
        self.dialog = bonanza_controls.controlsDialog()
        self.response = self.dialog.get_response()

    def create_fuel(self):
        # fuel tab
        self.dialog.create_fuel()
        self.dialog.realize()
        self.response = self.dialog.get_response()
