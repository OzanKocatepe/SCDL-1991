import time
import logging

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

"""Contains the utility logging functions.

The functions contained here are used for logging, but only for
specific utility usecases, such as checking current position while
on the ground, checking battery levels while charging, etc.
These are not used for any actual trials.

Methods:
    StartLoggingBattery:
        Creates and applies the log config for battery levels.
    BatteryCallback:
        Prints any battery data to the console.
"""

def StartLoggingBattery(scf, continuous=False):
    """Tells the Crazyflie to start logging battery levels.

    Creates the desired log config and callback function and
    starts logging.
    """

    # Creates the config.
    if (continuous):
        interval = 2000
    else:
        interval = 500
    config = LogConfig(name="Battery", period_in_ms=interval)

    # Adds the battery as a voltage.
    config.add_variable('pm.vbat', 'float')
    # Adds the battery as a percentage.
    config.add_variable('pm.batteryLevel', 'float')

    # Adds the configs to the crazyflie.
    scf.cf.log.add_config(config)

    # Adds the callback functions and starts logging.
    config.data_received_cb.add_callback(lambda timestamp, data, _logconf: BatteryCallback(scf.cf.link_uri, data, config, continuous))
    config.start()

def BatteryCallback(uri, data, config, continuous=False):
    """Outputs the battery data to the console.

    This function is called every time a packet containing battery
    data is received from the Crazyflie. It outputs the data to the console.
    """

    print(f'{uri},{data["pm.vbat"]},{data["pm.batteryLevel"]}')
    
    if (data["pm.vbat"] > 4.0 and continuous):
            config.stop()
            print(f"{uri} finished charging.")