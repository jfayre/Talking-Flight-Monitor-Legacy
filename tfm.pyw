# -*- coding: iso-8859-15 -*-
#==============================================================================
# Talking Flight Monitor - an accessibility application for Microsoft Flight Simulator and Lockheed Martin Prepar3d.
# Copyright (C) 2020 by Jason Fayre
# 
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



# Import built-ins
import logging
import os
import sys
import time
import warnings
import config
import winsound
#redirect the original stdout and stderr
stdout = sys.stdout
stderr = sys.stderr
sys.stdout = open(os.path.join(os.getenv("temp"), "stdout.log"), "w")
sys.stderr = open(os.path.join(os.getenv("temp"), "stderr.log"), "w")
import paths
from logger import logger
stdout_temp = sys.stdout
stderr_temp = sys.stderr
if hasattr(sys, 'frozen'):
    sys.stderr = open(os.path.join(paths.logs_path(), "stderr.log"), 'w')
    sys.stdout = open(os.path.join(paths.logs_path(), "stdout.log"), 'w')
else:
    sys.stdout=stdout
    sys.stderr=stderr
#the final log files have been opened succesfully, let's close the temporary files
stdout_temp.close()
stderr_temp.close()
#finally, remove the temporary files. TW Blue doesn't need them anymore, and we will get more free space on the harddrive
os.remove(stdout_temp.name)
os.remove(stderr_temp.name)
from win32event import CreateMutex
from win32api import GetLastError
from winerror import ERROR_ALREADY_EXISTS
from math import degrees, floor
import wx, wx.adv
import webbrowser
import application
from keyboard_handler.wx_handler import WXKeyboardHandler
import queue
import flightsim
import a2a
import settings
# import pyglet
import threading
from accessible_output2.outputs import sapi5
from accessible_output2.outputs import auto
from pubsub import pub
import widgetUtils
# Import own packages.

# initialize the log settings
# Set encoding
#reload(sys)
#sys.setdefaultencoding('iso-8859-15')  # @UndefinedVariable

# detect if another copy is running
handle = CreateMutex(None, 1, 'tfm')
if GetLastError(  ) == ERROR_ALREADY_EXISTS:
    output = sapi5.SAPI5()
    output.speak('Error! A version of Talking Flight Monitor (TFM) is already running. Exiting!')
    time.sleep(5)
    sys.exit(1)
                
# Import pyuipc package (except failure with debug mode). 

# pyglet.options['shadow_window'] = False
# cmd_sound = pyglet.media.load('sounds\\command.wav')

try:
    import pyuipc
    pyuipcImported = True
    debug = False
except ImportError:
        pyuipcImported = False
        debug = True
def reset_hotkeys(arg1=None):
    keyboard_handler.unregister_all_keys()
    keyboard_handler.register_keys({
        config.app['hotkeys']['command_key']: commandMode,
        config.app['hotkeys']['a2a_command_key']: a2a_command_mode
        })    
    

## Layered key support for reading various instrumentation
def commandMode():
    try:
        keyboard_handler.unregister_all_keys()
        # send a message indicating that the next speech event has been triggered by a hotkey.
        pub.sendMessage("triggered", msg=True)
        if config.app['config']['use_sapi'] == False:
            filename = 'sounds\\command.wav'
            winsound.PlaySound(filename, winsound.SND_FILENAME|winsound.SND_ASYNC)
        else:
            output.speak('command?', interrupt=True)
        keymap = {
            config.app['hotkeys']['asl_key']: tfm.readAltitude,
            config.app['hotkeys']['agl_key']: tfm.readGroundAltitude,
            config.app['hotkeys']['city_key']: tfm.readFlightFollowing,
            config.app['hotkeys']['heading_key']: tfm.readHeading,
            config.app['hotkeys']['waypoint_key']: tfm.readWaypoint,
            config.app['hotkeys']['tas_key']: tfm.readTAS,
            config.app['hotkeys']['ias_key']: tfm.readIAS,
            config.app['hotkeys']['mach_key']: tfm.readMach,
            config.app['hotkeys']['message_key']: tfm.readCachedSimConnectMessages,
            config.app['hotkeys']['dest_key']: tfm.readDest,
            config.app['hotkeys']['attitude_key']: tfm.toggleAttitudeMode,
            config.app['hotkeys']['manual_key']: tfm.toggleManualMode,
            config.app['hotkeys']['director_key']: tfm.toggleDirectorMode,
            config.app['hotkeys']['vspeed_key']: tfm.readVSpeed,
            config.app['hotkeys']['airtemp_key']: tfm.readTemp,
            config.app['hotkeys']['trim_key']: tfm.toggleTrim,
            config.app['hotkeys']['mute_simconnect_key']: tfm.toggleMuteSimconnect,
            config.app['hotkeys']['toggle_gpws_key']: tfm.toggleGPWS,
            config.app['hotkeys']['toggle_ils_key']:tfm.toggleILS,
            config.app['hotkeys']['toggle_flaps_key']: tfm.toggleFlaps,
            config.app['hotkeys']['autopilot_key']: tfm.toggleAutoPilot,
            config.app['hotkeys']['wind_key']: tfm.readWind,
            config.app['hotkeys']['runway_guidance_key']: tfm.runway_guidance_mode,
            'q': tfm.tip_tank_left_toggle,


        }
        keyboard_handler.register_keys(keymap)
    except Exception as e:
        logging.exception ("error in command mode.")
def a2a_command_mode():
    try:
        if 'Bonanza' in tfm.instr['AircraftName'].decode():
            keyboard_handler.unregister_all_keys()
            # send a message indicating that the next speech event has been triggered by a hotkey.
            pub.sendMessage("triggered", msg=True)
            if config.app['config']['use_sapi'] == False:
                filename = 'sounds\\command.wav'
                winsound.PlaySound(filename, winsound.SND_FILENAME|winsound.SND_ASYNC)
            else:
                output.speak('command?', interrupt=True)
            keymap = {
                config.app['hotkeys']['a2a_cht']: tfm.cht,
                config.app['hotkeys']['a2a_egt']: tfm.egt,
                config.app['hotkeys']['a2a_rpm']: tfm.read_rpm,
                config.app['hotkeys']['a2a_oil_temp']: tfm.oil_temp,
                config.app['hotkeys']['a2a_oil_pressure']: tfm.oil_pressure,
                config.app['hotkeys']['a2a_manifold_pressure']: tfm.manifold,
                config.app['hotkeys']['a2a_ammeter']: tfm.ammeter,
                config.app['hotkeys']['a2a_fuel_flow']: tfm.gph,    
                config.app['hotkeys']['a2a_fuel_quantity']: tfm.fuel_quantity,
                config.app['hotkeys']['a2a_tip_tank_left']: tfm.tip_tank_left_toggle,
                config.app['hotkeys']['a2a_tip_tank_right']: tfm.tip_tank_right_toggle}


            keyboard_handler.register_keys(keymap)
    except Exception as e:
        log.exception("error in a2a command mode")
class Form(wx.Panel):
    ''' The Form class is a wx.Panel that creates a bunch of controls
        and handlers for callbacks. Doing the layout of the controls is 
        the responsibility of subclasses (by means of the doLayout()
        method). '''

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        self.createControls()
        self.bindEvents()
        self.doLayout()

    def createControls(self):
        self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.hdg_label = wx.StaticText(self, label='heading:')
        self.hdg_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.alt_label = wx.StaticText(self, label='Altitude:')
        self.alt_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.spd_label = wx.StaticText(self, label='Speed:')
        self.spd_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.mch_label = wx.StaticText (self, label='Mach:')
        self.mch_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.vspd_label = wx.StaticText(self, label='Vertical speed:')
        self.vspd_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.trans_label = wx.StaticText(self, label='transponder:')
        self.trans_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.qnh_label = wx.StaticText (self, label='Altimeter QNH:')
        self.qnh_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.inches_label = wx.StaticText (self, label='Altimeter inches:')
        self.inches_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.com1_label = wx.StaticText(self, label='Com 1:')
        self.com1_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.timer = wx.Timer(self)  
    def bindEvents(self):
        for control, event, handler in \
            [(self.hdg_edit, wx.EVT_TEXT_ENTER, self.onHeadingEntered),
            (self.alt_edit, wx.EVT_TEXT_ENTER, self.onAltitudeEntered),
            (self.spd_edit, wx.EVT_TEXT_ENTER, self.onSpeedEntered),
            (self.mch_edit, wx.EVT_TEXT_ENTER,self.onMachEntered),
            (self.vspd_edit, wx.EVT_TEXT_ENTER, self.onVerticalSpeedEntered),
            (self.trans_edit, wx.EVT_TEXT_ENTER, self.OnTransponderEntered),
            (self.qnh_edit, wx.EVT_TEXT_ENTER, self.onQNHEntered),
            (self.inches_edit, wx.EVT_TEXT_ENTER, self.onInchesEntered),
            (self.com1_edit, wx.EVT_TEXT_ENTER, self.onCom1Entered)]:
                control.Bind(event, handler)
        pub.subscribe(self.update_logger, "update")
        
    def update_logger(self, msg):
        self.logger.AppendText(msg + '\n')

    def doLayout(self):
        ''' Layout the controls by means of sizers. '''

        # A horizontal BoxSizer will contain the GridSizer (on the left)
        # and the logger text control (on the right):
        boxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        # A GridSizer will contain the other controls:
        gridSizer = wx.FlexGridSizer(rows = 12, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)
    
        # Add the controls to the sizers:
        for control, options in \
                [(self.hdg_label, noOptions),
                 (self.hdg_edit, expandOption),
                 (self.alt_label, noOptions),
                 (self.alt_edit, expandOption),
                 (self.spd_label, noOptions),
                 (self.spd_edit, expandOption),
                 (self.mch_label, noOptions),
                 (self.mch_edit, expandOption),
                 (self.vspd_label, noOptions),
                 (self.vspd_edit, expandOption),
                 (self.trans_label, noOptions),
                 (self.trans_edit, expandOption),
                 (self.qnh_label, noOptions),
                 (self.qnh_edit, expandOption),
                 (self.inches_label, noOptions),
                 (self.inches_edit, expandOption),
                 (self.com1_label, noOptions),
                 (self.com1_edit, expandOption)]:
            gridSizer.Add(control, **options)

        for control, options in \
                [(gridSizer, dict(border=5, flag=wx.ALL)),
                 (self.logger, dict(border=5, flag=wx.ALL|wx.EXPAND, 
                    proportion=1))]:
            boxSizer.Add(control, **options)

        self.SetSizerAndFit(boxSizer)


    # callback methods for events

    def onHeadingEntered(self, event):
        tfm.set_heading(event.GetString())
    def onAltitudeEntered(self, event):
        tfm.set_altitude(event.GetString())
    def onSpeedEntered(self, event):
        tfm.set_speed(event.GetString())
    def onMachEntered(self, event):
        tfm.set_mach(event.GetString())
    def onQNHEntered(self, event):
        tfm.set_qnh(event.GetString())
    def onInchesEntered(self, event):
        tfm.set_inches(event.GetString())

    def onVerticalSpeedEntered(self, event):
        tfm.set_vspeed(event.GetString())
    def OnTransponderEntered(self, event):
        tfm.set_transponder(event.GetString())
    def onCom1Entered(self, event):
        tfm.set_com1(event.GetString())
class TFMFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TFMFrame, self).__init__(*args, **kwargs)
        panel = Form(self)
        # define the menu bar
        # application menu
        app_menu = wx.Menu()
        app_settings = app_menu.Append(wx.ID_ANY, "&Settings")
        app_exit = app_menu.Append (wx.ID_EXIT,"E&xit"," Terminate the program")
        # help menu
        help_menu = wx.Menu()
        help_website = help_menu.Append(wx.ID_ANY, "visit &website")
        help_issue = help_menu.Append(wx.ID_ANY, "&Report an issue")
        help_about = help_menu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        # set up the menu bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(app_menu, '&Application')
        menu_bar.Append(help_menu, '&Help')
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.
        # bind menu events
        self.Bind(wx.EVT_MENU, self.onSettings, app_settings)
        self.Bind(wx.EVT_MENU, self.onExit, app_exit)
        self.Bind(wx.EVT_MENU, self.onWebsite, help_website)
        self.Bind(wx.EVT_MENU, self.onAbout, help_about)
        self.Bind(wx.EVT_MENU, self.onIssue, help_issue)
        self.timer = wx.Timer(self)  
        self.Bind(wx.EVT_TIMER, self.update, self.timer)  
        self.timer.Start(50)
        pub.subscribe(self.onSimClose, "exit")


    # menu event handlers
    def onSettings(self, event):
        d = settings.settingsController()
        if d.response == widgetUtils.OK:
            d.save_configuration()
 
    def onExit(self, event):
        self.Close()

    def onAbout(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName(application.name)
        info.SetVersion(application.version)
        info.SetDescription(application.description)
        info.SetCopyright(application.copyright)
        #  info.SetLicence(application.licence)
        for i in application.authors:
            info.AddDeveloper(i)
        wx.adv.AboutBox(info)
    def onWebsite(self, event):
        webbrowser.open_new_tab(application.url)

    def onIssue(self, event):
        webbrowser.open_new_tab(application.report_bugs_url)
    
    def onSimClose(self, msg):
        self.Close()

    # event handler for the timer
    def update(self, event):
        if not main_queue.empty():
            message = main_queue.get_nowait()
            output.speak(message)
        if not sapi_queue.empty():
            message = sapi_queue.get_nowait()
            sapi_output.speak(message)

output = None
sapi_output = None
def setup_speech():
    global output, sapi_output
    voice_rate = int(config.app['config']['voice_rate'])
    sapi_output = sapi5.SAPI5()
    sapi_output.set_rate(voice_rate)

    if config.app['config']['use_sapi']:
        output = sapi5.SAPI5()
        output.set_rate(config.app['config']['voice_rate'])
    else:
        output = auto.Auto()
    geonames_username = config.app['config']['geonames_username']
    if geonames_username == 'your_username':
                get_username()
def get_username():
    dlg = wx.TextEntryDialog(None, "Please enter your Geonames user name in order to use flight following features.", "GeoNames username")
    dlg.ShowModal()
    config.app['config']['geonames_username'] = dlg.GetValue()
    config.app.write()
    
if __name__ == '__main__':
    log = logging.getLogger("main")
    app = wx.App(0)
    # setup configuration files
    config.setup()
    # set up speech object
    setup_speech()
    
    
    frame = TFMFrame(None, title='Talking Flight Monitor')
    # initialize the keyboard handler.
    
    keyboard_handler = WXKeyboardHandler(frame)
    # register the command key
    keyboard_handler.register_keys({
        config.app['hotkeys']['command_key']: commandMode,
        config.app['hotkeys']['a2a_command_key']: a2a_command_mode
        })    
    # register the listener for resetting hotkeys
    pub.subscribe(reset_hotkeys, "reset")
    # breakpoint()
    # setup the queue to receive speech messages
    main_queue = queue.Queue()
    sapi_queue = queue.Queue()
    # start the main tfm class.
    tfm = flightsim.TFM(main_queue, sapi_queue)
    tfm.daemon=True
    tfm.start()
    a2a = a2a.a2a(main_queue, sapi_queue)
    frame.Show()
    app.MainLoop()    



    
    pass
