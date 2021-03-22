from psychopy import visual, clock
from psychopy.iohub import client
import percepts
import utils
import stims
import expsetup
import numpy as np


# setting up the plaids
init = utils.load_init('./config/init.yaml') 
# get the stim parameters
stim_params = init['experiment']['stim']
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


# velocity is upward, computed from the oblique velocity vector
# this velocity is in periods/s 
# the velocity is thus relatif to the vertical period which is 1/(sin(theta)*sf) [deg]
sf_y = stim_params['sf'] * np.sin(stims._deg2rad(stim_params['ori']))
v_y = stims.get_angular_velocity(-90, stim_params['vel'], stim_params['ori'])
velocity = np.array([0, -v_y * sf_y])

# the actual plaids stimulus
plaid_stims = stims.plaids(win, **stim_params)
plaid = plaid_stims['amb']
for s in plaid: s.autoDraw = True

# the superimposed RDK
dots = stims.createDots(
    win,
    [stim_params['alpha']['amb']]*2, 
    stim_params['dc'],
    nDots=100,
    I0=stim_params['I0'])
dots.coherence = 1
dots.dir = 15
dots_velocity = lambda x: stims.get_angular_velocity(
    x, stim_params['vel'], stim_params['ori'])
dots.autoDraw = True

# the fixation disk
fix_disk = stims.fixation_disk(win)
for s in fix_disk: s.autoDraw = True

# Start the ioHub process. 'io' can now be used during the
# experiment to access iohub devices and read iohub device events
io = client.launchHubServer()
io.devices.mouse.reporting = False

print('Press [SPACE] to continue... ')
percepts.waitKeyPress(io, key=' ', timeout=10)

all_percepts = []
trial_timer = clock.CountdownTimer(start=20)

pb = percepts.get_percept_report(io, clear=True)
current_percept = pb[-1]

new_time = trial_timer.getTime()
current_dir = 0

while trial_timer.getTime()>0:
    old_time = new_time
    new_time = trial_timer.getTime()
    
    if new_time > 15:
        dots.coherence = 0
    elif new_time > 10:
        dots.coherence = 1
        dots.dir = 15
    elif new_time > 5:
        dots.dir = -90
    else:
        dots.dir = -165
    if dots.dir != current_dir:
        dots_vel = dots_velocity(dots.dir)
    current_dir = dots.dir

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