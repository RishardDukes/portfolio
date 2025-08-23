import matplotlib.pyplot as plt
def plot_progress(rows, exercise):
    if not rows: print("No data to plot."); return
    dates=[r[0] for r in rows]; weights=[r[1] for r in rows]
    plt.figure(); plt.plot(dates, weights, marker="o")
    plt.title(f"{exercise} Progress"); plt.xlabel("Date"); plt.ylabel("Weight")
    plt.xticks(rotation=45); plt.tight_layout(); plt.show()
