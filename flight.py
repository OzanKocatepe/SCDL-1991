import sys

from cflib.positioning.motion_commander import MotionCommander
from logs import *

DEFAULT_HEIGHT = 0.5
DEFAULT_DELAY = 5.0

"""Stores the functions related to movement of the drone.

Methods:
    DetectDeck:
        Checks whether the lighthouse deck is attached.
    DiagnosticFlight:
        Runs a simple test flight to confirm the drone is fully operational.
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

def DiagnosticFlight(scf):
    """Does a simple test flight to confirm the drone is fully operational.
    """

    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(DEFAULT_DELAY)
        mc.forward(1)
        time.sleep(DEFAULT_DELAY)
        mc.up(0.5)
        time.sleep(DEFAULT_DELAY)
        mc.turn_right(180)
        time.sleep(DEFAULT_DELAY)
        mc.forward(1)
        time.sleep(DEFAULT_DELAY)
        mc.down(0.5)
        time.sleep(DEFAULT_DELAY)
        mc.turn_left(180)
        time.sleep(DEFAULT_DELAY)


def RunOneTrial(scf, logFolder: str, distance: float, speed: float, horizontalSeparation: float, verticalSeparation: float, startTime: float) -> None:
    """Runs a single trial with the given parameters.

    A single trial consists of taking off, beginning logging,
    moving to the end of the trial, ending logging, moving
    back to the beginning, and then landing.

    Parameters:
        logFolder: str
            The folder to store the file in which all the trial data will be logged.
        distance: float
            The distance in meters to move forward. i.e.
            the length of the trial.
        speed: float
            The speed in m/s to travel at (only in the
            forward direction, the backwards direction is always
            0.2 m/s).
        horizontalSeparation: float
            The horizontal separation between the drones in this trial.
            Only given to this function to pass forward to the log file upon creation.
        verticalSeparation: float
            The height above DEFAULT_HEIGHT to take off to.
        startTime: float
            The time to wait until before starting to move.
    """

    # Takes off with motion commander to the desired height.
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT + verticalSeparation) as mc:
        # Pauses after taking off to stabilise.
        time.sleep(DEFAULT_DELAY)

        # Creates the required log file.
        CreateLogFile(logFolder, distance, speed, horizontalSeparation, verticalSeparation)

        # Starts logging.
        log = StartLogging(scf, logFile)

        # Waits until the start time to start flying.
        waitTime = startTime - time.time()
        while (waitTime > 0):
            time.sleep(waitTime)
        
        # Moves to the end of the trial.
        mc.forward(distance, velocity=speed)
        time.sleep(DEFAULT_DELAY)

        # Moves back to the beginning.
        mc.back(distance, velocity=0.2)
        time.sleep(DEFAULT_DELAY)

        # Stops logging.
        log.stop()