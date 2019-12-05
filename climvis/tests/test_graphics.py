import os
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from climvis import core, cfg, graphics, wind_data
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
import json



def test_annual_cycle(tmpdir):

    df_cities = pd.read_csv(cfg.world_cities)
    dfi = df_cities.loc[df_cities.Name.str.contains('innsbruck', case=False,
                                                    na=False)].iloc[0]
    df = core.get_cru_timeseries(dfi.Lon, dfi.Lat)

    fig = graphics.plot_annual_cycle(df)

    # Check that the text is found in figure
    ref = 'Climate diagram at location (11.25°, 47.25°)'
    test = [ref in t.get_text() for t in fig.findobj(mpl.text.Text)]
    assert np.any(test)

    # Check that figure is created
    fpath = str(tmpdir.join('annual_cycle.png'))
    graphics.plot_annual_cycle(df, filepath=fpath)
    assert os.path.exists(fpath)

    plt.close()

def test_plot_windrose(tmpdir):
    
    url = wind_data.url_from_input('ellboegen', '3', wind_data.base_url)        
    req = urlopen(Request(url)).read()
    data = json.loads(req.decode('utf-8'))
    data['time'] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in data['datumsec']]
    
    direction, wind_speed = data['dd'], data['ff']
    
    # Check that figure is created
    fpath = str(tmpdir.join('windrose.png'))
    graphics.plot_windrose(direction, wind_speed, filepath=fpath)
    assert os.path.exists(fpath)

    plt.close()