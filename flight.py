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

    # Defines the height we are going to take off to.
    height = DEFAULT_HEIGHT + extraHeight

    # Waits until the take off time to take off.
    while ((waitTime := takeOffTime - time.time()) > 0):
        print(f"{scf.cf.link_uri} sleeping for {waitTime} seconds before taking off.")
        time.sleep(waitTime)

    # Gets a reference to the commander.
    commander = scf.cf.commander

    # Creates the required log file.
    logFile = CreateLogFile(logFolder, distance, speed, horizontalSeparation, extraHeight, repetition)

    # If this is the leading drone,
    # it will move back.
    if (initialX > -1.0):
        newX = -1.5 + horizontalSeparation
    # If this is the trailing drone,
    # it will stay in place.
    else:
        newX = initialX

    # Takes off to the desired height.
    print(f"{scf.cf.link_uri} taking off at {time.time()}...")
    steps = 30
    for i in range(1, steps + 1):
        currentHeight = height * (i / steps)
        commander.send_position_setpoint(initialX, 0, currentHeight, 0)
        time.sleep(0.1)

    # Hovers in place to stabilise.
    print(f"{scf.cf.link_uri} hovering at {time.time()}...")
    for y in range(30):
        commander.send_position_setpoint(initialX, 0, height, 0)
        time.sleep(0.1)

    # Continue hovering or moves back, depending on which drone it is. 
    print(f"{scf.cf.link_uri} moving to {newX} at {time.time()}...")
    for y in range(30):
        commander.send_position_setpoint(newX, 0, height, 0)
        time.sleep(0.1)

    # Hovers in place until the movement time.
    print(f"{scf.cf.link_uri} waiting to move at {time.time()}...")
    while ((waitTime := movementTime - time.time()) > 0):
        commander.send_position_setpoint(newX, 0, height, 0)
        time.sleep(0.1)

    # Starts logging.
    log = StartLogging(scf, logFile, speed)

    # Moves forward the desired distance at the desired speed.
    print(f"{scf.cf.link_uri} moving forward at time {time.time()}...")
    
    # Uses velocity inputs.
    # flightTime = time.time() + (distance / speed)
    # while ((waitTime := flightTime - time.time()) > 0):
    #     # print(f"{scf.cf.link_uri} currently flying.")
    #     commander.send_hover_setpoint(speed, 0, 0, height)
    #     time.sleep(0.1)        

    # Uses position inputs.
    flightDuration = 10 * distance / speed
    for i in range(int(flightDuration)):
        x = newX + (i * distance / flightDuration)
        commander.send_position_setpoint(x, 0, height, 0)
        time.sleep(0.1)

    # Stops logging.
    log.stop()

    # Hovers for 5 seconds at the desired position.
    print(f"{scf.cf.link_uri} hovering at time {time.time()}...")
    hoverTime = time.time() + 5.0
    while ((waitTime := hoverTime - time.time()) > 0):
        commander.send_position_setpoint(newX + distance, 0, height, 0)
        # commander.send_hover_setpoint(0, 0, 0, DEFAULT_HEIGHT + extraHeight)
        time.sleep(0.1)

    # Moves back to the beginning.
    print(f"{scf.cf.link_uri} moving back to beginning at {time.time()}...")
    flightTime = time.time() + (distance / 1.0)
    while ((waitTime := flightTime - time.time()) > 0):
        commander.send_position_setpoint(initialX, 0, height, 0)
        time.sleep(0.1)        

    # Lands the drone.
    print(f"{scf.cf.link_uri} landing at {time.time()}...")
    steps = 30
    for i in range(steps, 2, -1):
        currentHeight = height * (i / steps)
        commander.send_position_setpoint(initialX, 0, currentHeight, 0)
        time.sleep(0.1)