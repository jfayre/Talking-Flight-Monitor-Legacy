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
    
    gridSizer = wx.FlexGridSizer(rows = 12, cols=2, vgap=10, hgap=10)
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
                 (self.vheading_key, expandOption),
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
                 (self.vspeed_label, noOptions),
                 (self.vvspeed_key, expandOption),
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
                 (self.wind_key, expandOption)]:
            gridSizer.Add(control, **options)


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

