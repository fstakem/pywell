import os
import pathlib
from datetime import datetime

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, save, output_file

from load_data import load_data, adjust_time


# Graph data from file

# Script params
raw_path = os.path.dirname(os.path.realpath(__file__))
path = pathlib.PurePosixPath(raw_path)
data_path = path / 'signals' / 'signal_d.txt'
graph_path = path / 'graphs' / 'output_d.html'


def graph_time_domain(df, path):
    tools = "pan,wheel_zoom,box_zoom,reset,save,box_select"
    title = 'Time Domain Plot'
    page_title = title

    fig = figure(title=title, tools=tools)

    for c in df.columns:
        fig.line(df.index, df[c], legend=c)

    output_file(path, title=page_title)
    save(gridplot(fig, ncols=1, plot_width=400, plot_height=400))

def run():
    df = load_data(data_path)
    current_time = datetime.utcnow()
    adjust_time(current_time, df)
    graph_time_domain(df, graph_path)

if __name__ == '__main__':
    run()