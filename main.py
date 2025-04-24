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
    # 'radio://0/80/2M/E7E7E7E7E6'
    # 'radio://0/80/2M/E7E7E7E7E7'
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
        
        # Dictionary contatining args.
        # Each URI entry corresponds to a tuple.
        # The elements of the tuple then correspond to each parameter of the
        # function being called.
        flightArgs = {
            # URI: (relative_pos, speeds, logFolder),
            uris[0]: ((-1, 1), (0.2, 0.4), LOG_FOLDER),
        }

        swarm.parallel_safe(TakeOff)
        swarm.parallel_safe(FlyRouteWithDifferingSpeeds, args_dict=flightArgs)
        time.sleep(3.0)
        swarm.parallel_safe(Land)