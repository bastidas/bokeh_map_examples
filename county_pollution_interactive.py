"""
county_pollution_interactive.py creates a map of pollution in US counties where data is availble
It uses population data from https://www.kaggle.com/sogun3/uspollution, pollution_us_2000_2016.csv
To show and interact with the plot use this command on the CL: bokeh serve --show county_pollution_interactive.py
"""
import pandas as pd
import numpy as np
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper,
    Range1d
)
from bokeh.layouts import row, widgetbox
from bokeh.models import Select, Label, Slider
from bokeh.plotting import curdoc, figure
from bokeh.palettes import brewer
import get_map
palette = brewer['YlGnBu'][9]
palette[8] = '#cccccc'
palette.reverse()

# there is high res and low res map data, choose one
map_high_res = "cb_2015_us_county_500k"
map_low_res = "cb_2015_us_county_20m"
map_file = map_low_res

local_dir = "/home/alex/Documents/data/maps/"  # dir to place the data in
url = "http://www2.census.gov/geo/tiger/GENZ2015/shp/"
get_map.download_map_data(map_file, local_dir, url)
map_df = get_map.get_map_data(map_file, local_dir, 5, 0)
map_df.rename(columns={'province': 'county_name'}, inplace=True)
state_strs = get_map.fix_state_names(map_df)

poll = pd.read_csv("/home/alex/Documents/data/pollution_us_2000_2016.csv")
poll = poll[['State', 'State Code', 'Date Local', 'County', 'CO AQI', 'NO2 AQI', 'O3 AQI', 'SO2 AQI']]
poll['Date Local'] = pd.to_datetime(poll['Date Local'], format='%Y-%m-%d')  # Change date from string to date value
# the data appears to have duplications, this issue should be examined closer
poll = poll.groupby(['State', 'County', 'Date Local']).mean().reset_index()  # hack to average out duplicates, suspect!
yr_splitter = lambda x: x.year
poll['Date Local'] = poll['Date Local'].apply(yr_splitter)
poll.rename(columns={'Date Local': 'Year'}, inplace=True)
poll = poll.groupby(['State', 'County', 'Year']).mean().reset_index()  # hack to average out duplicates, suspect!
pol_strs = ['CO AQI', 'NO2 AQI', 'O3 AQI', 'SO2 AQI']


yrs = poll['Year'].unique()
df_year_array = []
yr_strs = []
for yr in yrs:
    yr_strs.append(str(yr))
    spol = poll[poll['Year'] == yr].reset_index()
    x_lat = []
    y_lon = []
    c_nam = []
    s_nam = []
    p_val1 = []
    p_val2 = []
    p_val3 = []
    p_val4 = []

    for j in map_df.index:
        q = np.intersect1d(np.where(spol['County'] == map_df.get_value(j, 'county_name'))[0],
                           np.where(spol['State'] == map_df.get_value(j, 'state'))[0])
        # what about counties that have the same name as the state?
        if len(q) == 1:
            i = q[0]
            x_lat.append(map_df.get_value(j, 'x'))
            y_lon.append(map_df.get_value(j, 'y'))
            c_nam.append(map_df.get_value(j, 'county_name'))
            s_nam.append(map_df.get_value(j, 'state'))
            p_val1.append(spol.get_value(i, 'CO AQI'))
            p_val2.append(spol.get_value(i, 'SO2 AQI'))
            p_val3.append(spol.get_value(i, 'NO2 AQI'))
            p_val4.append(spol.get_value(i, 'O3 AQI'))
        else:
            x_lat.append(map_df.get_value(j, 'x'))
            y_lon.append(map_df.get_value(j, 'y'))
            c_nam.append(map_df.get_value(j, 'county_name'))
            s_nam.append(map_df.get_value(j, 'state'))
            p_val1.append(0)
            p_val2.append(0)
            p_val3.append(0)
            p_val4.append(0)

    map_df = pd.DataFrame({'x': x_lat, 'y': y_lon, 'state': s_nam, 'county_name': c_nam, 'CO AQI': p_val1,
                           'SO2 AQI': p_val2, 'NO2 AQI': p_val3, 'O3 AQI': p_val4})
    df_year_array.append(map_df)


def create_figure():
    yr_id = np.where(np.asarray(yr_strs) == str(year.value))[0]
    fds = df_year_array[yr_id[0]]
    print('state.value', state.value)
    fds = fds[fds['state'] == state.value]
    p_left, p_right, p_bottom, p_top = get_map.reasonable_bounds(fds['x'], fds['y'])
    pol_id = aqi.value
    print('aqi.value', aqi.value)
    fds = fds[['x', 'y', 'state', 'county_name', pol_id]]
    fds.rename(columns={pol_id: 'pollution'}, inplace=True)
    cd_source = ColumnDataSource(fds)

    p_title = "Pollution " + str(year.value)
    tools = "pan,wheel_zoom,box_zoom,reset,hover,save"
    p = figure(
        title=p_title, tools=tools, x_axis_location=None, y_axis_location=None,
        plot_width=550, plot_height=550, x_range=Range1d(p_left, p_right), y_range=Range1d(p_bottom, p_top))
    p.grid.grid_line_color = None
    color_mapper = LogColorMapper(palette=palette)
    p.patches('x', 'y', source=cd_source, fill_color={'field': 'pollution', 'transform': color_mapper},
              fill_alpha=0.7, line_color="white", line_width=0.5)

    hover = p.select_one(HoverTool)
    hover.point_policy = "follow_mouse"
    hover.tooltips = [("State", "@state"), ("County", "@county_name"), (pol_id, "@pollution")]
    return p


def update(attr, old, new):
    layout.children[1] = create_figure()


year = Select(title='Year', value=yr_strs[0], options=yr_strs)
year.on_change('value', update)
state = Select(title='State', value=state_strs[1], options=state_strs)
state.on_change('value', update)
aqi = Select(title='Air Quality Index', value=pol_strs[0], options=pol_strs)
aqi.on_change('value', update)
controls = widgetbox([year, state, aqi], width=210)
layout = row(controls, create_figure())
curdoc().add_root(layout)
curdoc().title = "US Pollution"
