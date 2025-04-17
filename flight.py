import time
import logging
import math

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

# Makes the drone take off.
def take_off(scf):
    commander = scf.cf.high_level_commander

    # Tells commander to command take off.
    commander.takeoff(1.0, 2.0)
    time.sleep(3)

# Makes the drone land, and then stops the commander.
def land(scf):
    commander = scf.cf.high_level_commander

    # Tells commander to command landing.
    commander.land(0.0, 2.0)
    time.sleep(2)

    commander.stop()

# Takes off and then lands.
def hover_sequence(scf):
    take_off(scf)
    land(scf)

# Goes to a specified position with a certain speed. 
def go_to_relative_at_velocity(scf, parameters):
    commander = scf.cf.high_level_commander

    x = parameters[0]
    y = parameters[1]
    z = parameters[2]
    yaw = parameters[3]
    velocity = parameters[4]
    
    distance = math.sqrt(x * x + y * y + z * z)
    flight_time = distance / velocity

    commander.go_to(x, y, z, yaw, flight_time, relative=True)
    time.sleep(flight_time + 1.0)

def run_through_trials(scf, relative_pos, speeds):
    for speed in speeds:
        parameters = [relative_pos[0], relative_pos[1], 0, math.atan(relative_pos[1] / relative_pos[0]), speed]
        go_to_relative_at_velocity(scf, parameters)

        parameters = [-relative_pos[0], -relative_pos[1], 0, math.atan(relative_pos[1] / relative_pos[0]) + math.pi, speed]
        go_to_relative_at_velocity(scf, parameters)
