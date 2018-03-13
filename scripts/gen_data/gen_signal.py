import json
import os
import pathlib
from datetime import datetime, timedelta
from collections import namedtuple

import numpy as np
import pandas as pd


# Import params from file and concatenate signals in order

# Script params
raw_path = os.path.dirname(os.path.realpath(__file__))
path = pathlib.PurePosixPath(raw_path)
config_path = path / 'signal_params.json'
export_path = path / 'signals' / 'signal_d.txt'


def import_config(path):
    with open(path, 'r') as json_file:
        config = json.load(json_file)

    return config

def create_signal(config):
    start_time = datetime.utcnow()
    sampling_rate = config['samples_sec']
    raw_segments = config['segments']
    signal = pd.DataFrame()

    for s in raw_segments:
        components = create_components(start_time, s['components'], sampling_rate)
        df = mix_components(components)
        signal = signal.append(df)
        start_time = df.index[-1]

    return signal

def create_components(start_time, raw_components, sampling_rate):
    components = []

    for component in raw_components:
        if component['type'] == 'sine':
            signal = create_sine(start_time, component, sampling_rate)
            components.append(signal)
        else:
            print('Signal unknown')

    return components

def mix_components(components):
    df_comb = pd.concat(components, ignore_index=True, axis=1)
    series_sum = df_comb.sum(axis=1)
    df = series_sum.to_frame()
    df.rename(columns={0:'val'}, inplace=True)

    return df

def create_sine(start_time, params, sampling_rate):
    freq = params['frequency']
    duration = params['duration_sec']
    min_value = params['amplitude'][0]
    max_value = params['amplitude'][1]

    num_samples = duration * sampling_rate
    sampling_interval = 1 / sampling_rate
    sampling_interval = timedelta(seconds=sampling_interval)
    
    x = np.arange(num_samples)
    t = [start_time +  i * sampling_interval for i in x]
    y = np.sin(2 * np.pi * freq * x / sampling_rate)
    y = scale_amp(y, min_value, max_value)

    df = pd.DataFrame(y)
    df.index = df.index = pd.DatetimeIndex(t)
    df.index.name = 'time'
    df.rename(columns={0: 'val'}, inplace=True)

    return df

def scale_amp(signal, min_value, max_value):
    scale = np.arange(min_value, max_value, len(signal))

    return scale * signal

def export_signal(path, df):
    with open(path, 'w') as f:
        for i in range(len(df)):
            f.write('{},{}\n'.format(df.index[i], df.val[i]))

def run():
    config = import_config(config_path)
    signal = create_signal(config)
    export_signal(export_path, signal)


if __name__ == '__main__':
    run()