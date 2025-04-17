import logging
import time

# For connecting to the Crazyflie
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

# For logging (synchronous)
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

# Used to connect and disconnect from the crazyflie.
# Mostly for testing that the connection works.
def simple_connect():
    print("Yeah, I'm connected! :D")
    time.sleep(3)
    print("Now I will disconnect :'(")

# Used to log data from the Crazyflie asynchronously.
def simple_log_async(scf, logconf):
    cf = scf.cf
    # Adds logging configuration to the logging framework - will return an error if the
    # desired variables don't exist.
    cf.log.add_config(logconf)

    # Adds the callback function to the logging framework.
    logconf.data_received_cb.add_callback(log_stab_callback)
    
    # Manually starts and stops the log config.
    logconf.start()
    time.sleep(5)
    logconf.stop()

# Prints out the desired parameter.
def param_stab_est_callback(name, value):
    print("The crazyflie has parameter " + name + " set at number: " + value)

# Receives parameters from the Crazyflie asynchronously
def simple_param_async(scf, groupstr, namestr):
    cf = scf.cf
    full_name = groupstr + "." + namestr
    
    # Sets the callback function which will print out changes to the parameters.
    cf.param.add_update_callback(group=groupstr, name=namestr, cb=param_stab_est_callback)
    
    # Updates the given parameter and then resets it.
    # NOTE: Changed parameters remain changed until the Crazyflie is completely turned off and on.
    # So if you only want a parameter to change temporarily, ideally change it back before the program disconnects
    # to avoid future issues.
    time.sleep(1)
    cf.param.set_value(full_name, 2)
    time.sleep(1)
    cf.param.set_value(full_name, 1)
    time.sleep(1)

# Prints the contents of the given log variables.
def log_stab_callback(timestamp, data, logconf):
    print("[%d][%s]: %s" % (timestamp, logconf.name, data))

# Used to log data from the Crazyflie.
# scf: SyncCrazyflie instance
# logconf: logging configuration
def simple_log(scf, logconf):
    with SyncLogger(scf, lg_stab) as logger:
        # Prints out the entry in the logger.
        for log_entry in logger:
            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2]

            print("[%d][%s]: %s" % (timestamp, logconf_name, data))

            # Remove this break line if you want the logging to print continuously.
            # This just makes it so it prints one entry and then stops to not clog up
            # terminal.
            break

# URI to the Crazyflie to connect to (found using cfclient and a USB cable).
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E6')
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

# something something main function
if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    # Add the variables we would like to read out from the crazyflie.
    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10) # period_in_ms likely how often to read the data.
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    # Group name and parameter name to deal with.
    # i.e. it looks for stabilizer.estimator in the Crazyflie.
    group = "stabilizer"
    name = "estimator"

    # Connect to the Crazyflie?
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # simple_log_async(scf, lg_stab)
        simple_param_async(scf, group, name) 