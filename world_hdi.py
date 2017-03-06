"""
world_hdi.py creates a map of the world human development index in each country
It uses population data from https://www.kaggle.com/undp/human-development, human_development.csv
"""

import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper
)
import get_map
from bokeh.palettes import viridis
palette = viridis(256)
palette[255] = '#cccccc'

fname = "ne_10m_admin_0_countries"
url = "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/"
local_dir = "/home/alex/Documents/data/maps/"  # dir to place the data in
get_map.download_map_data(fname, local_dir, url)
map_df = get_map.get_map_data(fname, local_dir, 8, 18)
map_df.rename(columns={'state': 'nation'}, inplace=True)
del map_df['province']

hd = pd.read_csv("/home/alex/Documents/data/human_development/human_development.csv", header=0)#, encoding="ISO-8859-1")

hdi = []
for nation in map_df['nation']:
    q = np.where(hd['Country'] == nation)[0]
    if len(q) == 1:
        print(nation, ':', hd.get_value(q[0], 'Human Development Index (HDI)'))
        hdi.append(hd.get_value(q[0], 'Human Development Index (HDI)'))
    else:
        print(nation, ' : ', 'unknown (0)')
        hdi.append(0)

df = pd.DataFrame({'x': map_df['x'], 'y': map_df['y'], 'country': map_df['nation'], 'hdi': hdi})
df = df[df['country'] != "Antarctica"]
cd_source = ColumnDataSource(df)
tools = "pan,wheel_zoom,box_zoom,reset,hover,save"
p = figure(title="Human Development Index", tools=tools, x_axis_location=None, y_axis_location=None, plot_width=900,
           plot_height=600)
p.grid.grid_line_color = None

palette.reverse()
color_mapper = LogColorMapper(palette=palette)

p.patches('x', 'y', source=cd_source,
          fill_color={'field': 'hdi', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5)

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [("Name", "@country"), ("Human Development Index)", "@hdi"), ("(Long, Lat)", "($x, $y)")]

show(p)
