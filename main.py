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

MODE_PIN = Pin(13, Pin.IN)  # D7

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
next = 0
now = 0
last_toggle = 0
current_mode = NORMAL
autostop = True


def ypt(ts):
    # Bolt insertion rate in cm/s: y'(t)
    # Note, if you run this for ~359 minutes, it goes to infinity!!
    return LENGTH_CM * RADS_PER_SEC/math.pow(math.cos(THETAO + RADS_PER_SEC * ts), 2)


def step_motor():
    """
    This is the callback function that gets called when te timer
    expires. It moves the motor, updates lists, recomputes
    the step interval based on the current tangent error,
    and sets a new timer.
    """
    pass


def do_step(current_step):
    # apply a single step of the stepper motor on its pins.
    for i in NUM_PINS:
        if current_step[i] is 1:
            motorPins[i].value(1)
        else:
            motorPins[i].value(0)


def setup():
    setup_gpio()
    setup_timer()
    
    buttonUp = Pin(MODE_PIN)
    if not buttonUp:
        print("Manual REWIND")
        autostop = False
        current_mode = REWINDING


def setup_timer():
    machine.disable_irq()
    timer = Timer(2)
    timer.init(freq=1000)
    timer.callback(lambda t:step_motor())
    machine.enable_irq()


def setup_gpio():
    #all_pins_off()
    MODE_PIN.irq(trigger=Pin.IRQ_FALLING, handler=toggle_mode)


def all_pins_off(pin):
    for i in NUM_PINS:
        pin.value(0)


def toggle_mode():
    # We have several modes that we can toggle between with a button,
    # NORMAL, REWIND, and STOPPED.
    # Need to find replacement for ESP.getCycleCount();
    #if ESP.getCycleCount() - last_toggle < 0.2*CYCLES_PER_SECOND:
    #    return 
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


def loop():
    pass
