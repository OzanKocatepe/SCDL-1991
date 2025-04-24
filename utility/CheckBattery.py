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
    # 'radio://0/80/2M/E7E7E7E7E4',
    'radio://0/80/2M/E7E7E7E7E6',
]

# Only output errors.
logging.basicConfig(level=logging.ERROR)

if __name__ == "__main__":
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache="./cache")

    with Swarm(uris, factory=factory) as swarm:
        # Starts loggings battery levels.
        swarm.parallel_safe(StartLoggingBattery)
        print("Logging started.")
        time.sleep(2)