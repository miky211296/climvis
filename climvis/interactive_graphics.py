"""A module for plotting interactive graphics using holoviews and bokeh.

This module helps you produce an interactive plot of temperature and 
precipitation data for a given pair of coordinates. Not all places have
available data.

@author: stefano
"""
from climvis import core
import holoviews as hv
import holoviews.plotting.bokeh
from bokeh.plotting import show
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

# Initializing a holoviews renderer. It will be used in the class.
renderer = hv.renderer('bokeh')


def annual_cycle_for_hv(lon, lat, variable='tmp'):
    """Obtaining the annual cycle in a format suitable for holoviews DynamicMap.

    Using the ``get_cru_timeseries`` function of the ``core`` module to get a
    pandas dataframe. The use is for temperature or precipitation.

    Parameters
    ----------
    lon : int or float
        The longitude of the point.
        
    lat : int or float
        The latitude of the point.
        
    variable : {'tmp','pre'}, optional
        The variable for which the data is extracted. Either temperature or
        precipitation.
        
    Returns
    -------
    pandas Series
        The monthly aggregated series on the whole dataset timespan. It
        contains 12 entries.
    """
    df = core.get_cru_timeseries(lon, lat)
    df = df.groupby(df.index.month).mean()
    return df[variable]

def real_lon_lat(lon, lat):
    """Obtaining the real coordinates of the point in the dataset.

    Using the ``get_cru_timeseries`` function of the ``core`` module to get a
    pandas dataframe. It outputs the actual coordinates to which the data refer
    to.

    Parameters
    ----------
    lon : int or float
        The longitude of the point.
        
    lat : int or float
        The latitude of the point.
        
    Returns
    -------
    dict
        Two entries. ``'lon'`` contains the longitude and ``'lat'`` contains
        the latitude.
    """
    df = core.get_cru_timeseries(lon, lat)
    df = df.groupby(df.index.month).mean()
    return {'lon': df['lon'][1], 'lat': df['lat'][1]}

class ClimvisHVPlot:
    """
    A class with holoviews for interactive precipitation and temperature plots.
    
    Multiple methods are present for displaying a static plot as well as
    methods to display dynamic plots through the deployment of a bokeh app.
    
    Parameters
    ----------
    lon : int or float
        The longitutde of the point.
        
    lat : int or float
        The latitude of the point.
        
    overlay : bool, optional
        Defines if the plots of temperature and precipitation should be
        overlayed.
        
    """
    def __init__(self, lon, lat, overlay=False):
        self._lon = lon
        self._lat = lat
        self._overlay = overlay


    def precipitation(self, lon, lat):
        """Creates an **holoviews.Bars** object for precipitation.
        
        Parameters
        ----------
        lon : int or float
            The longitutde of the point.
        
        lat : int or float
            The latitude of the point.
        
        """
        self.reinitialize(lon, lat, self._overlay)
        return hv.Bars(annual_cycle_for_hv(lon, lat, variable='pre'), 
                       ).opts(tools=['hover'])
        
        
    def temperature(self, lon, lat):
        """Creates an **holoviews.Curve** object for temperature.
        
        Parameters
        ----------
        lon : int or float
            The longitutde of the point.
        
        lat : int or float
            The latitude of the point.
        
        """
        self.reinitialize(lon, lat, self._overlay)
        return hv.Curve(annual_cycle_for_hv(lon, lat, variable='tmp'),
                        ).opts(color='red', tools=['hover'])
        
    def combined(self, lon, lat):
        """Combines the temperature and precipitation holoviews objects.
        
        Parameters
        ----------
        lon : int or float
            The longitutde of the point.
        
        lat : int or float
            The latitude of the point.
        
        """
        self.reinitialize(lon, lat, self._overlay)
        curve = hv.Curve(annual_cycle_for_hv(lon, lat, variable='tmp'),
                         ).opts(color='red', tools=['hover'])
        bars = hv.Bars(annual_cycle_for_hv(lon, lat, variable='pre'), 
                       ).opts(tools=['hover'])
        print('Hi')
        if self._overlay:
            out = (bars * curve).opts(xlabel = 'Month', 
                                      ylabel = 'Precipitation and Temperature')
        else:
            out = (bars.opts(xlabel = 'Month', 
                             ylabel = 'Precipitation') + 
                   curve.opts(xlabel = 'Month', 
                              ylabel = 'Temperature'))
                
        #real_lon, real_lat = real_lon_lat(lon, lat).values()
        
        return out
    
    def show_tmp(self):
        show(hv.render(self.temperature(self._lon, self._lat)))
        
    def show_pre(self):
        show(hv.render(self.precipitation(self._lon, self._lat)))
        
    def show_pre_and_tmp(self):
        show(hv.render(self.combined(self._lon, self._lat)))
        
    def reinitialize(self, lon, lat, overlay):
        self.__init__(lon, lat, overlay)
    
    @property    
    def dmap(self):
        hv_dmap = hv.DynamicMap(self.overlay, kdims=[hv.Dimension('lon', range=(-180,180), default=self._lon),
                                                     hv.Dimension('lat', range=(-90,90), default=self._lat)])

        return hv_dmap

    @property
    def app(self):
        return renderer.app(self.dmap)

    def server_show(self):
        
        server = Server({'/': self.app}, port=0)

        server.start()
        server.show('/')
        loop = IOLoop.current()
        try:
            loop.start()
        except KeyboardInterrupt:
            loop.stop()
