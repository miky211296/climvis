from urllib.request import Request, urlopen
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import windrose
import random
from climvis import core, cfg


def test_get_ts():

    df_cities = pd.read_csv(cfg.world_cities)
    dfi = df_cities.loc[df_cities.Name.str.contains('innsbruck', case=False,
                                                    na=False)].iloc[0]

    df = core.get_cru_timeseries(dfi.Lon, dfi.Lat)
    assert df.grid_point_elevation > 500  # we are in the alps after all
    assert df.distance_to_grid_point < 50000  # we shouldn't be too far

    # It's different data but I wonder how we compare to the
    # Innsbruck climate station we studied a couple of weeks ago?
    url = ('https://raw.githubusercontent.com/fmaussion/'
           'scientific_programming/master/data/innsbruck_temp.json')
    req = urlopen(Request(url)).read()

    # Read the data
    data = json.loads(req.decode('utf-8'))
    for k, v in data.items():
        data[k] = np.array(data[k])

    # select
    t = data['TEMP'][np.nonzero((data['YEAR'] <= 2016))]
    yrs = data['YEAR'][np.nonzero((data['YEAR'] <= 2016))]
    dfs = df.loc[(df.index.year >= yrs.min()) &
                 (df.index.year <= yrs.max())].copy()
    assert len(dfs) == len(yrs)
    dfs['ref'] = t
    dfs = dfs[['tmp', 'ref']]

    # Check that we have good correlations at monthly and annual scales
    assert dfs.corr().values[0, 1] > 0.95
    assert dfs.groupby(dfs.index.year).mean().corr().values[0, 1] > 0.9

    # Check that altitude correction is helping a little
    z_diff = df.grid_point_elevation - dfi.Elevation
    dfs['tmp_cor'] = dfs['tmp'] + z_diff * 0.0065
    dfm = dfs.mean()
    assert np.abs(dfm.ref - dfm.tmp_cor) < np.abs(dfm.ref - dfm.tmp)


def test_get_url():

    df_cities = pd.read_csv(cfg.world_cities)
    dfi = df_cities.loc[df_cities.Name.str.contains('innsbruck', case=False,
                                                    na=False)].iloc[0]

    url = core.get_googlemap_url(dfi.Lon, dfi.Lat)
    assert 'maps.google' in url


def test_write_html(tmpdir):

    df_cities = pd.read_csv(cfg.world_cities)
    dfi = df_cities.loc[df_cities.Name.str.contains('innsbruck', case=False,
                                                    na=False)].iloc[0]

    dir = str(tmpdir.join('html_dir'))
    core.write_html(dfi.Lon, dfi.Lat, directory=dir)
    assert os.path.isdir(dir)


def test_perc_dir_from_data():

    url = core.url_from_input('ellboegen', '3', core.base_url)
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds
                    in data['datumsec']]

    wind_dir_percent = core.perc_dir_from_data(data)
    # check if there is no na value in the computation of percentages
    assert np.all(~np.isnan(list(wind_dir_percent.values())))


def test_max_wind_speed():

    url = core.url_from_input('ellboegen', '3', core.base_url)
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds
                    in data['datumsec']]

    # I want to be sure that the minutes present are not different than
    # [0, 10, 20, 30, 40, 50]
    data['time'] = test_name_to_data()

    # check if nan values are put in the right positions
    removed_index = random.sample(range(1, len(data['time'])-1), 10)
    time = np.delete(data['time'], removed_index)

    check = []
    for i in range(len(time)):
        check.append(time[i].minute)

    possible_minutes = [0, 10, 20, 30, 40, 50]
    position = possible_minutes.index(check[0])

    # get the sequence that has to repeat from the initial datetime minute
    sequence = []

    for i in range(position, position + 6):
        min = possible_minutes[i % 6]
        sequence.append(min)

    position = 0
    # convert to float to insert nan values
    check = np.array(check, dtype=float)
    sequence = np.array(sequence, dtype=float)

    ff = np.array(data['ff'])
    time_array = np.array(time)

    # check if every minute corresponds to the minute in the sequence
    # if not (so there is a jump of ten minutes in check) a nan is inserted
    # the loop ends when it arrives to the last element of array
    i = 0
    while True:

        if not check[i] == sequence[position]:
            check = np.insert(check, i, np.nan)
            time_array = np.insert(time_array, i, np.nan)
            ff = np.insert(ff, i, np.nan)
        if position < 5:
            position += 1
        else:
            position = 0
        i += 1
        try:
            check[i]
        except IndexError:
            break

    nan_indexes = np.argwhere(np.isnan(ff)).tolist()
    # np.argwhere output is a list of lists
    # itertools allows to make a list out of a list of lists
    import itertools
    nan_indexes = list(itertools.chain.from_iterable(nan_indexes))
    assert sorted(removed_index) == nan_indexes


def test_name_to_data():
    url = core.url_from_input('ellboegen', '3', core.base_url)
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds
                    in data['datumsec']]

    check = []
    possible_minutes = [0, 10, 20, 30, 40, 50]

    for i in range(0, len(data['time'])):
        check.append(data['time'][i].minute)

    check = np.array(check)
    boolean = np.isin(check, possible_minutes)

    # check if all the wrong minutes are corrected

    if False in boolean:
        indexes = list(np.where(boolean == False))[0].tolist()
        for i in indexes:
            right_min = data['time'][i].minute * 10
            if right_min < 60:
                data['time'][i] = data['time'][i].replace(minute=right_min)
            else:
                del data['time'][i]
            assert data['time'][i].minute in possible_minutes
    return data['time']


def test_windrose_data():
    url = core.url_from_input('ellboegen', '3', core.base_url)
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds
                    in data['datumsec']]

    fig = plt.figure(figsize=(6, 4))
    ax = core.windrose_data(data['dd'], data['ff'], fig)

    assert type(ax) == windrose.windrose.WindroseAxes


def test_write_html_windrose(tmpdir):

    station, days = 'ellboegen', '3'

    dir = str(tmpdir.join('html_windrose_dir'))
    core.write_html_wind_rose(station, days, directory=dir)
    # check if it exists the directory in which index_windrose.html is created
    assert os.path.isdir(dir)
