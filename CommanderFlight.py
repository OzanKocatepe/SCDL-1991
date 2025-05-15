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
        DiagnosticFlight:
            Makes the drone take off, hover, and then land.
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
        distanceMagnitude = math.sqrt(distance[0]**2 + distance[1]**2 + distance[2]**2)
        initialPosition = [self.x, self.y, self.z]
        
        flightSteps = int(10 * distanceMagnitude / velocity)
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
        """Makes the drone take off, hover, and land.

        logFolder: str
            The path to the log folder to output to.
        """

        logFile = logs.CreateSimpleLogFile(logFolder)
        logs.StartLogging(self, logFile, 1000) # Speed at 1000 so that the error is never printed to console
        time.sleep(0.2) # Pauses to let the log data update the position.

        self.TakeOff()
        self.Hover(5.0)
        self.Land()

    def Loop(self, logFolder: str, speed: float, height: float, startTime: float, separation: float, isLeading: bool) -> None:
        """Makes the drone do laps around the system.
        
        Parameters:
            logFolder: str
                The folder to save the log to.
            speed: float
                The speed for the drone to move at.
            height: float
                The height for this drone to take off to.
            startTime: float
                The time for both drones to initially start moving.
            separation: float
                The vertical and horizontal separation between the drones in m.
            isLeading: bool
                Whether the current drone is leading or not.
        """

        # Defines the range of the box.
        xRange = [-1, 1]
        yRange = [-1, 1]
        # Defines the corners of the box.
        corners = [(xRange[0], yRange[0]), (xRange[1], yRange[0]), (xRange[1], yRange[1]), (xRange[0], yRange[1])]

        # Changes the start and end positions of each leg depending on whether the drone
        # is leading or trailing.
        if (isLeading):
            # Start slightly ahead of the corner.
            startCoordinates = [(corners[0][0] + separation, corners[0][1]),
                                (corners[1][0], corners[1][1] + separation),
                                (corners[2][0] - separation, corners[2][1]),
                                (corners[3][0], corners[3][1] - separation)]
            # End on the corners.
            endCoordinates = [corners[1], corners[2], corners[3], corners[0]]
        else:
            # Start on the corner.
            startCoordinates = corners
            # End slightly behind the corners.
            endCoordinates = [(corners[1][0] - separation, corners[1][1]),
                              (corners[2][0], corners[2][1] - separation),
                              (corners[3][0] + separation, corners[3][1]),
                              (corners[0][0], corners[0][1] + separation)]

        # Creates the log file.
        logFile = logs.CreateSimpleLogFile(logFolder)
        logs.StartLogging(self, logFile, speed)

        # Takes off and hovers to stabilise.
        self.TakeOff(height)
        self.Hover(DEFAULT_DELAY)
        self.MoveToPosition([startCoordinates[0][0], startCoordinates[0][1], height], 0.5)
        self.Hover(DEFAULT_DELAY)

        # Hovers in place until the start time.
        while (startTime - time.time()) > 0:
            self.Hover(0.1)

        # Loops as long as the drone has enough battery.
        cornerIndex = 0
        # while (self.batV >= 3.4):
        for i in range(2):
            # Moves to the end position.
            position = [ endCoordinates[cornerIndex][0], endCoordinates[cornerIndex][1], height]
            self.MoveToPosition(position, velocity=speed)
            self.Hover(DEFAULT_DELAY)

            # Updates the corner index.
            cornerIndex += 1
            if (cornerIndex == 4):
                cornerIndex = 0

            # Moves to the next start position.
            position = [ startCoordinates[cornerIndex][0], startCoordinates[cornerIndex][1], height]
            self.MoveToPosition(position, velocity=speed)
            self.Hover(DEFAULT_DELAY)

        # Lands when the battery is too low.
        self.Land() 