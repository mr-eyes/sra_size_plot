import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import sys


if len(sys.argv) != 2:
    print("Usage: python fetch_and_plot.py <output_file_path>")
    sys.exit(1)

output_file_path = sys.argv[1]

data = pd.read_csv("https://www.ncbi.nlm.nih.gov/Traces/sra/sra_stat.cgi")
data["date"] = pd.to_datetime(data["date"], format="%m/%d/%Y")
data["Pbp"] = data["bases"] * 1e-15
data["Open_access_Pbp"] = data["open_access_bases"] * 1e-15


def format_tick(value, pos):
    value_in_gb = value * 1e6
    if value_in_gb < 1e3:
        return f"{value_in_gb:.0f} GB"
    elif value_in_gb < 1e6:
        return f"{value_in_gb / 1e3:.0f} TB"
    else:
        return f"{value:.0f} PB"


def calculate_5_year_doubling_times(df):
    df_sorted = df.sort_values(by="date")
    previous_value = df_sorted.iloc[0]["Pbp"]
    previous_date = df_sorted.iloc[0]["date"]
    doubling_times = [(previous_date, previous_value)]

    for _, row in df_sorted.iterrows():
        year_diff = row["date"].year - previous_date.year
        if row["Pbp"] >= previous_value * 2 and year_diff >= 5:
            doubling_times.append((row["date"], row["Pbp"]))
            previous_value = row["Pbp"]
            previous_date = row["date"]

    return doubling_times


five_year_doubling_times = calculate_5_year_doubling_times(data)


plt.figure(figsize=(10, 8))


plt.plot(data["date"], data["Pbp"], label="Total", color="blue")
plt.plot(data["date"], data["Open_access_Pbp"], label="Open access", color="goldenrod")


plt.yscale("log")
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_tick))


plt.grid(True, which="both", ls="--", linewidth=0.5)
plt.title("Sequence Read Archive (SRA) growth")
plt.xlabel("Year")
plt.ylabel("Data Volume")
plt.legend()


plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.gcf().autofmt_xdate()


for date, value in five_year_doubling_times:
    plt.annotate(
        f"{value:.1f} Pbp",
        xy=(date, value),
        xytext=(15, 15),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.5"),
        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="black", lw=2, alpha=0.8),
    )
    plt.axvline(x=date, color="grey", linestyle="--", lw=0.5)


last_date = data["date"].iloc[-1]
last_total_pbp = data["Pbp"].iloc[-1]
last_open_access_pbp = data["Open_access_Pbp"].iloc[-1]

plt.annotate(
    f"{last_total_pbp:.1f} Pbp",
    (last_date, last_total_pbp),
    xytext=(15, 15),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.5"),
    bbox=dict(boxstyle="round,pad=0.5", fc="lightblue", ec="blue", lw=2, alpha=0.5),
)


plt.annotate(
    f"{last_open_access_pbp:.1f} Pbp",
    (last_date, last_open_access_pbp),
    xytext=(15, -30),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-.5"),
    bbox=dict(boxstyle="round,pad=0.5", fc="yellow", ec="goldenrod", lw=2, alpha=0.5),
)


plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.gcf().autofmt_xdate()


plt.tight_layout()
plt.savefig(output_file_path, dpi=600)
