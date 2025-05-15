import logging
import time
import threading

from logs import *
from flight import *

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import reset_estimator

# Constants.
LARGE_BATTERY_FOLDER = "./350mAh_logs"
SMALL_BATTERY_FOLDER =  "./250mAh_logs"
LAP_FOLDER = "./lap_logs"
TEST_FOLDER = "./test_logs"
TRIAL_DISTANCE = 2.0 # The distance travelled by the leading drone when its 1.0m away from the trailing drone.

# Gets URI
URIS = [
    # "radio://1/80/2M/E7E7E7E7E4" # LEADING DRONE
    "radio://0/60/2M/E7E7E7E7E8"  # TRAILING DRONE
]

# Only logs errors.
logging.basicConfig(level=logging.ERROR)

# Initialises the drivers.
cflib.crtp.init_drivers()

# Stores the scf references.
scf = [SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) for uri in URIS]

# Opens the link to the Crazyflie
for s in scf:
    s.open_link()

# Stores the CommanderFlight references.
com = [CommanderFlight(s) for s in scf]

# Stores the trial parameters.
# horizontalSeparation = 1.0  # (1.0, 0.75, 0.5, 0.25)
# extraHeight = [0.25, 0]      # (0.75, 0.5, 0.25, 0)
# speed = 0.5                  # (0.5, 0.75, 1.0)
# distance = TRIAL_DISTANCE + (1.0 - horizontalSeparation)
# repetition = 0               # (0, 1, 2)

# Stores the initial X coordinate of the drones.
# Lighthouse and PositionHlCommander probably use different coordinate spaces, so I
# probably don't actually need these, but its nice to keep the two coordinate systems
# aligned.
# initialX = [-0.75, -1.5]

# Resets the estimators.
for s in scf:
    reset_estimator.reset_estimator(s)

# Sets the times for take off and movement.
referenceTime = time.time()
startTime = referenceTime + 7.0

speed = 0.5 # (0.5, 0.75, 1.0)
separation = 0.65 # (0.5, 0.65, 1.0)
takeOffHeight = [DEFAULT_HEIGHT + separation, DEFAULT_HEIGHT]
isLeading = [True, False]

# Launch each Crazyflie in its own thread
threads = []

# Creates a thread for each drone. 
for i in range(len(com)):
    # t = threading.Thread(target=RunOneTrial, args=(scf[i], initialX[i], LOG_FOLDER, distance, speed, horizontalSeparation, extraHeight[i], takeOffTime[i], movementTime, repetition))
    # t = threading.Thread(target=DiagnosticFlightSimple, args=(scf[i],))
    # t = threading.Thread(target=com[i].DiagnosticFlight, args=(TEST_FOLDER,))
    t = threading.Thread(target=com[i].Loop, args=(TEST_FOLDER, speed, takeOffHeight[i], startTime, separation, isLeading[i]))
    t.start()
    threads.append(t)
    time.sleep(2.0)

# Waits for all threads to complete.
for t in threads:
    t.join()

for s in scf:
    s.close_link()