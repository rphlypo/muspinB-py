from psychopy.iohub.client import launchHubServer
from psychopy.tools.typetools import float_uint8


def setup(filename, win):
    translate_eyes = {'l': ('LEFT_EYE', 1000), 'r': ('RIGHT_EYE', 1000), 'b': ('BINOCULAR', 500), '': ('BINOCULAR', 500)}
    while True:
        eyes = input("What eyes do you want to track ? [R]ight / [L]eft / [[B]]oth? ")
        try:
            track_eyes, srate = translate_eyes[eyes.lower()]
            break
        except KeyError:
            print("eyes to track must be either 'l', 'r', or 'b', received {}".format(eyes))

    while True:
        eye = input("Specify the subject's guiding eye: [L]eft / [R]ight? ")
        if eye.lower() in ['l', 'r']:
            guiding_eye = translate_eyes[eye.lower()]
            break
        else:
            print("guiding eye must either be 'l' or 'r', received {}".format(eye))

    bkgcolor = [float(float_uint8(c)) for c in win.color]
    bkgcolor.append(255)

    # see https://www.psychopy.org/api/iohub/device/eyetracker_interface/SR_Research_Implementation_Notes.html
    eyetracker_config = {'eyetracker.hw.sr_research.eyelink.eyetracker': {
                        'name': 'tracker',
                        'model_name': 'EYELINK 1000 DESKTOP',
                        'runtime_settings': {
                            'sampling_rate': srate,
                            'track_eyes': track_eyes},
                        'simulation_mode': True,  # this and the next should be set to true for debugging purposes
                        'enable_interface_without_connection': True,
                        'enable': True,
                        'saveEvents': True,
                        'monitor_event_types': ['BlinkStartEvent', 'BlinkEndEvent'],
                        'default_native_data_file_name': filename,
                        'calibration': {
                            'screen_background_color': bkgcolor}}}  # make backgroundcolor same as during stim representation


    return eyetracker_config, guiding_eye
