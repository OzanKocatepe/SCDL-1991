import datetime
import time

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
        Saves the drone data to a .csv every time a packet comes in.
    CreateLogFile:
        Creates the log file for a specific trial.
"""

def LightCheck(scf):
    """Turns the LEDS red for 2 seconds.
    """

    scf.cf.param.set_value('led.bitmask', 255)
    time.sleep(1.0)
    scf.cf.param.set_value('led.bitmask', 0)

def StartLogging(scf, logFile: str) -> LogConfig:
    """Tells the Crazyflie to start logging.

    Creates the desired log config and callback function and
    starts logging.

    Parameters:
        logFile: str
            The file that the logged data will be saved to.
            Assumes that the file already exists.

    Returns:
        LogConfig:
            The log config created in the function. This is returned
            so that the calling function can maintain a reference to
            the config in case it wants to stop logging.
    """

    # Defines our log configs.
    config = LogConfig(name='Pos, Vel & Battery', period_in_ms=100)

    # Adds the position variables.
    config.add_variable('stateEstimate.x', 'float')
    config.add_variable('stateEstimate.y', 'float')
    config.add_variable('stateEstimate.z', 'float')

    # Adds the velocity variables.
    config.add_variable('stateEstimate.vx', 'FP16')
    config.add_variable('stateEstimate.vy', 'FP16')
    config.add_variable('stateEstimate.vz', 'FP16')

    # Adds the battery as a voltage.
    config.add_variable('pm.vbat', 'float')

    # Adds the configs to the crazyflie.
    scf.cf.log.add_config(config)

    # Adds the callback functions and starts logging.
    config.data_received_cb.add_callback(lambda timestamp, data, _logconf: LogCallback(scf.cf.link_uri, timestamp, data, logFile))
    config.start()

    return config

def LogCallback(uri, timestamp, data, logFile: str):
    """Saves the data from the Crazyflie to a file. 

    This function is called every time a packet containing
    data is received from the Crazyflie. It saves the data
    into a .csv file.

    Parameters:
        logFile: str
            The file that the logged data will be saved to.
    """
    
    # Gets the position variables.
    # If a position retrieval fails and for some reason it doesn't throw an error, then
    # the position will be None.
    pos = [None, None, None]
    pos[0] = data['stateEstimate.x']
    pos[1] = data['stateEstimate.y']
    pos[2] = data['stateEstimate.z']

    # Gets the velocity variables.
    # If a velocity retrieval fails and for some reason it doesn't throw an error, then
    # the velocity will be None.
    vel = [None, None, None]
    vel[0] = data['stateEstimate.vx']
    vel[1] = data['stateEstimate.vy']
    vel[2] = data['stateEstimate.vz']

    # Opens the file in append mode.
    file = open(logFile, "a")

    # Writes to the file in csv form and then closes it.
    file.write(f'{timestamp},{uri},{pos[0]},{pos[1]},{pos[2]},{vel[0]},{vel[1]},{vel[2]},{data["pm.vbat"]}\n')
    file.close()

def CreateLogFile(logFile: str, distance: float, speed: float, horizontalSeparation: float, verticalSeparation: float):
    """Creates the log file for a specific trial.

    Parameters:
        logFile: str
            The file to create and set up the header in.
            Assumes the folder that the file is in already
            exists.
        distance: float
            The distance in m which the drone will travel during this trial.
        speed: float
            The speed in m/s that the drones will be travelling in this trial.
        horizontalSeparation: float
            The horizontal separation between the drones, in m.
        verticalSeparation.
            The vertical separation between the drones, in m.
    """

    file = open(logFile, 'a')
    file.write("timestamp,uri,x,y,z,vx,vy,vz,battery\n")
    file.write("==========================================\n")
    file.write(f"date: {str(datetime.date.today())}\n")
    file.write(f"time: {str(datetime.datetime.now().strftime('%H:%M:%S'))}\n")
    file.write(f"distance: {str(distance)}\n")
    file.write(f"verticalSeparation: {verticalSeparation}\n")
    file.write(f"horizontalSeparation: {horizontalSeparation}\n")
    file.write(f"velocity: {str(speed)}\n")
    file.write("==========================================\n")
    file.close()