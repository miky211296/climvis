#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:34:34 2019

@author: stefano
"""

from urllib.request import Request, urlopen
import json
import numpy as np
from windrose import WindroseAxes
from matplotlib import pyplot as plt
import matplotlib.cm as cm
#import argparse

base_url = 'http://meteo145.uibk.ac.at'
url = 'http://meteo145.uibk.ac.at/innsbruck/3'
# Parse the given url
req = urlopen(Request(url)).read()
# Read the data
data = json.loads(req.decode('utf-8'))

from datetime import datetime, timedelta
data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]

#import matplotlib.pyplot as plt
#plt.plot(data['time'], data['dd'], '.');
#plt.ylabel('Wind direction (°)'); 
#plt.title('Wind direction at Innsbruck');

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
#    midpoints = [i*sector for i in range(0, n_sectors)]
    
    sector_names = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
    
    wind_dir_count = {name: 0 for name in sector_names}
        
    for wind_dir in data['dd']:
        sec = int((wind_dir + int(sector/2)) % 360 / sector)
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
    
    meas_per_hr = 6
    
    ff = np.array(ff)
    ff = ff.reshape(int(len(ff)/meas_per_hr), meas_per_hr)
    ff = ff.mean(axis = 1)
    
    time_array = np.array(time)
    time_array = time_array.reshape(int(len(time_array)/meas_per_hr), 
                                    meas_per_hr)
    time_array = time_array.min(axis = 1)

    max_wind_1hr = {'speed': max(ff), 'time': time_array[ff.argmax()]}    
    
    return max_wind_speed, max_wind_1hr

def name_to_data(station_name, days, base_url = base_url):
    """
    Computes all releveant data to a station given its name.
    
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
            time: datetime
                The time it occured.
        
        second: dict
            dir: str
                The direction (second most frequent).
            time: datetime
                The time it occured.
        
        last: dict
            dir: str
                The direction (least prevailing).
            time: datetime
                The time it occured.
                
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
    """
    url = url_from_input(station_name, days, base_url)
    
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]
    
    directions_percentage = perc_dir_from_data(data)
    sorted_directions = [{'dir': d, 'perc': directions_percentage[d]} 
                         for d in sorted(directions_percentage, 
                                         key=directions_percentage.get,
                                         reverse=True)]
    
    max_wind_speed, max_wind_1hr = max_wind(data['ff'], data['time'])
    
    return {'first': sorted_directions[0], 'second': sorted_directions[1],
            'last': sorted_directions[-1], 'station_name': station_name,
            'days': days, 'max_wind': max_wind_speed,
            'max_wind_1hr': max_wind_1hr}, data
            
    
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
              'the time). The maximum wind speed was {} m/s ' \
              '({} UTC), while the strongest wind speed averaged ' \
              'over an hour was {:.1f} m/s ' \
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
    
#if __name__ == '__main__':
#    
#    possible_stations = ['innsbruck', 'ellboegen', 'obergurgl', 'sattelberg']
#    possible_days = ['1', '3', '7']
#    
#    parser = argparse.ArgumentParser('Returns weather info about stations ' \
#                                     'in and around Innsbruck.')
#    parser.add_argument('days', nargs='?', default='1', 
#                        choices=possible_days, const='1',
#                        help='Specify the number of days.')
#    parser.add_argument('-s', '--station', default='innsbruck',
#                        choices=possible_stations, help='Specify the station.')
#    args = parser.parse_args()
#        
#    directions_and_speed = name_to_data(args.station, args.days)
#    print(direction_message(directions_and_speed))