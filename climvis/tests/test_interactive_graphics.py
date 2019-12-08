"""Testing the interactive_graphics module.

@author: stefano
"""
import climvis.interactive_graphics as ig
import pandas as pd
import holoviews as hv
import holoviews.plotting.bokeh
import bokeh.application.application
import pytest


def test_renderer():
    assert type(ig.renderer) == hv.plotting.bokeh.renderer.BokehRenderer


# Initializing boundaries for function inputs.
bounds = {'lon': (-180, 180), 'lat': (-90, 90)}


def test_bounds():
    assert ig.bounds == bounds


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

    def test__init__(self):

        with pytest.raises(ValueError,
                           match="Latitude in ClimvisHVPlot.__init__ is out "
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

    def test_precipitation(self):
        with pytest.raises(ValueError,
                           match="Latitude in ClimvisHVPlot.precipitation is "
                           "out of bounds."):
            climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
            climvis_hv_plot.precipitation(0, 250)

        climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
        assert (type(climvis_hv_plot.precipitation(0, 0)) ==
                hv.element.chart.Bars)

    def test_temperature(self):
        with pytest.raises(ValueError,
                           match="Latitude in ClimvisHVPlot.temperature is "
                           "out of bounds."):
            climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
            climvis_hv_plot.temperature(0, 250)

        climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
        assert (type(climvis_hv_plot.temperature(0, 0)) ==
                hv.element.chart.Curve)

    def test_combined(self):
        with pytest.raises(ValueError,
                           match="Latitude in ClimvisHVPlot.combined is "
                           "out of bounds."):
            climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
            climvis_hv_plot.combined(0, 250)

        climvis_hv_plot = ig.ClimvisHVPlot(0, 0, overlay=False)
        assert (type(climvis_hv_plot.combined(0, 0)) ==
                hv.core.layout.Layout)

        climvis_hv_plot.reinitialize(0, 0, overlay=True)
        assert (type(climvis_hv_plot.combined(0, 0)) ==
                hv.core.overlay.Overlay)

# TODO: Tests for the show_tmp show_pre and show_pre_and_tmp needed.

    def test_reinitialize(self):
        with pytest.raises(ValueError,
                           match="Latitude in ClimvisHVPlot.reinitialize is "
                           "out of bounds."):
            climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
            climvis_hv_plot.reinitialize(0, 250, False)

        climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
        climvis_hv_plot.reinitialize(10, 45, True)
        assert climvis_hv_plot._lon == 10
        assert climvis_hv_plot._lat == 45
        assert climvis_hv_plot._overlay

    def test_dmap(self):
        climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
        assert type(climvis_hv_plot.dmap) == hv.core.spaces.DynamicMap

    def test_app(self):
        climvis_hv_plot = ig.ClimvisHVPlot(0, 0)
        assert (type(climvis_hv_plot.app) ==
                bokeh.application.application.Application)

# TODO: test_server_show needed.