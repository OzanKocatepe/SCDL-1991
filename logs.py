import time
import logging

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

"""Stores all the functions for logging.

Contains the functions for logging, data collection,
and any other methods related to communicating with the drones.

Methods:
    LightCheck:
        Turns the LEDs red for 2 seconds.
    StartLogging:
        Tells the Crazyflie to begin logging the required variables.
    PosAndBatCallback:
        Saves each packet of position and battery
        data to the desired file.
    VelCallback:
        Saves each packet of velocity data
        to the desired file.
"""

def LightCheck(scf):
    """Turns the LEDS red for 2 seconds.
    """

    scf.cf.param.set_value('led.bitmask', 255)
    time.sleep(2)
    scf.cf.param.set_value('led.bitmask', 0)

def StartLogging(scf, log_file):
    """Tells the Crazyflie to start logging.

    Creates the desired log config and callback function and
    starts logging.

    Parameters:
        log_file: str
            The file that the logged data will be saved to.
    """

    # Creates the log file.    
    file = open(log_file, "w")
    file.write("timestamp,URI,(x,y,z, batV) or (vx, vy, vz)\n")
    file.close()
    
    # Defines our log configs.
    posBatConfig = LogConfig(name='Position & Battery', period_in_ms=100)
    velConfig = LogConfig(name="Velocity", period_in_ms=100)

    # Adds the position variables.
    posBatConfig.add_variable('stateEstimate.x', 'float')
    posBatConfig.add_variable('stateEstimate.y', 'float')
    posBatConfig.add_variable('stateEstimate.z', 'float')

    # Adds the velocity variables.
    velConfig.add_variable('stateEstimate.vx', 'float')
    velConfig.add_variable('stateEstimate.vy', 'float')
    velConfig.add_variable('stateEstimate.vz', 'float')

    # Adds the battery as a voltage.
    posBatConfig.add_variable('pm.vbat', 'float')

    # Adds the configs to the crazyflie.
    scf.cf.log.add_config(posBatConfig)

    # Adds the callback functions and starts logging.
    posBatConfig.data_received_cb.add_callback(lambda timestamp, data, _logconf: PosAndBatCallback(scf.cf.link_uri, timestamp, data, log_file))
    posBatConfig.start()

    velConfig.data_received_cb.add_callback(lambda timestamp, data, _logconf: VelCallback(scf.cf.link_uri, timestamp, data, log_file))
    velConfig.start()

def PosAndBatCallback(uri, timestamp, data, log_file):
    """Saves the position and battery data from the Crazyflie to a file. 

    This function is called every time a packet containing position and battery
    data is received from the Crazyflie. It saves the data into a .csv file.

    Parameters:
        log_file: str
            The file that the logged data will be saved to.
    """

    # Gets the position variables.
    # If a position retrieval fails and for some reason it doesn't throw an error, then
    # the position will be None.
    pos = [None, None, None]
    pos[0] = data['stateEstimate.x']
    pos[1] = data['stateEstimate.y']
    pos[2] = data['stateEstimate.z']
    
    # Opens the file in append mode.
    file = open(log_file, "a")

    # Writes to the file in csv form and then closes it.
    file.write(f'{timestamp},{uri},{pos[0]},{pos[1]},{pos[2]},{data["pm.vbat"]}\n')
    file.close()

def VelCallback(uri, timestamp, data, log_file):
    """Saves the velocity data from the Crazyflie to a file. 

    This function is called every time a packet containing velocity
    data is received from the Crazyflie. It saves the data into a .csv file.

    Parameters:
        log_file: str
            The file that the logged data will be saved to.
    """

    # Gets the velocity variables.
    # If a velocity retrieval fails and for some reason it doesn't throw an error, then
    # the velocity will be None.
    vel = [None, None, None]
    vel[0] = data['stateEstimate.vx']
    vel[1] = data['stateEstimate.vy']
    vel[2] = data['stateEstimate.vz']
    
    # Opens the file in append mode.
    file = open(log_file, "a")

    # Writes to the file in csv form and then closes it.
    file.write(f'{timestamp},{uri},{vel[0]},{vel[1]},{vel[2]}\n')
    file.close()