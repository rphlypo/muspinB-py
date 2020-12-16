from psychopy import parallel, core
from psychopy import logging

# add a logging level in between the EXP and INFO level
logging.addLevel(21, 'TRIG')

class Trigger():
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
            nopercept       = 80,  # 80 + 0b000
            left            = 84,  # 80 + 0b100
            right           = 81,  # 80 + 0b001
            up              = 82,  # 80 + 0b010
            left_up         = 86,  # 80 + 0b110
            up_right        = 83,  # 80 + 0b011
            left_right      = 85,  # 80 + 0b101
            left_up_right   = 87,  # 80 + 0b111
            esc             = 89
        ),
        stimulus = dict(
            transpL         = 94,  # 90 + 0b100
            transpR         = 91,  # 90 + 0b001
            coh             = 92,  # 90 + 0b010
            amb             = 99
        ),
        eyelink = dict(
            drift           = 120,
            calibration     = 121
        )
    )


    def __init__(self, port=None):
        self.port = port

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, p):
        if p is not None:
            try:
                self.__port = parallel.ParallelPort(address=p)
            except FileNotFoundError:
                self.__port = None
        else:
            self.__port = None

    def send(self, triggertype, triggername, io=None):
        value = self.trigger[triggertype][triggername]
        logging.log('{}\t{}\t{}'.format(value, triggertype, triggername), level=logging.getLevel('TRIG'))
        if not io is None:
            io.sendMessageEvent(format(value), category='TRIGGER')
        
        if self.port is not None:
            sendTime = core.getTime()
            self.port.setData(value)
            while core.getTime() < sendTime + .004:
                self.port.setData(0)

        



if __name__ == '__main__':
    logging.LogFile(f='triggers.tsv', level=logging.getLevel('TRIG'))
    trigger = Trigger()
    trigger.send('acquisition', 'start')
    trigger.send('acquisition', 'end')
