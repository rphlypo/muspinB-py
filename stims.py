from numpy.core.arrayprint import str_format
from psychopy import visual
from psychopy.tools.monitorunittools import deg2pix
from math import sin, cos, pi, tan, atan, sqrt
import numpy as np
import random


def createPlaids(win, alpha, normalise=False, **plaid_params):  # use only for coherent
    """ plaids are created in true transparency (multiplicative)
    :Parameters:

    win : window
        the window in which they will be drawn

    alpha : tuple of 2 floats [0, 1]×[0, 1]
        transparency levels

    I0 : float [0, 1]
        background intensity

    normalise : bool
        whether or not to normalise intensity values for mean and contrast

    sf : float
        spatial frequency in deg^-1

    tex : string
        the texture which is mainly used for the duty cycle (last two characters as digits)

    texRes : int
        the resolution of the texture as number of pixels per period

    ori : float
        orientation of the gratings (± given orientation)

    :return:
    """
    bkgcol = win.color # mean intensity 

    sf = plaid_params['sf']
    plaid_params.pop('sf')
    dc = plaid_params['dc']
    plaid_params.pop('dc')
    plaid_params['opacity'] = 1
    plaid_params['blendmode'] = 'add'
    res = plaid_params['texRes']
    angle = plaid_params['ori'] * pi / 180
    plaid_params.pop('ori')
    I0 = plaid_params['I0']
    plaid_params['contrast'] = 1
    plaid_params.pop('I0')

    g = np.mgrid[:res, :res] / res
    Y, X = g[0], g[1]

    # this represents a square pattern that can be used as a texture (X-like pattern)
    grating_r = np.where(np.cos(2*np.pi*(Y+X)) > np.cos(2*np.pi*dc/2), alpha[0], 1)
    grating_l = np.where(np.cos(2*np.pi*(Y-X)) > np.cos(2*np.pi*dc/2), alpha[1], 1)

    # the grating is the background illumination I0 multiplied by the absorption coefficients
    grating = I0 * grating_r * grating_l
    if normalise:
        print(alpha, dc)
        grating = __normalise(grating, alpha, dc, normalisation='center')
        print(__normalise(1, alpha, dc))
    
    bkg = visual.Circle(win=win, size=12.7, lineWidth=0, fillColor=bkgcol, autoDraw=False)
    grating = visual.GratingStim(win=win, tex=grating, sf=(sf*cos(angle), sf*sin(angle)), **plaid_params)

    return bkg, grating


def __normalise(x, alpha, dc, normalisation='zscore'):
    transp_mean = (1 - dc) ** 2 * alpha[0] * alpha[1] + dc ** 2 + dc * (1 - dc) * (alpha[0] + alpha[1])
    if normalisation == 'centering':
        return x - transp_mean
    elif normalisation == 'zscore':
        return (x - transp_mean) / (1 - alpha[0] * alpha[1])
    else:
        return x


def createDots(win, alpha, dc, coherence=0.5, nDots=100, I0=1):
    ''' Create RDK within a circular aperture to overlay on the plaids
    :Parameters:

    dir: direction in degrees, 0° is left-right, -90° is down-up

    '''
    dp = dict(fieldShape='circle',
              fieldSize=12.7,
              signalDots='same',
              noiseDots='walk',
              coherence=coherence,
              nDots=nDots,
              dotSize=3,
              dotLife=10)
    color = I0  # __normalise(I0, alpha, dc, normalisation='center')
    dots = visual.DotStim(win, units='deg', contrast=I0, **dp)
    return dots


def fixation(win):
    bkgcol = win.color # mean intensity 
    bkg = visual.Circle(win=win, size=12.7, lineWidth=0, fillColor=bkgcol, autoDraw=False)
    circle = visual.Circle(win, size=2.5, lineWidth=0, lineColor=bkgcolor, fillColor=win.color, autoDraw=False)
    fix_point = visual.Circle(win, size=4, units='pix', lineWidth=0, lineColor="black", fillColor="black", autoDraw=False)
    return bkg, circle, fix_point


def plaids(win, alpha, sf, dc, ori, I0=1, normalise=False, **kwargs):
    """ create different moving plaids for different conditions ambiguous, coherent, transparent-left, transparent-right 

    :Parameters:

    win: psychopy.visual.Window
        a psychopy window in which to draw the stimuli

    alpha: dict
        different transparency values

    ori: float
        orientation of the gratings in degrees

    sf: float
        spatial frequency of the gratings

    dc: float
        duty cycle of the gratings
    """

    plaid_params = dict(
        dc=dc,
        I0=I0,
        normalise=normalise,
        mask='circle',
        blendmode='add', 
        sf=sf,
        ori=ori,
        size=12.74,
        units='deg',
        pos=(0,0),
        phase=0,
        texRes=1024,
        autoDraw=False)  # color=win.color,

    plaid_stims = dict(
        amb=createPlaids(win, [alpha['amb'], alpha['amb']], **plaid_params),
        transpL=createPlaids(win, [alpha['transp'], 1-alpha['transp']], **plaid_params),
        transpR=createPlaids(win, [1-alpha['transp'], alpha['transp']], **plaid_params),
        coh=createPlaids(win, [alpha['coh'], alpha['coh']], **plaid_params)
        )

    return plaid_stims


def fixation_disk(win):
    circle = visual.Circle(win, size=2.5, lineWidth=0, lineColor=win.color, fillColor=win.color, autoDraw=False)
    fix_point = visual.Circle(win, size=3, units='pix', lineWidth=0, lineColor="black", fillColor="black", autoDraw=False)
    return circle, fix_point


def sample_next_stim(current_stim=None, tm=None):  # TODO: implement transition between plaid_stims
    if tm is None:
        stim_set = list({'transpL', 'transpR', 'coh'} - set([current_stim]))
        weights = None  
    else:
        # tm is a dictionary encoding the transition matrix
        # tm['transpL'] = {'coh': 0.2, 'transpR':0.8}
        stim_set, weights = zip(*[(k, v) for k, v in tm[current_stim].items()])
    return random.choices(stim_set, weights, k=1)


def get_velocity_vector(vel=1, ori=0, sf=1, vel_units='cycle',**kwargs):
    """ takes stim parameters as input (as defined through the init.yaml) and returns the velocity vector
    :param vel: positive float
                velocity (perpendicular to the wavefront) in visual degrees per second
    :param ori: float
                angle in degrees of the wavefront with respect to the vertical axes
    """
    ori_rad = ori*pi/180  # deg --> rad
    vel_rad = vel*pi/180  # deg --> rad

    if vel_units == 'cycle':
        dots_vel = [atan(tan(vel_rad)/cos(ori_rad))*180/pi*cos(ori_rad)*sf,
                    atan(tan(vel_rad)/sin(ori_rad))*180/pi*sin(ori_rad)*sf]
    elif vel_units == 'deg':
        dots_vel = [atan(tan(vel_rad)/cos(ori_rad))*180/pi,
                    atan(tan(vel_rad)/sin(ori_rad))*180/pi]
    return dots_vel


def _deg2rad(d):
    return d / 180 * pi


def _rad2deg(r):
    return r / pi * 180


def get_angular_velocity(target_ori, vel_deg=1, stim_ori=0):
    Delta_theta = _deg2rad(target_ori - stim_ori)  # Delta_theta in radians
    return _rad2deg(atan(tan(_deg2rad(vel_deg)) * sqrt(1 + tan(Delta_theta) ** 2)))
