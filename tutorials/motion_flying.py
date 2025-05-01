import logging
import sys
import time
from threading import Event

# Imports simple_connect from the other python file for debugging purposes
# i.e. to see if the Crazyflie is actually connecting before doing anything else.
from connect_log_param import simple_connect

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

DEFAULT_HEIGHT = 1
BOX_LIMIT = 0.5

# Detects whether a deck is attached or not.
def detect_deck(scf, full_name):
    value = scf.cf.param.get_value(full_name, timeout=1)

    # Prints out the relevant debug message.
    if (value != 0):
        deck_attached_event.set()

def move_linear_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)
        mc.forward(1)
        time.sleep(1)
        mc.turn_left(180)
        time.sleep(1)
        mc.forward(1)
        time.sleep(1)

def take_off_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)
        mc.stop()

# Gets URI (as described in connect_log_param.py)
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')
# Creates an event for whether the deck is attached or not (idk how events work).
deck_attached_event = Event()
logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # simple_connect()
        
        # Arm the Crazyflie (told to do this in docs, don't know what exactly this does).
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        # Detects the desired deck.
        detect_deck(scf, "deck.bcLighthouse4")
        time.sleep(1.0)

        # Exits the program if the deck is not attached.
        if not deck_attached_event.wait(timeout=5):
            print('Deck is NOT detected!')
            sys.exit(1)
        else:
            print("Deck is attached!")

        move_linear_simple(scf)
