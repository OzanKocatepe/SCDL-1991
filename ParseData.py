import csv

LOG_FOLDER = "./logs"
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

    # Opens the file in a csv dictionary.
    file = open(fileName, "r")
    csvFile = csv.DictReader(file)
    print(csvFile[0:10])

    # Cuts off the header.
    # csvFile = csvFile[10:]

    # Extracts the timestamps and battery levels.
    # batteryLevels = [line.get("batteryV") for line in csvFile[10:]]

LinearBatteryUsageFromFile(LOG_FOLDER + "/2025-05-10-0.csv")