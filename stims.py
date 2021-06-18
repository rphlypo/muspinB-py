import numpy as np
import random
from psychopy import visual
from math import sin, cos, pi, tan, atan, sqrt
from collections import Iterable

def _deg2rad(d):
    """ helper function to transform degrees into radians
    """
    return d / 180 * pi


def _rad2deg(r):
    """ helper function to transform radians into degrees
    """
    return r / pi * 180


def __normalise(x, alpha, dc, normalisation='zscore'):
    transp_mean = (1 - dc[0]) * (1 - dc[1]) + dc[0] * dc[1] * alpha[0] * alpha[1] + dc[0] * (1 - dc[1]) * alpha[0] + dc[1] * (1 - dc[0]) * alpha[1]
    if normalisation == 'centering':
        return x - transp_mean
    elif normalisation == 'zscore':
        return (x - transp_mean) / (1 - alpha[0] * alpha[1])
    else:
        return x


def __get_couple(x):
    if not isinstance(x, Iterable):
        x = (x, x)
    elif len(x) < 2:
        x = (x[0], x[0])
    elif len(x) > 2:
        raise ValueError(f'Expected one or two values, got {len(x)}')
    else:
        x = tuple(x)
    return x


def transparent_Plaid(win, alpha, I0=1, dc=0.5, ori=15, sf=1, res=1024, **kwargs):
    """
    :param win: the psychopy window object

    :param alpha: the transparency value(s), either a single value, or 2-valued (alpha_left, alpha_right)

    :param I0: background luminosity in [0, 1]

    :param dc:  the duty cycle, common to both gratings

    :param ori: the orientations, common to both gratings

    :param sf: the spatial frequency, common to both gratings

    :param res: resolution of the texture
    """
    plaid_params = dict(
        size = 100,  # should be the radius in degrees, but seems to be the diameter
        units = 'deg',
        mask = 'circle',
        pos=(0, 0),
        phase=[0, 0],
        blendmode = 'avg',
        opacity = 1,
        autoDraw=False
    )

    alpha = __get_couple(alpha)
    dc = __get_couple(dc)

    g = np.mgrid[:res, :res] / res
    Y, X = g[0], g[1]
  
    # this represents a square pattern that can be used as a texture (X-like pattern)
    # the function np.mod(x+1/2, 1) - 1/2 is a periodic ramp function mapping 
    # for each integer k, [-1/2 + k; 1/2 + k] -> [-1/2; 1/2]
    grating_l = np.where(np.abs(np.mod(Y-X+1/2, 1)-1/2) <= dc[0]/2, alpha[0], 1)
    grating_r = np.where(np.abs(np.mod(Y+X+1/2, 1)-1/2) <= dc[1]/2, alpha[1], 1)
    # the grating is the background illumination I0 multiplied by the absorption coefficients
    grating = I0 * grating_r * grating_l
    
    grating = __normalise(grating, alpha, dc, normalisation='z-score')
    angle = _deg2rad(ori)

    grating = visual.GratingStim(win=win, tex=grating, texRes=res, sf=(sf*cos(angle), sf*sin(angle)), **plaid_params)
    return grating


def createDots(win, alpha, dc, coherence=0.5, nDots=100, I0=1):
    ''' Create RDK within a circular aperture to overlay on the plaids
    :Parameters:

    dir: direction in degrees, 0° is left-right, -90° is down-up

    '''
    dp = dict(
        fieldShape='circle',
        fieldSize=20,
        signalDots='same',
        noiseDots='direction',
        coherence=coherence,
        nDots=nDots,
        dotSize=7,
        dotLife=50
        )
    col = tuple([__normalise(I0, __get_couple(alpha), __get_couple(dc), normalisation='centering')] * 3)

    # element = visual.Line(win, start=(-500,0), end=(500,0), units='pix', lineWidth=3, lineColor=col, ori=180-20)
    dots = visual.DotStim(win, units='deg', color=col, **dp)
    return dots


def fixation_disk(win, radius=2.5, dot_radius=.1, dot_color="red"):
    circle = visual.Circle(win, radius=radius, lineColor=None, fillColor=win.color, autoDraw=False)
    fix_point = visual.Circle(win, radius=dot_radius, lineColor=None, fillColor=dot_color, autoDraw=False)
    return circle, fix_point


def sample_next_state(current_state=None, tm=None):  # TODO: implement transition between plaid_stims
    """
    :param current_state: entry in the transition matrix one is transitioning from
        tm[current_state] will give a dictionary with
    :param tm: transition matrix as a dictionary
        tm['from']['to'] is proportial to a transition probability
        tm['from']['to'] is a probability relative to [x + y for y in tm['from'].values()]
    """
    target_states, weights = zip(*[(k, v) for k, v in tm[current_state].items()])
    return random.choices(target_states, weights, k=1)


def get_angular_velocity(target_ori, vel_deg=1, stim_ori=0, correctFlat=False):
    Delta_theta = _deg2rad(target_ori - stim_ori)  # Delta_theta in radians
    c = cos(Delta_theta)
    if abs(c) > 1/2:
        angular_velocity = vel_deg / cos(Delta_theta)
    else:
        angular_velocity =  vel_deg * tan(Delta_theta) / sin(Delta_theta)
    return abs(angular_velocity)


def get_angular_frequency(target_ori, sf=1, stim_ori=0, correctFlat=False):
    Delta_theta = _deg2rad(target_ori - stim_ori)
    c = cos(Delta_theta)
    if abs(c) > 1/2:
        angular_frequency = sf * cos(Delta_theta)
    else:
        angular_frequency = sf * sin(Delta_theta) / tan(Delta_theta)
    return abs(angular_frequency)