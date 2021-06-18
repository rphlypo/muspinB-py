#%%
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
    allowStencil=True,
    winType='pyglet')  # for iohub to function well

aperture = visual.Aperture(win, size=20)
aperture.units='deg'

# velocity is upward, computed from the oblique velocity vector
# this velocity is in periods/s 
# the velocity is thus relatif to the vertical period which is 1/(sin(theta)*sf) [deg]
vel_ori = -90

sf_x = stims.get_angular_frequency(0, stim_params['sf'], stim_params['ori'])
sf_y = stims.get_angular_frequency(90, stim_params['sf'], stim_params['ori'])
v_y = stims.get_angular_velocity(90, stim_params['vel'], stim_params['ori'])
velocity = lambda vel_ori: np.array([v_y * sf_x * np.cos(stims._deg2rad(vel_ori)),
                                     v_y * sf_y * np.sin(stims._deg2rad(vel_ori))])

# the actual plaids stimulus
# plaid_stims = stims.plaids(win, **stim_params)
plaid = stims.transparent_Plaid(win, **stim_params)
plaid.phase = np.random.uniform(size=(2,))
win.getMovieFrame(buffer='back')


# the superimposed RDK
dots_C = stims.createDots(
    win,
    stim_params['alpha'], 
    stim_params['dc'],
    nDots=150,
    I0=stim_params['I0'])
dots_C.coherence = 1
current_C_dir = None
dots_C_velocity = lambda x: min(
    stims.get_angular_velocity(x, stim_params['vel'], stim_params['ori']),
    stims.get_angular_velocity(x, stim_params['vel'], -stim_params['ori']))

dots_R = stims.createDots(
    win,
    stim_params['alpha'], 
    stim_params['dc'],
    nDots=150,
    I0=stim_params['I0'])
dots_R.coherence = 1
current_R_dir = None
dots_R_velocity = lambda x: min(
    stims.get_angular_velocity(x, stim_params['vel'], stim_params['ori']),
    stims.get_angular_velocity(x, stim_params['vel'], -stim_params['ori']))

dots_L = stims.createDots(
    win,
    stim_params['alpha'], 
    stim_params['dc'],
    nDots=150,
    I0=stim_params['I0'])
dots_L.coherence = 1
current_L_dir = None
dots_L_velocity = lambda x: min(
    stims.get_angular_velocity(x, stim_params['vel'], stim_params['ori']),
    stims.get_angular_velocity(x, stim_params['vel'], -stim_params['ori']))

# the fixation disk
fix_disk = stims.fixation_disk(win)

# Start the ioHub process. 'io' can now be used during the
# experiment to access iohub devices and read iohub device events
io = client.launchHubServer()
io.devices.mouse.reporting = False

msg = 'Press [SPACE] to continue... '
print(msg)
visual.TextStim(win, msg, color=stim_params['I0']).draw()
 
win.flip()
percepts.waitKeyPress(io, key=' ', timeout=5)

all_percepts = []
trial_timer = clock.CountdownTimer(start=50)

pb = percepts.get_percept_report(io, clear=True)
current_percept = pb[-1]

new_time = trial_timer.getTime()

plaid.autoDraw = True


#win.getMovieFrame(buffer='back')
#win.getMovieFrame()


dots_C.autoDraw = True
dots_R.autoDraw = True
dots_L.autoDraw = True
for s in fix_disk: s.autoDraw = True
aperture.enable()
Condition = 'C' # R, L, C, Amb
'''
Percepts gauches et droite :
dots.dir = 0
dots.coherence = stim_params['coherence']
vel_ori = -90

Marche bien pour coherent :
juste :
dots.dir = -90  # "up"
vel_ori = -90
Mais ressemble moins aux nAMbL/R, donc plutot celui -ci :

dots.dir = -90
dots.coherence = stim_params['coherence']
vel_ori = -90

Soit mets dots.coherence = stim_params['coherence'] partour, soit nul part
'''
'''while trial_timer.getTime()>0:
    old_time = new_time
    new_time = trial_timer.getTime()
    
    if Condition == 'Amb':
        #dots.dir = 0
        dots.coherence = 0
        vel_ori = -90
        # et mettre alpha [0.5, 0.5] dans yalm
    elif Condition == 'L':
        dots.dir = 0
        dots.coherence = stim_params['coherence']
        vel_ori = -90
        # et mettre alpha [0.1, 0.6] dans yalm
    elif Condition == 'C':
        dots.dir = -90  # "up"
        dots.coherence = stim_params['coherence']
        # et mettre alpha [0.5, 0.5] dans yalm
        vel_ori = -90
    elif Condition == 'R':
        dots.dir = -180
        dots.coherence = stim_params['coherence']
        vel_ori = -90
        # et mettre alpha [0.6, 0.1] dans yalm
    else :
        print('Soucis')
    if dots.dir != current_dir:
        dots_vel = dots_velocity(dots.dir)
        # print(dots.dir, ': ', dots_vel)
        current_dir = dots.dir
    

    dots.speed = dots_vel * (new_time - old_time)  # speed in °/frame
    plaid.phase += velocity(vel_ori) * (new_time - old_time)
    win.flip()'''

while trial_timer.getTime()>0:
    old_time = new_time
    new_time = trial_timer.getTime()
    if new_time <20:#10
        Condition = 'Amb'
    elif new_time <30:
        Condition = 'L'
    elif new_time <40:
        Condition = 'R'
    
    if Condition == 'Amb':
        #dots.dir = 0
        dots_C.coherence = 0.5#stim_params['coherence']#0, stim_parmas cohernece mis à 1
        dots_R.coherence = 0.5
        dots_L.coherence = 0.5
        dots_C.dir = -90
        dots_R.dir = -150#180
        dots_L.dir = -30#0
        vel_ori = -90

    elif Condition == 'L':
        dots_C.dir = -30
        dots_R.dir = -30
        dots_L.dir = -30

        dots_C.coherence = 1
        dots_R.coherence = 1
        dots_L.coherence = 1
        vel_ori = -90# + stim_params['ori'] - 5
        # et mettre alpha [0.1, 0.6] dans yalm
    elif Condition == 'C':
        dots_C.dir = -90  # "up"
        dots_R.dir = -90
        dots_L.dir = -90

        dots_C.coherence = 1
        dots_R.coherence = 1
        dots_L.coherence = 1
        vel_ori = -90
    elif Condition == 'R':
        dots_C.dir = -150
        dots_R.dir = -150
        dots_L.dir = -150

        dots_C.coherence = 1
        dots_R.coherence = 1
        dots_L.coherence = 1
        vel_ori = -90# - stim_params['ori'] + 5
        # et mettre alpha [0.6, 0.1] dans yalm
    else :
        print('Soucis')
    if dots_C.dir != current_C_dir:
        dots_C_vel = dots_C_velocity(dots_C.dir)
        # print(dots.dir, ': ', dots_vel)
        current_C_dir = dots_C.dir

    if dots_R.dir != current_R_dir:
        dots_R_vel = dots_R_velocity(dots_R.dir)
        # print(dots.dir, ': ', dots_vel)
        current_R_dir = dots_R.dir

    if dots_L.dir != current_L_dir:
        dots_L_vel = dots_L_velocity(dots_L.dir)
        # print(dots.dir, ': ', dots_vel)
        current_L_dir = dots_L.dir
    

    dots_C.speed = dots_C_vel * (new_time - old_time)
    dots_R.speed = dots_R_vel * (new_time - old_time)
    dots_L.speed = dots_L_vel * (new_time - old_time)  # speed in °/frame

    plaid.phase += velocity(vel_ori) * (new_time - old_time)
    win.flip()

    

pb = percepts.get_percept_report(io)
io.devices.keyboard.reporting = False
print('Trial ended')

pb = percepts.merge_percepts(pb)
print(pb)

plaid.autoDraw = False
dots_C.autoDraw = False
dots_R.autoDraw = False
dots_L.autoDraw = False

for s in fix_disk: s.autoDraw = False
aperture.disable()



msg = 'Press [q] to quit... '
print(msg)
visual.TextStim(win, msg, color=stim_params['I0']).draw()
win.flip()
percepts.waitKeyPress(io, key='q', timeout=20)

# %%
# Vitesse et dots
'''
while trial_timer.getTime()>0:
    old_time = new_time
    new_time = trial_timer.getTime()
    if new_time <10:
        Condition = 'Amb'
    elif new_time <20:
        Condition = 'L'
    elif new_time <30:
        Condition = 'R'
    
    if Condition == 'Amb':
        #dots.dir = 0
        dots.coherence = 0
        vel_ori = -90
    elif Condition == 'L':
        dots.dir = 0
        dots.coherence = stim_params['coherence']
        vel_ori = -90 + stim_params['ori'] - 5
        # et mettre alpha [0.1, 0.6] dans yalm
    elif Condition == 'C':
        dots.dir = -90  # "up"
        dots.coherence = stim_params['coherence']
        vel_ori = -90
    elif Condition == 'R':
        dots.dir = -180
        dots.coherence = stim_params['coherence']
        vel_ori = -90 - stim_params['ori'] + 5
        # et mettre alpha [0.6, 0.1] dans yalm
    else :
        print('Soucis')
    if dots.dir != current_dir:
        dots_vel = dots_velocity(dots.dir)
        # print(dots.dir, ': ', dots_vel)
        current_dir = dots.dir
    

    dots.speed = dots_vel * (new_time - old_time)  # speed in °/frame
    plaid.phase += velocity(vel_ori) * (new_time - old_time)
    win.flip()
    '''