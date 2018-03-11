import os
import pathlib
from datetime import datetime

import pandas as pd

from load_data import load_data, adjust_time


# Mix two signals together

# Script params
raw_path = os.path.dirname(os.path.realpath(__file__))
path = pathlib.PurePosixPath(raw_path)
data_a_path = path / 'signals' / 'signal_a.txt'
data_b_path = path / 'signals' / 'signal_b.txt'
export_path = path / 'signals' / 'signal_c.txt'


def mix_signals(df_a, df_b):
    if len(df_b) > len(df_a):
        df_a, df_b = df_b, df_a

    df_comb = pd.concat([df_a, df_b], ignore_index=True, axis=1)
    df_comb = df_comb.fillna(0)
    series_comb = df_comb[0] + df_comb[1]
    df = pd.DataFrame(series_comb)
    df.index.name = 'Time'
    df.rename(columns={0: 'Values'}, inplace=True)

    return df

def export_signal(path, df):
    with open(path, 'w') as f:
        for i in range(len(df)):
            f.write('{},{}\n'.format(df.index[i], df.Values[i]))

def run():
    df_a = load_data(data_a_path)
    df_b = load_data(data_a_path)
    current_time = datetime.utcnow()
    adjust_time(current_time, df_a)
    adjust_time(current_time, df_b)
    df = mix_signals(df_a, df_b)
    export_signal(export_path, df)

if __name__ == '__main__':
    run()