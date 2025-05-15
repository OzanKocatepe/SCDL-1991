from CommanderFlight import CommanderFlight
import datetime
import os
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

def StartLogging(com: CommanderFlight, logFile: str, speed: float, threshold: float=0.1) -> LogConfig:
    """Tells the Crazyflie to start logging.

    Creates the desired log config and callback function and
    starts logging.

    Parameters:
        com: CommanderFlight
            An instance of CommanderFlight linked to a Crazyflie.
        logFile: str
            The file that the logged data will be saved to.
            Assumes that the file already exists.
        speed: float
            The speed this trial is meant to be at. Prints
            an error to the console if this speed is passed by more than
            the threshold.
        threshold: float
            A float from 0 to 1 which determines how far above the target
            velocity the drone can go before printing an error to the console.
            10% by default.

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
    # Adds the battery as a percentage.
    config.add_variable('pm.batteryLevel', 'FP16')

    # Adds the configs to the crazyflie.
    com.scf.cf.log.add_config(config)

    # Adds the callback functions and starts logging.
    config.data_received_cb.add_callback(lambda timestamp, data, _logconf: LogCallback(com, timestamp, data, logFile, speed, threshold))
    config.start()

    return config

def LogCallback(com: CommanderFlight, timestamp, data, logFile: str, speed: float, threshold: float) -> None:
    """Saves the data from the Crazyflie to a file. 

    This function is called every time a packet containing
    data is received from the Crazyflie. It saves the data
    into a .csv file.

    Parameters:
        com: CommanderFlight
            The instance of CommanderFlight that the drone is connected to.
        logFile: str
            The file that the logged data will be saved to.
        speed: float
            The speed this trial is meant to be at. Prints
            an error to the console if this speed is passed by more than
            the threshold.
        threshold: float
            A float from 0 to 1 which determines how far above the target
            velocity the drone can go before printing an error to the console.
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

    # Prints an error to the console if the speed in the x-direction is too high.
    if (vel[0] >= speed * (1 + threshold)):
        print(f"WARNING: {com.scf.cf.link_uri} is travelling at {vel[0]} m/s!")

    # Prints an error to the console if the battery level is too low.
    # if (data["pm.vbat"] < 3.5):
    #     print(f"WARNING: {uri} is at battery level {data['pm.vbat']}.")

    # Opens the file in append mode.
    file = open(logFile, "a")

    # Writes to the file in csv form and then closes it.
    file.write(f'{timestamp},{com.scf.cf.link_uri},{pos[0]},{pos[1]},{pos[2]},{vel[0]},{vel[1]},{vel[2]},{data["pm.vbat"]},{data["pm.batteryLevel"]}\n')
    com.UpdateState(pos, vel, data["pm.vbat"], data["pm.batteryLevel"])
    file.close()

def CreateLogFile(logFolder: str, distance: float, speed: float, horizontalSeparation: float, extraHeight: float, repetition: int) -> str:
    """Creates the log file for a specific trial.

    Parameters:
        logFolder: str
            The folder to create the log file in.
        distance: float
            The distance in m which the drone will travel during this trial.
        speed: float
            The speed in m/s that the drones will be travelling in this trial.
        horizontalSeparation: float
            The horizontal separation between the drones, in m.
        extraHeight: float
            The height above DEFAULT_HEIGHT that the drone is taking off to. 
        repetition: int
            The repetition currently being done for this trial (combination of parameters).

    Returns:
        The path to the newly created log file.
    """

    # Determines how many files have already been created today
    # so that it can accurately set the index in the log file's name.
    filesToday = 0
    logFile = f"{logFolder}/{str(datetime.date.today())}-{filesToday}.csv"
    while (os.path.exists(logFile)):
        filesToday += 1
        logFile = f"{logFolder}/{str(datetime.date.today())}-{filesToday}.csv"

    # Creates the file or appends data to an already
    # existing file and writes the header to the file.
    # We choose to append instead of overwrite so that if the code
    # above breaks and we write to a file that already exists, we don't
    # lose the data stored within that file.
    file = open(logFile, 'a')
    file.write("timestamp,uri,x,y,z,vx,vy,vz,batteryV,battery%\n")
    file.write("==========================================\n")
    file.write(f"date: {str(datetime.date.today())}\n")
    file.write(f"time: {str(datetime.datetime.now().strftime('%H:%M:%S'))}\n")
    file.write(f"distance: {str(distance)}\n")
    file.write(f"velocity: {str(speed)}\n")
    file.write(f"horizontalSeparation: {horizontalSeparation}\n")
    file.write(f"heightAboveDefault: {extraHeight}\n")
    file.write(f"trial: {repetition}\n")
    file.write("==========================================\n")
    file.close()

    return logFile