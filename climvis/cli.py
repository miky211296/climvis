import webbrowser
import sys
import climvis
import climvis.interactive_graphics as ig
import argparse


def print_version():
    print('cruvis: ' + climvis.__version__)
    print('License: public domain')
    print('cruvis is provided "as is", without warranty of any kind')


def handle_interactive(lon, lat):
    while True:
        choice = input('Do you want to overlay or have adjacent plots?\n'
                       'Warning: if overlay is selected the lateral axis '
                       'is in common. [O/a] (q for exiting) ')
        if choice in ('O', 'o', 'overlay', 'Overlay', ''):
            hv_climvis_plot = ig.ClimvisHVPlot(lon, lat, overlay=True)
            break
        elif choice in ('A', 'a', 'Adjacent', 'adjacent'):
            hv_climvis_plot = ig.ClimvisHVPlot(lon, lat, overlay=False)
            break
        elif choice in ('Q', 'q'):
            sys.exit()

    while True:
        choice = input('Do you want to proceed with the plotting?\n'
                       'Warning: a new webpage will be opened. Retrieving data'
                       ' might take a while so please be patient.\n'
                       'Warning: a blank plot might mean you are over '
                       'the ocean.\n\n'
                       'Proceed? [Y/n] ')
        if choice in ('Y', 'y', 'Yes', 'yes', ''):
            print('For exiting use KeyboardInterrupt\n')
            hv_climvis_plot.server_show()
            sys.exit()
        elif choice in ('N', 'n', 'No', 'no', 'Q', 'q', 'Quit', 'quit'):
            sys.exit()


def cruvis_location(lon, lat, nobrowser, interactive):
    html_path = climvis.write_html(lon, lat)
    if nobrowser:
        print('File successfully generated at: ' + html_path)
    elif interactive:
        handle_interactive(lon, lat)
    else:
        webbrowser.get().open_new_tab(html_path)


def windvis_windrose(station, days, nobrowser):
    html_path_windrose = climvis.write_html_wind_rose(station, days)
    if nobrowser:
        print('File successfully generated at: ' + html_path_windrose)
    else:
        webbrowser.get().open_new_tab(html_path_windrose)


def cruvis():
    """Entry point for the cruvis application script"""
    # Implemented by Stefano
    parser = argparse.ArgumentParser(prog='cruvis',
                                     description="CRU data visualization at"
                                     "a selected location.",
                                     epilog="also possible to call windvis "
                                     "for windrose data visualization")

    parser.add_argument('-v', '--version', action='store_const', const=True,
                        default=False, help='print the installed version')
    parser.add_argument('-l', '--loc', nargs=2, metavar=('LON', 'LAT'),
                        type=int, help='the location at which the climate data'
                        ' must be extracted')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--no-browser', action='store_const', const=True,
                       dest='nobrowser',
                       default=False, help='the default behavior is to open '
                                           'a browser with the newly '
                                           'generated visualisation. Set to '
                                           'ignore and print the path to '
                                           'the html file instead')

    group.add_argument('-i',
                       '--interactive',
                       action='store_const',
                       dest='interactive',
                       const=True,
                       default=False,
                       help='Plot an interactive plot only of temperature'
                            ' and precipitation at the given location.\n'
                            'Warning: it might be slow.')

    arguments = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    if arguments.version:
        print_version()

    if arguments.loc is not None:
        lon, lat = arguments.loc
        cruvis_location(lon, lat, arguments.nobrowser, arguments.interactive)


def windvis():
    """Entry point for the windvis application script"""
    # Implemented by Michele
    possible_stations = ['innsbruck', 'ellboegen', 'obergurgl', 'sattelberg']
    possible_days = ['1', '3', '7']
    windparser = argparse.ArgumentParser(prog='windvis',
                                         description="wind data visualization "
                                         "at a selected station for a selected"
                                         " number of days.",
                                         epilog="also possible to call cruvis "
                                         "for CRU data visualization")
    windparser.add_argument('-v', '--version', action='store_const',
                            const=True, default=False,
                            help='print the installed version')

    windparser.add_argument('-s', '--station', default='innsbruck',
                            choices=possible_stations,
                            help='Specify the station.')
    windparser.add_argument('-d', '--days', default='innsbruck',
                            choices=possible_days, help='Specify the days.')
    windparser.add_argument('--no-browser', action='store_const', const=True,
                            dest='nobrowser',
                            default=False,
                            help='the default behavior is to open '
                            'a browser with the newly '
                            'generated visualisation. Set to '
                            'ignore and print the path to '
                            'the html file instead.')

    arguments = windparser.parse_args()
    if len(sys.argv) < 2:
        windparser.print_help()
        sys.exit(0)

    if arguments.version:
        print_version()

    if arguments.station and arguments.days is not None:
        station, days = arguments.station, arguments.days
        windvis_windrose(station, days, arguments.nobrowser)
        