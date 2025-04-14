import time
import logging

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig

# commander.go_to(x, y, z, yaw, duration_s, relative)
# if Crazyflie is facing right, then relative coordinates
# are regular cartesian.

# commander.takeoff(height, duration)
# commander.land(height, duration)

# Turns on the LEDs.
def activate_led_bit_mask(scf):
    scf.cf.param.set_value('led.bitmask', 255)

# Turns off the LEDs.
def deactivate_led_bit_mask(scf):
    scf.cf.param.set_value('led.bitmask', 0)

# Flashes the LEDs for 2 seconds.
def light_check(scf):
    activate_led_bit_mask(scf)
    time.sleep(2)
    deactivate_led_bit_mask(scf)

# Makes the drone take off.
def take_off(scf):
    commander = scf.cf.high_level_commander

    # Tells commander to command take off.
    commander.takeoff(1.0, 2.0)
    time.sleep(3)

# Makes the drone land, and then stops the commander.
def land(scf):
    commander = scf.cf.high_level_commander

    # Tells commander to command landing.
    commander.land(0.0, 2.0)
    time.sleep(2)

    commander.stop()

# Takes off and then lands.
def hover_sequence(scf):
    take_off(scf)
    land(scf)

def test_trial(scf):
    distance = 2
    flight_time = 2

    commander = scf.cf.high_level_commander

    commander.go_to(distance, 0, 0, 3.1415, flight_time, relative=True)
    time.sleep(flight_time)

def start_logging(scf):
    log_conf1 = LogConfig(name='Position', period_in_ms=100)
    log_conf1.add_variable('stateEstimate.x', 'float')
    log_conf1.add_variable('stateEstimate.y', 'float')
    log_conf1.add_variable('stateEstimate.z', 'float')
    log_conf1.add_variable('pm.vbat', 'float')
    log_conf1.add_variable('pm.state', 'float')
    scf.cf.log.add_config(log_conf1)
    log_conf1.data_received_cb.add_callback(lambda _timestamp, data, _logconf: log_callback(scf.cf.link_uri, data))
    log_conf1.start()

def log_callback(uri, data):
    pos = []
    pos[0] = data['stateEstimate.x']
    pos[1] = data['stateEstimate.y']
    pos[2] = data['stateEstimate.z']
    print(f'URI={uri}, Position: x={pos[0]}, y={pos[1]}, z={pos[2]}, Battery={data["pm.vbat"]} V ({data["pm.state"]}%)')

# The URIs of the drones that are going to be flying.
uris = {
    'radio://0/80/2M/E7E7E7E7E4',
    'radio://0/80/2M/E7E7E7E7E7'
}

# Only output errors.
logging.basicConfig(level=logging.ERROR)

if __name__ == "__main__":
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache="./cache")

    lg_stab = LogConfig(name = "")

    with Swarm(uris, factory=factory) as swarm:
        # Executes light_check in parallel for all
        # drones in the swarm.
        print("Light check started.")
        swarm.parallel_safe(light_check)
        print("Light check completed.")

        # Resets the internal position estimator and waits
        # for its variance to drop below a certain threshold
        # in order to make sure the position estimations are accurate.
        print("Resetting estimators started.")
        swarm.reset_estimators()
        print("Estimators reset.")

        # Logs.
        swarm.parallel_safe(start_logging)

        swarm.parallel_safe(take_off)
        swarm.parallel_safe(test_trial)
        swarm.parallel_safe(land)