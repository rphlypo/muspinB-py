from psychopy import visual, clock
from psychopy.iohub import client
import percepts
import utils
import stims
import expsetup
import numpy as np



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
# getting the stims
velocity = np.array([0, -init['experiment']['stim']['vel']])
plaid_stims = stims.plaids(win, **init['experiment']['stim'])
plaid = plaid_stims['amb']
for s in plaid: s.autoDraw = True

# Start the ioHub process. 'io' can now be used during the
# experiment to access iohub devices and read iohub device events
io = client.launchHubServer()
io.devices.mouse.reporting = False

print('Press [SPACE] to continue... ')
percepts.waitKeyPress(io, key=' ', timeout=10)

all_percepts = []
trial_timer = clock.CountdownTimer(start=3)

pb = percepts.get_percept_report(io, clear=True)
current_percept = pb[-1]

new_time = trial_timer.getTime()

while trial_timer.getTime()>0:
    old_time = new_time
    new_time = trial_timer.getTime()
    plaid[1].phase += velocity * (new_time - old_time)
    win.flip()

pb = percepts.get_percept_report(io)
io.devices.keyboard.reporting = False
print('Trial ended')

print(pb)
pb = percepts.merge_percepts(pb)
for p in pb:
    print(p)

print('Press [q] to quit... ')
percepts.waitKeyPress(io, key='q', timeout=60)