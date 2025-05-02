import sys

from cflib.positioning.motion_commander import MotionCommander
from logs import *

DEFAULT_HEIGHT = 1.0
DEFAULT_DELAY = 3.0

"""Stores the functions related to movement of the drone.

Methods:
    DetectDeck:
        Checks whether the lighthouse deck is attached.
    RunOneTrial:
        Runs a single trial with the desired parameters
        (distance, speed, and height).
"""

def DetectDeck(scf) -> None:
    """Detects whether the lighthouse deck is attached.
    """

    value = scf.cf.param.get_value("deck.bcLighthouse4", timeout=1)
    time.sleep(1.0)
    
    # If the deck isn't attached, exits the program.
    if (value == 0):
        sys.exit(1)
    else:
        print("Deck attached.")

def RunOneTrial(scf, distance: float, speed: float, height: float=DEFAULT_HEIGHT) -> None:
    """Runs a single trial with the given parameters.

    A single trial consists of taking off, beginning logging,
    moving to the end of the trial, ending logging, moving
    back to the beginning, and then landing.

    Parameters:
        distance: float
            The distance in meters to move forward. i.e.
            the length of the trial.
        speed: float
            The speed in m/s to travel at (only in the
            forward direction, the backwards direction is always
            0.2 m/s).
        height: float
            The height to take off to. By default takes off
            to DEFAULT_HEIGHT.
    """

    # Takes off with motion commander to the desired height.
    with MotionCommander(scf, default_height=height) as mc:
        # Pauses after taking off to stabilise.
        time.sleep(DEFAULT_DELAY)

        # Creates the required log file.
        logFile = logFolder + "/" + str(datetime.datetime.now()) + ".csv"
        CreateLogFile(logFile, 0, speed, 0, 0) # Need to fix this part, actually put correct values.

        # Starts logging.
        log = StartLogging(scf, logFile)
        
        # Moves to the end of the trial.
        mc.forward(distance, speed)
        time.sleep(DEFAULT_DELAY)

        # Moves back to the beginning.
        mc.back(distance, speed=0.2)
        time.sleep(DEFAULT_DELAY)

        # Stops logging.
        log.stop()