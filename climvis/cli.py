import webbrowser
import sys
import climvis

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


def cruvis():
    """Entry point for the cruvis application script"""

    # Minimal code because we don't want to test for sys.argv
    # (we could, but this is too complicated for now)
    cruvis_io(sys.argv[1:])
