"""
county_population.py creates a map of the population in each US county
It uses population data from https://www.kaggle.com/stevepalley/us-county-population/version/1, CO-EST2015-alldata.csv
"""
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper,
    Range1d
)
from bokeh.palettes import brewer
import get_map

palette = brewer['YlGnBu'][9]
palette[8] = '#cccccc'

map_high_res = "cb_2015_us_county_500k"
map_low_res = "cb_2015_us_county_20m"
map_file = map_low_res

local_dir = "/home/alex/Documents/data/maps/"  # dir to place the data in
url = "http://www2.census.gov/geo/tiger/GENZ2015/shp/"
get_map.download_map_data(map_file, local_dir, url)
map_df = get_map.get_map_data(map_file, local_dir, 5, 0)
map_df.rename(columns={'province': 'county'}, inplace=True)
state_names = get_map.fix_state_names(map_df)


# population data for the counties
pop = pd.read_csv("/home/alex/Documents/data/CO-EST2015-alldata.csv", header=0, encoding="ISO-8859-1")
pop = pop[['STNAME', 'CTYNAME', 'POPESTIMATE2010']]
str_splitter = lambda x: x.rsplit(' ', 1)[0]
pop['CTYNAME'] = pop['CTYNAME'].apply(str_splitter)
# exclude Alaska
#pop = pop[pop['STNAME'] != 'Alaska'].reset_index()
# exclude Hawaii
#pop = pop[pop['STNAME'] != 'Hawaii'].reset_index()
# Select just one state
#pop = pop[pop['STNAME'] == 'California'].reset_index()

# match population and map shape data
x_lat = []
y_lon = []
state = []
county = []
population = []
for j in map_df.index:
    q = np.intersect1d(np.where(pop['CTYNAME'] == map_df.get_value(j, 'county'))[0],
                       np.where(pop['STNAME'] == map_df.get_value(j, 'state'))[0])
    if len(q) == 1:
        x_lat.append(map_df.get_value(j, 'x'))
        y_lon.append(map_df.get_value(j, 'y'))
        county.append(map_df.get_value(j, 'county'))
        state.append(map_df.get_value(j, 'state'))
        population.append(pop.get_value(q[0], 'POPESTIMATE2010'))
    if len(q) == 2:
        """
        The population data has rows that have the aggregate state population data.
        Many state have counties that are the same as the state.
        So in these cases's the correct county population should be the lesser population value.
        """
        x_lat.append(map_df.get_value(j, 'x'))
        y_lon.append(map_df.get_value(j, 'y'))
        county.append(map_df.get_value(j, 'county'))
        state.append(map_df.get_value(j, 'state'))
        county_population = np.min([pop.get_value(q[0], 'POPESTIMATE2010'), pop.get_value(q[1], 'POPESTIMATE2010')])
        population.append(county_population)

map_df = pd.DataFrame({'x': x_lat, 'y': y_lon, 'state': state, 'county': county, 'population': population})
cd_source = ColumnDataSource(map_df)

palette.reverse()
color_mapper = LogColorMapper(palette=palette)

tools = "pan,wheel_zoom,box_zoom,reset,hover,save"
left, right, bottom, top = -126, -67, 25, 50
#left, right, bottom, top = get_map.reasonable_bounds(map_df['x'], map_df['y'])
p = figure(
    title="Example County Plot", tools=tools, x_axis_location=None, y_axis_location=None,
    plot_width=950, plot_height=600, x_range=Range1d(left, right), y_range=Range1d(bottom, top))

p.grid.grid_line_color = None

p.patches('x', 'y', source=cd_source,
          fill_color={'field': 'population', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5)

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("State", "@state"),
    ("County", "@county"),
    ("value", "@population"),
    ("(Long, Lat)", "($x, $y)")]
show(p)
