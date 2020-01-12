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
hv.extension('bokeh')
renderer = hv.renderer('bokeh')

# Initializing boundaries for function inputs.
bounds = {'lon': (-180, 180), 'lat': (-90, 90)}


def out_of_bounds(lon, lat, method_or_function_name):
    """Checks if longitude and latitude are within the right interval.

    This function will check if longitude and latitude were supplied correctly
    otherwise it raises informative errors.

    Parameters
    ----------
    lon : int or float
        The longitude of the point.

    lat : int or float
        The latitude of the point.

    method_or_function_name : str
        The name of the method or function within whick this function is being
        called. Hellps give informative messages.

    Raises
    ------
    ValueError
        If either longitude or latitude or both are out of bounds.

    """
    out_of_bounds_vars = {'lon': not (bounds['lon'][0] <=
                                      lon <=
                                      bounds['lon'][1]),
                          'lat': not (bounds['lat'][0] <=
                                      lat <=
                                      bounds['lat'][1])}

    if tuple(out_of_bounds_vars.values()) == (True, True):
        error_message = 'Longitude and Latitude in {} are out of bounds.'
    elif tuple(out_of_bounds_vars.values()) == (True, False):
        error_message = 'Longitude in {} is out of bounds.'
    elif tuple(out_of_bounds_vars.values()) == (False, True):
        error_message = 'Latitude in {} is out of bounds.'
    else:
        error_message = None

    if error_message is not None:
        raise ValueError(error_message.format(method_or_function_name))


def annual_cycle_for_hv(lon, lat, variable='tmp'):
    """Obtaining the annual cycle in a holoviews DynamicMap suitable format.

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
    # Check if supplied longitude and latitude are within bounds.
    out_of_bounds(lon, lat, 'annual_cycle_for_hv')

    # Get the timeseries as pandas dataframe and output just one column
    # corresponding to the desired variable.
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
    # Check if supplied longitude and latitude are within bounds.
    out_of_bounds(lon, lat, 'real_lon_lat')

    # Get the real longitude and latitude for which the data are being
    # extracted.
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
        The longitutde of the point. It's also the default parameter shown if
        you choose to deploy the bokeh app provided you didn't reinitialize
        the object.

    lat : int or float
        The latitude of the point. It's also the default parameter shown if
        you choose to deploy the bokeh app provided you didn't reinitialize
        the object.

    overlay : bool, optional
        Defines if the plots of temperature and precipitation should be
        overlayed.

    Raises
    ------
    ValueError
        If either longitude or latitude or both are out of bounds.

    See Also
    --------
    reinitialize : Object reinitialization.
    server_show : Interactive plotting with default parameters as initialized.
    out_of_bounds : Checks if longitude and latitude are out of bounds.

    """
    def __init__(self, lon, lat, overlay=False):
        # Check if supplied longitude and latitude are within bounds.
        out_of_bounds(lon, lat, 'ClimvisHVPlot.__init__')

        # Initialize the hidden attributes.
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

        Raises
        ------
        ValueError
            If either longitude or latitude or both are out of bounds.

        See Also
        --------
        out_of_bounds : Checks if longitude and latitude are out of bounds.

        """
        out_of_bounds(lon, lat, 'ClimvisHVPlot.precipitation')
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

        Raises
        ------
        ValueError
            If either longitude or latitude or both are out of bounds.

        See Also
        --------
        out_of_bounds : Checks if longitude and latitude are out of bounds.

        """
        out_of_bounds(lon, lat, 'ClimvisHVPlot.temperature')
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

        Returns
        -------
        out : holoviews Layout or Overlay
            Layout or overlay depends on how the object was initialized.

        Raises
        ------
        ValueError
            If either longitude or latitude or both are out of bounds.

        See Also
        --------
        out_of_bounds : Checks if longitude and latitude are out of bounds.

        """
        out_of_bounds(lon, lat, 'ClimvisHVPlot.combined')
        self.reinitialize(lon, lat, self._overlay)

        real_coords = real_lon_lat(lon, lat)
        real_lon = real_coords['lon']
        real_lat = real_coords['lat']

        # Creating the holoviews Curve and Bars objects for temperature and
        # precipitation respectively
        tmp = hv.Curve(annual_cycle_for_hv(lon, lat, variable='tmp'),
                       label='Real lon, lat: {} {}'.format(real_lon,
                                                           real_lat)
                       ).opts(color='red', tools=['hover'])
        pre = hv.Bars(annual_cycle_for_hv(lon, lat, variable='pre'),
                      ).opts(tools=['hover'])

        # Formatting xlables and ylabels
        if self._overlay:
            out = hv.Overlay([pre, tmp.relabel('')],
                             label='Real lon, lat: {} {}'.format(real_lon,
                                                                 real_lat))
            out.opts(xlabel='Month',
                     ylabel='Prec. and Temp. '
                            '(°C and mm mth^-1)')

        else:
            out = hv.Layout([tmp.opts(xlabel='Month',
                                      ylabel='Temperature (°C)'),
                             pre.opts(xlabel='Month',
                             ylabel='Precipitation (mm mth^-1)')])

        return out

    def show_tmp(self):
        """Opens the webbrowser and shows the annual temperature cycle.

        Renders the holoviews curve of temperature in a new webpage.
        """
        show(hv.render(self.temperature(self._lon, self._lat)))

    def show_pre(self):
        """Opens the webbrowser and shows the annual precipitation cycle.

        Renders the holoviews bars of precipitation in a new webpage.
        """
        show(hv.render(self.precipitation(self._lon, self._lat)))

    def show_pre_and_tmp(self):
        """Shows the annual temperature and precipitation cycle.

        Renders the holoviews curve of temperature and the holoviews bars of
        precipitation in a new webpage.
        """
        show(hv.render(self.combined(self._lon, self._lat)))

    def reinitialize(self, lon, lat, overlay):
        """Reinitialization method.

        Reinitializes the object.

        Raises
        ------
        ValueError
            If either longitude or latitude or both are out of bounds.

        See Also
        --------
        out_of_bounds : Checks if longitude and latitude are out of bounds.

        """
        out_of_bounds(lon, lat, 'ClimvisHVPlot.reinitialize')
        self.__init__(lon, lat, overlay)

    @property
    def dmap(self):
        """Outputs DynamicMap of the combination of the two annual datasets.

        It takes a holoviews Layout or a holoviews Overlay and creates a
        holoviews DynamicMap.

        See Also
        --------
        combined : combining temperature and pressure data for plotting

        """
        hv_dmap = hv.DynamicMap(self.combined,
                                kdims=[hv.Dimension('lon',
                                                    range=(-180, 180),
                                                    default=self._lon),
                                       hv.Dimension('lat',
                                                    range=(-90, 90),
                                                    default=self._lat)]
                                )
        
#        real_coords = real_lon_lat(self._lon, self._lat)
#        real_lon = real_coords['lon']
#        real_lat = real_coords['lat']        
#                           
#        hv_dmap.opts(title='New title for Overlay {} {}'.format(real_lon, real_lat))

        return hv_dmap

    @property
    def app(self):
        """Creates a bokeh app from a holoviews DynamiMap

        Returns
        -------
        bokeh App
            A bokeh app obtained from the holoviews DynamicMap.

        See Also
        --------
        dmap : Holoviews DynamicMap

        """
        return renderer.app(self.dmap)

    def server_show(self):
        """Deploys the bokeh app on a bokeh server.

        Opens a new webpage for the bokeh app corresponding to the object.
        A tornado.ioloop.IOLoop is started.

        Notes
        -----
        Might raise warnings if run from ipython or jupyter

        """
        # Bokeh server setup
        server = Server({'/': self.app}, port=0)
        server.start()
        server.show('/')

        # Starting input-output loop to capture events asynchronously.
        # KeyboardInterrupt stops the loop.
        loop = IOLoop.current()
        try:
            loop.start()
        except KeyboardInterrupt:
            loop.stop()
