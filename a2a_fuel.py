# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str
from builtins import object
import os
import paths
import widgetUtils
import config
import application
from dialogs import fuel_bonanza, fuel_cherokee, fuel_c182
# from wxUI import commonMessageDialogs
from pubsub import pub
import logging
import config_utils
log = logging.getLogger("Fuel")
from collections import OrderedDict
import fsdata
import time

def get_fuel_data(tank):
    # get fuel tank quantities
    if tank == 0:
        percentage = fsdata.instr['lvl_main_left'] / (128 * 65536)
        quantity = round(fsdata.instr['cap_main_left'] * percentage)
    if tank == 1:
        percentage = fsdata.instr['lvl_main_right'] / (128 * 65536)
        quantity = round(fsdata.instr['cap_main_right'] * percentage)
    if tank == 2:
        percentage = fsdata.instr['lvl_tip_left'] / (128 * 65536)
        quantity = round(fsdata.instr['cap_tip_left'] * percentage)
    if tank == 3:
        percentage = fsdata.instr['lvl_tip_right'] / (128 * 65536)
        quantity = round(fsdata.instr['cap_tip_right'] * percentage)
    
    return str(quantity)

class fuelControllerBonanza(object):
    def __init__(self):
        super(fuelControllerBonanza, self).__init__()
        self.dialog = fuel_bonanza.fuelDialog()
        self.create_fuel()

    def create_fuel(self):
        # fuel tab
        self.dialog.create_fuel()
        self.dialog.set_value("fuel", "wing_left", get_fuel_data(0))
        self.dialog.set_value("fuel", "wing_right", get_fuel_data(1))
        if fsdata.instr['TipTanksAvailable']:
            self.dialog.set_value("fuel", "tip_left", get_fuel_data(2))
            self.dialog.set_value("fuel", "tip_right", get_fuel_data(3))
        # payload tab
        self.dialog.create_payload()
        pub.sendMessage("payload", msg=True)
        time.sleep(0.5)
        self.dialog.set_value ("payload", "seat1", fsdata.a2a_payload['seat1'])
        self.dialog.set_value ("payload", "seat1_weight", str(fsdata.a2a_payload['Seat1Weight']))
        self.dialog.set_value ("payload", "seat2", fsdata.a2a_payload['seat2'])
        self.dialog.set_value ("payload", "seat2_weight", str(fsdata.a2a_payload['Seat2Weight']))
        self.dialog.set_value ("payload", "seat3", fsdata.a2a_payload['seat3'])
        self.dialog.set_value ("payload", "seat3_weight", str(fsdata.a2a_payload['Seat3Weight']))
        self.dialog.set_value ("payload", "seat4", fsdata.a2a_payload['seat4'])
        self.dialog.set_value ("payload", "seat4_weight", str(fsdata.a2a_payload['Seat4Weight']))
        self.dialog.realize()
        self.response = self.dialog.get_response()
        
            
class fuelControllerCherokee(object):
    # controller for A2A Cherokee
    def __init__(self):
        super(fuelControllerCherokee, self).__init__()
        self.dialog = fuel_cherokee.fuelDialog()
        self.create_fuel()
        
    def create_fuel(self):
        # fuel tab
        self.dialog.create_fuel()
        self.dialog.set_value("fuel", "wing_left", get_fuel_data(0))
        self.dialog.set_value("fuel", "wing_right", get_fuel_data(1))
        # payload tab
        self.dialog.create_payload()
        pub.sendMessage("payload", msg=True)
        time.sleep(0.5)
        self.dialog.set_value ("payload", "seat1", fsdata.a2a_payload['seat1'])
        self.dialog.set_value ("payload", "seat1_weight", str(fsdata.a2a_payload['Seat1Weight']))
        self.dialog.set_value ("payload", "seat2", fsdata.a2a_payload['seat2'])
        self.dialog.set_value ("payload", "seat2_weight", str(fsdata.a2a_payload['Seat2Weight']))
        self.dialog.set_value ("payload", "seat3", fsdata.a2a_payload['seat3'])
        self.dialog.set_value ("payload", "seat3_weight", str(fsdata.a2a_payload['Seat3Weight']))
        self.dialog.set_value ("payload", "seat4", fsdata.a2a_payload['seat4'])
        self.dialog.set_value ("payload", "seat4_weight", str(fsdata.a2a_payload['Seat4Weight']))
        self.dialog.realize()
        self.response = self.dialog.get_response()
class fuelControllerC182(object):
    # controller for A2A C182
    def __init__(self):
        super(fuelControllerC182, self).__init__()
        self.dialog = fuel_c182.fuelDialog()
        self.create_fuel()
        
    def create_fuel(self):
        # fuel tab
        self.dialog.create_fuel()
        self.dialog.set_value("fuel", "wing_left", get_fuel_data(0))
        self.dialog.set_value("fuel", "wing_right", get_fuel_data(1))
        # payload tab
        self.dialog.create_payload()
        pub.sendMessage("payload", msg=True)
        time.sleep(0.5)
        self.dialog.set_value ("payload", "seat1", fsdata.a2a_payload['seat1'])
        self.dialog.set_value ("payload", "seat1_weight", str(fsdata.a2a_payload['Seat1Weight']))
        self.dialog.set_value ("payload", "seat2", fsdata.a2a_payload['seat2'])
        self.dialog.set_value ("payload", "seat2_weight", str(fsdata.a2a_payload['Seat2Weight']))
        self.dialog.set_value ("payload", "seat3", fsdata.a2a_payload['seat3'])
        self.dialog.set_value ("payload", "seat3_weight", str(fsdata.a2a_payload['Seat3Weight']))
        self.dialog.set_value ("payload", "seat4", fsdata.a2a_payload['seat4'])
        self.dialog.set_value ("payload", "seat4_weight", str(fsdata.a2a_payload['Seat4Weight']))
        self.dialog.realize()
        self.response = self.dialog.get_response()

    
    