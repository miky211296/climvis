#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:34:34 2019

@author: Michele
"""

from urllib.request import Request, urlopen
from urllib.error import URLError
import sys
import json
import numpy as np
import warnings
with  warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    from windrose import WindroseAxes

#from matplotlib import pyplot as plt
#import matplotlib.cm as cm
#import argparse

base_url = 'http://meteo145.uibk.ac.at'
url = 'http://meteo145.uibk.ac.at/innsbruck/3'

# Parse the given url
try:
    req = urlopen(Request(url)).read()
except URLError:
    sys.exit('cannot reach the website. Check the connection.') 

# Read the data
data = json.loads(req.decode('utf-8'))

from datetime import datetime, timedelta
data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for
                ds in data['datumsec']]

def url_from_input(station_name, days, base_url):
    """
    Returns a nicely formatted url.
    
    Arguments
    ---------
    station_name: str
        The name of the station. All lowercase.
        
    days: str
        The number of days.
    
    base_url: str
        The base of the url.
        
    Returns
    -------
    nice_url: str
        Nicely formatted url.
    """
    return base_url + '/' + station_name + '/' + days

def perc_dir_from_data(data):
    """
    Returns the percentage of prevalence for each sector given raw wind data.
    
    Arguments
    ---------
    data: list of float
        The raw wind directions for every 10 min. Float with precision of 1.
        
    Returns
    -------
    wind_dir_percent: dict
        Dictionary of the wind direction percentages. Keys are the 8 sectors.
        e.g. 'N'. Values are the percentages.
    """
    n_sectors = 8
    sector = 360/n_sectors
    
    sector_names = ['N', 'NE', 'E', 'SE', 'S', 'SW','W', 'NW']
    
    wind_dir_count = {name: 0 for name in sector_names}
    
    #count how many wind data directions fall in a certain sector    
    for wind_dir in data['dd']:
        sec = int(((wind_dir + int(sector/2)) % 360) / sector)
        wind_dir_count[sector_names[sec]] += 1

    total_counts = sum(wind_dir_count.values())
    
    wind_dir_percent = {}
    
    for wind_dir in wind_dir_count:
        wind_dir_percent[wind_dir] = wind_dir_count[wind_dir] / total_counts * 100

    return wind_dir_percent

def max_wind(ff, time):
    """
    Computes the max wind speed and the max wind speed on 1hr averages.
    
    Arguments
    ---------
    ff: list
        List of speeds in m/s.
    time: list
        List of datetime stamps.
        
    Returns
    -------
    max_wind_speed: dict
        speed: maximum speed
        time: the time it occured as datetime
    
    max_wind_1hr: dict
        speed: maximum speed on 1hr averages
        time: the time it occured as datetime (time is the beginning of the
        hour)
    """
    max_wind_speed = {'speed': max(ff), 'time': time[ff.index(max(ff))]}
    
    #It could happen that some data are missing in a hour. In order to handle
    #with this issue, I introduce nan values in the variables time and ff:
    #in time because I want to display the right associated datetime to the
    #max 1hour windspeed; in ff because I don't want to average windspeed
    #for those hours in which nans occur.
    
    #Get the initial datetime minute
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
    
    ff = np.array(ff)
    time_array = np.array(time)
    
    #check if every minute corresponds to the minute in the sequence
    #if not (so there is a jump of ten minutes in check) a nan is 
    # inserted
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
    
    meas_per_hr = 6
    #it may happen some wind data are in excess and don't complete a hour
    less_than_one_hour = np.arange(1,6)
    #how many data don't complete a hour ?
    remainder = len(ff)%meas_per_hr 
    #if I have some data that don't complete a hour
    if remainder != 0:
        #save the extra-data
        partial_data = ff[-remainder:]
        partial_time = time_array[-remainder:]
        #Remove those extra-data from ff and time_array
        ff = ff[:-remainder]
        time_array = time_array[:-remainder]
        
    ff = ff.reshape(int(len(ff)/meas_per_hr), meas_per_hr)
    nan_counter = np.isnan(ff).sum(1)
    ff = np.nanmean(ff[np.where(nan_counter == 0)], axis = 1)
    
    time_array = time_array.reshape(int(len(time_array)/meas_per_hr), 
                              meas_per_hr)
    time_array = np.nanmax(time_array[np.where(nan_counter == 0)], axis = 1)
    
    #If I miss only 1 or 2 data to complete the hour, I consider them anyway
    if remainder in less_than_one_hour[-2:]:
        partial_data = partial_data.mean()
        np.append(ff,partial_data)
        np.append(time_array,partial_time.max())
     
    max_wind_1hr = {'speed': max(ff), 'time': time_array[ff.argmax()]}    
    
    return max_wind_speed, max_wind_1hr

def name_to_data(station_name, days, base_url = base_url):
    """
    Computes all releveant wind data in a station given the name and the
    number of days
    
    Arguments
    ---------
    station_name: str
        The station name.
    
    days: str
        The number of days.
    
    base_url: str, optional
        The base url of the data.
        
    Returns
    -------
    wind_data: dict
        first: dict
            dir: str
                The direction (most frequent).
            perc: float
                percentage of occurrance.
        
        second: dict
            dir: str
                The direction (second most frequent).
            perc: float
                percentage of occurrance.
        
        last: dict
            dir: str
                The direction (least prevailing).
            perc: float
                percentage of occurrance.
                
        station_name: str
            The station name.
        
        days: str
            The number of days.
        
        max_wind: dict
            speed: float
                The max windspeed.
            time: datetime
                The time it occured.
                
        max_wind_1hr: dict
            speed: float
                The max windspeed on 1hr averages.
            time: datetime
                The time it occured (timestamp at the beginning of the hour).
    
    data: dict
        ff: list
            wind speed
        dd: list
            wind direction
        time: datatime
            The time of occurrance
                   
    """
    url = url_from_input(station_name, days, base_url)        
    try:
        req = urlopen(Request(url)).read()
    except URLError:
        sys.exit('cannot reach the website. Check the connection.')
    
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]
    
    #check if minutes are represented in tens: for example sometimes I noticed
    #that the last 10 was replaced by 1 and I noticed also the presence of a 54
    #after 50. Eventhough the website seems to solve the conversion later 
    #in time, for that instant I needed in anycase to correct it. 
    #This problem was noticed with the ellboegen station, but I am
    #not totally sure if it didn't occur also for the other stations. So I 
    #implemented the code for a general station
    check = []
    possible_minutes = [0,10,20,30,40,50]
    
    for i in range(0,len(data['time'])):
        check.append(data['time'][i].minute)
        
    check = np.array(check)
    bool = np.isin(check, possible_minutes)
    
    if False in bool:
        indexes = list(np.where(bool == False))[0].tolist()
        for i in indexes:
            right_min = data['time'][i].minute * 10
            if right_min < 60:
                data['time'][i] = data['time'][i].replace(minute = right_min)
            else:
                del data['time'][i]
                
    directions_percentage = perc_dir_from_data(data)
    sorted_directions = [{'dir': d, 'perc': directions_percentage[d]} 
                         for d in sorted(directions_percentage, 
                                         key=directions_percentage.get,
                                         reverse=True)]
    
    max_wind_speed, max_wind_1hr = max_wind(data['ff'], data['time'])
    
    relevant_wind_data = {'first': sorted_directions[0], 'second': sorted_directions[1],
            'last': sorted_directions[-1], 'station_name': station_name,
            'days': days, 'max_wind': max_wind_speed,
            'max_wind_1hr': max_wind_1hr}
    
    data = {'ff': data['ff'], 'dd': data['dd'], 'time': data['time']}
    
    return relevant_wind_data, data
            
def windrose_data(wind_direction, wind_speed, figure):
    """
    Creates a windrose plot
    
    Arguments
    ---------
    wind_direction: list
        wind direction time series
        
    wind_speed: list
        wind speed time series
        
    figure: matplotlib.figure.Figure
        figure on which windrose is plotted
    
    Returns
    -------
    message: str
        The nicely formatted message.
    """
    ax = WindroseAxes.from_ax(fig = figure)
    ax.bar(wind_direction, wind_speed, normed=True, opening=1, edgecolor='white',
           nsector = 8)
    ax.set_legend(loc = "best", prop={'size': 5})
    return ax
    
def direction_message(prevailing_directions_and_speed_dict):
    """
    Creates a nicely formatted message with all the data.
    
    Arguments
    ---------
    prevailing_directions_and_speed_dict: dict
        The output of name_to_data
    
    Returns
    -------
    message: str
        The nicely formatted message.
    """
    data_dict = prevailing_directions_and_speed_dict
    message = 'At station {}, over the last {} days, the dominant ' \
              'wind direction was {} ({:.1f}% of the time). The second most ' \
              'dominant wind direction was {} ({:.1f}% of the time), ' \
              'the least dominant wind direction was {} ({:.2f}% of ' \
              'the time). The maximum wind speed was {:.2f} m/s ' \
              '({} UTC), while the strongest wind speed averaged ' \
              'over an hour was {:.2f} m/s ' \
              '({} UTC).'.format(data_dict['station_name'], 
                                        data_dict['days'],
                                        data_dict['first']['dir'],
                                        data_dict['first']['perc'],
                                        data_dict['second']['dir'],
                                        data_dict['second']['perc'],
                                        data_dict['last']['dir'],
                                        data_dict['last']['perc'],
                                        data_dict['max_wind']['speed'],
                                        data_dict['max_wind']['time'],
                                        data_dict['max_wind_1hr']['speed'],
                                        data_dict['max_wind_1hr']['time'])
              
    return message