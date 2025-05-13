import csv
from typing import Tuple
import matplotlib.pyplot as plt
from scipy import stats

LOG_FOLDER = "./350mAh_logs"
OUTPUT_FOLDER = "."

def LinearBatteryUsageFromFile(fileName: str) -> float:
    """Gets the rate of battery usage from a file.
    
    Assumes the battery usage is linear and fits a
    linear trendline to the data.
    
    Parameters:
        fileName: str
            The file to parse through.

    Returns:
        float:
            The gradient of the fitted trendline.
            This will have units of V/s.
    """

    slope = stats.linregress(timestamps, batteryLevels)
    return slope

def ExtractBatteryUsageFromFile(fileName: str) -> Tuple[list[float], list[float]]:
    """Extracts the battery usage data from a file.
    
    Parameters:
        fileName: str
            The file to parse through.

    Returns:
        Tuple[list[float], list[float]]:
            A tuple where
                the first entry contains the timestamps of the data and
                the second entry contains the batteryLevels at those corresponding
                timestamps.
    """

    # Opens the file in a csv dictionary.
    file = open(fileName, "r")
    csvFile = csv.DictReader(file)

    # Cuts off the header.
    for i in range(10):
        csvFile.__next__()

    # Gets the timestamp and battery level data.
    timestamps = []
    batteryLevels = []
    for line in csvFile:
       timestamps.append(int(line["timestamp"]))
       batteryLevels.append(float(line["batteryV"]))

    # Shifts the timestamps to start at 0.
    timestamps = [(time - timestamps[0]) for time in timestamps]

    return timestamps, batteryLevels

def CreateTrendline(x: list[float], y: list[float]) -> list[float]:
    """Creates a trendline given a set of input data.

    Parameters:
        x: list[float]
            The x-coordinates of the data.
        y: list[float]
            The y-coordinates of the data.
    
    Returns:
        list[float]:
            A list of the y-coordinates of the data
            when the input is the corresponding x-coordinate
            in the list.
    """

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    return [slope * t + intercept for t in x]

def ExtractHeaderFromFile(fileName: str) -> Tuple[float, float, float, bool]:
    """Extracts the relevant information from the header of a .csv file.
    
    Parameters:
        fileName: str
            The file to parse.
    
    Returns:
        Tuple[float, float, float, bool]:
            A tuple containing the velocity, horizontalSeparation, and
            verticalSeparation, and a boolean stating whether
            the drone was the leading drone.
    """

    file = open(fileName, "r")

    # Stores the lines as an array.
    lines = file.readlines()

    distance = 

def ExtractBatteryUsageFromFolder(folder: str) -> dict[list[float], float]:
    """Extracts the battery usage for each trial from a folder.

    Automatically averages all the trials for the same configuration
    in the folder.

    Parameters:
        folder: str
            The folder where the data is stored.
            Assumes the only thing in this folder is valid .csv files.

    Returns:
        dict[list[float], float]:
            A dictionary where the keys are a list of floats of the form
            [velocity, horizontalSeparation, verticalSeparation]
            and the values are the average battery usage for that
            configuration in V/s.
    """

    # Stores the averaged entries.
    output = {}
    # Stores the number of entries that have been averaged so far in each key.
    numEntries = {}

    