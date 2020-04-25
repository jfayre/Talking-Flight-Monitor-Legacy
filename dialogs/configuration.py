# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from builtins import range
import logging as original_logger
import wx
import application
import config
import widgetUtils
from . import baseDialog
from multiplatform_widgets import widgets

class general(wx.Panel, baseDialog.BaseWXDialog):
 def __init__(self, parent):
  super(general, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  lbl = wx.StaticText(self, wx.ID_ANY, "Geonames username: ")
  self.geonames_username = wx.TextCtrl(self, -1)
  geonames_box = wx.BoxSizer(wx.HORIZONTAL)
  geonames_box.Add(lbl, 0, wx.ALL, 5)
  geonames_box.Add(self.geonames_username, 0, wx.ALL, 5)
  sizer.Add(geonames_box, 0, wx.ALL, 5)
  self.use_sapi = wx.CheckBox(self, -1, "Use SAPI for speech output")
  sizer.Add(self.use_sapi, 0, wx.ALL, 5)
  voice_rate_box = wx.BoxSizer(wx.HORIZONTAL)
  voice_rate_box.Add(wx.StaticText(self, -1, "SAPI speech rate"), 0, wx.ALL, 5)
  self.voice_rate = wx.SpinCtrl(self, wx.ID_ANY)
  self.voice_rate.SetRange(1, 10)
  self.voice_rate.SetSize(self.voice_rate.GetBestSize())
  voice_rate_box.Add(self.voice_rate, 0, wx.ALL, 5)
  sizer.Add(voice_rate_box, 0, wx.ALL, 5)
  self.flight_following = wx.CheckBox(self, -1, "Enable flight following")
  sizer.Add(self.flight_following, 0, wx.ALL, 5)
  self.read_instrumentation = wx.CheckBox(self, -1, "Enable reading of instrumentation")
  sizer.Add(self.read_instrumentation, 0, wx.ALL, 5)
  self.read_simconnect = wx.CheckBox(self, -1, "Read SimConnect messages")
  sizer.Add(self.read_simconnect, 0, wx.ALL, 5)
  self.read_gpws = wx.CheckBox(self, -1, "Enable GPWS callouts")
  sizer.Add(self.read_gpws, 0, wx.ALL, 5)
  self.read_ils = wx.CheckBox(self, -1, "Enable ILS")
  sizer.Add(self.read_ils, 0, wx.ALL, 5)
  self.read_groundspeed = wx.CheckBox(self, -1, "Announce groundspeed while on ground")
  sizer.Add(self.read_groundspeed, 0, wx.ALL, 5)
  self.use_metric = wx.CheckBox(self, -1, "Use metric measurements")
  sizer.Add(self.use_metric, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class timing(wx.Panel, baseDialog.BaseWXDialog):

 def __init__(self, parent):
  super(timing, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  lbl = wx.StaticText(self, wx.ID_ANY, "Interval between flight following messages (in minutes): ")
  self.flight_following_interval = wx.TextCtrl(self, -1)
  ff_interval_box = wx.BoxSizer(wx.HORIZONTAL)
  ff_interval_box.Add(lbl, 0, wx.ALL, 5)
  ff_interval_box.Add(self.flight_following_interval, 0, wx.ALL, 5)
  sizer.Add(ff_interval_box, 0, wx.ALL, 5)
  lbl = wx.StaticText(self, wx.ID_ANY, "Interval between announcements in manual flight mode (in seconds): ")
  self.manual_interval = wx.TextCtrl(self, wx.ID_ANY)
  manual_box = wx.BoxSizer(wx.HORIZONTAL)
  manual_box.Add(lbl, 0, wx.ALL, 5)
  manual_box.Add(self.manual_interval, 0, wx.ALL, 5)
  sizer.Add(manual_box, 0, wx.ALL, 5)
  lbl = wx.StaticText(self, wx.ID_ANY, "Interval between ILS announcements: ")
  self.ils_interval = wx.TextCtrl(self, wx.ID_ANY)
  ils_box = wx.BoxSizer(wx.HORIZONTAL)
  ils_box.Add(lbl, 0, wx.ALL, 5)
  ils_box.Add(self.ils_interval, 0, wx.ALL, 5)
  sizer.Add(ils_box, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class hotkeys(wx.Panel, baseDialog.BaseWXDialog):
  def __init__(self, parent):
    super(hotkeys, self).__init__(parent)
    self.command_label = wx.StaticText(self, wx.ID_ANY, "Command mode key: ")
    self.command_key = wx.TextCtrl(self, -1)
    self.asl_label = wx.StaticText(self, wx.ID_ANY, "ASL Altitude: ")
    self.asl_key = wx.TextCtrl(self, -1)
    self.agl_label = wx.StaticText(self, wx.ID_ANY, "AGL Altitude: ")
    self.agl_key = wx.TextCtrl(self, -1)
    self.city_label = wx.StaticText(self, wx.ID_ANY, "Read nearest city: : ")
    self.city_key = wx.TextCtrl(self, -1)
    self.heading_label = wx.StaticText(self, wx.ID_ANY, "current heading: ")
    self.heading_key = wx.TextCtrl(self, -1)
    self.waypoint_label = wx.StaticText(self, wx.ID_ANY, "next waypoint: ")
    self.waypoint_key = wx.TextCtrl(self, -1)
    self.ias_label = wx.StaticText(self, wx.ID_ANY, "Indicated airspeed: ")
    self.ias_key = wx.TextCtrl(self, -1)
    self.tas_label = wx.StaticText(self, wx.ID_ANY, "True airspeed: ")
    self.tas_key = wx.TextCtrl(self, -1)
    self.mach_label = wx.StaticText(self, wx.ID_ANY, "Mach: ")
    self.mach_key = wx.TextCtrl(self, -1)
    self.message_label = wx.StaticText(self, wx.ID_ANY, "repeat last SimConnect message: ")
    self.message_key = wx.TextCtrl(self, -1)
    self.attitude_label = wx.StaticText(self, wx.ID_ANY, "Attitude mode: ")
    self.attitude_key = wx.TextCtrl(self, -1)
    self.manual_label = wx.StaticText(self, wx.ID_ANY, "Manual flight mode: ")
    self.manual_key = wx.TextCtrl(self, -1)
    self.dest_label = wx.StaticText(self, wx.ID_ANY, "Destination info: ")
    self.dest_key = wx.TextCtrl(self, -1)
    self.director_label = wx.StaticText(self, wx.ID_ANY, "Flight director mode: ")
    self.director_key = wx.TextCtrl(self, -1)
    self.vspeed_label = wx.StaticText(self, wx.ID_ANY, "Vertical speed: ")
    self.vspeed_key = wx.TextCtrl(self, -1)
    self.trim_label = wx.StaticText(self, wx.ID_ANY, "Toggle trim announcements: ")
    self.trim_key = wx.TextCtrl(self, -1)
    self.airtemp_label = wx.StaticText(self, wx.ID_ANY, "Outside air temperature: ")
    self.airtemp_key = wx.TextCtrl(self, -1)
    self.toggle_flaps_label = wx.StaticText(self, wx.ID_ANY, "Toggle flap announcements: ")
    self.toggle_flaps_key = wx.TextCtrl(self, -1)
    self.toggle_gpws_label = wx.StaticText(self, wx.ID_ANY, "Toggle GPWS announcements: ")
    self.toggle_gpws_key = wx.TextCtrl(self, -1)
    self.mute_simconnect_label = wx.StaticText(self, wx.ID_ANY, "Mute SimConnect messages: ")
    self.mute_simconnect_key = wx.TextCtrl(self, -1)
    self.toggle_ils_label = wx.StaticText(self, wx.ID_ANY, "Toggle ILS announcements: ")
    self.toggle_ils_key = wx.TextCtrl(self, -1)
    self.autopilot_label = wx.StaticText(self, wx.ID_ANY, "Toggle autopilot announcements: ")
    self.autopilot_key = wx.TextCtrl(self, -1)
    self.wind_label = wx.StaticText(self, wx.ID_ANY, "Wind information: ")
    self.wind_key = wx.TextCtrl(self, -1)
    self.runway_guidance_label = wx.StaticText(self, wx.ID_ANY, "Runway guidance mode: ")
    self.runway_guidance_key = wx.TextCtrl(self, -1)
    self.fuel_report_label = wx.StaticText(self, wx.ID_ANY, "Fuel Report: ")
    self.fuel_report_key = wx.TextCtrl(self, -1)
    self.fuel_flow_label = wx.StaticText(self, wx.ID_ANY, "Fuel Flow Report: ")
    self.fuel_flow_key = wx.TextCtrl(self, -1)
    self.tank1_label = wx.StaticText(self, wx.ID_ANY, "Fuel Tank 1: ")
    self.tank1_key = wx.TextCtrl(self, -1)
    self.tank2_label = wx.StaticText(self, wx.ID_ANY, "Tank 2: ")
    self.tank2_key = wx.TextCtrl(self, -1)
    self.tank3_label = wx.StaticText(self, wx.ID_ANY, "Tank 3: ")
    self.tank3_key = wx.TextCtrl(self, -1)
    self.tank4_label = wx.StaticText(self, wx.ID_ANY, "Tank 4: ")
    self.tank4_key = wx.TextCtrl(self, -1)
    self.tank5_label = wx.StaticText(self, wx.ID_ANY, "Tank 5: ")
    self.tank5_key = wx.TextCtrl(self, -1)
    self.tank6_label = wx.StaticText(self, wx.ID_ANY, "Tank 6: ")
    self.tank6_key = wx.TextCtrl(self, -1)
    self.tank7_label = wx.StaticText(self, wx.ID_ANY, "Tank 7: ")
    self.tank7_key = wx.TextCtrl(self, -1)


    gridSizer = wx.FlexGridSizer(rows = 25, cols=4, vgap=10, hgap=10)
    # Prepare some reusable arguments for calling sizer.Add():
    expandOption = dict(flag=wx.EXPAND)
    noOptions = dict()
    emptySpace = ((0, 0), noOptions)
    
    # Add the controls to the sizers:
    for control, options in \
                [(self.command_label, noOptions),
                 (self.command_key, expandOption),
                 (self.asl_label, noOptions),
                 (self.asl_key, expandOption),
                 (self.agl_label, noOptions),
                 (self.agl_key, expandOption),
                 (self.city_label, noOptions),
                 (self.city_key, expandOption),
                 (self.heading_label, noOptions),
                 (self.heading_key, expandOption),
                 (self.waypoint_label, noOptions),
                 (self.waypoint_key, expandOption),
                 (self.tas_label, noOptions),
                 (self.tas_key, expandOption),
                 (self.ias_label, noOptions),
                 (self.ias_key, expandOption),
                 (self.mach_label, noOptions),
                 (self.mach_key, expandOption),
                 (self.message_label, noOptions),
                 (self.message_key, expandOption),
                 (self.dest_label, noOptions),
                 (self.dest_key, expandOption),
                 (self.attitude_label, noOptions),
                 (self.attitude_key, expandOption),
                 (self.manual_label, noOptions),
                 (self.manual_key, expandOption),
                 (self.director_label, noOptions),
                 (self.director_key, expandOption),
                 (self.runway_guidance_label, noOptions),
                 (self.runway_guidance_key, expandOption),

                 (self.vspeed_label, noOptions),
                 (self.vspeed_key, expandOption),
                 (self.airtemp_label, noOptions),
                 (self.airtemp_key, expandOption),
                 (self.trim_label, noOptions),
                 (self.trim_key, expandOption),
                 (self.mute_simconnect_label, noOptions),
                 (self.mute_simconnect_key, expandOption),
                 (self.toggle_gpws_label, noOptions),
                 (self.toggle_gpws_key, expandOption),
                 (self.toggle_ils_label, noOptions),
                 (self.toggle_ils_key, expandOption),
                 (self.toggle_flaps_label, noOptions),
                 (self.toggle_flaps_key, expandOption),
                 (self.autopilot_label, noOptions),
                 (self.autopilot_key, expandOption),
                 (self.wind_label, noOptions),
                 (self.wind_key, expandOption),
                 
                 (self.fuel_report_label, noOptions),
                 (self.fuel_report_key, expandOption),
                 (self.fuel_flow_label, noOptions),
                 (self.fuel_flow_key, expandOption),
                 (self.tank1_label, noOptions),
                 (self.tank1_key, expandOption),
                 (self.tank2_label, noOptions),
                 (self.tank2_key, expandOption),
                 (self.tank3_label, noOptions),
                 (self.tank3_key, expandOption),
                 (self.tank4_label, noOptions),
                 (self.tank4_key, expandOption),
                 (self.tank5_label, noOptions),
                 (self.tank5_key, expandOption),
                 (self.tank6_label, noOptions),
                 (self.tank6_key, expandOption),
                 (self.tank7_label, noOptions),
                 (self.tank7_key, expandOption)]:
            gridSizer.Add(control, **options)
            self.SetSizerAndFit(gridSizer)


class configurationDialog(baseDialog.BaseWXDialog):
 def set_title(self, title):
  self.SetTitle(title)

 def __init__(self):
  super(configurationDialog, self).__init__(None, -1)
  self.panel = wx.Panel(self)
  self.SetTitle("{0} preferences".format(application.name,))
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.notebook = wx.Notebook(self.panel)
 def create_general(self):
  self.general = general(self.notebook)
  self.notebook.AddPage(self.general, "General")
  self.general.SetFocus()


 def create_timing(self):
  self.timing = timing(self.notebook)
  self.notebook.AddPage(self.timing, "Timing")
 def create_hotkeys(self):
  self.hotkeys = hotkeys(self.notebook)
  self.notebook.AddPage(self.hotkeys, "Hotkeys")


 

 def realize(self):
  self.sizer.Add(self.notebook, 0, wx.ALL, 5)
  ok_cancel_box = wx.BoxSizer(wx.HORIZONTAL)
  ok = wx.Button(self.panel, wx.ID_OK, "Save")
  ok.SetDefault()
  cancel = wx.Button(self.panel, wx.ID_CANCEL, "Close")
  self.SetEscapeId(cancel.GetId())
  ok_cancel_box.Add(ok, 0, wx.ALL, 5)
  ok_cancel_box.Add(cancel, 0, wx.ALL, 5)
  self.sizer.Add(ok_cancel_box, 0, wx.ALL, 5)
  self.panel.SetSizer(self.sizer)
  self.SetClientSize(self.sizer.CalcMin())

 def get_value(self, panel, key):
  p = getattr(self, panel)
  return getattr(p, key).GetValue()

 def set_value(self, panel, key, value):
  p = getattr(self, panel)
  control = getattr(p, key)
  getattr(control, "SetValue")(value)

