import os
import csv
from calc_swOBA import base_out_swOBA
import tqdm
from typing import Dict
import sys
from pybaseball import playerid_reverse_lookup # type: ignore

print("Note. The dependencies for this aren't in requirements.txt.")

files = sorted(os.listdir("downloads"))
files_filtered: list[str] = []
for file in files:
    # if file.endswith(".ROS"):
    #     print(file)
    if file.endswith(".ROS") and file[3:7] == "2021":
        files_filtered.append("downloads/" + file)

players: list[Dict[str, str]] = []
for file in files_filtered:
    with open(file, "r") as f:
        reader = csv.reader(f)
        for line in reader:
            players.append({"pid": line[0], "pname": line[2] + " " + line[1]})

if not os.path.isdir("chadwick_csv"):
    print("The folder chadwick_csv doesn't exist. Have you run retrosheet_to_csv.sh?", file=sys.stderr)
    sys.exit(1)
files = sorted(os.listdir("chadwick_csv"))
if not len(files):
    print("The folder chadwick_csv doesn't have any folders. Have you run retrosheet_to_csv.sh?", file=sys.stderr)
    sys.exit(1)

files = sorted(os.listdir("chadwick_csv"))
files_filtered = []
for file in files:
    if int(file[0:4]) != 2021:
        continue
    else:
        files_filtered.append(file)
plays: list[Dict[str, str]] = []

for file in tqdm.tqdm(files_filtered):
    if int(file[0:4]) != 2021:
        continue
    file = "chadwick_csv/" + file
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        plays.extend(list(reader))

if not os.path.isfile("base_out_weights.csv"):
    print("base_out_weights.csv not found. Have you run avgoutcomes.py?", file=sys.stderr)
    sys.exit(1)
with open("base_out_weights.csv", "r") as f:
    weights = list(csv.DictReader(
        f, quoting=csv.QUOTE_NONNUMERIC, quotechar='"'))

swobas: list[Dict[str, int | str | float]] = []
for player in tqdm.tqdm(players):
    swobas.append({"pname": player["pname"],"pid": player["pid"], "swoba": base_out_swOBA(plays, player["pid"], list(weights)), "woba": 0.0})


with open("fangraphs.csv", "r", encoding='utf-8-sig') as f:
    fg = list(csv.DictReader(f, quoting=csv.QUOTE_ALL, quotechar='"'))
wobas = []
for player in tqdm.tqdm(fg):
    done = False
    retro_id: str = playerid_reverse_lookup([int(player["playerid"])], key_type="fangraphs")["key_retro"].iloc[0] # type: ignore
    # retro_id = retro_id[0]
    for player_w in swobas:
        if retro_id == player_w['pid']:
            player_w['woba'] = float(player['wOBA'])
            done = True
            break
    if not done:
        print(player['Name'])

woba_and_swoba: list[Dict[str, int | str | float]] = []
for player in swobas:
    if player['woba'] != 0:
        woba_and_swoba.append(player)

# print(sorted(woba_and_swoba, key=lambda x: x['woba'], reverse=True)[:10])
# print(sorted(woba_and_swoba, key=lambda x: x['swoba'], reverse=True)[:10])

import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
from matplotlib.ticker import FormatStrFormatter # type: ignore

xpoints = [p['woba'] for p in sorted(woba_and_swoba, key=lambda x: x['woba'], reverse=True)[:75]]
ypoints = [p['swoba'] for p in sorted(woba_and_swoba, key=lambda x: x['woba'], reverse=True)[:75]]
labels = [p['pname'] for p in sorted(woba_and_swoba, key=lambda x: x['woba'], reverse=True)[:10]]

ax = plt.scatter(xpoints, ypoints, s=2).axes # type: ignore
plt.xlabel("wOBA") # type: ignore
plt.ylabel("swOBA") # type: ignore
plt.title("Top 75 qualified wOBA leaders in 2021. wOBA vs swOBA") # type: ignore

texts = []
for i, item in enumerate(labels):
    texts.append(plt.text(xpoints[i], ypoints[i], item, fontsize=6, horizontalalignment='center')) # type: ignore
from adjustText import adjust_text # type: ignore
adjust_text(texts, only_move={'points':'y', 'texts':'y'}, arrowprops=dict(arrowstyle="-", color='black', lw=0.5))
lims = [ # type: ignore
    np.min([ax.get_xlim(), ax.get_ylim()]),  # type: ignore # min of both axes
    np.max([ax.get_xlim(), ax.get_ylim()]),  # type: ignore # max of both axes
]
ax.plot(lims, lims, 'k-', alpha=0.5, zorder=0, linewidth=1) # type: ignore
ax.set_aspect('equal')
ax.set_aspect('equal')
ax.set_xlim(lims) # type: ignore
ax.set_ylim(lims) # type: ignore
ax.set_aspect('equal')

ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f')) # type: ignore

plt.show() # type: ignore

plt.bar(range(len(woba_and_swoba)), [p['swoba'] - p['woba'] for p in sorted(woba_and_swoba, key=lambda x: x['woba'], reverse=True)],) # type: ignore
plt.xticks(range(len(woba_and_swoba)), [p['pname'] for p in sorted(woba_and_swoba, key=lambda x: x['woba'], reverse=True)], rotation=90, fontsize=7) # type: ignore
plt.xlabel("Name") # type: ignore
plt.ylabel("swOBA - wOBA") # type: ignore
plt.title("Top 50 qualified wOBA leaders in 2021. swOBA - wOBA") # type: ignore
plt.show() # type: ignore

for p in woba_and_swoba:
    if p['swoba'] - p['woba'] <= 0: # type: ignore
        print(p)