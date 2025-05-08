import logging
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
TRIAL_DISTANCE = 2.0 # The distance travelled by the leading drone when its 1.0m away from the trailing drone.

# Gets URI
URIS = [
    "radio://0/60/2M/E7E7E7E7E6", # LEADING DRONE
    "radio://1/80/2M/E7E7E7E7E4"  # TRAILING DRONE
]

# Only logs errors.
logging.basicConfig(level=logging.ERROR)

# Initialises the drivers.
cflib.crtp.init_drivers()

with SyncCrazyflie(URIS[0], cf=Crazyflie(rw_cache='./cache')) as scf1:
    with SyncCrazyflie(URIS[1], cf=Crazyflie(rw_cache='./cache')) as scf2:
        # Stores the scf references.
        scf = [scf1, scf2]
        
        # Manually sets the start pos.
        startPos = [ [-0.31, 0, 0.12], [-1.47, 0.01, -0.09] ]

        for s in scf:
            s.cf.param.set_value('kalman.resetEstimation', '1')
            time.sleep(0.5)
            s.cf.param.set_value('kalman.resetEstimation', '0')
            time.sleep(2)

        # Stores the trial parameters.
        horizontalSeparation = 1.0  # (1.0, 0.75, 0.5, 0.25)
        extraHeight = [0.75, 0]      # (0.75, 0.5, 0.25, 0)
        speed = 0.5                 # (0.5, 0.75, 1.0)
        distance = TRIAL_DISTANCE + (1.0 - horizontalSeparation)
        repetition = 2              # (0, 1, 2)

        # Sets the times for take off and movement.
        referenceTime = time.time()
        takeOffTime = [referenceTime, referenceTime + 5.0]
        movementTime = takeOffTime[1] + 10.0

        # Launch each Crazyflie in its own thread
        threads = []

        # Creates a thread for each drone. 
        for i in range(len(URIS)):
            t = threading.Thread(target=RunOneTrial, args=(scf[i], LOG_FOLDER, distance, speed, horizontalSeparation, extraHeight[i], takeOffTime[i], movementTime, repetition))
            # t = threading.Thread(target=DiagnosticFlightSimple, args=(scf[i],))
            t.start()
            threads.append(t)

        # Waits for all threads to complete.
        for t in threads:
            t.join()