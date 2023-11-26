"""
 Skytracker by Nick Touran for ESP8266 and Stepper Motors
 Port by Jon Saul <jonsaul@puppetmaster.lol>
 This accelerates the motor to correct the tangent error. It can rewind too!

 Motors are 28BYJ-48 5V + ULN2003 Driver Board from Amazon
 Hook up power and ground and then hook inputs 1-4 up to GPIO pins. 
 
 See Also: http://www.raspberrypi-spy.co.uk/2012/07/stepper-motor-control-in-python/
 This motor has a 1:64 gear reduction ratio and a stride angle of 5.625 deg (1/64th of a circle). 
 
 So it takes 64*64 = 4096 single steps for one full rotation, or 2048 double-steps.
 with 3 ms timing, double-stepping can do a full rotation in 2048*0.003 =  6.144 seconds 
 so that's a whopping 1/6.144 * 60 = 9.75 RPM. But it has way more torque than I expected. 
  
 Can get 2ms timing going with double stepping on ESP8266. Pretty fast!
 Should power it off of external 5V. 
 
 Shaft diameter is 5mm with a 3mm inner key thing. Mounting holes are 35mm apart.  """

import machine
from machine import Pin
from machine import Timer
import math
import time

NUM_PINS = 4
NUM_STEPS = 8
RADS_PER_SEC = 7.292115e-05
LENGTH_CM = 28.884  # fill in with precise measured value
# For theta zero, I used relative measurement between two boards w/ level.
# Got 0.72 degrees, which is 0.012566 radians
THETAO = 0.012566
ROTATIONS_PER_CM = 7.8740157
DOUBLESTEPS_PER_ROTATION = 2048.0
CYCLES_PER_SECOND = 80000000

# Modes
NORMAL = 0
REWINDING = 1
STOPPED = 2

motorPins = [
    Pin(14, Pin.OUT),  # D5
    Pin(12, Pin.OUT),  # D6
    Pin(13, Pin.OUT),  # D7
    Pin(15, Pin.OUT)  # D8
]

MODE_PIN = Pin(5, Pin.IN)  # D1

STEPPER_SEQUENCE = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

step_delta = 0
step_num = 0
total_seconds = 0.0
totalsteps = 0
step_interval_s = 0.001
current_step = 0
nxt = 0
now = 0
last_toggle = 0
current_mode = NORMAL
autostop = True
timer = Timer(1)

def ypt(ts):
    # Bolt insertion rate in cm/s: y'(t)
    # Note, if you run this for ~359 minutes, it goes to infinity!!
    return LENGTH_CM * RADS_PER_SEC/math.pow(math.cos(THETAO + RADS_PER_SEC * ts), 2)


def step_motor(pin):
    """
    This is the callback function that gets called when te timer
    expires. It moves the motor, updates lists, recomputes
    the step interval based on the current tangent error,
    and sets a new timer.
    """
    global total_seconds
    global step_num 
    global step_delta
    global totalsteps
    global nxt
    global now
    if current_mode == NORMAL:
        step_interval_s = 1.0/(ROTATIONS_PER_CM*ypt(total_seconds)*2*DOUBLESTEPS_PER_ROTATION)
        step_delta = 1
        step_num %= len(STEPPER_SEQUENCE)
        #return
    elif current_mode == REWINDING:
        step_interval_s = 0.0025
        step_delta = -2 
        if(step_num<0):
            step_num += len(STEPPER_SEQUENCE)
        #return
    elif current_mode == STOPPED:
        step_interval_s = 0.2
        #return
    else:
        print("we should never be here")

    if current_mode != STOPPED:
        total_seconds += step_interval_s
        current_step = STEPPER_SEQUENCE[step_num]
        do_step(current_step)
        step_num += step_delta
        totalsteps += step_delta
    now = time.time()
    nxt = now+step_interval_s*CYCLES_PER_SECOND-(now-nxt);
    timer.init(mode=Timer.ONE_SHOT, period=4, callback=step_motor) 

def _debounce(pin):
    cur_value = pin.value()
    active = 0
    while active < 20:
        if pin.value() != cur_value:
            active += 1
        else:
            active = 0
        time.sleep(1.0)

def do_step(current_step):
    # apply a single step of the stepper motor on its pins.
    for i in range(NUM_PINS):
        if current_step[i] is 1:
            motorPins[i].value(1)
        else:
            motorPins[i].value(0)


def setup():
    setup_gpio()
    setup_timer()
    
    if MODE_PIN.value():
        print("Manual REWIND")
        autostop = False
        current_mode = REWINDING


def setup_timer():
    print("setting up timer")
    irq = machine.disable_irq()
    timer.init(freq=1000, callback=step_motor)
    #timer.callback(lambda t:step_motor())
    machine.enable_irq(irq)


def setup_gpio():
    print("setup_gpio() called")
    all_pins_off()
    print("setting button press callback to toggle_mode")
    MODE_PIN.irq(trigger=Pin.IRQ_FALLING, handler=toggle_mode)


def all_pins_off():
    for i in range(len(motorPins)):
        motorPins[i].value(0)


def toggle_mode(pin):
    # We have several modes that we can toggle between with a button,
    # NORMAL, REWIND, and STOPPED.
    # Need to find replacement for ESP.getCycleCount();
    #if ESP.getCycleCount() - last_toggle < 0.2*CYCLES_PER_SECOND:
    #    return 
    _debounce(MODE_PIN)
    print("got a button press")

    if current_mode is REWINDING:
        print("STOPPING")
        current_mode = STOPPED
        all_pins_off()
        if not autostop:
            step_num = 0
            total_seconds = 0
            totalsteps = 0
            autostop = True
    elif current_mode is NORMAL:
        print("REWINDING")
        current_mode = REWINDING
    else:
        print("RESTARTING")
        current_mode = NORMAL
    last_toggle = 0# FIND REPLACEMENT FOR ESP.getCycleCount();
        
    pass

setup()
while True:
    time.sleep(0.05)
    if current_mode == REWINDING:
        if(totalsteps<1 and autostop):
            print("Ending the rewind and stopping")
            current_mode = STOPPED
            all_pins_off()
            total_seconds = 0.0