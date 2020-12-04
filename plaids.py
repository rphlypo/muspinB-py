import random
import expsetup
import triggers
import utils
import stims

from psychopy import visual, core, clock, logging
from psychopy.data import ExperimentHandler


init_file = 'init.json'

expInfo, win, kb = expsetup.init( init_file)
plaid_stims = stims.plaids( win, init_file)

expInfo['Data'] = ExperimentHandler( name="Muspin-B", dataFileName=expInfo['metaData']['paths']['root'])  # give filename to store data to
exp = expInfo['Data']  # just a short-hand reference
exp_structure = expInfo['Setup']['exp_structure']

nAmb_plaids = set( plaid_stims.keys()) - set( ['amb'])  # get a set of the non-ambiguous plaids
percept_times = []

init = utils.load_init( init_file)

expInfo['Params'] = dict(
    velocity=init['stim']['vel'],  # speed in degrees per second (this is the speed of the individual gratings)
    ori=init['stim']['ori']
)
velocity = utils.velocity_vector( expInfo['Params']['speed'], expInfo['Params']['ori'], expInfo['Params']['wavelength'])

# TODO: initialise the log-normal parameters to some sensible values
mu, sigma = 3, 2

global_timer = core.Clock()  # start a global timer at the experiment level, useful to check sync a posteriori
flip_timer = core.CountdownTimer( 0)  # time to wait until next flip in non-ambiguous stimulus condition
percept_duration = core.Clock()  # time between different percepts, useful to estimate the parameters mu and sigma
trial_timer = core.CountdownTimer( 0)  # total duration of the trial

logging.setDefaultClock( global_timer)  # logging messages will be logged using the global_timer as a clock (which should never be reset across the experiment)

for phase in exp_structure:
    exp.addLoop( phase['trials'])  # register current trial in experiment structure
    """ TODO show instructions specific to the phase
    """
    for trial in phase['trials']:
        if not trial.thisN % 28:  # every 28 trials (start and halfway the 14×4 trials in testing), give the subject a big, big break, then launch a calibration ? 
            pass  # TODO launch calibration
            
        elif not trial.thisN % 8:  # launch a drift correction every 8 trials if no calibration was run ? Give the subject a break
            pass  # TODO launch drift correction
            
        exp.addData( 'trial.phase', phase['name'])
        stim_cond, kb_cond = trial['cond'].split( '_')  # get the explicit stim condition and keyboard condition
        duration = random.uniform( 40, 45)  # each trial lasts in between 40 and 45 seconds
        exp.addData( 'trial.duration', duration)

        # TODO
        # deal with all four of the conditions STIM × RESPONSE 
        kb.clock.reset()  # when you want to start the timer
        if stim_cond == 'nAmb':
            flip_timer.reset( t=utils.draw_next_waiting_time( mu, sigma))  # will automatically trigger a stim change when entering the trial
            stim = random.sample( nAmb_plaids, 1)  # select a plaid randomly from the set of non-ambiguous plaids
            stimChanges = []
            plaid = plaid_stims[stim]
            exp.addData( 'trial.mu', mu)  # get the mu and sigma used for the realisations of the waiting times
            exp.addData( 'trial.sigma', sigma)
        else:
            stim = 'amb'
            plaid = plaid_stims[ stim]
        for s in plaid: s.autoDraw = True
        
        if kb_cond == 'Kb':
            current_keys = 0
            current_percept = 0
            percepts = []
            perceptual_timeline = []
            percept_duration = core.Clock()

        """ TODO: show instructions here before the timers start ticking
        """

        """ Getting the timers started and get into the trial
        """
        exp.addData( 'trial.startTime', global_timer.getTime())  # choose one among these two logging methods ?
        win.logOnFlip( level=logging.EXP, msg=trial['cond']) 

        triggers.sendTrigger( triggers.trigger['condition'][ trial['cond']])  # send trigger to indicate a start of the trial condition
        trial_timer.reset( duration)
        if stim_cond == 'Amb':
            triggers.sendTrigger( triggers.trigger['stimulus'][ stim])  # stim should be 'amb'

        while timer.getTime() > 0:  # add minimum number of transitions ? add max number of transitions ?
            # TODO
            if stim_cond == 'nAmb' and flip_timer <= 0:  # time to change the non-ambiguous plaid
                for s in plaid: s.autoDraw = False
                stim = random.sample( nAmb_plaids - set( [stim]), 1)
                stimChanges.append( ( global_timer.getTime(), stim))
                plaid = plaid_stims[stim]
                for s in plaid: s.autoDraw = True
                flip_timer.reset( t=utils.draw_next_waiting_time( mu, sigma))  # time until next change; TODO : set mu, sigma
                triggers.sendTrigger( triggers.trigger['stimulus'][ stim])
            
            if kb_cond == "Kb":  # keyboard press is registered
                # key presses
                new_keys = current_keys
                key_pressed = kb.getKeys( ['right', 'left', 'up', 'esc'], waitRelease=False, clear=False)  # get keys pressed, do not clear key from buffer
                keys = kb.getKeys( ['right', 'left', 'up', 'esc'], waitRelease=True)  # get keys released, clear key from buffer
                new_percept = 0
                if 'esc' in key_pressed:
                    quit = input('Do you really want to quit? [Y]/[[N]]').upper()
                    if quit == "Y":
                        triggers.quit( 'interrupted')
                for key in key_pressed:  # key is pressed
                    # print(key.name, key.rt)
                    new_keys |= utils.encode( key.name)  # use bitwise operations to check keycodes: key was or is pressed
                    new_percept |= utils.encode( key.name)  # only newly added keypresses decode the new percept
                for key in keys:  # key is released
                    # print(key.name, key.rt, key.duration)
                    new_keys &= ~utils.encode( key.name)  # use bitwise operations to check keycodes: key was pressed and is not released
                if not new_keys == current_keys:
                    percepts.append( ( global_timer.getTime(), new_keys))  
                    triggers.sendTrigger( 80 + new_keys)  # send a trigger with keycode and offset 80 (keypress)
                    print('{:03b}'.format(new_keys))
                    current_keys = new_keys

                    if not new_percept == current_percept:
                        perc_dur = percept_duration.getTime()
                        perceptual_timeline.append( ( global_timer.getTime(), current_percept, perc_dur))
                        percept_duration.reset( )
                        current_percept = new_percept
                        if trial['cond'] == 'Amb_Kp' and new_percept:
                            percept_times.append( perc_dur)

                    if new_percept in {1, 2, 4}:
                        print( 'Pure state {:s} ({:.1d}s)'.format( decode( new_percept), perc_dur))
                    else:
                        print( 'Mixed state {:03b} decoded as  ({:.1d}s'.format( new_keys, current_percept, ))

            plaid.phase += velocity
            win.flip()

        exp.addData( 'trial.stims', stimChanges)
        exp.addData( 'trial.percepts', percepts)
        exp.addData( 'trial.perceptual_timeline', perceptual_timeline)
        exp.nextEntry()  # going to the next trial
        expInfo.saveAsPickle( Path(expInfo['metaData']['paths']['root'], ExpInfo['id'] + '_expInfo.psydat').resolve())  # save after each 

    if not phase['name'] == 'learn':
        mu, sigma = utils.loglikelihood_lognormal( percept_times)

    exp.loopEnded( phase['trials'])
    win.saveFrameIntervals( filename=Path( ExpInfo['metaData']['paths']['root'], ExpInfo['id'] + '_fi.log'), clear=True)