from psychopy import visual
from psychopy.tools.monitorunittools import deg2pix
from math import sin, cos, pi, tan, atan
import numpy as np
import random


def createPlaids(win, alpha, I0=1, normalise=True, **plaid_params):  # use only for coherent
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
    dc = int(plaid_params['tex'][3:]) / 100
    plaid_params.pop('tex')
    plaid_params['opacity'] = 1
    plaid_params['blendmode'] = 'add'
    res = plaid_params['texRes']
    angle = plaid_params['ori'] * pi / 180
    plaid_params.pop('ori')
    plaid_params['contrast'] = I0

    g = np.mgrid[:res, :res] / res
    Y, X = g[0], g[1]
    h = (1-dc) / 2

    # this represents a square pattern that can be used as a texture (X-like pattern)
    grating_r = np.where(np.logical_or(
                    np.logical_and(Y>1-h-X, Y<1+h-X),
                    np.logical_or(Y>2-h-X, Y<h-X)), 1, alpha[0])
    grating_l = np.where(np.logical_or(
                    np.logical_and(Y>-h+X, Y<h+X),
                    np.logical_or(Y>1-h+X, Y<-1+h+X)), 1, alpha[1])

    transp_mean = (1 - dc) ** 2 * alpha[0] * alpha[1] + dc ** 2 + dc * (1 - dc) * (alpha[0] + alpha[1])
    grating = I0 * grating_r * grating_l
    if normalise:
        grating = (grating - transp_mean) / (1 - alpha[0] * alpha[1])
    
    bkg = visual.Circle(win=win, size=12.7, lineWidth=0, fillColor=bkgcol, autoDraw=False)
    grating = visual.GratingStim(win=win, tex=grating, sf=(sf*cos(angle), sf*sin(angle)), **plaid_params)

    return bkg, grating


def createDots(win, coherence=0.5, nDots=100):
    ''' Create RDK within a circular aperture to overlay on the plaids
    :Parameters:

    dir: direction in degrees, 0° is left-right, 90° is down-up

    '''
    dp = dict(fieldShape='circle',
              fieldSize=12.7,
              signalDots='same',
              noiseDots='walk',
              dotSize=3,
              dotLife=30)
    dp['nDots'] = nDots
    dots = visual.DotStim(win, opacity=0.7, units='deg', **dp)
    return dots


def fixation(win):
    bkgcol = win.color # mean intensity 
    bkg = visual.Circle(win=win, size=12.7, lineWidth=0, fillColor=bkgcol, autoDraw=False)
    circle = visual.Circle(win, size=2.5, lineWidth=0, lineColor=bkgcolor, fillColor=win.color, autoDraw=False)
    fix_point = visual.Circle(win, size=4, units='pix', lineWidth=0, lineColor="black", fillColor="black", autoDraw=False)
    return bkg, circle, fix_point


def plaids(win, alpha, ori, sf, dc, **kwargs):
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
    texture = 'sqr{:2d}'.format(dc)

    plaid_params = dict(
        tex=texture,
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

    circle = visual.Circle(win, size=2.5, lineWidth=0, lineColor=win.color, fillColor=win.color, autoDraw=False)
    fix_point = visual.Circle(win, size=2, units='pix', lineWidth=0, lineColor="black", fillColor="black", autoDraw=False)

    plaid_stims = dict(
        amb=createPlaids(win, [alpha['amb'], alpha['amb']], **plaid_params),
        transpL=createPlaids(win, [alpha['transp'], 1-alpha['transp']], **plaid_params),
        transpR=createPlaids(win, [1-alpha['transp'], alpha['transp']], **plaid_params),
        coh=createPlaids(win, [alpha['coh'], alpha['coh']], **plaid_params)
        )

    for stim in plaid_stims:
        plaid_stims[stim] = (*plaid_stims[stim], circle, fix_point)

    return plaid_stims


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
    ori_rad = ori*pi/180
    vel_rad = vel*pi/180
    if vel_units == 'cycle':
        dots_vel = [atan(tan(vel_rad)/cos(ori_rad))*180/pi*cos(ori_rad)*sf,
                    atan(tan(vel_rad)/sin(ori_rad))*180/pi*sin(ori_rad)*sf]
    elif vel_units == 'deg':
        dots_vel = [atan(tan(vel_rad)/cos(ori_rad))*180/pi,
                    atan(tan(vel_rad)/sin(ori_rad))*180/pi]
    return dots_vel