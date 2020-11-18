from expsetup import win
from psychopy import visual
from psychopy.tools.monitorunittools import deg2pix
from math import sqrt, sin, cos, pi
import numpy as np

# The grating stim: values range from -opacity to opacity about 0 (gray), using default color [1, 1, 1] 
plaid_params = dict(win=win,
                    tex='sqr65',
                    mask='circle',
                    blendmode='add', 
                    sf=1/3,
                    ori=30,
                    size=12.74,
                    units='deg',
                    pos=(0,0),
                    phase=0,
                    texRes=1024,
                    autoDraw=False)  # color=win.color,


def createPlaids(alpha, **plaid_params):  # use only for coherent
    I0 = 1  # contrast
    bkgcol = plaid_params['win'].color # mean intensity 

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

    grating_r = np.where(np.logical_or(
                    np.logical_and(Y>1-h-X, Y<1+h-X),
                    np.logical_or(Y>2-h-X, Y<h-X)), alpha[0], 1)
    grating_l = np.where(np.logical_or(
                    np.logical_and(Y>-h+X, Y<h+X),
                    np.logical_or(Y>1-h+X, Y<-1+h+X)), alpha[1], 1)

    transp_mean = dc ** 2 * alpha[0] * alpha[1] + (1 - dc) ** 2 + dc * (1 - dc) * (alpha[0] + alpha[1])
    print(transp_mean)
    grating = (grating_r * grating_l - transp_mean) / (1 - alpha[0] * alpha[1])
    
    bkg = visual.Circle(win=win, size=12.7, lineWidth=0, fillColor=bkgcol, autoDraw=False)
    grating = visual.GratingStim(win=win, tex=grating, sf=(sf/2/sin(angle), sf/2/cos(angle)), **plaid_params)

    return bkg, grating


plaid = dict( Amb=createPlaids([.5, .5], **plaid_params),
              transpL=createPlaids([.1, .9], **plaid_params),
              transpR=createPlaids([.9, .1], **plaid_params),
              coh=createPlaids([.8, .8], **plaid_params))

circle = visual.Circle(win, size=2.5, lineWidth=0, lineColor=win.color, fillColor=win.color, autoDraw=False)
fix_point = visual.Circle(win, size=2, units='pix', lineWidth=0, lineColor="red", fillColor="red", autoDraw=False)