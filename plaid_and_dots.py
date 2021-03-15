from psychopy import visual, clock
from psychopy.iohub import client
import percepts
import utils
import stims
import expsetup
import numpy as np
from math import sin


# settuing up the plaids
init = utils.load_init('./config/init.yaml') 
# launch a win instance to intercept the keypresses 
# so that they are not sent to the console
# set-up the Display and monitor
# make a monitor with monitor constants from the init file
mon = expsetup.makeMonitor(init['monitor_constants'])  
# and make a window using that monitor
win = visual.Window(
    monitor=mon, 
    color=init['experiment']['bkgcolor'],
    size=mon.getSizePix(), 
    units='deg', 
    screen=1,  # 0 is the monitor of the experiment control
    fullscr=True, 
    allowGUI=False,  
    waitBlanking=False, 
    winType='pyglet')  # for iohub to function well
# getting the stims and its parameters
velocity = np.array(
    [0,
     -stims.get_velocity_vector(**init['experiment']['stim'])[1]]
    )
plaid_stims = stims.plaids(win, **init['experiment']['stim'])
plaid = plaid_stims['amb']
for s in plaid[:-3]: s.autoDraw = True
dots = stims.createDots(win)
dots.coherence = .7
dots.dir = -90
dots.autoDraw = True
for s in plaid[-3:]: s.autoDraw = True

# Start the ioHub process. 'io' can now be used during the
# experiment to access iohub devices and read iohub device events
io = client.launchHubServer()
io.devices.mouse.reporting = False

print('Press [SPACE] to continue... ')
percepts.waitKeyPress(io, key=' ', timeout=10)

all_percepts = []
trial_timer = clock.CountdownTimer(start=10)

pb = percepts.get_percept_report(io, clear=True)
current_percept = pb[-1]

new_time = trial_timer.getTime()

while trial_timer.getTime()>0:
    old_time = new_time
    new_time = trial_timer.getTime()
    if dots.dir in [-90, 90]:
        dots_vel = stims.get_velocity_vector(vel_units='deg', **init['experiment']['stim'])[1]
    elif dots.dir in [0, 180]:
        dots_vel = stims.get_velocity_vector(vel_units='deg', **init['experiment']['stim'])[0]
    dots.speed =  dots_vel * (new_time - old_time)  # speed in °/frame
    plaid[1].phase += velocity * (new_time - old_time)
    win.flip()

pb = percepts.get_percept_report(io)
io.devices.keyboard.reporting = False
print('Trial ended')

pb = percepts.merge_percepts(pb)
print(pb)

print('Press [q] to quit... ')
percepts.waitKeyPress(io, key='q', timeout=60)