import webbrowser
import sys
import climvis
import argparse

#aggiungere nell HELP windrose: windrose visualization for selected station
# and number of days
HELP = """cruvis: CRU data visualization at a selected location.

Usage:
   -h, --help            : print the help
   -v, --version         : print the installed version
   -l, --loc [LON] [LAT] : the location at which the climate data must be
                           extracted
   -w, --windrose [STATION] [DAYS]: windrose at one of the possible stations 
                                    and for one of the possible days.       
                                    possible_stations : ['innsbruck',
                                    'ellboegen', 'obergurgl', 'sattelberg']
                                    possible_days :['1', '3', '7']                        
   --no-browser          : the default behavior is to open a browser with the
                           newly generated visualisation. Set to ignore
                           and print the path to the html file instead
   Required packages: motionless, windrose                        
"""


def cruvis_io(args):
    """The actual command line tool.

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    """

    if len(args) == 0:
        print(HELP)
    elif args[0] in ['-h', '--help']:
        print(HELP)
    elif args[0] in ['-v', '--version']:
        print('cruvis: ' + climvis.__version__)
        print('License: public domain')
        print('cruvis is provided "as is", without warranty of any kind')
        #TODO: GESTIONE ARGOMENTI DA IMPLEMENTARE: per ora ho messo abbastanza
        #a caso per vedere che funzionasse
    elif args[0] in ['-l', '--loc'] and args[3] in ['-w', '--windrose']:
        if len(args) < 3:
            print('cruvis --loc needs lon and lat parameters!')
            return
        lon, lat = float(args[1]), float(args[2])
        html_path = climvis.write_html(lon, lat)
        station, days = args[4], args[5] 
        html_path_windrose = climvis.write_html_wind_rose(station, days)
        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab(html_path)
            #open browser page for windrose
            webbrowser.get().open_new_tab(html_path_windrose)
    else:
        print('cruvis: command not understood. '
              'Type "cruvis --help" for usage options.')


def print_version():
    print('cruvis: ' + climvis.__version__)
    print('License: public domain')
    print('cruvis is provided "as is", without warranty of any kind')
    
def cruvis_location(lon, lat, nobrowser):
    html_path = climvis.write_html(lon, lat)
    if nobrowser:
        print('File successfully generated at: ' + html_path)
    else:
        webbrowser.get().open_new_tab(html_path)
        
def cruvis_windrose(station, days, nobrowser):
    html_path_windrose = climvis.write_html_wind_rose(station, days)
    if nobrowser:
        print('File successfully generated at: ' + html_path_windrose)
    else:
        webbrowser.get().open_new_tab(html_path_windrose)
    
def cruvis():
    """Entry point for the cruvis application script"""

    parser = argparse.ArgumentParser(prog = 'cruvis',
                                     description = 'CRU data visualization at a selected location.')

    parser.add_argument('-v','--version', action='store_const', const=True,
                        default=False, help='print the installed version')
    parser.add_argument('-l', '--loc', nargs=2, metavar=('LON', 'LAT'), type=int,
                        help='the location at which the climate data must be extracted')
    parser.add_argument('-w', '--windrose', nargs=2, metavar=('STATION', 'DAYS'),
                        help="windrose at one of the possible stations" \
                             "and for one of the possible days." \
                             "possible_stations : ['innsbruck', " \
                             "ellboegen', 'obergurgl', 'sattelberg']" \
                             "possible_days :['1', '3', '7']")
    parser.add_argument('--no-browser', action='store_const', const=True,
                        dest='nobrowser',
                        default=False, help='the default behavior is to open ' \
                                            'a browser with the newly ' \
                                            'generated visualisation. Set to ' \
                                            'ignore and print the path to ' \
                                            'the html file instead')
    
    arguments = parser.parse_args()
    
    if arguments.version:
        print_version()
    
    if arguments.loc is not None:
        lon, lat = arguments.loc
        cruvis_location(lon, lat, arguments.nobrowser)
        
    if arguments.windrose is not None:
        station, days = arguments.windrose
        cruvis_windrose(station, days, arguments.nobrowser)