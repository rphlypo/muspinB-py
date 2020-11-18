import ctypes
try:
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
except OSError:
    pass

from psychopy import monitors, visual
from psychopy.hardware import keyboard

from scipy.constants import inch
from math import cos, atan, tan
from constants import monitor_constants, trials
from functions import register_subject, get_subjectid
from pathlib import Path


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

expInfo = dict(metaData=dict(), Data=dict())

# We register a new subject
subject, subject_path = register_subject(modalities={'Gaze', 'EEG'})
expInfo['metaData'].update(**subject)
expInfo['id'] = get_subjectid(subject)  # to be used for the filenames
for m in expInfo['metaData']['modalities'].split(','):
    expInfo['Data'][m] = dict()
    expInfo['Data'][m]['path'] = Path(subject_path, m)