import ctypes
try:
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
except OSError:
    pass

from typing import Callable
from psychopy.core import getTime


class Percept():
    percept_dict = {
        'keys': {'left': 0b100, 'up': 0b010, 'right': 0b001},
        'perceptual_states': {'transparent_left': 0b100, 'coherent': 0b010, 'transparent_right': 0b001}
    }

    def __init__(self, perceptual_state: int=0, from_keys: bool=False, onset: float=None, end: float=None):
        if from_keys:
            self.perceptual_state = self.__from_keys(perceptual_state)
        elif hasattr(perceptual_state, '__iter__'):
            self.perceptual_state = self.__from_state_list(perceptual_state)
        else:
            self.perceptual_state = perceptual_state

        self.onset = onset
        self.end = end

    @property
    def perceptual_state(self):
        return self.__perceptual_state

    @perceptual_state.setter
    def perceptual_state(self, x: int):
        self.__perceptual_state = int(x)

    @property
    def onset(self):
        return self.__onset

    @onset.setter
    def onset(self, t: float):
        self.__onset = t

    @property
    def end(self):
        return self.__end
    
    @end.setter
    def end(self, t: float):
        if t is None:
            self.__end = t
        elif self.onset is not None:
            if t < self.onset:
                raise ValueError('end time ({}s) must be later than onset time ({}s)'.format(t, self.__onset))
            else:
                self.__end = t
        else:
            raise AttributeError('Impossible to define an end time before initialising an onset time')

    @property
    def duration(self):
        if not self.end is None:
            return self.end - self.onset
        else:
            return None

    @property
    def ongoing(self):
        return True if self.end is None and self.onset is not None else False

    @property
    def is_active(self, t):
        if self.onset is not None:
            return t > self.onset and (self.end is None or t<self.end)
        else:
            False

    def __from_keys(self, keys):
        p = 0
        if not hasattr(keys, '__iter__') or isinstance(keys, str):
            keys = [keys]
        for k in keys:
            p |= self.percept_dict['keys'][ k]
        return p

    def __from_state_list(self, states):
        p = 0
        if not hasattr(states, '__iter__') or isinstance(states, str):
            states = [states]
        for k in states:
            p |= self.percept_dict['perceptual_states'][ k]
        return p

    def __decompose_into_pure_states(self):
        states = []
        for v in self.percept_dict['perceptual_states'].values():
            if v & self.perceptual_state:
                states.append(v)
        return states

    def is_pure_state(self):
        if len(self.__decompose_into_pure_states()) == 1:
            return True
        else:
            False

    def __decode_states(self, mod='perceptual_states'):
        states = self.__decompose_into_pure_states()
        return set(k for k in self.percept_dict[mod] if self.percept_dict[mod][k] in states)

    def as_perceptual_states(self):
        return self.__decode_states(mod='perceptual_states')

    def as_keys(self):
        return self.__decode_states(mod='keys')

    def __add__(self, other):
        return Percept(self.perceptual_state | other.perceptual_state)

    def __sub__(self, other):
        """ use '-' to return the states in self that are not in other
        """
        return Percept(self.perceptual_state & ~other.perceptual_state)

    def __invert__(self):
        return Percept(~self.perceptual_state)

    def __iadd__(self, other):
        self.perceptual_state |= other.perceptual_state

    def __isub__(self, other):
        self.perceptual_state &= ~other.perceptual_state

    def __gt__(self, other):
        """ self contains all perceptual states of other
        """
        return self - other > 0

    def __lt__(self, other):
        """ other contains all perceptual states of self
        """
        return other - self > 0

    def __eq__(self, other):
        """ only the state matters, not the timing
        """
        return self.perceptual_state == other.perceptual_state

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __int__(self):
        return self.perceptual_state

    def __repr__(self):
        dur = '{}' if self.end is None else '{:.3f}s'
        t_on = '{}' if self.onset is None else '{:.3f}s'
        return ('Percept({:03b}, onset=' + t_on + ' , duration=' + dur + ')').format(self.perceptual_state, self.onset, self.duration)


def waitKeyPress(keyboard, key: (list,str)=None, timeout:float =60) -> bool:
    
    sTime = getTime()

    if not hasattr(key, '__iter__') or isinstance(key, str):
        key = [key]  # make sure we test whether the response is in the list of keys not in the name of the key

    while getTime() - sTime < timeout:
        try:
            for e in keyboard.getEvents(clear=True):
                if type(e).__name__ == 'KeyboardReleaseEventNT' and (e.key in key or key is None):
                    raise StopIteration
        except StopIteration:
            break              
    else:  # means we break out of the loop without the right keypress
        print('timed out, continuing anyway...')
        return True  # left due to time-out

    return False  # left with keypress, i.e., without timing out


def percept_report_buffering(f):
    percept_buffer = [ Percept(0, onset=getTime())]

    def wrapper(*args, clear: bool=False, **kwargs) -> Callable:   
        if clear:  # do not continue to fill the buffer, start a new one (useful when new trial is started)
            del percept_buffer[:]
            percept_buffer.append(Percept(0, onset=getTime()))
            
        kwargs['response'] = percept_buffer[-1].perceptual_state  # get the last (current) reponse
        responses = f(*args, **kwargs)

        if responses:
            percept_buffer.extend(responses)
            percept_buffer.sort( key=lambda x:x.onset)

        for ix in range(len(percept_buffer) - 1):
            percept_buffer[ix].end = percept_buffer[ix+1].onset

        return percept_buffer
    return wrapper


@percept_report_buffering
def get_percept_report(keyboard:'keyboard', response: int):
    keymap = {'up': 0b010, 'left': 0b100, 'right': 0b001}
    responses = []
    
    for e in keyboard.getEvents(clear=True):
        if type(e).__name__ == 'KeyboardPressEventNT':  # is returned as namedtuple
            # print('{} has been pressed at {}s'.format(e.key, e.time))  # should transform to logging statement
            try:
                response |= keymap[e.key]
            except KeyError:
                print('Key [{}] pressed, not handled properly'.format(e.key))  # handle with logging (warning)
        elif type(e).__name__ == 'KeyboardReleaseEventNT':  # is returned as namedtuple
            #  print('{} has been released at {}s'.format(e.key, e.time))  # should transform to logging statement
            try:
                response &= ~keymap[e.key]
            except KeyError:
                print('Key [{}] pressed, not handled properly'.format(e.key))  # handle with logging (warning)

        # print('{:03b}'.format(response))  # transform to logging statement

        responses.append(Percept(response, onset=e.time))
    return responses


if __name__=='__main__':
    from psychopy import iohub, visual
    from psychopy.iohub import devices

    # Start the ioHub process. 'io' can now be used during the
    # experiment to access iohub devices and read iohub device events.
    io = iohub.launchHubServer()

    kb = io.devices.keyboard
    kb.reporting = True  
    win = visual.Window()  # intercepts the keypresses so that they are not sent to the console


    print('Press [SPACE] to continue... ')
    waitKeyPress(kb, key=' ', timeout=10)

    print('press arrow keys')
    for i in range(120):
        win.flip()
        pb = get_percept_report(kb)
    print (pb)

    print('press arrow keys')
    for i in range(120):
        win.flip()
        pb = get_percept_report(kb)
    print(pb)

    get_percept_report(kb, clear=True)
    print('press arrow keys')
    for i in range(120):
        win.flip()
        pb = get_percept_report(kb)
    print(pb)

    # Stop the ioHub Server
    io.quit()