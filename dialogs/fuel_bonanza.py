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
        wl_label = wx.StaticText(self, wx.ID_ANY, "left wing tank in gallons (max 40): ")
        self.wing_left = wx.TextCtrl(self, -1)
        wl_box = wx.BoxSizer(wx.HORIZONTAL)
        wl_box.Add(wl_label, 0, wx.ALL, 5)
        wl_box.Add(self.wing_left, 0, wx.ALL, 5)
        sizer.Add(wl_box, 0, wx.ALL, 5)
        wr_box = wx.BoxSizer(wx.HORIZONTAL)
        wr_box.Add(wx.StaticText(self, -1, "Right wing tank in gallons (max 40): "), 0, wx.ALL, 5)
        self.wing_right = wx.TextCtrl(self, -1)
        wr_box.Add(self.wing_right, 0, wx.ALL, 5)
        sizer.Add(wr_box, 0, wx.ALL, 5)
        if fsdata.instr['TipTanksAvailable']:
            ttl_box = wx.BoxSizer(wx.HORIZONTAL)
            ttl_box.Add(wx.StaticText(self, -1, "Left Tip Tank in gallons (max 20): "), 0, wx.ALL, 5)
            self.tip_left = wx.TextCtrl(self, -1)
            ttl_box.Add(self.tip_left, 0, wx.ALL, 5)
            sizer.Add(ttl_box, 0, wx.ALL, 5)
            ttr_box = wx.BoxSizer(wx.HORIZONTAL)
            ttr_box.Add(wx.StaticText(self, -1, "Right Tip Tank in gallons (max 20): "), 0, wx.ALL, 5)
            self.tip_right = wx.TextCtrl(self, -1)
            ttr_box.Add(self.tip_right, 0, wx.ALL, 5)
            sizer.Add(ttr_box, 0, wx.ALL, 5)
        oil_box = wx.BoxSizer(wx.HORIZONTAL)
        oil_box.Add(wx.StaticText(self, -1, "Oil quantity in gallons (max 2.5): "), 0, wx.ALL, 5)
        self.oil_quantity = wx.TextCtrl(self, -1)
        oil_box.Add(self.oil_quantity, 0, wx.ALL, 5)
        sizer.Add(oil_box, 0, wx.ALL, 5)
        self.SetSizer(sizer)


class fuelDialog(baseDialog.BaseWXDialog):
    def set_title(self, title):
        self.SetTitle(title)

    def __init__(self):
        super(fuelDialog, self).__init__(None, -1)
        self.panel = wx.Panel(self)
        self.SetTitle("A2A Bonanza Fuel manager")
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(self.panel)
    def create_fuel(self):
        self.fuel = fuel(self.notebook)
        self.notebook.AddPage(self.fuel, "Fuel")
        self.fuel.SetFocus()

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

