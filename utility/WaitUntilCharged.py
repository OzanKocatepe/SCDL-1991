import datetime
import time
import logging
import math

from UtilityLogs import *

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

# The URIs of the drones that are going to be flying.
uris = [
    'radio://0/80/2M/E7E7E7E7E4',
    'radio://1/60/2M/E7E7E7E7E6',
    # 'radio://0/80/2M/E7E7E7E7E8'
]

# Only output errors.
logging.basicConfig(level=logging.ERROR)

if __name__ == "__main__":
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache="./cache")

    with Swarm(uris, factory=factory) as swarm:
        # Sets continuous to true in the logging function.
        args = {
            uris[0]: (True,),
            uris[1]: (True,),
            # uris[2]: (True,)
        }

        # Starts loggings battery levels.
        swarm.parallel_safe(StartLoggingBattery, args_dict=args)
        print("Logging started.")

        # Blocks the main program, when any input is given
        # the program exits.
        input()
        exit()