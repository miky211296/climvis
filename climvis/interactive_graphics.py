"""
@author: stefano
"""
from climvis import core
import pandas as pd
import numpy as np
import holoviews as hv
import holoviews.plotting.bokeh
from bokeh.plotting import show

renderer = hv.renderer('bokeh')

class ClimvisHVPlot:
    """
    A class that has holoviews objects for precipitation and temperature
    
    """
    def __init__(self, lon, lat):
        df = core.get_cru_timeseries(lon, lat)
        df = df.groupby(df.index.month).mean()
        df['month'] = list('JFMAMJJASOND')
        self._df = df
        
        self.temperature = hv.Curve(self._df,
                                    ['time', 'tmp'],
                                    'month'
                                    ).opts(color='red', tools=['hover'])
        self.precipitation = hv.Bars(self._df, 
                                     'time',
                                     'pre'
                                     ).opts(tools=['hover'])
        
    def show_temperature(self):
        show(hv.render(self.temperature))
        
    def show_precipitation(self):
        show(hv.render(self.precipitation))
        
    def show_overlay(self):
        show(hv.render(self.precipitation * self.temperature))
        