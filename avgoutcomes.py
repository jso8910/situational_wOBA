"""
Should I also calculate per inning? Wonder how much running changes from innings 1-9 and extras
Probably can't hurt

Run script populating chadwick_csv (cwdata) and downloading files first

cwdata command I'm thinking of, refine this but, in this, are the necessary fields and more. Uses example of 2021:
cwevent -f 2,4,11,15,26-28,34,37,40-43,47-48,58-65 -x 0-3,8,13,14,51-55 -y 2021 -n 2021CHN.EVN

Allow input of start and end year for processing
"""
import argparse
import sys
import os
import csv
from typing import Dict
import tqdm


def base_outs_weights(plays: list[Dict[str, str]]) -> list[list[str | int]]:
    """
    Returns a 2D array. First column is the number of outs, 2nd-4th columns are baserunners, subsequent columns are weights
    """
    run_exp_by_sit = [
        # ["Outs", "Runner state", "RUNS", "COUNT", "AVG"],
        [0, 0b000, 0, 0, 0.0],
        [1, 0b000, 0, 0, 0.0],
        [2, 0b000, 0, 0, 0.0],
        [0, 0b001, 0, 0, 0.0],
        [1, 0b001, 0, 0, 0.0],
        [2, 0b001, 0, 0, 0.0],
        [0, 0b010, 0, 0, 0.0],
        [1, 0b010, 0, 0, 0.0],
        [2, 0b010, 0, 0, 0.0],
        [0, 0b011, 0, 0, 0.0],
        [1, 0b011, 0, 0, 0.0],
        [2, 0b011, 0, 0, 0.0],
        [0, 0b100, 0, 0, 0.0],
        [1, 0b100, 0, 0, 0.0],
        [2, 0b100, 0, 0, 0.0],
        [0, 0b101, 0, 0, 0.0],
        [1, 0b101, 0, 0, 0.0],
        [2, 0b101, 0, 0, 0.0],
        [0, 0b110, 0, 0, 0.0],
        [1, 0b110, 0, 0, 0.0],
        [2, 0b110, 0, 0, 0.0],
        [0, 0b111, 0, 0, 0.0],
        [1, 0b111, 0, 0, 0.0],
        [2, 0b111, 0, 0, 0.0],
    ]

    for play in tqdm.tqdm(plays):
        base_state = int(play["END_BASES_CD"])
        outs = int(play["OUTS_CT"]) + int(play["EVENT_OUTS_CT"])
        if outs >= 3:
            continue
        run_exp_by_sit[base_state * 3 + outs][2] += int(play["FATE_RUNS_CT"])
        run_exp_by_sit[base_state * 3 + outs][3] += 1

    for idx in range(len(run_exp_by_sit)):
        run_exp_by_sit[idx][4] = run_exp_by_sit[idx][2]/run_exp_by_sit[idx][3]

    # __import__('pprint').pprint(run_exp_by_sit)

    avg_outcomes: list[list[int | dict[str, int | dict[str, int]]]] = [
        # ["Outs", "Base State", "1B",
        #     "2B", "3B", "HR", "UBB", "HBP", "K", "Out"],
        [0, 0b000, {},
         {}, {}, {}, {}, {}, {}, {}],
        [1, 0b000, {},
         {}, {}, {}, {}, {}, {}, {}],
        [2, 0b000, {},
         {}, {}, {}, {}, {}, {}, {}],
        [0, 0b001, {},
         {}, {}, {}, {}, {}, {}, {}],
        [1, 0b001, {},
         {}, {}, {}, {}, {}, {}, {}],
        [2, 0b001, {},
         {}, {}, {}, {}, {}, {}, {}],
        [0, 0b010, {},
         {}, {}, {}, {}, {}, {}, {}],
        [1, 0b010, {},
         {}, {}, {}, {}, {}, {}, {}],
        [2, 0b010, {},
         {}, {}, {}, {}, {}, {}, {}],
        [0, 0b011, {},
         {}, {}, {}, {}, {}, {}, {}],
        [1, 0b011, {},
         {}, {}, {}, {}, {}, {}, {}],
        [2, 0b011, {},
         {}, {}, {}, {}, {}, {}, {}],
        [0, 0b100, {},
         {}, {}, {}, {}, {}, {}, {}],
        [1, 0b100, {},
         {}, {}, {}, {}, {}, {}, {}],
        [2, 0b100, {},
         {}, {}, {}, {}, {}, {}, {}],
        [0, 0b101, {},
         {}, {}, {}, {}, {}, {}, {}],
        [1, 0b101, {},
         {}, {}, {}, {}, {}, {}, {}],
        [2, 0b101, {},
         {}, {}, {}, {}, {}, {}, {}],
        [0, 0b110, {},
         {}, {}, {}, {}, {}, {}, {}],
        [1, 0b110, {},
         {}, {}, {}, {}, {}, {}, {}],
        [2, 0b110, {},
         {}, {}, {}, {}, {}, {}, {}],
        [0, 0b111, {},
         {}, {}, {}, {}, {}, {}, {}],
        [1, 0b111, {},
         {}, {}, {}, {}, {}, {}, {}],
        [2, 0b111, {},
         {}, {}, {}, {}, {}, {}, {}],
        # ["Outs", "Base State", "1B",
        #     "2B", "3B", "HR", "UBB", "HBP", "K", "Out"],
    ]

    event_cd_lookup = {
        # lookup from event type code (https://chadwick.readthedocs.io/en/latest/cwevent.html#event-type-code-field-34) to index within situation array
        2: 9,
        3: 8,
        14: 6,
        16: 7,
        20: 2,
        21: 3,
        22: 4,
        23: 5
    }

    for idx in range(len(avg_outcomes)):
        for idx_inner in range(2, len(avg_outcomes[idx])):
            avg_outcomes[idx][idx_inner] = {"first": {"total": 0, "average": 0}, "second": {"total": 0, "average": 0}, "third": {
                "total": 0, "average": 0}, "outs": {"total": 0, "average": 0}, "run_exp_after": {"total": 0.0, "average": 0.0}, "runs_on_play": {"total": 0.0, "average": 0.0}, "n_scenarios": 0}

    for play in tqdm.tqdm(plays):
        base_state = int(play["START_BASES_CD"])
        end_base_state = int(play["END_BASES_CD"])
        outs = int(play["OUTS_CT"])
        end_outs = outs + int(play["EVENT_OUTS_CT"])
        event_outcome_idx = event_cd_lookup[int(play["EVENT_CD"])] if int(
            play["EVENT_CD"]) in event_cd_lookup else 0
        if not event_outcome_idx:
            continue
        sit_idx = base_state * 3 + outs
        end_sit_idx = end_base_state * 3 + end_outs
        situation = avg_outcomes[sit_idx]
        outcome: dict[str, int | dict[str, int]
                      ] = situation[event_outcome_idx]

        outcome['first']['total'] += bool(end_base_state & 0b001)
        outcome['second']['total'] += bool(end_base_state & 0b010)
        outcome['third']['total'] += bool(end_base_state & 0b100)
        outcome['outs']['total'] += int(play["OUTS_CT"]) + \
            int(play["EVENT_OUTS_CT"])
        outcome['run_exp_after']['total'] += run_exp_by_sit[end_sit_idx][-1] if end_outs < 3 else 0
        outcome['runs_on_play']['total'] += int(play["EVENT_RUNS_CT"])
        outcome['n_scenarios'] += 1

    for idx in range(len(avg_outcomes)):
        for idx_inner in range(2, len(avg_outcomes[idx])):
            avg_outcomes[idx][idx_inner]['first']['average'] = avg_outcomes[idx][idx_inner]['first']['total'] / \
                avg_outcomes[idx][idx_inner]['n_scenarios']
            avg_outcomes[idx][idx_inner]['second']['average'] = avg_outcomes[idx][idx_inner]['second']['total'] / \
                avg_outcomes[idx][idx_inner]['n_scenarios']
            avg_outcomes[idx][idx_inner]['third']['average'] = avg_outcomes[idx][idx_inner]['third']['total'] / \
                avg_outcomes[idx][idx_inner]['n_scenarios']
            avg_outcomes[idx][idx_inner]['outs']['average'] = avg_outcomes[idx][idx_inner]['outs']['total'] / \
                avg_outcomes[idx][idx_inner]['n_scenarios']
            avg_outcomes[idx][idx_inner]['run_exp_after']['average'] = avg_outcomes[idx][idx_inner]['run_exp_after']['total'] / \
                avg_outcomes[idx][idx_inner]['n_scenarios']
            avg_outcomes[idx][idx_inner]['runs_on_play']['average'] = avg_outcomes[idx][idx_inner]['runs_on_play']['total'] / \
                avg_outcomes[idx][idx_inner]['n_scenarios']

    run_exp = [
        # ["Outs", "Base State", "1B",
        #     "2B", "3B", "HR", "UBB", "HBP", "K", "Out", "LI"],
        # (Runs scored + New run expectancy) - existing run expectancy
        [0, 0b000, 0,
            0, 0, 0, 0, 0, 0, 0, 0.9],
        [1, 0b000, 0,
            0, 0, 0, 0, 0, 0, 0, 0.6],
        [2, 0b000, 0,
            0, 0, 0, 0, 0, 0, 0, 0.4],
        [0, 0b001, 0,
            0, 0, 0, 0, 0, 0, 0, 1.5],
        [1, 0b001, 0,
            0, 0, 0, 0, 0, 0, 0, 1.2],
        [2, 0b001, 0,
            0, 0, 0, 0, 0, 0, 0, 0.8],
        [0, 0b010, 0,
            0, 0, 0, 0, 0, 0, 0, 1.3],
        [1, 0b010, 0,
            0, 0, 0, 0, 0, 0, 0, 1.2],
        [2, 0b010, 0,
            0, 0, 0, 0, 0, 0, 0, 1.2],
        [0, 0b011, 0,
            0, 0, 0, 0, 0, 0, 0, 2.1],
        [1, 0b011, 0,
            0, 0, 0, 0, 0, 0, 0, 1.9],
        [2, 0b011, 0,
            0, 0, 0, 0, 0, 0, 0, 1.7],
        [0, 0b100, 0,
            0, 0, 0, 0, 0, 0, 0, 1.2],
        [1, 0b100, 0,
            0, 0, 0, 0, 0, 0, 0, 1.1],
        [2, 0b100, 0,
            0, 0, 0, 0, 0, 0, 0, 1.3],
        [0, 0b101, 0,
            0, 0, 0, 0, 0, 0, 0, 1.7],
        [1, 0b101, 0,
            0, 0, 0, 0, 0, 0, 0, 1.7],
        [2, 0b101, 0,
            0, 0, 0, 0, 0, 0, 0, 1.8],
        [0, 0b110, 0,
            0, 0, 0, 0, 0, 0, 0, 1.5],
        [1, 0b110, 0,
            0, 0, 0, 0, 0, 0, 0, 1.6],
        [2, 0b110, 0,
            0, 0, 0, 0, 0, 0, 0, 2.2],
        [0, 0b111, 0,
            0, 0, 0, 0, 0, 0, 0, 2.3],
        [1, 0b111, 0,
            0, 0, 0, 0, 0, 0, 0, 2.5],
        [2, 0b111, 0,
            0, 0, 0, 0, 0, 0, 0, 2.8],
    ]

    # for idx in range(len(run_exp)):
    #     # We don't want to consider leverage index
    #     for idx_inner in range(2, len(run_exp[idx]) - 1):
    #         run_exp[idx][idx_inner] = {
    #             "runs_scored": 0, "n_scenarios": 0, "avg": 0.0}

    for idx in range(len(run_exp)):
        # We don't want to consider leverage index
        for idx_inner in range(2, len(run_exp[idx]) - 1):
            # (Runs scored + New run expectancy) - existing run expectancy
            run_exp[idx][idx_inner] += (avg_outcomes[idx][idx_inner]["run_exp_after"]["average"] + avg_outcomes[idx][idx_inner]['runs_on_play']['average']) - \
                (run_exp_by_sit[idx][-1])
            # Divide by leverage index
            run_exp[idx][idx_inner] /= run_exp[idx][-1]
            # Subtract value of the out (value of out is negative)
            run_exp[idx][idx_inner] -= run_exp[idx][-1]

    for idx in range(len(run_exp)):
        # We don't want to consider leverage index
        for idx_inner in range(2, len(run_exp[idx]) - 1):
            # Subtract value of the out (value of out is negative)
            run_exp[idx][idx_inner] -= run_exp[idx][-2]

    # __import__("pprint").pprint(run_exp)
    # __import__("pprint").pprint(avg_outcomes)

    numerators = [
        # ["Outs", "Base State", "numerator", "<on base>/numerator"],
        [0, 0b000, 0, 0],
        [1, 0b000, 0, 0],
        [2, 0b000, 0, 0],
        [0, 0b001, 0, 0],
        [1, 0b001, 0, 0],
        [2, 0b001, 0, 0],
        [0, 0b010, 0, 0],
        [1, 0b010, 0, 0],
        [2, 0b010, 0, 0],
        [0, 0b011, 0, 0],
        [1, 0b011, 0, 0],
        [2, 0b011, 0, 0],
        [0, 0b100, 0, 0],
        [1, 0b100, 0, 0],
        [2, 0b100, 0, 0],
        [0, 0b101, 0, 0],
        [1, 0b101, 0, 0],
        [2, 0b101, 0, 0],
        [0, 0b110, 0, 0],
        [1, 0b110, 0, 0],
        [2, 0b110, 0, 0],
        [0, 0b111, 0, 0],
        [1, 0b111, 0, 0],
        [2, 0b111, 0, 0],
    ]

    # Based on 2022 https://www.baseball-reference.com/leagues/split.cgi?t=b&lg=MLB&year=2022
    # Scaled every stat down to 600 PAs, a standard amount and rounded in a way that the numbers added up
    # Rate stats are very slightly off but whatever
    # On base 189 times
    avg_batting_line = {
        "PAs": 600,
        "ABs": 539,
        "Hits": 131,
        "2B": 26,
        "3B": 2,
        "HR": 17,
        "UBB": 49,
        "HBP": 7,
        "SH": 1,
        "SF": 4,
        "ROE": 2,
        "K": 135,
        "BA": .247,
        "OBP": .323,
        "SLG": .393
    }

    # ["Outs", "Base State", "1B",
    #     "2B", "3B", "HR", "UBB", "HBP", "K", "Out", "LI"],
    # __import__('pprint').pprint(run_exp)
    for idx in range(len(numerators)):
        numerators[idx][2] = (avg_batting_line["Hits"] -
                              avg_batting_line["2B"] - avg_batting_line["3B"] - avg_batting_line["HR"])*run_exp[idx][2] + avg_batting_line["2B"]*run_exp[idx][3] + \
            avg_batting_line["3B"]*run_exp[idx][4] + avg_batting_line["HR"]*run_exp[idx][5] + avg_batting_line["UBB"]*run_exp[idx][6] + \
            avg_batting_line["HBP"]*run_exp[idx][7] + \
            avg_batting_line["K"]*run_exp[idx][8]
        # Based on stats above (not rate stats, they're messed up), hitters get on base 189 times per 600 PA
        numerators[idx][3] = 189/numerators[idx][2]
        # Don't include 2 inputs and LI
        for idx_inner in range(2, len(run_exp[idx]) - 1):
            run_exp[idx][idx_inner] *= numerators[idx][3]

    # __import__('pprint').pprint(run_exp)

    # Header
    run_exp.insert(0, ["Outs State", "Base State", "1B", "2B",
                   "3B", "HR", "UBB", "HBP", "K", "Out", "LI"])

    return [row[:-1] for row in run_exp]


parser = argparse.ArgumentParser()
parser.add_argument('--start-year', '-s',
                    help="Start year of data gathering (defaults to 2000 for a somewhat reasonable default)", type=int, default=2000)
parser.add_argument('--end-year', '-e',
                    help="End year of data gathering (defaults to 2021, current retrosheet year as of coding)", type=int, default=2021)
parser.add_argument('--use-innings', '-i',
                    help="Use innings rather than just base-outs in weights. The output file is named differently if you use innings", type=int, default=False)

args = parser.parse_args(sys.argv[1:])

if args.start_year > args.end_year:
    print("START_YEAR must be less than END_YEAR")
    sys.exit(1)
elif args.start_year < 1915 or args.end_year > 2021:
    print("START_YEAR and END_YEAR must be between 1915 and 2021. If 2022 or a future year has been added to retrosheet, feel free to edit this file.")
    sys.exit(1)

files = sorted(os.listdir("chadwick_csv"))
files_filtered = []
for file in files:
    if int(file[0:4]) < args.start_year or int(file[0:4]) > args.end_year:
        continue
    else:
        files_filtered.append(file)
plays: list[Dict[str, str]] = []

for file in tqdm.tqdm(files_filtered):
    if int(file[0:4]) < args.start_year or int(file[0:4]) > args.end_year:
        continue
    file = "chadwick_csv/" + file
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        plays.extend(list(reader))

if args.use_innings:
    raise NotImplementedError()
else:
    weights = base_outs_weights(plays)
    with open("base_out_weights.csv", "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        [writer.writerow(row) for row in weights]
    print("Outputted weights to base_out_weights.csv")
