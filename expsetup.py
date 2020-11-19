import ctypes
try:
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
except OSError:
    pass

from psychopy import monitors, visual
from psychopy.hardware import keyboard
from psychopy.iohub.client import launchHubServer

from scipy.constants import inch
from math import cos, atan, tan
from constants import monitor_constants, trials
from functions import register_subject, get_subjectid
from pathlib import Path
import eyetracking


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

while True:
    mode = input('Do you want to run the [[F]]ull experiment or only a [T]est? ')
    if mode.lower() in {'f', ''}:
        run_mode = "full"
        break
    elif mode.lower() == 't':
        run_mode = "test"
        break
    else:
        print("Run mode {} unknown, please choose either 't' or 'f'.".format(mode))
    

if run_mode == "full":
    # We register a new subject
    subject, subject_path = register_subject(modalities={'Gaze', 'EEG'})
    expInfo['metaData'].update(**subject)
    expInfo['id'] = get_subjectid(subject)  # to be used for the filenames
    for m in expInfo['metaData']['modalities'].split(','):
        expInfo['Data'][m] = dict()
        expInfo['Data'][m]['path'] = Path(subject_path, m)
    # setting up the Gaze procedure
    if 'gaze' in [m.lower() for m in expInfo['metaData']['modalities'].split(',')]: 
        et_config, guiding_eye = eyetracking.setup( get_subjectid( subject), win)
        io = launchHubServer(**et_config)
        # run eyetracker calibration (later)
        r = io.devices.tracker.runSetupProcedure()  # <<<<< needs working pylink

"""
hubserver = launchHubServer(
    experiment_code = 'Muspin-B',
    session_code = subject_id,
    experiment_info = dict(
        version = '0.1.0'
    ),
    session_info = dict(
        user_variables = expInfo
    ),
    datastore_name = get_subjectid( subject),
    psychopy_monitor_name = 'my_mon',
    iohub_config_name = '',  # should be completed for the configuration file of eyetracker
    **eyetracker_config,

)
"""