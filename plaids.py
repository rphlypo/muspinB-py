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

print()
print(mon.getDistance()*12*0.017455)
print(cm2pix(deg2cm(12, mon, correctFlat=False), mon))
print('ok?')


params = dict(win=win,
              tex='sqr',
              mask='circle',
              opacity=.5,
              blendmode='add',
              sf=1/deg2pix(3/2, mon),
              size=200, #deg2pix(6, mon),
              units='pix',
              pos=(0,0),
              phase=0,
              contrast=.35,
              texRes=512)

stim1 = visual.GratingStim(ori=30, **params)
stim1.setAutoDraw(True)

stim2 = visual.GratingStim(ori=-30, **params)
stim2.setAutoDraw(True)

speed = 1  # deg per second

timer = clock.CountdownTimer(start=3)
now = timer.getTime()
kb.clock.reset()  # when you want to start the timer from

stim1.draw()
stim2.draw()
# msg.draw()
keycode = {'right': 1, 'up': 2, 'left':4}
current_keys = 0
new_keys = 0

while timer.getTime() > 0:
    lastTime, now = now, timer.getTime()
    stim1.phase -= speed * (lastTime - now)
    stim2.phase += speed * (lastTime - now)
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