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
    LogCallback:
        Saves each packet of data to the desired file."""

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

    log_config = LogConfig(name='Position & Battery', period_in_ms=100)

    # Adds the position variables.
    log_config.add_variable('stateEstimate.x', 'float')
    log_config.add_variable('stateEstimate.y', 'float')
    log_config.add_variable('stateEstimate.z', 'float')

    # Adds the velocity variables.
    log_config.add_variable('stateEstimate.vx', 'float')
    log_config.add_variable('stateEstimate.vy', 'float')
    log_config.add_variable('stateEstimate.vz', 'float')

    # Adds the battery variables (pm.vbat is battery voltage, pm.state is battery %).
    log_config.add_variable('pm.vbat', 'float')
    # log_config.add_variable('pm.batteryLevel', 'float')
    
    scf.cf.log.add_config(log_config)

    # Adds the callback function and starts logging.
    log_config.data_received_cb.add_callback(lambda _timestamp, data, _logconf: LogCallback(scf.cf.link_uri, data, log_file))
    log_config.start()

def LogCallback(uri, data, log_file):
    """Saves the data from the Crazyflie to a file. 

    This function is called every time a packet is received from the Crazyflie.
    It saves the data into a .csv file.

    Parameters:
        log_file: str
            The file that the logged data will be saved to.
    """

    # Gets the positions variables.
    # If a position retrieval fails and for some reason it doesn't throw an error, then
    # the position will be None.
    pos = [None, None, None]
    pos[0] = data['stateEstimate.x']
    pos[1] = data['stateEstimate.y']
    pos[2] = data['stateEstimate.z']

    velocity = [None, None, None]
    velocity[0] = data['stateEstimate.vx']
    velocity[1] = data['stateEstimate.vy']
    velocity[2] = data['stateEstimate.vz']
    
    # If the file doesn't exist, we will create it
    # and then create the header row.
    try:
        file = open(log_file, "x")
        file.close()
        file = open(log_file, "w")
        file.write("URI,x,y,z,vx,vy,vz,batV\n")
    # If the file already exists, we will simply append to it.
    except:
        file = open(log_file, "a")

    # Writes to the file in csv form and then closes it.
    file.write(f'{uri},{pos[0]},{pos[1]},{pos[2]},{velocity[0]},{velocity[1]},{velocity[2]},{data["pm.vbat"]}\n')
    file.close()