import ctypes
try:
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
except OSError:
    pass

from psychopy import monitors, visual
from psychopy.hardware import keyboard
from psychopy.iohub import client
from psychopy.data import ExperimentHandler, TrialHandler

from scipy.constants import inch
from math import cos, atan, tan, sqrt
from pathlib import Path
import eyetracking
import utils


def makeMonitor( **monitor_constants):
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


def init( init_file=None):
    if init_file is None:
        while True:
            try:
                init_file = Path(input( 'Specify path to init file: ')).resolve()
                break
            except Exception as e:
                print(e)

    init = utils.load_init( init_file)

    mon = makeMonitor( init['monitor_constants'])
    win = visual.Window(monitor=mon, color=[-0.3]*3, size=mon.getSizePix(), units='deg', screen=1, fullscr=True, waitBlanking=False, blendmode='add')

    kb = keyboard.Keyboard()

    expInfo = dict(metaData=dict(), Setup=dict(), Data=dict())
    
    run_mode = utils.set_experiment_mode()    
    if run_mode == "full":
        # We register a new subject
        subject, subject_path = utils.register_subject( modalities={'Gaze', 'EEG'})
        expInfo['metaData'].update( **subject)
        expInfo['metaData']['paths'] = dict()
        expInfo['metaData']['paths']['root'] = subject_path
        expInfo['id'] = utils.get_subjectid(subject)  # to be used for the filenames
        for m in expInfo['metaData']['modalities'].split( ','):
            expInfo['metaData']['paths'][m] = Path( subject_path, m)
        # setting up the Gaze procedure
        if 'gaze' in [m.lower() for m in expInfo['metaData']['modalities'].split( ',')]: 
            et_config, guiding_eye = eyetracking.setup( utils.get_subjectid( subject), win)
            io = client.launchHubServer( **et_config)
            # run eyetracker calibration (later)
            r = io.devices.tracker.runSetupProcedure()  # <<<<< needs working pylink
    else :
        expInfo['metaData'] = dict( paths=dict( root=Path('.').resolve()))



    conditions = ['nAmb_nKp', 'nAmb_Kp', 'Amb_nKp', 'Amb_Kp']  # the four different conditions, key to our experiment
    learning_phase = TrialHandler( [ dict( cond=conditions[k]) for k in range(3)], nBlocks['learn'], method='sequential')  # learning the four percepts
    training_phase = TrialHandler( [ dict( cond=conditions[3])], nBlocks['train'])  # learn the log-normal parameters through the keypress responses
    testing_phase = TrialHandler( [ dict( cond=conditions[k]) for k in range(4)], nBlocks['test'], method='random')  # get randomised blocks of all 4 conditions

    exp_structure = TrialHandler(
        [ dict( name="learn", trials=learning_phase),
        dict( name="train", trials=training_phase),
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
