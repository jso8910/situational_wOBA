import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--player-id', '-p',
                    help="Retrosheet ID of the player you want to calculate wOBA of", type=str, required=True)
parser.add_argument('--use-innings', '-i',
                    help="Turn this on if you want to use the innings weights csv.", type=str, required=False, default=False)

args = parser.parse_args(sys.argv[1:])

if args.use_innings:
    raise NotImplementedError()
else:
    filename = "base_out_weights.csv"
    raise NotImplementedError()
