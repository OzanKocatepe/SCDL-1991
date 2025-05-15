from flight import DEFAULT_HEIGHT, DEFAULT_TIME, DEFAULT_DELAY
import logs
import math
import time

class CommanderFlight:
    """Contains the functions for controlling a Crazyflie using
    the commander interface.

    Attributes:
        scf: SyncCrazyflie
            The crazyflie that the instance controls.
        commander:
            The commander of this instance's crazyflie.
        x: float
            The x-position of the drone.
        y: float
            The y-position of the drone.
        z: float
            The z-position of the drone.
        vx: float
            The velocity in the x-direction of the drone.
        vy: float
            The velocity in the y-direction of the drone.
        vz: float
            The velocity in the z-direction of the drone.
        batV: float
            The battery level in volts.
    
    Methods:
        UpdateState:
            Updates the attributes of the instance.
        TakeOff:
            Makes the drone take off.
        Land:
            Makes the drone land.
        MoveToPosition:
            Moves the drone to a position at a certain velocity.
        Hover:
            Makes the drone hover in place.
        Loop:
            Makes the drone do laps around a square path
            until it drops below 20% battery.
    """
    
    def __init__(self, scf):
        """Initialises a CommanderFlight object.
        """

        self.scf = scf
        self.commander = scf.cf.commander
        self.x = 0
        self.y = 0
        self.z = 0
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.batV = 0
        self.batP = 0

    def UpdateState(self, position: list[float], velocity: list[float], batV: float, batP: float) -> None:
        """Updates the attributes of the CommanderFlight instance.
        
        Parameters:
            position: list[float]
                The position as an [x, y, z] list.
            velocity: list[float]
                The velocity as an [vx, vy, vz] list.
            batV: float
                The battery of the drone in volts.
            batP: float
                The battery of the drone as a percentage.
        """

        self.x = position[0]
        self.y = position[1]
        self.z = position[2]

        self.vx = velocity[0]
        self.vy = velocity[1]
        self.vz = velocity[2]

        self.batV = batV
        self.batP = batP

    def TakeOff(self, height: float=DEFAULT_HEIGHT, time_s: float=DEFAULT_TIME, yaw: float=0) -> None:
        """Makes the drone take off.

        Uses the commander.

        Parameters:
            height: float
                The height in meters to take off to.
            time_s: float
                The time in seconds that takeoff should take.
            yaw: float
                The direction relative to the positive x-axis
                that the drone should be facing in during take off.
        """

        steps = int(time_s * 10)
        # Loops through the steps, each step should take 0.1 seconds
        # since the commands other than .sleep are negligible.
        for i in range(1, steps + 1):
            currentHeight = height * (i / steps)
            self.commander.send_position_setpoint(self.x, self.y, currentHeight, yaw)
            time.sleep(0.1)

    def Land(self, time_s: float=DEFAULT_TIME) -> None:
        """Lands the drone at its current coordinates.
        
        Parameters:
            time_s: float
                The duration of the landing in seconds.
        """

        steps = int(time_s * 10)
        height = self.z
        for i in range(steps, 2, -1):
            currentHeight = height * (i / steps)
            self.commander.send_position_setpoint(self.x, self.y, currentHeight, 0)
            time.sleep(0.1)

    def MoveToPosition(self, position: list[float], velocity: float, yaw: float=0) -> None:
        """Moves to a new position at a desired velocity.

        Moves the drone at the desired velocity by giving it updated
        positions to move to every 0.1 seconds. The velocity
        will vary slightly around (usually above) the desired value
        since the drone is not being given direct velocity inputs,
        since these cause the drone to drift from its position.
        
        Parameters:
            position: list[float]
                The position in world coordinates [x, y, z] in m.
            velocity: float
                The speed at which to travel in m/s.
            yaw: float
                The yaw of the drone during the movement.
        """

        distance = [ position[0] - self.x, position[1] - self.y, position[2] - self.z ]
        initialPosition = [self.x, self.y, self.z]
        
        flightSteps = int(10 * distance / velocity)
        for i in range(flightSteps):
            newX = initialPosition[0] + (i * distance[0] / flightSteps)
            newY = initialPosition[1] + (i * distance[1] / flightSteps)
            newZ = initialPosition[2] + (i * distance[2] / flightSteps)
            self.commander.send_position_setpoint(newX, newY, newZ, yaw)
            time.sleep(0.1)
    
    def Hover(self, time_s: float, yaw: float=0) -> None:
        """Hovers in place for the allotted time.

        Parameters:
            time_s: float
                The time to hover for in seconds.
            yaw: float
                The yaw of the drone during the hovering.
        """

        pos = [self.x, self.y, self.z]

        hoverTime = time.time() + time_s
        while ((waitTime := hoverTime - time.time()) > 0):
            self.commander.send_position_setpoint(pos[0], pos[1], pos[2], yaw)
            time.sleep(0.1)

    def DiagnosticFlight(self, logFolder: str):
        """Makes the drone take off, move forward, and land.

        logFolder: str
            The path to the log folder to output to.
        """

        logFile = logs.CreateSimpleLogFile(logFolder)
        logs.StartLogging(self, logFile, 1000) # Speed at 1000 so that the error is never printed to console
        time.sleep(0.2) # Pauses to let the log data update the position.

        self.TakeOff()
        self.Hover(5.0)
        self.Land()

    def Loop(self, logFolder: str, speed: float) -> None:
        """Makes the drone do laps around the system.
        
        Parameters:
            logFolder: str
                The folder to save the log to.
            speed: float
                The speed for the drone to move at.
        """

        cornerCoordinates = [(-1.5, -1), (1.5, -1), (1.5, 1), (-1.5, 1)]

        # Creates the log file.
        logFile = logs.CreateSimpleLogFile(logFolder)
        logs.StartLogging(self, logFile, speed)

        # Takes off and hovers to stabilise.
        self.TakeOff()
        self.Hover(DEFAULT_DELAY)

        # Loops as long as the drone has enough battery.
        cornerIndex = 0
        # while (self.batP >= 20):
        for i in range(4):
            position = [ cornerCoordinates[cornerIndex][0], cornerCoordinates[cornerIndex][1], self.z]
            self.MoveToPosition(position, velocity=speed)
            cornerIndex += 1
            self.Hover(DEFAULT_DELAY)

        # Lands when the battery is too low.
        self.Land() 