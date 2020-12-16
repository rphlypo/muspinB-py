import random

import expsetup
import triggers
import utils
import stims
import percepts
import stats

# logging in triggers has the extra logLevel of TRIG
from triggers import logging
from psychopy import visual, core, clock
from psychopy.data import ExperimentHandler


# change the init file according to your needs
io, win, exp_structure, plaid_stims = expsetup.init('init.yaml')
eyelink = io.devices.eyelink
io.devices.keyboard.reporting = False

if expsetup.check_modality('gaze', io):
    # see: https://discourse.psychopy.org/t/iohub-eyelink-unresponsive-keyboard-during-calibration/1023/16
    # win.winHandle.minimize()
    eyelink.runSetupProcedure()
    # win.winHandle.activate()
    # win.winHandle.maximize()




# get a set of the non-ambiguous plaids:
# transparent left/right and coherent
nAmb_plaids = set(plaid_stims.keys()) - set(['amb', 'fix'])  

# get the velocity parameter that will be useful later on
parameters = io.getSessionMetaData()['user_variables']['parameters']
velocity = parameters['velocity']

# TODO: initialise the log-normal parameters to some sensible values
mu, sigma = 3, 2

# set up some timers
# a global timer is available at the experiment level 
# this clock should never be reset to have a unique time base
global_timer = core.Clock()
# time to wait until next flip in non-ambiguous stimulus condition
flip_timer = clock.CountdownTimer(0)
# time between different percepts, useful to estimate the parameters mu and sigma  
percept_duration = clock.Clock()  
# total duration of the trial
trial_timer = clock.CountdownTimer(0)

# markov renewal process, can be updated all throughout the experiment
mrp = stats.MarkovRenewalProcess(list(
    percepts.Percept().percept_dict['perceptual_states']))

# logging experiment messages to file
log_filename = io.getSessionMetaData()['user_variables']['logfile']
logFile = logging.LogFile(f=log_filename, level=logging.EXP)
trigger_filename = io.getSessionMetaData()['user_variables']['triggerfile']
triggerFile = logging.LogFile(f=trigger_filename, level=logging.getLevel('TRIG'))

# set-up the triggers
trigger = triggers.Trigger(port=io.getSessionMetaData()['user_variables']['hw']['parallel_port'])

for phase in exp_structure:
    # exp.addLoop(phase['trials'])  # register current trial in experiment structure
    io.clearEvents()
    io.sendMessageEvent('BEGIN PHASE {}'.format(phase['name']), category='EXP')
    io.createTrialHandlerRecordTable(phase)

    # show instructions
    # this is only true before the subject's learning phase
    if phase['img']:
        img = visual.ImageStim(win, image=phase['img'])
        img.draw()
        win.flip()
        percepts.waitKeyPress(io, key=' ', timeout=20)

    # show the current phase
    text = visual.TextStim(win, text=phase['text'])
    text.draw()
    win.flip()
    percepts.waitKeyPress(io, key=' ', timeout=20)

    for trial in phase['trials']:
        io.addTrialHandlerRecord(trial)
        if not trial.thisN % 28:  
            # every 28 trials (start and halfway the 14×4 trials in testing), give the subject a big, big break, then launch a calibration ?  
            pass  # TODO launch calibration
        elif not trial.thisN % 8:  
            # launch a drift correction every 8 trials if no calibration was run ? Give the subject a break
            pass  # TODO launch drift correction
            
        stim_cond, kb_cond = trial['cond'].split('_')  # get the explicit stim condition and keyboard condition
      
        # choose one among these two logging methods ? or both ?
        trial['startTime'] = global_timer.getTime() 
        win.logOnFlip(level=logging.EXP, msg=trial['cond']) 
       
        """ show trial indications here before the timers start ticking
        """
        win.callOnFlip(trigger.send, 'trial', 'start', io)
        img = visual.ImageStim(win, image=trial['img'])
        img.draw()
        win.flip()
        percepts.waitKeyPress(io, key=' ', timeout=20)

        """ fixation of 200 to 500 ms at start of trial
        """
         # send trigger to indicate a start of the trial condition
        win.callOnFlip(trigger.send, 'condition', trial['cond'], io)
        fix_duration = random.uniform(0.2, 0.5)
        trial['fix_duration'] = fix_duration
        stim = plaid_stims['fix']
        for s in stim: s.draw()
        win.flip()
        clock.wait(fix_duration)
        # TODO: we could potentially do a drift check here (is the subject truly fixating)

        """ set kb reporting as a function of the condition
        """
        io.devices.keyboard.reporting = True if kb_cond == 'Kp' else False

        """ prepare the stimulus
        """
        if stim_cond == 'nAmb':
            trial['mu'] = mu
            trial['sigma'] = sigma
            # reset the timer for the waiting times
            flip_timer.reset(t=0)
        trial_start = True
        needs_flip = True

        # make the plaids autoDraw themselves as the window flips    
        # for s in plaid: s.autoDraw = True

        """ starting the actual trial
        """
        trial_duration = random.uniform(40, 45)  # each trial lasts in between 40 and 45 seconds
        trial['duration'] = trial_duration
        trial_timer.reset(trial_duration)

        while trial_timer.getTime() > 0:  # add minimum number of transitions ? add max number of transitions ?
            # check if we need to load a new simtulus
            if flip_timer <= 0 and stim_cond == 'nAmb': 
                # time to change the non-ambiguous plaid
                needs_flip = True
                stim = stims.sample_next_stim(stim)
                # when do we change the next time ?
                next_stim_change = utils.draw_next_waiting_time(mu, sigma)
                flip_timer.reset(t=next_stim_change)
            elif trial_start and stim_cond == 'Amb':
                # only needs change if at start of trial
                needs_flip = True
                stim = 'Amb'

            if needs_flip:
                # no flip in the next frame... unless flip_timer < 0
                needs_flip = False
                # desactivate old stimulus
                if not trial_start:
                    for s in plaid: s.autoDraw = False
                # new stimulus
                plaid = plaid_stims[stim]
                # random phase for the new stimulus
                if trial_start:
                    plaid.phase = [0, random.uniform(0, 1)]
                    trial['initial_phase'] = plaid.phase[1]
                    trial_start = False
                    # clear the percept buffer
                    if kb_cond == 'Kp':
                        pb = percepts.get_percept_report(io, clear=True)
                        current_percept = pb[-1]
                        percept_duration.reset()
                        percept_ = 0
                # send a trigger on next flip
                win.callOnFlip(trigger.send, 'stimulus', stim, io)
                # set autoDraw to True so we do not need explicit drawing
                for s in plaid: s.autoDraw = True

            # update phase for continuous motion
            plaid.phase += velocity
            
            # will also cause triggers to be send
            win.flip()

            if kb_cond == "Kb":  # keyboard press is registered
                new_percept = percepts.get_percept_report(io)[-1]
                # if the perceptual state has changed, send a trigger
                if not new_percept == current_percept:
                    current_percept = new_percept
                    trigger.send('keypress', current_percept.as_trigger(), io)

        
        # get the current list of percepts
        pb = percepts.get_percept_report(io)
        io.devices.keyboard.reporting = False
        trial['percepts'] = [[p.perceptual_state, p.onset, p.duration] for p in pb]
        
        # make the perceptual timeline
        pb_ = percepts.merge_percepts(pb)
        # get the perceptual residence times, excluding the "0" percept
        percept_times.extend([(p.as_perceptual_states, p.duration) for p in pb_ if p])

        # flush log information after trial
        logging.flush()
        io.flushDataStoreFile()

    # estimate mu and sigma from the percept_times    
    if not phase['name'] == 'learn':
        # get the percept_times
        mu, sigma = utils.loglikelihood_lognormal(percept_times)

    io.flushDataStoreFile()
    # win.saveFrameIntervals(filename=Path(ExpInfo['metaData']['paths']['root'], ExpInfo['id'] + '_fi.log'), clear=True)