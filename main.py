import datetime
import time
import logging
import math

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

from logs import *
from flight import *

# The URIs of the drones that are going to be flying.
uris = [
    'radio://0/80/2M/E7E7E7E7E4',
    'radio://0/80/2M/E7E7E7E7E6'
]

# Only output errors.
logging.basicConfig(level=logging.ERROR)

# The folder in which to store the logs.
LOG_FOLDER = "./logs"

if __name__ == "__main__":
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache="./cache")

    with Swarm(uris, factory=factory) as swarm:
        # Executes LightCheck in parallel for all
        # drones in the swarm.
        print("Starting light check...")
        swarm.parallel_safe(LightCheck)
        print("Light check completed.\n")

        # Resets the internal position estimator and waits
        # for its variance to drop below a certain threshold
        # in order to make sure the position estimations are accurate.
        print("Resetting estimators...")
        swarm.reset_estimators()
        
        # Configures the estimators (see function for more detail)
        print("Configuring estimators...")
        swarm.parallel_safe(ConfigureEstimator)
        
        print("Estimators nominal.\n")
        
        relativePos = (-1 , 1) # Relative position to travel to in each trial.
        speeds = (0.2, 0.4, 0.6, 0.8, 1) # Speeds to iterate through.
        verticalSeperations = (0, 0.25, 0.5, 0.75, 1) # Vertical seperations to iterate through.
        horizontalSeperations = (0.25, 0.5, 0.75, 1, 1.25, 1.5) # Horizontal seperations to iterate through.

        # Loops through all of the horizontal seperations. Assumes the drones are placed
        # on the ground with a default horizontal seperation of 25cm.
        for horizSep in (0.25, 0.5):
            # If the current horizontal separation is not 0.25, we must move forward 0.25 units.
            if horizSep != 0.25:
                # Sets the arguments so that only the front drone moves.
                moveArgs = {
                    # URI: (distance,)
                    uris[0]: (0.25,),
                    uris[1]: (0,)
                }

                swarm.parallel_safe(MoveForward, args_dict=moveArgs)

            # Loops through all of the vertical seperations.
            for vertSep in (0, 0.25):
                speeds = (0.2, 0.4)
                # Dictionary contatining args.
                # Each URI entry corresponds to a tuple.
                # The elements of the tuple then correspond to each parameter of the
                # function being called.
                flightArgs = {
                    # URI: (relativePos, speeds, heightOffset, logFolder),
                    uris[0]: (relativePos, speeds, vertSep, LOG_FOLDER),
                    uris[1]: (relativePos, speeds, 0, LOG_FOLDER)
                }

                swarm.parallel_safe(FlyRouteWithDifferingSpeeds, args_dict=flightArgs)