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

from machine import Pin
from machine import Timer
import math
import time

NUM_PINS = 4
NUM_STEPS = 8
RADS_PER_SEC = 7.292115e-05
LENGTH_CM = 28.884 # fill in with precise measured value
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
    Pin(16, Pin.out), # D0
    Pin(5, Pin.out), # D1
    Pin(4, Pin.out), #D2
    Pin(14, Pin.out) #D5
]

MODE_PIN = Pin(13, Pin.out) #D7

STEPPER_SEQUENCE = [
    [1,0,0,1],
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1]
]

step_delta = 0
step_num = 0
total_seconds = 0.0
totalsteps  = 0
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
    return LENGTH_CM * RADS_PER_SEC/math.pow(math.cos(THETAO + RADS_PER_SEC * ts),2)

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
    pass
def setup():
    pass
def setup_timer():
    pass
def setup_gpio():
    for i in NUM_PINS:
        Pin(motorPins[i], Pin.OUT)
    all_pins_off()
    button = Pin(MODE_PIN, Pin.IN)
    button.irq(trigger=Pin.IRQ_FALLING, handler=toggle_mode)
    pass
def all_pins_off():
    for i in NUM_PINS:
        Pin(motorPins[i], Pin.low())

def toggle_mode():
    # We have several modes that we can toggle between with a button,
    # NORMAL, REWIND, and STOPPED.
    pass
def loop():
    pass