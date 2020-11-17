# Set the monitor constants, giving the monitor a name to reload settings at a later time
monitor_constants = dict( monitor_name = 'mymon',  # give your monitor a name
                          diag_mon = 23,  # monitor diagonal in inches
                          pixels = [1920, 1080],  # width and height of the monitor in number of pixels
                          viewing_distance = 56)  # viewing distance in centimeters


# Specify the different trialTypes
trialTypes = ['Amb_nKp', 'Amb_Kp', 'nAmb_nKp', 'nAmb_Kp']

nBlocks = dict( learn=1,  # blocks consisting of 1 of each type of trials
                train=4,  # blocks consisting only of a single 'Amb_Kp'
                test=14)  # blocks consisting of 1 of each type of trials

trials = dict( learn=trialTypes * nBlocks['learn'],
               train=['Amb_Kp'] * nBlocks['train'],
               test=trialTypes * nBlocks['test'])