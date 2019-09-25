"""Start the GACP GUI"""
import wx
import gui_classes
import general_helpers

APP = wx.App(False)
FRAME = gui_classes.MainWindow(None,
                               "GA Cookie Parser {}".format(general_helpers.APPLICATION_VERSION))
APP.MainLoop()
