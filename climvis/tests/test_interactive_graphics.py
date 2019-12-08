"""Testing the interactive_graphics module.

@author: stefano
"""
from climvis import core
import climvis.interactive_graphics as ig
import pandas as pd
import holoviews as hv
import holoviews.plotting.bokeh
from bokeh.plotting import show
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
import pytest

# Initializing a holoviews renderer. It will be used in the class.
renderer = hv.renderer('bokeh')

# Initializing boundaries for function inputs.
bounds = {'lon': (-180, 180), 'lat': (-90, 90)}


def test_out_of_bounds():
    with pytest.raises(ValueError,
                       match="Longitude and Latitude in out_of_bounds are "
                             "out of bounds."):
        ig.out_of_bounds(250, 250, 'out_of_bounds')

    with pytest.raises(ValueError,
                       match="Longitude in out_of_bounds is out of bounds."):
        ig.out_of_bounds(250, 0, 'out_of_bounds')

    with pytest.raises(ValueError,
                       match="Latitude in out_of_bounds is out of bounds."):
        ig.out_of_bounds(0, 250, 'out_of_bounds')


def test_annual_cycle_for_hv():
    assert (type(ig.annual_cycle_for_hv(0, 0, variable='tmp')) ==
            pd.core.series.Series)

    assert (type(ig.annual_cycle_for_hv(0, 0, variable='pre')) ==
            pd.core.series.Series)

    with pytest.raises(KeyError):
        ig.annual_cycle_for_hv(0, 0, 'foo')

    with pytest.raises(ValueError,
                       match='Latitude in annual_cycle_for_hv '
                             'is out of bounds.'):
        ig.annual_cycle_for_hv(0, 250)


def test_real_lon_lat():
    assert type(ig.real_lon_lat(0, 0)) == dict

    assert tuple(ig.real_lon_lat(10, 45).values()) == (10.25, 45.25)

    with pytest.raises(ValueError,
                       match='Latitude in real_lon_lat is out of bounds.'):
        ig.real_lon_lat(0, 300)


class TestClimvisHVPlot:
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
    def test__init__(self):

        with pytest.raises(ValueError,
                           match="Latitude in ClimvisHVPlot.__init__ is out"
                           "of bounds."):
            climvis_hv_plot = ig.ClimvisHVPlot(0, 250)
        
        climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
        assert climvis_hv_plot._lon == 0
        assert climvis_hv_plot._lat == 0
        assert not climvis_hv_plot._overlay
        
        climvis_hv_plot = ig.ClimvisHVPlot(0, 0, overlay=True)
        assert climvis_hv_plot._lon == 0
        assert climvis_hv_plot._lat == 0
        assert climvis_hv_plot._overlay


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

        # Creating the holoviews Curve and Bars objects for temperature and
        # precipitation respectively
        tmp = hv.Curve(annual_cycle_for_hv(lon, lat, variable='tmp'),
                       ).opts(color='red', tools=['hover'])
        pre = hv.Bars(annual_cycle_for_hv(lon, lat, variable='pre'),
                      ).opts(tools=['hover'])

        # Formatting xlables and ylabels
        if self._overlay:
            out = (pre * tmp).opts(xlabel='Month',
                                   ylabel='Precipitation and Temperature')
        else:
            out = (pre.opts(xlabel='Month',
                            ylabel='Precipitation') +
                   tmp.opts(xlabel='Month',
                            ylabel='Temperature'))

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

        # Starting input-output loop to capture events asynchronously
        loop = IOLoop.current()
        try:
            loop.start()
        except KeyboardInterrupt:
            loop.stop()
