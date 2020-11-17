from psychopy import visual, core, clock
from expsetup import win, kb
from stims import circle, fix_point, plaid

stim1, stim2 = plaid['Amb']
current_stims = (stim1, stim2, circle, fix_point)
for s in current_stims:
    s.autoDraw = True

speed = 1  # pixels per second

timer = clock.CountdownTimer(start=1)
now = start_time = timer.getTime()
kb.clock.reset()  # when you want to start the timer


keycode = {'right': 1, 'up': 2, 'left':4}
current_keys = 0
new_keys = 0

while timer.getTime() > 0:
    now = timer.getTime()
    stim1.phase = (speed * (now - start_time)) % 1
    stim2.phase = (-speed * (now - start_time)) % 1
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
    
for s in current_stims:
    s.autoDraw = False

win.close()