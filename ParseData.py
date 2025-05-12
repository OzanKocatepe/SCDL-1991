import csv
from typing import Tuple
import matplotlib.pyplot as plt

LOG_FOLDER = "./logs"
OUTPUT_FOLDER = "."

def LinearBatteryUsageFromFile(fileName: str) -> Tuple[list[float], list[float]]:
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

timestamps, batteryLevels = LinearBatteryUsageFromFile(LOG_FOLDER + "/2025-05-10-0.csv")
plt.plot(timestamps, batteryLevels, 'ro')
plt.show()