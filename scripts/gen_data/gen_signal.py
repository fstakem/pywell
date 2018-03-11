import json
import os
import pathlib
from datetime import datetime, timedelta
from collections import namedtuple

import numpy as np


# Import params from file and concatenate signals in order

# Script params
raw_path = os.path.dirname(os.path.realpath(__file__))
path = pathlib.PurePosixPath(raw_path)
config_path = path / 'signal_params.json'
export_path = path / 'signals' / 'signal_b.txt'

Signal = namedtuple('Signal', 'type timestamps values')


def import_config(path):
    with open(path, 'r') as json_file:
        config = json.load(json_file)

    return config

def create_signals(config):
    start_time = datetime.utcnow()
    signals = []

    for signal in config['signals']:
        if signal['type'] == 'sine':
            wave = create_sine(start_time, signal)
            signals.append(wave)
        else:
            print('Signal unknown')

    return signals

def create_sine(start_time, params):
    sampling_rate = params['sampling_rate']
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

    return Signal('sine', t, y)

def scale_amp(signal, min_value, max_value):
    scale = np.arange(min_value, max_value, len(signal))

    return scale * signal

def export_signal(path, signals):
    raw_times = [s.timestamps for s in signals]
    comb_times = np.concatenate(raw_times, axis=0)

    raw_values = [s.values for s in signals]
    comb_values = np.concatenate(raw_values, axis=0)

    with open(path, 'w') as f:
        for t, v in zip(comb_times, comb_values):
            f.write('{},{}\n'.format(t, v))


def run():
    config = import_config(config_path)
    signals = create_signals(config)
    export_signal(export_path, signals)


if __name__ == '__main__':
    run()