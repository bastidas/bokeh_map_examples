# [Bokeh Map Examples](https://bastidas.github.io/bokeh_map_examples/)


Map examples using bokeh, custom downloaded map shape files, and data sources including population, pollution, and human development index.

  * county_pollution_interactive.py creates a map of pollution in US countie where data is availble
  It uses population data from https://www.kaggle.com/sogun3/uspollution, pollution_us_2000_2016.csv
  To show and interact with the plot use this command on your CL: bokeh serve `--show county_pollution_interactive.py`

  * county_population.py creates a map of the population in each county
  It uses population data from https://www.kaggle.com/stevepalley/us-county-population/version/1, CO-EST2015-alldata.csv
  [See county population live here.](https://bastidas.github.io/bokeh_map_examples/county_population.html)

  * world_hdi.py creates a map of the world human development index in each country
  It uses population data from https://www.kaggle.com/undp/human-development, human_development.csv. [See world hdi live here.](https://bastidas.github.io/bokeh_map_examples/world_hdi.html)
  
  * state_population.py creates a map of the population in each US state
  It uses population data from https://www.kaggle.com/stevepalley/us-county-population/version/1, CO-EST2015-alldata.csv
  [See state population live here.](https://bastidas.github.io/bokeh_map_examples/state_population.html)

  * get_map.py has tools for downloading custom shape data, loading custom map shape data, preparing data for bokeh plotting, and other custom map making tools.

