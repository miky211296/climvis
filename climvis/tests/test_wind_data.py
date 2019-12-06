#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 09:23:57 2019

@author: michele211296
"""
from climvis import wind_data
from urllib.request import Request, urlopen
#from urllib.error import URLError
from datetime import datetime, timedelta
import numpy as np
from matplotlib import pyplot as plt
import windrose
#import sys
import json
import random

#possible_stations = ['innsbruck', 'ellboegen', 'obergurgl', 'sattelberg']
#possible_days = ['1', '3', '7']
#random_station = random.sample(possible_stations, 1)[0]
#random_days = random.sample(possible_days, 1)[0]
#
#url = wind_data.url_from_input(random_station, random_days, wind_data.base_url)        
#try:
#    req = urlopen(Request(url)).read()
#except URLError:
#    sys.exit('cannot reach the website. Check the connection.')

#data = json.loads(req.decode('utf-8'))
#data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]

def test_perc_dir_from_data():
    
    url = wind_data.url_from_input('ellboegen', '3', wind_data.base_url)        
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]
    
    wind_dir_percent = wind_data.perc_dir_from_data(data)
    #check if there is no na value in the computation of percentages
    assert np.all(~np.isnan(list(wind_dir_percent.values())))
    
def test_max_wind_speed():
    
    url = wind_data.url_from_input('ellboegen', '3', wind_data.base_url)        
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]
    
    #I want to be sure that the minutes present are not different than
    #[0, 10, 20, 30, 40, 50]
    data['time'] = test_name_to_data()
    
    #check if nan values are put in the right positions
    removed_index = random.sample(range(0, len(data['time'])), 10)
    time = np.delete(data['time'], removed_index)
    
    check = []
    for i in range(0,len(time)):
            check.append(time[i].minute)
            
    possible_minutes = [0, 10, 20, 30, 40, 50]
    position = possible_minutes.index(check[0])
    
    #get the sequence that has to repeat from the initial datetime minute
    sequence = []
    
    for i in range(position, position + 6):
         min = possible_minutes[i%6]
         sequence.append(min)
    
    position = 0
    #convert to float to insert nan values
    check = np.array(check, dtype = float)
    sequence = np.array(sequence, dtype = float)
    
    ff = np.array(data['ff'])
    time_array = np.array(time)
    
    #check if every minute corresponds to the minute in the sequence
    #if not (so there is a jump of ten minutes in check) a nan is inserted
    #the loop ends when it arrives to the last element of array
    i= 0
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
            x = check[i]
        except:
            break
        
    nan_indexes = np.argwhere(np.isnan(ff)).tolist()
    #np.argwhere output is a list of lists
    #itertools allows to make a list out of a list of lists
    import itertools
    nan_indexes = list(itertools.chain.from_iterable(nan_indexes))
    assert sorted(removed_index) == nan_indexes
    
def test_name_to_data():
    url = wind_data.url_from_input('ellboegen', '3', wind_data.base_url)        
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]
    
    check = []
    possible_minutes = [0,10,20,30,40,50]
    
    for i in range(0,len(data['time'])):
        check.append(data['time'][i].minute)
        
    check = np.array(check)
    bool = np.isin(check, possible_minutes)
    
    #check if all the wrong minutes are corrected 
    
    if False in bool:
        indexes = list(np.where(bool == False))[0].tolist()
        for i in indexes:
            right_min = data['time'][i].minute * 10
            if right_min < 60: #sometimes
                data['time'][i] = data['time'][i].replace(minute = right_min)
            else:
                del data['time'][i]
            assert data['time'][i].minute in possible_minutes
    return data['time']
    
def test_windrose_data():
    url = wind_data.url_from_input('ellboegen', '3', wind_data.base_url)        
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]
    
    fig = plt.figure(figsize=(6,4))
    ax = wind_data.windrose_data(data['dd'], data['ff'], fig)
    
    assert type(ax) == windrose.windrose.WindroseAxes
    
    