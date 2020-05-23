# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str
from builtins import object
import os
import paths
import widgetUtils
import config
import application
from dialogs import fuel_bonanza, fuel_cherokee
# from wxUI import commonMessageDialogs
from pubsub import pub
import logging
import config_utils
log = logging.getLogger("Fuel")
from collections import OrderedDict

class fuelControllerBonanza(object):
    def __init__(self):
        super(fuelControllerBonanza, self).__init__()
        self.dialog = fuel_bonanza.fuelDialog()
        self.create_fuel()

    def create_fuel(self):
        # fuel tab
        self.dialog.create_fuel()
        self.dialog.realize()
        self.response = self.dialog.get_response()
        
class fuelControllerCherokee(object):
    def __init__(self):
        super(fuelControllerCherokee, self).__init__()
        self.dialog = fuel_cherokee.fuelDialog()
        self.create_fuel()

    def create_fuel(self):
        # fuel tab
        self.dialog.create_fuel()
        self.dialog.realize()
        self.response = self.dialog.get_response()
        
