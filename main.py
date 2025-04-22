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
        # Executes light_check in parallel for all
        # drones in the swarm.
        print("Starting light check...")
        swarm.parallel_safe(LightCheck)
        print("Light check completed.")

        # Resets the internal position estimator and waits
        # for its variance to drop below a certain threshold
        # in order to make sure the position estimations are accurate.
        print("Resetting estimators...")
        swarm.reset_estimators()
        print("Estimators reset.")
        
        file_args = {
            uris[0]: (LOG_FOLDER + "/" + datetime.datetime.now() + ".csv",),
            # uris[1]: (LOG_FOLDER + "/" + "test.csv",)
        }

        # Sets up the logging config so that it outputs to the proper file.
        swarm.parallel_safe(StartLogging, args_dict=file_args)
        print("Logging started.")
        # time.sleep(2)

        args = {
            uris[0]: ((-1, 1), (1, 2)),
            # uris[1]: ((-1, 1), (1, 2))
        }

        swarm.parallel_safe(TakeOff)
        swarm.parallel_safe(RunThroughTrials, args_dict=args)
        swarm.parallel_safe(Land)