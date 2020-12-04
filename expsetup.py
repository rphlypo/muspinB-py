import ctypes
try:
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
except OSError:
    pass

import shutil
import utils

from psychopy import monitors, visual
from psychopy.hardware import keyboard
from psychopy.iohub import client
from psychopy.data import ExperimentHandler, TrialHandler

from scipy.constants import inch
from psychopy.tools.typetools import float_uint8
from math import cos, atan, tan, sqrt
from pathlib import Path


def makeMonitor( monitor_constants):
    """ 
    :param name: name of the monitor, useful to recall settings or to override existing settings
    :param res: resolution in pixels; list containing [width, height]
    :param diag: diagonal of the screen [inch]
    :param width: width of the screen [cm]
    """
    mon = monitors.Monitor( monitor_constants['name'])  # save or load the monitor
    if 'res' in monitor_constants:
        mon.setSizePix( monitor_constants['res'])  # if one would like to change the resolution of the screen

    factor = sqrt(1 + mon.getSizePix()[1] / mon.getSizePix()[0])  # for convenience

    if 'diag' in monitor_constants:
        mon.setNotes( dict( diag =monitor_constants['diag']))
        mon.setWidth( mon.getNotes()['diag'] * inch * 100 / factor)  # compute width [cm] from screen diagonal [inches] and pixel size
    elif 'width' in monitor_constants:
        mon.setWidth = monitor_constants['width']
        mon.setNotes( dict( diag=mon.getWidth() * factor / inch / 100)) 

    if 'viewing_distance' in monitor_constants:
        mon.setDistance( monitor_constants['viewing_distance'])  # distance to monitor in cm

    print( 'Using monitor {mon:s} of {diag:d}" {pix_w:d}×{pix_h:d} pixels, viewed at a distance of {dist:d} cm'.format(
        mon=mon.name(),
        diag=mon.getNotes()['diag'],
        pix_w=mon.getSizePix()[0],
        pix_h=mon.getSizePix()[1],
        dist=mon.getDistance()
    ))
    save = input( 'Do you want to save this configuration to disk under the name {}? [[Y]]es / [N]o / [R]ename '.format(monitor.name)).upper()
    if save in {'Y', ''}:
        mon.save()
    elif save == 'R':
        new_mon_name = input( 'Specify the new monitor name: ')
        mon.copyCalib( newname)
        print( 'Monitor succesfully saved under {}'.format( new_mon_name))
    
    return mon


def eyes_setup( ):
    translate_eyes = {'l': ('LEFT_EYE', 1000), 'r': ('RIGHT_EYE', 1000), 'b': ('BINOCULAR', 500), '': ('BINOCULAR', 500)}
    while True:
        eyes = input("What eyes do you want to track ? [R]ight / [L]eft / [[B]]oth? ").lower()
        try:
            track_eyes, srate = translate_eyes[eyes]
            break
        except KeyError:
            print("eyes to track must be either 'l', 'r', or 'b', received {}".format(eyes))

    while True:
        eye = input("Specify the subject's guiding eye: [L]eft / [R]ight? ")
        if eye.lower() in ['l', 'r']:
            guiding_eye = translate_eyes[eye]
            break
        else:
            print("guiding eye must either be 'l' or 'r', received {}".format(eye))
    return track_eyes, srate, guiding_eye


def eyetracker_setup( win, track_eyes, srate, filename, init_params, dummymode=False):

    init_params = utils.load_init( )
    bkgcolor = [float(float_uint8(c)) for c in win.color]
    bkgcolor.append(255)

    # see https://www.psychopy.org/api/iohub/device/eyetracker_interface/SR_Research_Implementation_Notes.html
    eyetracker_config = utils.load_init( )  # load eyelink settings
    return eyetracker_config


def init( init_file=None: str):
    """ this is the init function that is called with an appropriate json init-file

    :Parameters:

    init_file : str
        a json formatted init file containing parameters about the experimental set-up

    :return:

    expInfo : dict
        dictionary gathering information about the experiment

    win : psychopy.visual.win
        window in which the experiment will be run

    kb : psychopy.hardware.keyboard
        the keyboard configuration that will be used with the appropriate listeners
    """
    if init_file is None:
        

        while True:
            try:
                init_file = Path(input( 'Specify path to init file: ')).resolve()
                break
            except Exception as e:
                print(e)

    init = utils.load_init( init_file)

    mon = makeMonitor( init['monitor_constants'])
    win = visual.Window( monitor=mon, color=[-0.3]*3, size=mon.getSizePix(), units='deg', screen=1, fullscr=True, waitBlanking=False, blendmode='add')

    kb = keyboard.Keyboard()

    expInfo = dict(metaData=dict(), Setup=dict(), Data=dict())
    
    try:
        dummy_mode = init['experiment']['dummy']
    except KeyError:
        dummy_mode = False
    if not dummy_mode:
        # We register a new subject
        subject, subject_path = utils.register_subject( modalities=init['modalities'])
        expInfo['metaData'].update( **subject)
        expInfo['metaData']['paths'] = dict()
        expInfo['metaData']['paths']['root'] = subject_path
        expInfo['id'] = utils.get_subjectid( subject)  # to be used for the filenames
    else :
        expInfo['metaData'] = dict( paths=dict( root=Path('../test').resolve()))

    for m in expInfo['metaData']['modalities'].split( ','):  # register the path names to the structure
        expInfo['metaData']['paths'][m.upper()] = Path( expInfo['metaData']['paths']['root'], m.upper())

    # setting up the eye-tracker
    if 'GAZE' in expInfo['metaData']['paths']: 
        track_eyes, srate, guiding_eye = eyes_setup()
        et_config = eyetracker_setup( win, track_eyes, srate, expInfo['metaData']['paths']['gaze'])
        expInfo['metaData']['GAZE']['hw'] = et_config
        io = client.launchHubServer( **et_config)
        # run eyetracker calibration (later)
        r = io.devices.tracker.runSetupProcedure()  # <<<<< needs working pylink

    # setting up the EEG
    if 'EEG' in ExpInfo['metaData']['paths']:
        eeg_config = {
            'eeg': {
                'name': 'brainamp',
                'runtime_settings': {
                    'sampling_rate': srate
                }
            }
        }

    shutil.copy( init_file, expInfo['metaData']['paths']['root'])


    conditions = ['nAmb_nKp', 'nAmb_Kp', 'Amb_nKp', 'Amb_Kp']  # the four different conditions, key to our experiment
    learning_phase = TrialHandler( [ dict( cond=conditions[k]) for k in range(3)], nBlocks['learn'], method='sequential')  # learning the four percepts
    estimation_phase = TrialHandler( [ dict( cond=conditions[3])], nBlocks['estim'])  # learn the log-normal parameters through the keypress responses
    testing_phase = TrialHandler( [ dict( cond=conditions[k]) for k in range(4)], nBlocks['test'], method='random')  # get randomised blocks of all 4 conditions

    exp_structure = TrialHandler(
        [ dict( name="learn", trials=learning_phase),
        dict( name="estim", trials=estimation_phase),
        dict( name="test", trials=testing_phase)], nReps=1, method='sequential')

    expInfo['Setup'] = dict(
        exp_structure = exp_structure,
        init_file = init_file
    )

    return expInfo, win, kb

"""
hubserver = launchHubServer(
    experiment_code = 'Muspin-B',
    session_code = subject_id,
    experiment_info = dict(
        version = '0.1.0'
    ),
    session_info = dict(
        user_variables = expInfo
    ),
    datastore_name = get_subjectid( subject),
    psychopy_monitor_name = 'my_mon',
    iohub_config_name = '',  # should be completed for the configuration file of eyetracker
    **eyetracker_config,

)
"""
