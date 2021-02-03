import ctypes
try:
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
except OSError:
    pass

import shutil
import utils
import math
import stims
import triggers

from pathlib import Path
from psychopy import monitors, visual
from psychopy.iohub import client

from psychopy.data import ExperimentHandler, TrialHandler
from scipy.constants import inch
from psychopy.tools.typetools import float_uint8


def makeMonitor(monitor_constants):
    """ 
    :param name: name of the monitor, useful to recall settings or to override existing settings
    :param res: resolution in pixels; list containing [width, height]
    :param diag: diagonal of the screen [inch]
    :param width: width of the screen [cm]
    """
    mon = monitors.Monitor(monitor_constants['name'])  # save or load the monitor
    if 'res' in monitor_constants:
        mon.setSizePix(monitor_constants['res'])  # if one would like to change the resolution of the screen

    factor = math.sqrt(1 + mon.getSizePix()[1] / mon.getSizePix()[0])  # for convenience

    if 'diag' in monitor_constants:
        mon.setNotes(dict(diag =monitor_constants['diag']))
        mon.setWidth(mon.getNotes()['diag'] * inch * 100 / factor)  # compute width [cm] from screen diagonal [inches] and pixel size
    elif 'width' in monitor_constants:
        mon.setWidth = monitor_constants['width']
        mon.setNotes(dict(diag=mon.getWidth() * factor / inch / 100)) 

    if 'viewing_distance' in monitor_constants:
        mon.setDistance(monitor_constants['viewing_distance'])  # distance to monitor in cm

    print('Using monitor {mon:s} of {diag:d}" {pix_w:d}×{pix_h:d} pixels, viewed at a distance of {dist:d} cm'.format(
        mon=mon.name,
        diag=mon.getNotes()['diag'],
        pix_w=mon.getSizePix()[0],
        pix_h=mon.getSizePix()[1],
        dist=mon.getDistance()
    ))
    
    all_monitors = monitors.getAllMonitors()
    if mon.name in all_monitors:
        save = input('A monitor with this name already exists. Do you want to save the new configuration to disk under the name {}? [[Y]]es / [N]o / [R]ename '.format(mon.name)).upper()
        if save in {'Y', ''}:
            mon.save()
        elif save == 'R':
            mon.name = input('Specify the new monitor name: ')

    print('Monitor succesfully saved under {}'.format(mon.name))
    
    return mon


def get_guiding_eye():
    translate_eyes = {'l': 'LEFT_EYE', 'r': 'RIGHT_EYE'}

    while True:
        eye = input("Specify the subject's guiding eye: [L]eft / [R]ight? ").lower()
        if eye in translate_eyes:
            guiding_eye = translate_eyes[eye]
            break
        else:
            print("guiding eye must either be 'l' or 'r', received {}".format(eye))
    return guiding_eye


def eyetracker_setup(win, et_config_file=None):
    """ loads the eyetracker configuration file
    see https://www.psychopy.org/api/iohub/device/eyetracker_interface/SR_Research_Implementation_Notes.html
    """
    if et_config_file is None:
        eyetracker_config = {
            'eyetracker.hw.sr_research.eyelink.EyeTracker': {
                'calibration': dict(),
                'simulation_mode': True,
                'enable_interface_without_connection': True
            }
        }
    else:
        eyetracker_config = utils.load_init(et_config_file)  # load eyelink settings

    bkgcolor = [int(float_uint8(c)) for c in win.color]
    k = list(eyetracker_config.keys())[0]  # this is the hw specification path
    eyetracker_config[k]['calibration'].update(dict(screen_background_color=bkgcolor))

    return eyetracker_config


def check_modality( mod, io):
    modalities = io.getSessionMetaData()['user_variables']['modalities']
    return mod.lower() in [m.lower() for m in modalities]


def init(init_file=None):
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
    # dictionary with the parameters from the init file
    init = utils.load_init(init_file)  

    # set-up the Display and monitor
    # make a monitor with monitor constants from the init file
    mon = makeMonitor(init['monitor_constants'])  
    # and make a window using that monitor
    win = visual.Window(
        monitor=mon, 
        color=init['experiment']['bkgcolor'],
        size=mon.getSizePix(), 
        units='deg', 
        screen=1,  # 0 is the monitor of the experiment control
        fullscr=True, 
        allowGUI=False,
        blendmode='add',  
        waitBlanking=False, 
        winType='pyglet')  # for iohub to function well

    # start to fill the ioHub_config
    ioHub_config = dict(
        experiment_code = init['experiment']['name'],
        experiment_info = dict(
            total_sessions_to_run = 2
        ),
        session_info = dict(
            user_variables = dict(
                modalities = init['experiment']['modalities'],
                observer = init['experiment']['observer'],
                dummy_mode = init['experiment']['dummy_mode'],
                hw = dict(
                    parallel_port = init['devices']['parallel_port']
                ),
                parameters = init['experiment']['stim']
            )
        ),
        psychopy_monitor_name = mon.name,
        data_store = dict(
            enable = False
        ),
        mouse = dict(
            enable = False
        )
    )

    # transform the velocity of the gratings to the plaid (vertical) velocity
    v = init['experiment']['stim']['vel']
    theta = init['experiment']['stim']['ori'] * math.pi / 180
    sf = init['experiment']['stim']['sf']
    ioHub_config['session_info']['user_variables']['parameters']['velocity'] = [0, v / math.sin(theta) * sf]

    # make sure the eyetracker is available as eyelink
    try:
        et_init_file = init['devices']['eyetracker']
        et_init = eyetracker_setup(win, et_init_file)
    except KeyError:
        print('no eyetracker configuration file given, using default Eyelink')
        et_init = eyetracker_setup(win)
    
    if 'GAZE' in [m.upper() for m in init['experiment']['modalities']]:
        ioHub_config.update(et_init)

    # Are we running in dummy_mode ?
    try:
        dummy_mode = init['experiment']['dummy_mode']
    except KeyError:
        dummy_mode = False

    # for a given subject the data directory is
    # <session_type><subject_id>
    # and all files are named as
    # <session_type><subject_id>_<session_number>_<modality>.<ext>
    if not dummy_mode:
        session_id, subject_path = utils.register_subject(datapath=init['data']['path'], modalities=init['modalities'])  
    else:
        session_id = 'tmp'
        subject_path = Path(Path.cwd(), 'subject_data')
        subject_path.mkdir()

    shutil.copy(init_file, Path(subject_path).joinpath(session_id + '_init.yaml'))
    ioHub_config['session_code'] = session_id
    ioHub_config['data_store'].update(dict(
                enable = True,
                filename = session_id,
                parent_dir = subject_path
            ))
    logfile = Path(subject_path).joinpath(session_id + '_log.tsv')
    triggerfile = Path(subject_path).joinpath(session_id + '_triggers.tsv')
    ioHub_config['session_info']['user_variables']['logfile'] = logfile
    ioHub_config['session_info']['user_variables']['triggerfile'] = triggerfile

    # setting up the eye-tracker
    if 'GAZE' in [m.upper() for m in init['experiment']['modalities']]:
        ioHub_config['session_info']['user_variables']['guiding_eye'] = get_guiding_eye()
    
    # Start the ioHub process. 'io' can now be used during the
    # experiment to access iohub devices and read iohub device events
    # important devices for us are
    #   io.getDevice('keyboard')
    #   io.getDevice('eyelink')
    io = client.launchHubServer(**ioHub_config)

    # the four different conditions, key to our experiment
    nBlocks = init['experiment']['structure']['nBlocks']
    conditions = [
        dict(
            cond='nAmb_nKp',
            img='img/noPRESS.jpg',
         ),
         dict(
             cond='nAmb_Kp',
             img='img/PRESS.jpg',
         ),
         dict(
             cond='Amb_nKp',
             img='img/noPRESS.jpg',
         ),
         dict(
             cond='Amb_Kp',
             img='img/PRESS.jpg',
         )]  

    # the subject learns the different conditions (only first three of them)
    learning_phase = TrialHandler(conditions[:-1], nReps=nBlocks['learn'], method='sequential') 
    # the subject goes through 4 blocks of a single trial 'Amb_Kp', will be used to estimate the parameters for the perceptual transitions
    estimation_phase = TrialHandler([conditions[3]], nReps=nBlocks['estim'], method='sequential') 
    # this is the final phase of the experiments with blocks of randomly shuffled conditions
    testing_phase = TrialHandler(conditions, nReps=nBlocks['test'], method='random')

    exp_structure = TrialHandler([
        dict(name="learn", trials=learning_phase, img='img/Consigne.jpg', text="Phase d'habituation I"),
        dict(name="estim", trials=estimation_phase, img='', text="Phase d'habituation II"),
        dict(name="test", trials=testing_phase, img='', text="Phase d'expérimentation")
        ], 
        nReps=1, method='sequential')

    # generate the different stimuli
    plaid_stims = stims.plaids(win, **init['experiment']['stim'])
    plaid_stims.update(dict(fix=stims.fixation(win)))
    return io, win, exp_structure, plaid_stims