from psychopy import visual, core, clock
from psychopy.data import ExperimentHandler
from expsetup import win, kb, expInfo
from stims import plaid_stims
import utils
import random


expInfo['Data'] = ExperimentHandler(name="Muspin-B", dataFileName=expInfo['metaData']['paths']['root'])  # give filename to store data to
exp_structure = utils.create_experiment_structure( nBlocks=1)

expInfo['Params'] = dict(speed = 1)  # speed in degrees per second
# TODO
# initialise the log-normal parameters to some sensible values >> add to 'Params' ?
exp = expInfo['Data']  # just as a short-hand reference

keycode = {'right': 1, 'up': 2, 'left':4}
current_keys = 0
new_keys = 0
nflips = 0

global_timer = core.Clock()

for phase in exp_structure:
    exp.addLoop(phase['trials'])  # register
    for trial in phase['trials']:

        if not trial.thisN % 28:  # every 28 trials (start and halfway the 14×4 trials in testing), give the subject a big, big break, then launch a calibration ? 
            pass
            
        elif not trial.thisN % 8:  # launch a drift correction every 8 trials if no calibration was run ? Give the subject a break
            pass
            
        exp.addData('trial.phase', phase['name'])
        stim_cond, kb_cond = trial['cond'].split('_')  # get the explicit stim condition and keyboard condition
        duration = random.uniform(40, 45)  # each trial lasts in between 40 and 45 seconds
        exp.addData('trial.duration', duration)

        # TODO
        # deal with all four of the conditions STIM X RESPONSE
        timer = core.CountdownTimer( duration)  
        now = start_time = timer.getTime()
        kb.clock.reset()  # when you want to start the timer
        if stim_cond == 'nAmb':
            stim = stimTransition(None)  # TODO implement stimTransition
            plaid = plaid_stims[stim]
            flip_timer.reset( t= ) # TODO : random time
        else:
            plaid = plaid_stims['amb']
        for s in plaid: s.autoDraw = True
        
        while timer.getTime() > 0:  # add minimum number of transitions ? add max number of transitions ?
            # TODO
            if stim_cond == 'nAmb' and flip_timer < 0 :
                flip_timer.reset( t= )  # TODO : draw time from log-normal
                for s in plaid: s.autoDraw = False
                stim = stimTransition(stim)  # will account for all phases
                stimChange.append((global_timer.getTime(), stim))
                plaid = plaid_stims[stim]
                for s in plaid: s.autoDraw = True
            pass
        exp.nextEntry()
    if phase['name'] == 'training':
        pass
        # add the end of the training phase
        # estimate the most likely parameters in the log-normal family  >> repeat if too few samples ?
    exp.loopEnded(phase['trials'])
    

print(exp.getAllEntries())


for stim in plaid_stims:
    for s in plaid_stims[stim]:
        s.autoDraw = True
    nflips += 1
    print(stim)
    flip_time = timer.getTime()
    while now < nflips * 5:
        now = timer.getTime()
        plaid_stims[stim][1].phase = (0, speed * (now - start_time))
        
        win.flip()

    for s in plaid_stims[stim]:
        s.autoDraw = False

        

"""
while timer.getTime() > 0:
    now = timer.getTime()
    if now > 15:
        p.phase = (0, -speed * (now - start_time))
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
"""
    
# for s in current_stims:
#    s.autoDraw = False

win.close()
# io.devices.tracker.setRecordingState(False)
# io.quit()