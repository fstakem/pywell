import json
import os
import pathlib
from datetime import datetime, timedelta
from collections import namedtuple
from random import gauss

import numpy as np
import pandas as pd
from scipy.signal import sawtooth


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
        components = create_segment(start_time, s, sampling_rate)
        df = mix_components(components)
        signal = signal.append(df)
        start_time = df.index[-1]

    return signal

def create_segment(start_time, raw_segment, sampling_rate):
    duration = raw_segment['duration_sec']
    components = []

    for component in raw_segment['components']:
        if component['type'] == 'sine':
            signal = create_sine(start_time, component, sampling_rate, duration)
            components.append(signal)
        elif component['type'] == 'cos':
            signal = create_cos(start_time, component, sampling_rate, duration)
            components.append(signal)
        elif component['type'] == 'dc':
            signal = create_dc_offset(start_time, component, sampling_rate, duration)
            components.append(signal)
        elif component['type'] == 'white_noise':
            signal = create_white_noise(start_time, component, sampling_rate, duration)
            components.append(signal)
        elif component['type'] == 'impulse':
            signal = create_impulse(start_time, component, sampling_rate, duration)
            components.append(signal)
        elif component['type'] == 'sawtooth':
            signal = create_sawtooth(start_time, component, sampling_rate, duration)
            components.append(signal)
        elif component['type'] == 'square':
            signal = create_square(start_time, component, sampling_rate, duration)
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

def create_sine(start_time, params, sampling_rate, duration):
    freq = params['frequency']
    min_value = params['amplitude'][0]
    max_value = params['amplitude'][1]

    num_samples = int(duration * sampling_rate)
    sampling_interval = 1 / sampling_rate
    sampling_interval = timedelta(seconds=sampling_interval)
    
    x = np.arange(num_samples)
    t = [start_time +  i * sampling_interval for i in x]
    y = np.sin(2 * np.pi * freq * x / sampling_rate)
    y = scale_amp(y, min_value, max_value)

    return to_df(t, y)

def create_cos(start_time, params, sampling_rate, duration):
    freq = params['frequency']
    min_value = params['amplitude'][0]
    max_value = params['amplitude'][1]

    num_samples = int(duration * sampling_rate)
    sampling_interval = 1 / sampling_rate
    sampling_interval = timedelta(seconds=sampling_interval)
    
    x = np.arange(num_samples)
    t = [start_time +  i * sampling_interval for i in x]
    y = np.cos(2 * np.pi * freq * x / sampling_rate)
    y = scale_amp(y, min_value, max_value)

    return to_df(t, y)

def scale_amp(signal, min_value, max_value):
    delta = max_value - min_value

    if delta == 0:
        return signal

    step = delta / len(signal)
    scale = np.arange(min_value, max_value, step)

    return scale * signal

def create_dc_offset(start_time, params, sampling_rate, duration):
    amplitude = params['amplitude']
    num_samples = int(duration * sampling_rate)
    sampling_interval = 1 / sampling_rate
    sampling_interval = timedelta(seconds=sampling_interval)

    x = np.arange(num_samples)
    t = [start_time +  i * sampling_interval for i in x]
    y = [amplitude] * num_samples

    return to_df(t, y)

def create_white_noise(start_time, params, sampling_rate, duration):
    mean = params['mean']
    mu = params['mu']
    num_samples = int(duration * sampling_rate)
    sampling_interval = 1 / sampling_rate
    sampling_interval = timedelta(seconds=sampling_interval)

    x = np.arange(num_samples)
    t = [start_time +  i * sampling_interval for i in x]
    y = [gauss(mean, mu) for _ in range(num_samples)]

    return to_df(t, y)

def create_impulse(start_time, params, sampling_rate, duration):
    amplitude = params['amplitude']
    num_samples = int(duration * sampling_rate)
    sampling_interval = 1 / sampling_rate
    sampling_interval = timedelta(seconds=sampling_interval)

    x = np.arange(num_samples)
    t = [start_time +  i * sampling_interval for i in x]
    imp = [amplitude]
    zeros = [0] * (num_samples - 1)
    y = imp + zeros

    return to_df(t, y)

def create_sawtooth(start_time, params, sampling_rate, duration):
    min_value = params['amplitude'][0]
    max_value = params['amplitude'][1]
    num_of_cycles = params['num_of_cycles']
    num_samples = int(duration * sampling_rate)
    sampling_interval = 1 / sampling_rate
    sampling_interval = timedelta(seconds=sampling_interval)

    x = np.arange(num_samples)
    t = [start_time +  i * sampling_interval for i in x]
    x = np.linspace(0, 1, num_samples)
    y = sawtooth(2 * np.pi * num_of_cycles * x)
    y = scale_amp(y, min_value, max_value)

    return to_df(t, y)

def create_square(start_time, params, sampling_rate, duration):
    amplitude = params['amplitude']
    num_of_cycles = params['num_of_cycles']
    num_samples = int(duration * sampling_rate)
    sampling_interval = 1 / sampling_rate
    sampling_interval = timedelta(seconds=sampling_interval)

    x = np.arange(num_samples)
    t = [start_time +  i * sampling_interval for i in x]

    sections = 2 * num_of_cycles
    samples_per_section = int(num_samples / sections)
    y = []

    for i in range(sections):
        if i % 2 == 0:
            signal = [amplitude] * samples_per_section
        else:
            signal = [-amplitude] * samples_per_section

        y.extend(signal)

    diff = num_samples - len(y)
    extra = [y[-1]] * diff
    y.extend(extra)

    return to_df(t, y)

def to_df(x, y):
    df = pd.DataFrame(y)
    df.index = df.index = pd.DatetimeIndex(x)
    df.index.name = 'time'
    df.rename(columns={0: 'val'}, inplace=True)

    return df

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