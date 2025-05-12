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
    "radio://1/80/2M/E7E7E7E7E4", # LEADING DRONE
    "radio://0/60/2M/E7E7E7E7E8"  # TRAILING DRONE
]

# Only logs errors.
logging.basicConfig(level=logging.ERROR)

# Initialises the drivers.
cflib.crtp.init_drivers()

with SyncCrazyflie(URIS[0], cf=Crazyflie(rw_cache='./cache')) as scf1:
    with SyncCrazyflie(URIS[1], cf=Crazyflie(rw_cache='./cache')) as scf2:
        # Stores the scf references.
        scf = [scf1, scf2]

        for s in scf:
            # Resets the estimators.
            s.cf.param.set_value('kalman.resetEstimation', '1')
            time.sleep(0.5)
            s.cf.param.set_value('kalman.resetEstimation', '0')
            time.sleep(2.0)

        # Stores the trial parameters.
        horizontalSeparation = 1.0  # (1.0, 0.75, 0.5, 0.25)
        extraHeight = [0.75, 0]      # (0.75, 0.5, 0.25, 0)
        speed = 1.0                  # (0.5, 0.75, 1.0)
        distance = TRIAL_DISTANCE + (1.0 - horizontalSeparation)
        repetition = 2              # (0, 1, 2)

        # Stores the initial X coordinate of the drones.
        # Lighthouse and PositionHlCommander probably use different coordinate spaces, so I
        # probably don't actually need these, but its nice to keep the two coordinate systems
        # aligned.
        initialX = [-0.5, -1.5]

        # Sets the times for take off and movement.
        referenceTime = time.time()
        takeOffTime = [referenceTime, referenceTime]
        movementTime = takeOffTime[1] + 10.0

        # Launch each Crazyflie in its own thread
        threads = []

        # Creates a thread for each drone. 
        for i in range(len(URIS)):
            t = threading.Thread(target=RunOneTrial, args=(scf[i], initialX[i], LOG_FOLDER, distance, speed, horizontalSeparation, extraHeight[i], takeOffTime[i], movementTime, repetition))
            # t = threading.Thread(target=DiagnosticFlightSimple, args=(scf[i],))
            t.start()
            threads.append(t)
            time.sleep(2.0)

        # Waits for all threads to complete.
        for t in threads:
            t.join()