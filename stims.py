from expsetup import win

plaid_params = dict(win=win,
                    tex='sqr65',
                    mask='circle',
                    color=win.color,
                    blendmode='add',
                    sf=1/3,
                    size=12,
                    units='deg',
                    pos=(0,0),
                    phase=0,
                    texRes=1024,
                    autoDraw=False)

def createPlaids(alpha, **plaid_params):
    try:
        alpha0, alpha1 = alpha[0], alpha[1]
        contrast0 = 0.6
        contrast1 = (1 - alpha1) / alpha1 * contrast0
    except TypeError:
        alpha0, alpha1 = alpha, 1 - alpha
        contrast0 = contrast1 = .6
    return visual.GratingStim(ori=30, opacity=alpha0, contrast=contrast0, **plaid_params), visual.GratingStim(ori=-30, opacity=alpha1, contrast=contrast1, **plaid_params)


plaid = dict( Amb=createPlaids(0.5, **plaid_params),
              transpL=createPlaids(0.1, **plaid_params),
              transpR=createPlaids(0.9, **plaid_params),
              coh=createPlaids([1, .7], **plaid_params))

circ = visual.Circle(win, size=2.25, lineWidth=0, lineColor=win.color, fillColor=win.color, autoDraw=False)
fix_point = visual.Circle(win, size=2, units='pix', lineWidth=0, lineColor="red", fillColor="red", autoDraw=False)