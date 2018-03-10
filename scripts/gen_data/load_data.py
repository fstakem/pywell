import os
import pathlib

import pandas as pd

# Script params
raw_path = os.path.dirname(os.path.realpath(__file__))
path = pathlib.PurePosixPath(raw_path)
data_path = path / 'out' / 'signal.txt'


def load_data(path):
    df = pd.read_csv(path, header=None)
    df.index = pd.DatetimeIndex(df[0])
    df.drop([0], axis=1, inplace=True)
    df.index.name = 'Time'
    df.rename(columns={1: 'Values'}, inplace=True)

def run():
    df = load_data(data_path)

if __name__ == '__main__':
    run()