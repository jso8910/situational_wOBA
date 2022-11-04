import argparse
import sys
import csv
from typing import Dict
import os
import tqdm
import os.path


def base_out_swOBA(plays: list[Dict[str, str]], player_id: str, weights: list[Dict[str, str | int]]) -> float:
    swOBA_numerator = 0
    swOBA_denominator = 0
    """
    numerators[idx][2] = 1b*run_exp[idx][2] + \
            2b*run_exp[idx][3] + \
            3b*run_exp[idx][4] + hr*run_exp[idx][5] + UBB*run_exp[idx][6] + \
            HBP*run_exp[idx][7] + \
            K*run_exp[idx][8]
    denom = AB+BB+SF+HBP
    """
    # event_lookup = {
    #     3: "n",
    #     14: "d+"
    # }
    for play in plays:
        if play["BAT_ID"] != player_id:
            continue

        base_state = int(play["START_BASES_CD"])
        outs = int(play["OUTS_CT"])
        sit_idx = base_state * 3 + outs
        match int(play["EVENT_CD"]):
            case 2:
                swOBA_denominator += 1
            case 3:
                swOBA_denominator += 1
            case 14:
                swOBA_numerator += weights[sit_idx]["UBB"]
                swOBA_denominator += 1
            case 16:
                swOBA_numerator += weights[sit_idx]["HBP"]
                swOBA_denominator += 1
            case 19:
                swOBA_denominator += 1
            case 20:
                swOBA_numerator += weights[sit_idx]["1B"]
                swOBA_denominator += 1
            case 21:
                swOBA_numerator += weights[sit_idx]["2B"]
                swOBA_denominator += 1
            case 22:
                swOBA_numerator += weights[sit_idx]["3B"]
                swOBA_denominator += 1
            case 23:
                swOBA_numerator += weights[sit_idx]["HR"]
                swOBA_denominator += 1

    if swOBA_denominator == 0:
        return -1
    return swOBA_numerator / swOBA_denominator

def main(start_year: int, end_year: int, use_innings: bool, player_id: str):
    if args.start_year > args.end_year:
        print("START_YEAR must be less than END_YEAR")
        sys.exit(1)
    elif args.start_year < 1915 or args.end_year > 2021:
        print("START_YEAR and END_YEAR must be between 1915 and 2021. If 2022 or a future year has been added to retrosheet, feel free to edit this file.")
        sys.exit(1)

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
        if not os.path.isfile("base_out_weights.csv"):
            print("base_out_weights.csv not found. Have you run avgoutcomes.py?", file=sys.stderr)
            sys.exit(1)
        with open("base_out_weights.csv", "r") as f:
            weights = list(csv.DictReader(
                f, quoting=csv.QUOTE_NONNUMERIC, quotechar='"'))
        # swOBA = round(base_out_swOBA(plays, args.player_id, list(weights)), 3)
        return base_out_swOBA(plays, args.player_id, list(weights))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--player-id', '-p',
                        help="Retrosheet ID of the player you want to calculate the swOBA of", type=str, required=True)
    parser.add_argument('--use-innings', '-i',
                        help="Turn this on if you want to use the innings weights csv.", type=str, required=False, default=False)
    parser.add_argument('--start-year', '-s',
                        help="Start year of data gathering (defaults to 2000 for a somewhat reasonable default)", type=int, default=2000)
    parser.add_argument('--end-year', '-e',
                        help="End year of data gathering (defaults to 2021, current retrosheet year as of coding)", type=int, default=2021)

    args = parser.parse_args(sys.argv[1:])

    print(main(args.start_year, args.end_year, args.use_innings, args.player_id))