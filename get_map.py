import pandas as pd
import requests
import os
import itertools
import shapefile
import requests
import numpy as np


def download_map_data(shape_data_file, local_file_path, url):
    """
    Downloads data from us census, unzips it
    :param shape_data_file:
    :param local_file_path:
    :return: map_data, state_strings
    """
    url = url + shape_data_file + ".zip"
    zfile = local_file_path + shape_data_file + ".zip"
    sfile = local_file_path + shape_data_file + ".shp"
    if not os.path.exists(zfile):
        print("Getting file: ", url)
        response = requests.get(url)
        with open(zfile, "wb") as code:
            code.write(response.content)

    if not os.path.exists(sfile):
        uz_cmd = 'unzip ' + zfile + " -d " + local_file_path
        print("Executing command: " + uz_cmd)
        os.system(uz_cmd)


def get_map_data(shape_data_file, local_file_path, province_record_id, state_record_id):
    """
    Sorts the map data into lattiude and longitude shape data for each provience, state
    :param shape_data_file:
    :param local_file_path:
    :param province_record_id:
    :param state_record_id:
    :return: map_data
    """
    sfile = local_file_path + shape_data_file + ".shp"
    dfile = local_file_path + shape_data_file + ".dbf"
    shp = open(sfile, "rb")
    dbf = open(dfile, "rb")
    sf = shapefile.Reader(shp=shp, dbf=dbf)

    lats = []
    lons = []
    province = []
    state = []
    for shprec in sf.shapeRecords():
            #state.append(int(shprec.record[0]))
            #province.append(shprec.record[5])
            #prov_name = str(shprec.record[8])
            #country_name = str(shprec.record[43])
            province.append(shprec.record[province_record_id])  # province means either county or state
            state.append(shprec.record[state_record_id])  # state means either nation or state
            #print('state', state)
            lat, lon = map(list, zip(*shprec.shape.points))
            indices = shprec.shape.parts.tolist()
            lat = [lat[i:j] + [float('NaN')] for i, j in zip(indices, indices[1:]+[None])]
            lon = [lon[i:j] + [float('NaN')] for i, j in zip(indices, indices[1:]+[None])]
            lat = list(itertools.chain.from_iterable(lat))
            lon = list(itertools.chain.from_iterable(lon))
            lats.append(lat)
            lons.append(lon)

    map_data = pd.DataFrame({'x': lats, 'y': lons, 'state': state, 'province': province})
    return map_data


def fix_state_names(dfi):
    """
    Converts the state value in the data frame from and id  to a proper name string
    Throws warning: set on copy
    :param dfi: map data census data frame
    :return: state string array
    """
    st_id = dfi['state']
    sf = pd.read_csv("/home/alex/Documents/data/maps/state_abrev_fip.csv", header=0)
    state_strings = np.ndarray.tolist(np.asarray(sf['state']))
    state_fip = sf.set_index('fip').to_dict()['state']
    for i in range(len(st_id)):
        if int(st_id[i]) in state_fip:
            st_id[i] = state_fip[int(st_id[i])]
    return state_strings


def reasonable_bounds(x, y):
    """
    Finds reasonable bounds for the map plot which preserve a square aspect ratio
    :param x:
    :param y:
    :return: left, right, top, bottom
    """
    x = np.asarray(x)
    y = np.asarray(y)
    left, right, top, bottom = [], [], [], []
    for county in x:
        left.append(np.nanmin(county))
        right.append(np.nanmax(county))
    for county in y:
        top.append(np.nanmax(county))
        bottom.append(np.nanmin(county))
    left = np.nanmin(left)
    right = np.nanmax(right)
    top = np.nanmax(top)
    bottom = np.nanmin(bottom)
    x_center = (left + right) / 2.0
    y_center = (top + bottom) / 2.0
    mr = np.max([right - left, top - bottom])
    right = x_center + mr / 2. + .2
    top = y_center + mr / 2. + .2
    left = x_center - mr / 2. - .2
    bottom = y_center - mr / 2. - .2
    return left, right, bottom, top
