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
    RunThroughTrials:
        Performs a simple trial repeatedly with different speeds.
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

def GoToRelativePositionWithVelocity(scf, parameters):
    """Goes to a new position at a desired velocity.

    Parameters:
        parameters: list[float]
            A list of parameters given in the form
            [x, y, z, yaw, velocity] where the (x, y, z) position and yaw
            are relative to the drones current position. The velocity is
            m/s.
    """

    commander = scf.cf.high_level_commander

    # Extracts the parameters.
    x = parameters[0]
    y = parameters[1]
    z = parameters[2]
    yaw = parameters[3]
    velocity = parameters[4]
    
    # Calculates the distance to the point.
    distance = math.sqrt(x * x + y * y + z * z)
    # Using the distance and desired velocity, calculates the desired flight time.
    flight_time = distance / velocity

    commander.go_to(x, y, z, yaw, flight_time, relative=True)
    time.sleep(flight_time + 1.0)

def RunThroughTrials(scf, relative_pos, speeds):
    """Performs a trial with various speeds.

    Makes the Crazyflie fly the same path repeatedly with different speeds.

    Parameters:
        relative_pos: tuple[int]
            The position to fly the Crazyflie to (end point of each trial)
            relative to the initial position of the Crazyflie.
        speeds: tuple[int]
            The different speeds, in m/s, for the Crazyflie to iterate through.
    """
    # Loops through each speed.
    for speed in speeds:
        # Goes to the relative position with the desired parameters.
        parameters = [relative_pos[0], relative_pos[1], 0, math.atan(relative_pos[1] / relative_pos[0]), speed]
        GoToRelativePositionWithVelocity(scf, parameters)

        # Goes back to the initial position with the same positions.
        parameters = [-relative_pos[0], -relative_pos[1], 0, math.atan(relative_pos[1] / relative_pos[0]) + math.pi, speed]
        GoToRelativePositionWithVelocity(scf, parameters)
