from psychopy import parallel


trigger = dict(
    acquisition = dict(
        start           = 10,
        end             = 11,
        interrupt       = 12
    ),
    trial = dict(
        start           = 20,
        consigne        = 21,
        feedback        = 22,
        end             = 29
    ),
    general = dict(
        init            = 0,
        fixationcross   = 30,
        consigne        = 34
    ),
    condition = dict(
        nAmb_nKp        = 40,  # 40 + 0x00
        nAmb_Kp         = 41,  # 40 + 0x01
        Amb_nKp         = 42,  # 40 + 0x10
        Amb_Kp          = 43,  # 40 + 0x11
        end             = 49
    ),
    keypress = dict(
        left            = 84,  # 80 + 0x100
        right           = 81,  # 80 + 0x001
        up              = 82,  # 80 + 0x010
        up_left         = 86,  # 80 + 0x110
        up_right        = 83,  # 80 + 0x011
        left_right      = 85,  # 80 + 0x101
        up_left_right   = 87,  # 80 + 0x111
        esc             = 89
    ),
    stimulus = dict(
        transpL         = 94,  # 90 + 0x100
        transpR         = 91,  # 90 + 0x001
        coh             = 92,  # 90 + 0x010
        amb             = 99
    ),
    eyelink = dict(
        drift           = 120,
        calibration     = 121
    )
)

port = parallel.ParallelPort(address=0x0378)
port.setData( triggers['general']['init'])


def sendTrigger( value):
    port.setData( value)
    # TODO : send trigger as message to the Eyelink ?


def quit( reason='end'):
    # TODO save all that is there to save
    if reason == 'interrupt':
        sendTrigger( trigger['acquisition']['interrupt'])
    elif reason == 'end'
        sendTrigger( trigger['acquisition']['end'])
    core.quit()