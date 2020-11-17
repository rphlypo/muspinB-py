import ctypes
xlib = ctypes.cdll.LoadLibrary("libX11.so")
xlib.XInitThreads()

from psychopy import monitors, visual
from psychopy.hardware import keyboard

from scipy.constants import inch
from math import cos, atan, tan
from constants import monitor_constants, trials


def make_monitor(monitor_name, diag_mon, pixels, viewing_distance):
    return monitors.Monitor(monitor_name,  # give the monitor a name
                width=diag_mon * inch * cos(atan(pixels[1] / pixels[0])) * 100,  # compute width [cm] from screen diagonal [inches] and pixel size
                distance=viewing_distance,  # distance to monitor in cm
                )


mon = make_monitor(**monitor_constants)
mon.setSizePix(monitor_constants['pixels'])
mon.save()

win = visual.Window(monitor=mon, color=[-0.3]*3, size=mon.getSizePix(), units='deg', screen=1, fullscr=True, waitBlanking=False, blendmode='add')
kb = keyboard.Keyboard()