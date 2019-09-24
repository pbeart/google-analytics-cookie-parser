"""Start the GACP GUI"""
import wx
import gui_classes

APP = wx.App(False)
FRAME = gui_classes.MainWindow(None, "GA Cookie Parser")
APP.MainLoop()
