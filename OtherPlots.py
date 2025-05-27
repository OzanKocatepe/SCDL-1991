import matplotlib.pyplot as plt
import numpy as np

separations = ("25x25", "65x65", "100x100")
halfSpeed = {
    "Experimental": (0.13, 0.12, 0.08),
    "Simulated": (0.18, 0.16, 0.18)
}
fullSpeed = {
    "Experimental": (0.15, 0.13, 0.10),
    "Simulated": (0.36, 0.32, 0.26)
}

for i in range(2):
    x = np.arange(len(separations))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')
    ax.grid(axis='y')
    ax.set_axisbelow(True)

    speedLabels = ("0.5", "1.0")
    speeds = (halfSpeed, fullSpeed)

    for attribute, measurement in speeds[i].items():
        offset = width * multiplier
        if (multiplier == 0):
            color = 'blue'
        else:
            color = 'red'
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Battery Consumption Rate (%/s)')
    # ax.set_title('Battery Consumption Rate at 0.5 m/s')
    ax.set_xticks(x + width, separations)
    ax.legend(loc='upper left')
    ax.set_ylim(0, 0.5)

    plt.savefig(f"{speedLabels[i]} m s Comparison.png")
    plt.clf()