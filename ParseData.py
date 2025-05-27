import os
import csv
from typing import Tuple
import matplotlib.pyplot as plt
from scipy import stats
import statistics

LOG_FOLDER = "./350mAh_logs"
OUTPUT_FOLDER = "./plots"

MIN_VOLTAGE = 3.0
MAX_VOLTAGE = 4.2

def ExtractBatteryUsageRateFromFile(fileName: str) -> float:
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

    timestamps, batteryLevels = ExtractBatteryUsageDataFromFile(fileName)

    slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, batteryLevels)
    return slope

def ExtractBatteryUsageDataFromFile(fileName: str) -> Tuple[list[float], list[float]]:
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
    timestamps = [(time - timestamps[0]) / 1000.0 for time in timestamps]

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

def GetRSquared(x: list[float], y: list[float]) -> float:
    """Gets the R^2 value of a linear regression.
    
    Parameters
        x: list[float]
            The x-coordinates of the data.
        y: list[float]
            The y-coordinates of the data.

    Returns:
        float:
            The R^2 value of the linear regression.
    """

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    return r_value**2

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

    velocity = lines[5].split(":")
    velocity = float(velocity[1])

    horizontalSeparation = lines[6].split(":")
    horizontalSeparation = float(horizontalSeparation[1])

    verticalSeparation = lines[7].split(":")
    verticalSeparation = float(verticalSeparation[1])

    heightAboveDefault = lines[8].split(":")
    heightAboveDefault = float(heightAboveDefault[1])

    # Determines whether the drone was leading or trailing based on its extra vertical height.
    if (heightAboveDefault == 0.0):
        leading = False
    else:
        leading = True
    
    trialNum = lines[9].split(":")
    trialNum = int(trialNum[1])

    return velocity, horizontalSeparation, verticalSeparation, leading, trialNum

def ExtractBatteryUsageFromFolder(folder: str, percentage: bool=False, minVoltage: float=MIN_VOLTAGE, maxVoltage: float=MAX_VOLTAGE) -> dict[tuple[float, float, float, bool], float]:
    """Extracts the battery usage for each trial from a folder.

    Automatically averages all the trials for the same configuration
    in the folder.

    Parameters:
        folder: str
            The folder where the data is stored.
            Assumes the only thing in this folder is valid .csv files.
        percentage: bool
            Determines whether to return the rates in V/s or %/s.
        minVoltage: float
            The voltage corresponding to a fully uncharged battery.
        maxVoltage: float
            The voltage corresponding to a fully charged battery.

    Returns:
        dict[list[float, float, float, bool], (float, float)]:
            A dictionary where
                the keys are a list of floats of the form
                [velocity, horizontalSeparation, verticalSeparation, leading] and
                
                the values are a tuple containing the mean battery usage for
                that configuration in V/s or %/s, and the variance of that configuration.
    """

    # Stores the list of the battery rates in each configuration.
    batteryRates = {}

    for file in os.listdir(folder):
        vel, horiz, vert, leading, trialNum = ExtractHeaderFromFile(folder + "/" + file)
        key = (vel, horiz, vert, leading)

        rate = ExtractBatteryUsageRateFromFile(folder + "/" + file)
        # If desired, we convert from V/s to %/s.
        if (percentage):
            rate = rate * 100 / (maxVoltage - minVoltage)

        # If we've already seen this entry before, append it to the
        # corresponding list.
        if key in batteryRates.keys():
            batteryRates[key].append(rate)
        else:
            # Otherwise, create a list with the rate in it.
            batteryRates[key] = [rate,]

    # Turns each list in the dictionary into a tuple
    # containing the (mean, std. dev.) of the original list.
    for key in batteryRates.keys():
        currentList = batteryRates[key]
        mean = statistics.mean(currentList)
        stddev = statistics.stdev(currentList)
        batteryRates[key] = (mean, stddev)

    return batteryRates

def FilterDronePositions(rates: dict[tuple[float, float, float, bool], float], filterLeading: bool) -> dict[tuple[float, float, float, bool], float]:
    """Filters out all of the leading or trailing drone data.
    
    Parameters:
        rates: dict[tuple[float, float, float, bool], float]
            A dict where the keys are tuples containing the
            (velocity, horizontalSeparation, verticalSeparation, isLeading)
            and the corresponding values are the battery consumption rates.
        filterLeading: bool
            If true, leaves only the leading drones.
            If false, leaves only the trailing drones.

    Returns:
        dict[tuple[float, float, float, bool], float]
            The data give in "rates" with only the leading
            or trailing drones remaining.
    """

    output = {}

    # Loops through every key in the dictionary.
    for key in rates.keys():
        # If we want the leading drones and
        # this is a leading drone, add it to output.
        if (key[3] and filterLeading):
            output[key] = rates[key]

        # If we want trailing drones and this
        # is a trailing drone, add it to the output.
        elif (not key[3] and not filterLeading):
            output[key] = rates[key]

    return output

def SaveBatteryPlotToFolder(fileName: str, outputFolder: str, convertToPercentage: bool=True, minVoltage: float=MIN_VOLTAGE, maxVoltage: float=MAX_VOLTAGE) -> None:
    """Plots the battery level over time and saves it to a folder.

    Parameters:
        fileName: str
            The name of the file containing the battery data.
        outputFolder: str
            The folder to save the plot to.
        convertToPercentage: bool
            Whether to plot the battery level in percentage or volts.
        minVoltage: float
            The voltage corresponding to a fully uncharged battery.
        maxVoltage: float
            The voltage corresponding to a fully charged battery.
    """
    
    # Extracts the data from the file.
    timestamps, batteryLevels = ExtractBatteryUsageDataFromFile(fileName)
    
    # Converts the voltages to percentages if desired.
    if (convertToPercentage):
        batteryLevels = [(bat - minVoltage) / (maxVoltage - minVoltage) for bat in batteryLevels]

    # Gets the trendline data.
    trendlineBatteryLevels = CreateTrendline(timestamps, batteryLevels)

    # Gets the file label.
    vel, hSep, vSep, isLead, trialNum = ExtractHeaderFromFile(fileName)

    # Determines the next valid file name.
    outputFileName = f"({vel}, {hSep}, {vSep}, {isLead})-{trialNum}"

    # Plots the curve.
    plt.plot(timestamps, batteryLevels, 'o', color="black", markersize=3)
    # Plots the trendline.
    plt.plot(timestamps, trendlineBatteryLevels, color="red")

    # Writes the title and axis labels.
    # plt.title(f"Vel={vel}, hSep={hSep}, vSep={vSep}, isLead={isLead}, trialNum={trialNum}")
    plt.xlabel("Time (s)")
    if convertToPercentage:
        plt.ylabel("Battery Charge (%)")
    else:
        plt.ylabel("Battery Charge (V)")

    # Saves the figure to the output folder.
    plt.savefig(outputFolder + "/" + outputFileName + ".png")
    plt.clf()

def PlotBatteryFromFolder(folderName: str, outputFolder: str, convertToPercentage: bool=True, minVoltage: float=MIN_VOLTAGE, maxVoltage: float=MAX_VOLTAGE) -> None:
    """Plots the battery level over time of all the trial files in a folder.
    
    Parameters:
        folderName: str
            The name of the folder to parse through.
        outputFolder: str
            The folder to save the plot to.
        convertToPercentage: bool
            Whether to plot the battery level in percentage of volts.
        minVoltage: float
            The voltage corresponding to a fully uncharged battery.
        maxVoltage: float
            The voltage corresponding to a fully charged battery.
    """ 

    for file in os.listdir(folderName):
        SaveBatteryPlotToFolder(folderName + "/" + file, outputFolder, convertToPercentage, minVoltage, maxVoltage)

def ReplaceLineInFile(fileName: str, lineNumber: int, text: str) -> None:
    """Replaces a line in a file with the desired text.
    
    Used once to fix the header files of old trials that weren't originally used.
    Not currently used in any code, left here for transparency and bookkeeping.
    
    Parameters:
        fileName: str
            The name of the file to use.
        lineNumber: int
            The line (indexed from 1) to replace.
        text: str
            The text to replace the line with, *without* a newline character at the end.
    """

    file = open(fileName, 'r')
    lines = file.readlines()
    file.close()

    if (lineNumber > len(lines)):
        print(f"Error, file {fileName} does not have line {lineNumber}")
        exit()

    lines[lineNumber - 1] = text + "\n"

    file = open(fileName, 'w')
    for line in lines:
        file.write(line)

def DetermineMinAndMaxFromFolder(folderName: str) -> tuple[float, float]:
    """Determines the minimum and maximum battery voltage that occurs in a folder of .csv files.
    
    Parameters:
        folderName: str
            The path to the folder to parse through.
    
    Returns:
        tuple(float, float):
            Returns the min and max in a tuple of floats.
    """

    mins = []
    maxs = []

    # Loops through the files in the folder.
    for file in os.listdir(folderName):
        # Gets the min and max battery level in volts from the file.
        timestamps, batteryLevels = ExtractBatteryUsageDataFromFile(f"{folderName}/{file}")
        mins.append(min(batteryLevels))
        maxs.append(max(batteryLevels))

    # Returns the overall min and max.
    return min(mins), max(maxs)

def PlotBatteryConsumptionTable(convertToPercentage: bool, logFolder: str=LOG_FOLDER, outputFolder: str=OUTPUT_FOLDER,ncludeBarChart: bool=False) -> None:
    """Plots the battery consumption values as a table from a folder.
    
    Parameters:
        convertToPercentage: bool
            Whether to use percentages or volts.
        logFolder: str
            The folder containing the logs to use.
        outputFolder: str
            The folder to output the table to.
        includeBarChart: bool
            Whether to include an accompanying bar chart.
    """

    # Gets the battery usage rates in V/s or %/s.
    rates = ExtractBatteryUsageFromFolder(LOG_FOLDER, convertToPercentage)

    # Filters out all of the leading drones, so we are left with only trailing drones.
    rates = FilterDronePositions(rates, False)

    # Lists all possible separations and velocities.
    possibleVelocities = (0.5, 0.75, 1.0)
    possibleVerticalSeparations = (0.25, 0.5, 0.75)

    # Defines the data.
    # Reminder: keys for rates dictionary are of the form (vel, hsep, vsep, lead).
    data = [[rates[(vel, 1.0, 0.25, False)] for vel in possibleVelocities],
            [rates[(vel, 1.0, 0.5, False)] for vel in possibleVelocities],
            [rates[(vel, 1.0, 0.75, False)] for vel in possibleVelocities]]
    
    data = [[f"{0:1.1f}".format(entry) for entry in row] for row in data]

    # Defines the row and column headers.
    columns = [str(vel) for vel in possibleVelocities]
    rows = [str(sep) for sep in possibleVerticalSeparations]

    # Creates the table.
    table = plt.table(cellText=data, rowLabels=rows, colLabels=columns, colColours=None, loc='center')

    # Removes the bar chart.
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.box(on=None)

    # Saves the figure.
    plt.savefig(f"{outputFolder}/ConsumptionTable.png")

# ===========================================================================================================

# file = open("rates.csv", 'w')

# # Gets the battery usage rates in V/s and %/s.
# ratesVoltage = ExtractBatteryUsageFromFolder(LOG_FOLDER)
# ratesPercentage = ExtractBatteryUsageFromFolder(LOG_FOLDER, True)

# # Filters out all of the leading drones, so we are left with only trailing drones.
# ratesVoltage = FilterDronePositions(ratesVoltage, False)
# ratesPercentage = FilterDronePositions(ratesPercentage, False)

# # Writes it to the file.
# file.write("(velocity (m/s), horizontal (m), vertical (m), leading), rate (V/s), stddev (V/s), rate (%/s), stddev (%/s)\n")
# for key in ratesVoltage.keys():
#     file.write(f"{key}, {ratesVoltage[key][0]}, {ratesVoltage[key][1]}, {ratesPercentage[key][0]}, {ratesPercentage[key][1]}\n")

# file.write(f"\nTotal number of unique datasets: {len(ratesVoltage.keys())}")

# PlotBatteryFromFolder(LOG_FOLDER, OUTPUT_FOLDER + "/volts", False)
# PlotBatteryFromFolder(LOG_FOLDER, OUTPUT_FOLDER + "/percentage")

PlotBatteryConsumptionTable(True, LOG_FOLDER)