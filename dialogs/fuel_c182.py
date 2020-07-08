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
import fsdata
class fuel(wx.Panel, baseDialog.BaseWXDialog):
    def __init__(self, parent):
        super(fuel, self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        wl_label = wx.StaticText(self, wx.ID_ANY, "left wing tank in gallons (max 45): ")
        self.wing_left = wx.TextCtrl(self, -1)
        wl_box = wx.BoxSizer(wx.HORIZONTAL)
        wl_box.Add(wl_label, 0, wx.ALL, 5)
        wl_box.Add(self.wing_left, 0, wx.ALL, 5)
        sizer.Add(wl_box, 0, wx.ALL, 5)
        wr_box = wx.BoxSizer(wx.HORIZONTAL)
        wr_box.Add(wx.StaticText(self, -1, "Right wing tank in gallons (max 45): "), 0, wx.ALL, 5)
        self.wing_right = wx.TextCtrl(self, -1)
        wr_box.Add(self.wing_right, 0, wx.ALL, 5)
        sizer.Add(wr_box, 0, wx.ALL, 5)
        self.oil = wx.CheckBox(self, -1, "Fill oil tank ( 9 quarts)")
        sizer.Add(self.oil, 0, wx.ALL, 5)
        self.SetSizer(sizer)

class payload(wx.Panel, baseDialog.BaseWXDialog):
    def __init__(self, parent):
        super(payload, self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.seat1 = wx.CheckBox(self, -1, "Pilot (required for other passengers)")
        seat1_label = wx.StaticText(self, wx.ID_ANY, "Pilot weight in pounds (min 100, max 300):")
        self.seat1_weight = wx.TextCtrl(self, -1)
        seat1_box = wx.BoxSizer(wx.HORIZONTAL)
        seat1_box.Add(self.seat1, 0, wx.ALL, 5)
        seat1_box.Add(seat1_label, 0, wx.ALL, 5)
        seat1_box.Add(self.seat1_weight, 0, wx.ALL, 5)
        sizer.Add(seat1_box, 0, wx.ALL, 5)
        self.seat2 = wx.CheckBox(self, -1, "Passenger 1")
        seat2_label = wx.StaticText(self, wx.ID_ANY, "Passenger 1 weight in pounds (min 100, max 300):")
        self.seat2_weight = wx.TextCtrl(self, -1)
        seat2_box = wx.BoxSizer(wx.HORIZONTAL)
        seat2_box.Add(self.seat2, 0, wx.ALL, 5)
        seat2_box.Add(seat2_label, 0, wx.ALL, 5)
        seat2_box.Add(self.seat2_weight, 0, wx.ALL, 5)
        sizer.Add(seat2_box, 0, wx.ALL, 5)
        self.seat3 = wx.CheckBox(self, -1, "Passenger 2")
        seat3_label = wx.StaticText(self, wx.ID_ANY, "Passenger 2 weight in pounds (min 100, max 300): ")
        self.seat3_weight = wx.TextCtrl(self, -1)
        seat3_box = wx.BoxSizer(wx.HORIZONTAL)
        seat3_box.Add(self.seat3, 0, wx.ALL, 5)
        seat3_box.Add(seat3_label, 0, wx.ALL, 5)
        seat3_box.Add(self.seat3_weight, 0, wx.ALL, 5)
        sizer.Add(seat3_box, 0, wx.ALL, 5)
        self.seat4 = wx.CheckBox(self, -1, "Passenger 3")
        seat4_label = wx.StaticText(self, wx.ID_ANY, "Passenger 3 weight in pounds (min 100, max 300): ")
        self.seat4_weight = wx.TextCtrl(self, -1)
        seat4_box = wx.BoxSizer(wx.HORIZONTAL)
        seat4_box.Add(self.seat4, 0, wx.ALL, 5)
        seat4_box.Add(seat4_label, 0, wx.ALL, 5)
        seat4_box.Add(self.seat4_weight, 0, wx.ALL, 5)
        sizer.Add(seat4_box, 0, wx.ALL, 5)
        self.SetSizer(sizer)




class fuelDialog(baseDialog.BaseWXDialog):
    def set_title(self, title):
        self.SetTitle(title)

    def __init__(self):
        super(fuelDialog, self).__init__(None, -1)
        self.panel = wx.Panel(self)
        self.SetTitle("A2A C182 Fuel manager")
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(self.panel)
    def create_fuel(self):
        self.fuel = fuel(self.notebook)
        self.notebook.AddPage(self.fuel, "Fuel")
        self.fuel.SetFocus()
    def create_payload(self):
        self.payload = payload(self.notebook)
        self.notebook.AddPage(self.payload, "Payload")

    def realize(self):
        self.sizer.Add(self.notebook, 0, wx.ALL, 5)
        ok_cancel_box = wx.BoxSizer(wx.HORIZONTAL)
        ok = wx.Button(self.panel, wx.ID_OK, "Ok")
        ok.SetDefault()
        cancel = wx.Button(self.panel, wx.ID_CANCEL, "cancel")
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

