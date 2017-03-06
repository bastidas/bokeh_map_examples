"""
state_population.py creates a map of the population in each US state
It uses population data from https://www.kaggle.com/stevepalley/us-county-population/version/1, CO-EST2015-alldata.csv
"""
import pandas as pd
import numpy as np
import get_map
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper
)
from bokeh.palettes import brewer
palette = brewer['YlGnBu'][9]
palette[8] = '#cccccc'

fname = "ne_10m_admin_1_states_provinces"
url = "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/"
local_dir = "/home/alex/Documents/data/maps/"  # dir to place the data in
get_map.download_map_data(fname, local_dir, url)
map_df = get_map.get_map_data(fname, local_dir, 8, 43)
map_df.rename(columns={'state': 'nation'}, inplace=True)
map_df.rename(columns={'province': 'state'}, inplace=True)
df = map_df[map_df["nation"] == "United States of America"]
print(df.columns)
print(df.groupby('state').size())

pop = pd.read_csv("/home/alex/Documents/data/CO-EST2015-alldata.csv", header=0, encoding="ISO-8859-1")#, nrows=1000)
pop = pop[['STNAME', 'CTYNAME', 'POPESTIMATE2010']]

st_pop = []
for state in df['state']:
    q = np.where(pop['CTYNAME'] == state)[0]
    if len(q) == 1:
        pop_est = np.round(pop.get_value(q[0], 'POPESTIMATE2010')/1e6, 2)
        print(state, ':', pop_est)
        st_pop.append(pop_est)
    else:
        st_pop.append(0)


map_df = pd.DataFrame({'x': df['x'], 'y': df['y'], 'state': df['state'], 'pop': st_pop})
# remove outlying states that make for poor looking map
map_df = map_df[map_df['state'] != "Alaska"]
map_df = map_df[map_df['state'] != "Hawaii"]

cd_source = ColumnDataSource(map_df)

tools = "pan,wheel_zoom,box_zoom,reset,hover,save"
p = figure(title="Population 2010", tools=tools, plot_width=900, plot_height=600)
p.grid.grid_line_color = None

palette.reverse()
color_mapper = LogColorMapper(palette=palette)
p.patches('x', 'y', source=cd_source, fill_color={'field': 'pop', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5)

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [("Name", "@state"), ("Population", "@pop million"), ("(Long, Lat)", "($x, $y)")]

show(p)

