from psychopy import visual, core, clock
from expsetup import win, kb, expInfo
from stims import plaid_stims


speed = 1  # degrees per second

timer = clock.Clock()
now = start_time = timer.getTime()
kb.clock.reset()  # when you want to start the timer

keycode = {'right': 1, 'up': 2, 'left':4}
current_keys = 0
new_keys = 0
nflips = 0

for stim in plaid_stims:
    for s in plaid_stims[stim]:
        s.autoDraw = True
    nflips += 1
    print(stim)
    flip_time = timer.getTime()
    while now < nflips * 5:
        now = timer.getTime()
        plaid_stims[stim][1].phase = (0, speed * (now - start_time))
        
        win.flip()

    for s in plaid_stims[stim]:
        s.autoDraw = False

        

"""
while timer.getTime() > 0:
    now = timer.getTime()
    if now > 15:
        p.phase = (0, -speed * (now - start_time))
    win.flip()

    # key presses
    new_keys = current_keys
    key_pressed = kb.getKeys(['right', 'left', 'up', 'esc'], waitRelease=False, clear=False)
    keys = kb.getKeys(['right', 'left', 'up', 'esc'], waitRelease=True)
    for key in key_pressed:  # key pressed
        # print(key.name, key.rt)
        new_keys |= keycode[key.name] 
    for key in keys:  # key released
        # print(key.name, key.rt, key.duration)
        new_keys &= ~keycode[key.name] 
    if not current_keys == new_keys:
        current_keys = new_keys
        print('{:03b}'.format(current_keys))
"""
    
# for s in current_stims:
#    s.autoDraw = False

win.close()
# io.devices.tracker.setRecordingState(False)
# io.quit()