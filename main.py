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

LOG_FOLDER = "./logs"

# Gets URI
URIS = [
    "radio://0/80/2M/E7E7E7E7E4",
    "radio://1/60/2M/E7E7E7E7E6"
]

# Only logs errors.
logging.basicConfig(level=logging.ERROR)

def main(uri):
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Flashes the lights on the connected drone.
        LightCheck(scf)

        # Arm the Crazyflie.
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        # Detects the desired deck.
        DetectDeck(scf)

        DiagnosticFlight(scf)

        # Loops through the possible speeds.
        # for speed in (0.2):
        #     RunOneTrial(scf, 2.0, speed, LOG_FOLDER)
        #     time.sleep(DEFAULT_DELAY)
            
        #     block = input("Continue? ")
        #     if (block != "y"):
        #         exit()
    
# Launch each Crazyflie in its own thread
threads = []
    
for uri in URIS:
    t = threading.Thread(target=main, args=(uri,))
    t.start()
    threads.append(t)

# Wait for all threads to complete
for t in threads:
    t.join()