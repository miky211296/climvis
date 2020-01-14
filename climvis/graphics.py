import matplotlib.pyplot as plt
from climvis import core
from scipy.stats import linregress



def plot_annual_cycle(df, filepath=None):

    z = df.grid_point_elevation
    df = df.loc['1981':'2010']
    df = df.groupby(df.index.month).mean()
    df.index = list('JFMAMJJASOND')

    f, ax = plt.subplots(figsize=(6, 4))

    df['pre'].plot(ax=ax, kind='bar', color='C0', label='Precipitation', rot=0)
    ax.set_ylabel('Precipitation (mm mth$^{-1}$)', color='C0')
    ax.tick_params('y', colors='C0')
    ax.set_xlabel('Month')
    ax = ax.twinx()
    df['tmp'].plot(ax=ax, color='C3', label='Temperature')
    ax.set_ylabel('Temperature (°C)', color='C3')
    ax.tick_params('y', colors='C3')
    title = 'Climate diagram at location ({}°, {}°)\nElevation: {} m a.s.l'
    plt.title(title.format(df.lon[0], df.lat[0], int(z)),
              loc='left')
    plt.tight_layout()

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()

    return f


def plot_trend_temp(df, filepath=None):
    """Calculates and plots the annual mean and trend of temperature 
    for the period 1901 - 2018 for this grid point.

    Author
    ------
    Raphael Tasch

    Parameters
    ----------
    df : dataframe

    filepath: str

    Returns
    -------
    f_trend_tmp : shows the annual mean and trend of temperature

    """

    # Gets year array for linregress and plot
    time = df.index
    year = time.year[::12]

    # Gets temperature and reshapes to get annual mean
    tmp = df.values[:, 2]
    tmp_2d = tmp.reshape(len(tmp) // 12, 12)
    tmp_annual = tmp_2d.mean(axis=1)

    # Linregress
    t_slope, t_intercept, t_rvalue, t_pvalue, t_stderr = linregress(year,
                                                                    tmp_annual)
    # Trend calculation
    trend_temp = year * t_slope + t_intercept
    
    #standard for trend
    
    #Confidence intervalls of the trend
    #st.t.interval(0.95, len(tmp_annual)-1, loc=np.mean(tmp_annual), scale=st.sem(tmp_annual))

    # Plot
    f_trend_tmp = plt.figure(figsize=(6, 4))
    plt.plot(year, trend_temp, color='dimgrey',
             label='Trend: {0:.2f} \u00B1 {1:.2f} K per decade'.format(t_slope *10 , t_stderr * 10))
    plt.plot(year, tmp_annual, label='Annual Mean', color='orangered')
    title = 'Temperature trend at location ({}°, {}°)'
    plt.title(title.format(df.lon[0], df.lat[0]), loc='center')
    plt.ylabel('Temperature (°C)')
    plt.xlabel('Years')
    plt.legend(loc='best')
   

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()

    return f_trend_tmp


def plot_trend_prec(df, filepath=None):
    """ Calculates and plots the annual mean and trend of precipitation 
    for the period 1901 - 2018 for this grid point.

    Author
    ------
    Raphael Tasch

    Parameters
    ----------
    df : dataframe

    filepath: str

    Returns
    -------
    f_trend_prc : shows the annual mean and trend of precipitation

    """

    # Gets year array for linregress and plot
    time = df.index
    year = time.year[::12]

    # Gets precipitation and reshapes to get annual mean
    prc = df.values[:, 3]
    prc_2d = prc.reshape(len(prc) // 12, 12)
    prc_annual = prc_2d.mean(axis=1)

    # Linregress
    p_slope, p_intercept, p_rvalue, p_pvalue, p_stderr = linregress(year,
                                                                    prc_annual)
    # Calculates trend
    trend_prec = year * p_slope + p_intercept

    # Plot
    f_trend_prc = plt.figure(figsize=(6, 4))
    plt.plot(year, trend_prec, color='dimgrey',
             label='Trend: {0:.2f} \u00B1 {1:.2f}mm per decade'.format(p_slope * 10, p_stderr * 10))
    plt.plot(year, prc_annual, label='Annual Mean', color='cornflowerblue')
    title = 'Precipitation trend at location ({}°, {}°)'
    plt.title(title.format(df.lon[0], df.lat[0]), loc='center')
    plt.ylabel('Precipitation (mm)')
    plt.xlabel('Years')
    plt.legend(loc='best')
  

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()

    return f_trend_prc


def plot_windrose(wind_direction, wind_speed, filepath=None):
    """creates windrose plot in windrose.png
    Author: Michele
    Parameters
    ----------
    wind_direction: list
        time series of wind direction
    wind_speed: list
        time series of wind speed
    filepath: str, optional
        The path where save the figure
    Returns
    -------
    html file
    """
    fig = plt.figure(figsize=(3, 3))
    # hard-coded: inserting fig as optional parameter, the ax output refers to
    # fig itself.
    ax = core.windrose_data(wind_direction, wind_speed, fig)

    if filepath is not None:
        fig.savefig(filepath, dpi=150)

    return fig


