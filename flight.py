import time
import logging
import math

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

DEFAULT_HEIGHT = 1.0
DEFAULT_TIME = 2.0

"""Stores the functions related to movement of the drone.

Methods:
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

def TakeOff(scf):
    """Makes the drone take off.

    Takes off to a height of DEFAULT_HEIGHT in DEFAULT_TIME seconds.
    """

    commander = scf.cf.high_level_commander

    # Tells commander to command take off.
    commander.takeoff(DEFAULT_HEIGHT, DEFAULT_TIME)
    time.sleep(DEFAULT_TIME)

def Land(scf):
    """Makes the drone land.

    Tells the drone to descend to a height of 0 in DEFAULT_TIME seconds.
    The drone will land directly below wherever it is at the moment.
    The high-level commander will then be stopped.
    """

    commander = scf.cf.high_level_commander

    # Tells commander to command landing.
    commander.land(0.0, DEFAULT_TIME)
    time.sleep(DEFAULT_TIME)

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
    time.sleep(flight_time + 1.0)

def FlyRouteWithDifferingSpeeds(scf, relative_pos: tuple[float], speeds: tuple[float]):
    """Moves the drone back and forth with varying speed.

    Moves the drone back and forth between two different points at the same altitude
    repeatedly with various speeds. The end point is given, and the beginning point is
    the initial position of the Crazyflie when this function is called.

    Parameters:
        relative_pos: tuple[float]
            The (x, y) position to fly the Crazyflie to (end point of each trial)
            relative to the initial position of the Crazyflie.
        speeds: tuple[float]
            The different speeds, in m/s, for the Crazyflie to iterate through.
    """

    # Loops through each speed.
    for speed in speeds:
        # Gets the desired position and orientation.
        position = (relative_pos[0], relative_pos[1], 0)
        orientation = math.atan(relative_pos[1] / relative_pos[0])

        # Goes to the position.
        GoToRelativePositionWithVelocity(scf, newPosition, math.atan(relative_pos[1] / relative_pos[0]), speed)
        # Returns back to the initial position.
        GoToRelativePositionWithVelocity(scf, -position, orientation + math.pi, speed)