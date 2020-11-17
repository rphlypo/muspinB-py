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

plaid_params = dict(win=win,
                    tex='sqr65',
                    mask='circle',
                    color=win.color,
                    blendmode='add',
                    sf=1/3,
                    size=12,
                    units='deg',
                    pos=(0,0),
                    phase=0,
                    texRes=1024,
                    autoDraw=False)

def createPlaids(alpha, **plaid_params):
    try:
        alpha0, alpha1 = alpha[0], alpha[1]
        contrast0 = 0.6
        contrast1 = (1 - alpha1) / alpha1 * contrast0
    except TypeError:
        alpha0, alpha1 = alpha, 1 - alpha
        contrast0 = contrast1 = .6
    return visual.GratingStim(ori=30, opacity=alpha0, contrast=contrast0, **plaid_params), visual.GratingStim(ori=-30, opacity=alpha1, contrast=contrast1, **plaid_params)


plaid = dict( Amb=createPlaids(0.5, **plaid_params),
              transpL=createPlaids(0.1, **plaid_params),
              transpR=createPlaids(0.9, **plaid_params),
              coh=createPlaids([1, .7], **plaid_params))
