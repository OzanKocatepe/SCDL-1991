import sys

from cflib.positioning.motion_commander import MotionCommander
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.crazyflie.high_level_commander import HighLevelCommander
from logs import *

DEFAULT_HEIGHT = 0.5
DEFAULT_TIME = 2.0
DEFAULT_DELAY = 5.0

"""Stores the functions related to movement of the drone.

Methods:
    DetectDeck:
        Checks whether the lighthouse deck is attached.
    DiagnosticFlightSimple:
        Takes off, pauses, then lands the drone immediately.
        This is used when a full diagnostic flight isn't necessary.
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

def DiagnosticFlightSimple(scf) -> None:
    """Takes off, pauses, then immediately lands the drone.
    """

    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(DEFAULT_DELAY)

def DiagnosticFlight(scf) -> None:
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


def RunOneTrial(scf, initialX, logFolder: str, distance: float, speed: float, horizontalSeparation: float, extraHeight: float, takeOffTime: float, movementTime: float, repetition: int) -> None:
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
        extraHeight: float
            The height above DEFAULT_HEIGHT to take off to.
        takeOffTime: float
            The time to wait until before taking off.
        movementTime: float
            The time to wait until before starting to move.
        repetition: int
            The repetition for this trial that is being completed.
            Only passed through so that it can be sent to the
            log file header.
    """

    # Waits until the take off time to take off.
    while ((waitTime := takeOffTime - time.time()) > 0):
        print(f"{scf.cf.link_uri} sleeping for {waitTime} seconds before taking off.")
        time.sleep(waitTime)

    # Takes off with motion commander to the desired height.
    # with MotionCommander(scf, default_height=DEFAULT_HEIGHT + extraHeight) as mc:
    # with PositionHlCommander(scf, x=initialX, y=0, z=0, default_height=DEFAULT_HEIGHT + extraHeight) as commander:
    commander = HighLevelCommander(scf)

    commander.takeoff(DEFAULT_HEIGHT + extraHeight, 3.0)

    # Pauses after taking off to stabilise.
    time.sleep(DEFAULT_DELAY)

    # Creates the required log file.
    logFile = CreateLogFile(logFolder, distance, speed, horizontalSeparation, extraHeight, repetition)

    # Starts logging.
    log = StartLogging(scf, logFile)
        
    # Waits until the start time to start moving.
    while ((waitTime := movementTime - time.time()) > 0):
        print(f"{scf.cf.link_uri} sleeping for {waitTime} seconds before moving.")
        time.sleep(waitTime)
        
    # Moves to the end of the trial.
    commander.go_to(initialX + distance, 0, DEFAULT_HEIGHT + extraHeight, yaw=0, duration_s = distance / speed)
    # commander.move_distance(distance, 0, 0, velocity=speed)
    time.sleep(distance / speed + 2.0)

    # Stops logging.
    log.stop()

    # Moves back to the beginning.
    # commander.go_to(initialX, 0, DEFAULT_HEIGHT + extraHeight, velocity=0.5)
    # time.sleep(distance / 0.5 + 2.0)

    commander.land(0, 3.0)