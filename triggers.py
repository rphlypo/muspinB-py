from psychopy import parallel


triggers = dict(
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
    stimulus = dict(
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
    plaid = dict(
        transp_left     = 94,  # 90 + 0x100
        transp_right    = 91,  # 90 + 0x001
        coherent        = 92   # 90 + 0x010
    ),
    eyelink = dict(
        drift           = 120,
        calibration     = 121
    )
)

port = parallel.ParallelPort(address=0x0378)
port.setData( triggers['general']['init'])


def sendTrigger(value):
    port.setData(value)
