from psychopy import visual, core, clock
from psychopy.hardware import keyboard
from psychopy.tools.monitorunittools import deg2pix, deg2cm, cm2pix
from expsetup import mon  # , deg2pix, pix2deg
from numpy import array

import ctypes
xlib = ctypes.cdll.LoadLibrary("libX11.so")
xlib.XInitThreads()

win = visual.Window(monitor=mon, size=mon.getSizePix(), units='deg', screen=1, fullscr=True)
kb = keyboard.Keyboard()

params = dict(win=win,
              tex='sqr',
              mask='circle',
              opacity=.5,
              blendmode='add',
              sf=1/3,
              size=12, #deg2pix(6, mon),
              units='deg',
              pos=(0,0),
              phase=0,
              contrast=.3,
              texRes=1024)

stim1 = visual.GratingStim(ori=30, **params)
stim1.setAutoDraw(True)

stim2 = visual.GratingStim(ori=-30, **params)
stim2.setAutoDraw(True)

circ = visual.Circle(win, size=1.25, lineWidth=0, lineColor=win.color, fillColor=win.color, autoDraw=True)
circ = visual.Circle(win, size=2, units='pix', lineWidth=0, lineColor="red", fillColor="red", autoDraw=True)

speed = 1  # deg per second

timer = clock.CountdownTimer(start=20)
kb.clock.reset()  # when you want to start the timer from
now = timer.getTime()
start_time = now

keycode = {'right': 1, 'up': 2, 'left':4}
current_keys = 0
new_keys = 0

while timer.getTime() > 0:
    now = timer.getTime()
    stim1.phase = speed * (now - start_time)
    stim2.phase = -speed * (now - start_time)
    win.flip()

    # key presses
    new_keys = current_keys
    key_pressed = kb.getKeys(['right', 'left', 'up', 'esc'], waitRelease=False, clear=False)
    keys = kb.getKeys(['right', 'left', 'up', 'esc'], waitRelease=True)
    for key in key_pressed:  # key pressed
        # print(key.name, key.rt)
        new_keys |= keycode[key.name] 
    for key in keys:  # key released
        # print(key.name, key.rt, key.duration)
        new_keys &= ~keycode[key.name] 
    if not current_keys == new_keys:
        current_keys = new_keys
        print('{:03b}'.format(current_keys))
    
win.close()