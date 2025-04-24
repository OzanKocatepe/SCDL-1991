import datetime
import logging
import math
import os

from logs import *

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

DEFAULT_HEIGHT = 1.5 # Default height to fly at.
DEFAULT_TIME = 3.0 # Default take-off or landing duration.
DEFAULT_DELAY = 2.0 # Default extra time to wait after giving the Crazyflie a command.

"""Stores the functions related to movement of the drone.

Methods:
    ConfigureEstimator:
        Sets the estimators to the kalman estimator and the best lighthouse quality.
    TakeOff:
        Makes the drone take off in place.
    Land:
        Makes the drone land directly below its current position.
    GoToRelativePositionWithVelocity:
        Goes to a position relative to the drone's current position
        with a desired velocity.
    FlyRouteWithDifferingSpeeds:
        Flies a straight-line route with a constant altitude
        repeatedly with different speeds.
"""

def ConfigureEstimator(scf):
    """Tells the drone to use the kalman estimator and the best lighthouse quality.
    """

    # Sets the kalman stabilizer.
    scf.cf.param.set_value('stabilizer.estimator', '2')
    time.sleep(0.1)
    scf.cf.param.set_value('lighthouse.method', '0')  # 0 = best quality
    time.sleep(0.1)


def TakeOff(scf, height: float=DEFAULT_HEIGHT, duration: float=DEFAULT_TIME):
    """Makes the drone take off.

    Takes off to a height of DEFAULT_HEIGHT in DEFAULT_TIME seconds.

    Parameters:
        height: float
            The height to take off to. Default value of DEFAULT_HEIGHT.
        duration: float
            The desired duration of the take-off. Default value of DEFAULT_TIME.
    """

    commander = scf.cf.high_level_commander

    # Tells commander to command take off.
    commander.takeoff(height, duration)
    time.sleep(duration + DEFAULT_DELAY)
    
    # Hovers in the same position after take off.
    # For some reason, the drone likes it when you do this.
    # Also rotates the drone to face forward during the trial.
    commander.go_to(0.0, 0.0, 0.0, 0.0, 1.0, relative=True)
    time.sleep(1.0)

def Land(scf, duration: int=DEFAULT_TIME):
    """Makes the drone land.

    Tells the drone to descend to a height of 0.
    The drone will land directly below wherever it is at the moment.
    The high-level commander will then be stopped.

    Parameters:
        duration: int
            The desired duration of the landing. Default value is DEFAULT_TIME.
    """

    commander = scf.cf.high_level_commander

    # Tells commander to command landing.
    commander.land(0.0, duration)
    time.sleep(duration + DEFAULT_DELAY)

    commander.stop()

def GoToRelativePositionWithVelocity(scf, position: tuple[float], yaw: float, velocity: float):
    """Goes to a new position at a desired velocity.

    Note: There is a 1.0 second delay after movement, so
    there will be a delay between repeated calls of this function
    in order to allow the crazyflie time to stabilise.

    Parameters:
        position: tuple[float]:
            The relative (x, y, z) coordinates to go to.
        yaw: float
            The amount of radians counterclockwise to rotate
            during the flight.
        velocity: float
            The desired velocity in m/s.
    """

    commander = scf.cf.high_level_commander

    # Extracts the position.
    x = position[0]
    y = position[1]
    z = position[2]
    
    # Calculates the distance to the point.
    distance = math.sqrt(x * x + y * y + z * z)
    # Using the distance and desired velocity, calculates the desired flight time.
    flight_time = distance / velocity

    commander.go_to(x, y, z, yaw, flight_time, relative=True)
    time.sleep(flight_time + DEFAULT_DELAY)

def FlyRouteWithDifferingSpeeds(scf, endPos: tuple[float], speeds: tuple[float], heightOffset: float, logFolder: str):
    """Moves the drone back and forth with varying speed.

    Moves the drone back and forth between two different points at the same altitude
    repeatedly with various speeds. The end point is given, and the beginning point is
    the initial position of the Crazyflie when this function is called.
    The drone should start on the ground when this funciton is called.
    It will take off at the beginning of each round trip, and land
    at the end of each round trip.

    Parameters:
        endPos: tuple[float]
            The (x, y) position to fly the Crazyflie to (end point of each trial)
            relative to the initial position of the Crazyflie.
        speeds: tuple[float]
            The different speeds, in m/s, for the Crazyflie to iterate through.
        heightOffset: float
            The height, in m, above DEFAULT_HEIGHT that the drone should take off to.
        logFolder: str
            The folder to store all of the logs in. If the folder doesn't exist, it will be created.
    """

    # Loops through each speed.
    for speed in speeds:
        # If the speed is greater than 1, we don't allow the speed to be used.
        if speed > 1:
            print(f"Specified speed of {speed} is over 1 m/s. Speed skipped.")
            continue
        
        # Makes the drone take off.
        TakeOff(scf, height=DEFAULT_HEIGHT + heightOffset)

        # If the log folder doesn't exist, we create it.
        if (not os.path.isdir(logFolder)):
            os.mkdir(logFolder)

        # Sets up the log file for this trial.
        logFile = logFolder + "/" + str(datetime.datetime.now()) + ".csv"
        CreateLogFile(logFile, endPos, speed, heightOffset, 0)

        # Starts logging to the log file.
        logConfig = StartLogging(scf, logFile)

        # Gets the desired position and orientation.
        position = (endPos[0], endPos[1], 0)
        # orientation = math.atan(endPos[1] / endPos[0])

        # Goes to the position.
        GoToRelativePositionWithVelocity(scf, position, 0, speed)

        # Stops logging.
        logConfig.stop()
        
        # Returns back to the initial position.
        position = (-endPos[0], -endPos[1], 0)
        GoToRelativePositionWithVelocity(scf, position, 0, 0.2)

        # Lands the drone and stops logging.
        Land(scf)

def MoveForward(scf, distance: float):
    """Moves the drone forward some distance.

    The "forward" direction is defined as moving
    along the straight line path all the trials take,
    in the direction of the end point.
    The drone will take off, move, and then land.

    Parameters:
        distance: float
            The distance to move forward, in meters.
    """
    # If the distance to move is zero, just skip the rest of the function.
    if (abs(distance) < 0.001):
        return
    
    TakeOff(scf)
    # Moves slowly to the new position.
    GoToRelativePositionWithVelocity(scf, (-distance / math.sqrt(2), distance / math.sqrt(2)), 0, 0.2)
    Land(scf)