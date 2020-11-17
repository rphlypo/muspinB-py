from psychopy import visual, core, clock
from expsetup import win, kb, plaid

stim1, stim2 = plaid['Amb']
stim1.setAutoDraw(True)
stim2.setAutoDraw(True)

speed = 1  # pixels per second

timer = clock.CountdownTimer(start=1)
now = start_time = timer.getTime()
kb.clock.reset()  # when you want to start the timer

stim1.autoDraw = True
stim2.autoDraw = True
circ = visual.Circle(win, size=2.25, lineWidth=0, lineColor=win.color, fillColor=win.color, autoDraw=True)
circ = visual.Circle(win, size=2, units='pix', lineWidth=0, lineColor="red", fillColor="red", autoDraw=True)

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
    


win.close()