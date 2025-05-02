import logging
import sys
import time
from threading import Event

from logs import *
from flight import *

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

LOG_FOLDER = "./logs"

# Gets URI
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')

# Only logs errors.
logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Flashes the lights on the connected drone.
        LightCheck(scf)
        time.sleep(1.0)

        # Arm the Crazyflie (told to do this in docs, don't know what exactly this does).
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        # Detects the desired deck.
        DetectDeck(scf)

        # Loops through the possible speeds.
        for speed in (0.2, 0.4, 0.6, 0.8, 1.0):
            RunOneTrial(scf, 1.0, speed)
            time.sleep(DEFAULT_DELAY)