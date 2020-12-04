from psychopy import visual
from psychopy.tools.monitorunittools import deg2pix
from math import sqrt, sin, cos, pi
import numpy as np
import utils


def createPlaids(win, alpha, **plaid_params):  # use only for coherent
    """ plaids are created in true transparency (multiplicative)
    :Parameters:

    win : window
        the window in which they will be drawn

    alpha : float
        transparency level

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
    I0 = 1  # contrast
    bkgcol = win.color # mean intensity 

    sf = plaid_params['sf']
    plaid_params.pop('sf')
    win = plaid_params['win']
    plaid_params.pop('win')
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
                    np.logical_or(Y>2-h-X, Y<h-X)), alpha[0], 1)
    grating_l = np.where(np.logical_or(
                    np.logical_and(Y>-h+X, Y<h+X),
                    np.logical_or(Y>1-h+X, Y<-1+h+X)), alpha[1], 1)

    transp_mean = dc ** 2 * alpha[0] * alpha[1] + (1 - dc) ** 2 + dc * (1 - dc) * (alpha[0] + alpha[1])
    grating = (grating_r * grating_l - transp_mean) / (1 - alpha[0] * alpha[1])
    
    bkg = visual.Circle(win=win, size=12.7, lineWidth=0, fillColor=bkgcol, autoDraw=False)
    grating = visual.GratingStim(win=win, tex=grating, sf=(sf/2/sin(angle), sf/2/cos(angle)), **plaid_params)

    return bkg, grating



def plaids( win, init_file):
    """ create different moving plaids for different conditions ambiguous, coherent, transparent-left, transparent-right 

    :Parameters:

    win : psychopy.visual.Window
        a psychopy window in which to draw the stimuli

    init_file : str
        path to the init file containing parameters such as alpha, ori and sf of the stimuli
    """

    init = utils.load_init( init_file)
    alphas = init['stim']['alpha']
    ori = init['stim']['ori']
    sf = init['stim']['sf']

    plaid_params = dict(
        tex='sqr65',
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
        amb=createPlaids(win, [alphas['amb'], alphas['amb']], **plaid_params),
        transpL=createPlaids(win, [alphas['transp'], 1-alphas['transp']], **plaid_params),
        transpR=createPlaids(win, [1-alphas['transp'], alphas['transp']], **plaid_params),
        coh=createPlaids(win, [alphas['coh'], alphas['coh']], **plaid_params)
        )

    for stim in plaid_stims:
        plaid_stims[stim] = ( *plaid_stims[stim], circle, fix_point)

    return plaid_stims