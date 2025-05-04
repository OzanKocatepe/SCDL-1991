import logging
import sys
import time
import threading

from logs import *
from flight import *

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

# Constants.
LOG_FOLDER = "./logs"
DISTANCE = 2.0

# Gets URI
URIS = [
    "radio://0/80/2M/E7E7E7E7E4", # LEADING DRONE
    "radio://1/60/2M/E7E7E7E7E6"  # TRAILING DRONE
]

# Only logs errors.
logging.basicConfig(level=logging.ERROR)

def main(uri: str) -> None:
    """This is the main code that will be run by each drone in each thread.
    
    Parameters:
        uri: str
            The URI of the drone currently being controlled.
    """

    # Initialises the drivers.
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Flashes the lights on the connected drone.
        LightCheck(scf)

        # Arms the Crazyflie.
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        # Detects the desired deck.
        DetectDeck(scf)

        HORIZONTAL_SEPARATION = 1.5     # (0.25, 0.5, 0.75, 1.0, 1.25, 1.5)
        VERTICAL_SEPARATION = 1.0       # (0, 0.25, 0.5, 0.75, 1.0)
        SPEED = 0.2                     # (0.2, 0.4, 0.6, 0.8, 1.0)

        # If the current drone is the leading drone,
        # gives it an extra height for vertical separation.
        if (uri == uri[0]):
            extraHeight = VERTICAL_SEPARATION
        else:
            extraHeight = 0

        # Runs the trial with the proper parameters.
        RunOneTrial(scf, LOG_FOLDER, DISTANCE, SPEED, HORIZONTAL_SEPARATION, extraHeight)
                
# Launch each Crazyflie in its own thread
threads = []

# Creates a thread for each drone. 
for uri in URIS:
    t = threading.Thread(target=main, args=(uri,))
    t.start()
    threads.append(t)

# Waits for all threads to complete.
for t in threads:
    t.join()