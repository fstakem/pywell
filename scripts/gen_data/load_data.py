import os
import pathlib
from datetime import datetime, timedelta

import pandas as pd


# Script params
raw_path = os.path.dirname(os.path.realpath(__file__))
path = pathlib.PurePosixPath(raw_path)
data_path = path / 'signals' / 'signal.txt'


def load_data(path):
    df = pd.read_csv(path, header=None)
    df.index = pd.DatetimeIndex(df[0])
    df.drop([0], axis=1, inplace=True)
    df.index.name = 'Time'
    df.rename(columns={1: 'Values'}, inplace=True)

    return df

def adjust_time(start_time, df):
    time_interval = df.index[1] - df.index[0]
    time_interval = timedelta(seconds=time_interval.total_seconds())
    new_time = [start_time + i * time_interval for i in range(len(df))]
    df.index = pd.DatetimeIndex(new_time)

def run():
    df = load_data(data_path)
    current_time = datetime.utcnow()
    adjust_time(current_time, df)

if __name__ == '__main__':
    run()