# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from . import baseDialog
import wx
from pubsub import pub
class controlsDialog(baseDialog.BaseWXDialog):
    def __init__(self, value=""):
        super(controlsDialog, self).__init__(None, -1)
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetTitle("A2A mini controls")
        self.ttl = wx.CheckBox(self, -1, "Left tip tank pump")
        sizer.Add(self.ttl, 0, wx.ALL, 5)
        ok = wx.Button(panel, wx.ID_OK, "ok")
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        btnsizer = wx.BoxSizer()
        btnsizer.Add(ok, 0, wx.ALL, 5)
        btnsizer.Add(cancel, 0, wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        self.SetClientSize(sizer.CalcMin())
        self.ttl.Bind(wx.EVT_CHECKBOX, self.onTtl)
    def onTtl(self, event):
        if event.IsChecked():
            pub.sendMessage("ttl", msg=True)
        else:
            pub.sendMessage("ttl", msg=False)
