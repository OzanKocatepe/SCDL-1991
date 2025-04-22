import time
import logging
import math

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

DEFAULT_HEIGHT = 1.5 # Default height to fly at.
DEFAULT_TIME = 2.0 # Default take-off or landing duration.
DEFAULT_DELAY = 2.0 # Default extra time to wait after giving the Crazyflie a command.

"""Stores the functions related to movement of the drone.

Methods:
    WaitForEstimators:
        Returns once the kalman estimators have been stabilized.
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

def WaitForEstimators(scf):
    """Waits for the estimators to converge before flying.
    """
    
    # Creates a 10 item list, with each item set to 100.
    # We will be using it as a queue.
    history = [1000] * 10

    config = LogConfig(name="Kalman", period_in_ms=100)
    config.add_variable("kalman.varPX", 'float')
    config.add_variable("kalman.varPY", 'float')

    # Continuously loops. We accept potentially an infinite loop because
    # it will only occur before the Crazyflies start flying, so it can't
    # cause any mid-air issues (which are our main safety concern).
    while True:
        # Gets the value of the kalman stabilizer.
        var_x = float(scf.cf.param.get_value('kalman.varPX'))
        var_y = float(scf.cf.param.get_value('kalman.varPY'))

        # Using history as a queue, appends the sum of the stabilizer
        # values to the end and pops the beginning of the list.
        history.append(var_x + var_y)
        history.pop(0)

        # Checks if the difference between the maximum and minimum of
        # the last 10 stabilizer values is less than 0.001.
        # If so, the stabilizer values must clearly have converged.
        if max(history) - min(history) < 0.001:
            break
        
        # Sleeps for 0.1 seconds so as to not overload the Crazyflie.
        time.sleep(0.1)

def TakeOff(scf):
    """Makes the drone take off.

    Takes off to a height of DEFAULT_HEIGHT in DEFAULT_TIME seconds.
    """

    commander = scf.cf.high_level_commander

    # Tells commander to command take off.
    commander.takeoff(DEFAULT_HEIGHT, DEFAULT_TIME)
    time.sleep(DEFAULT_TIME + DEFAULT_DELAY)
    
    # Hovers in the same position after take off.
    # For some reason, the drone likes it when you do this.
    commander.go_to(0.0, 0.0, 0.0, 0.0, 1.0, relative=True)
    time.sleep(1.0)

def Land(scf):
    """Makes the drone land.

    Tells the drone to descend to a height of 0 in DEFAULT_TIME seconds.
    The drone will land directly below wherever it is at the moment.
    The high-level commander will then be stopped.
    """

    commander = scf.cf.high_level_commander

    # Tells commander to command landing.
    commander.land(0.0, DEFAULT_TIME)
    time.sleep(DEFAULT_TIME + DEFAULT_DELAY)

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
        GoToRelativePositionWithVelocity(scf, position, orientation, speed)
        
        # Returns back to the initial position.
        position = (-relative_pos[0], -relative_pos[1], 0)
        GoToRelativePositionWithVelocity(scf, position, orientation + math.pi, speed)