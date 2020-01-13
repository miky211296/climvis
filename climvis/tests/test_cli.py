import climvis
import climvis.cli as cli
from unittest.mock import patch


def test_print_version(capsys):

    cli.print_version()
    captured = capsys.readouterr()
    assert climvis.__version__ in captured.out


#@patch('climvis.cli.input', side_effect=['o', 'y'])
#def test_handle_interactive(capsys):
#    cli.handle_interactive(23, 45)
#    captured = capsys.readouterr()
#    assert 'Warning: a blank plot might mean you are over ' in captured.out
#        #assert cli.handle_interactive() == 'expected_output'


def test_cruvis_location(capsys):
    cli.cruvis_location(23, 45, nobrowser=True, interactive=False)
    captured = capsys.readouterr()
    assert 'File successfully generated at: ' in captured.out


def test_windvis_windrose(capsys):
    cli.windvis_windrose('innsbruck', '3', nobrowser=True)
    captured = capsys.readouterr()
    assert 'File successfully generated at: ' in captured.out
    

def test_cruvis_parser(capsys):
    parser = cli.cruvis_parser()
    try:
        arguments = parser.parse_args(['-h'])
    except SystemExit:
        captured = capsys.readouterr()
    assert 'CRU data visualization at' in captured.out
    
    arguments = parser.parse_args(['-i', '-l', '23', '45'])
    assert arguments.interactive is True
    assert arguments.nobrowser is False
    assert arguments.loc is not None
    lon, lat = arguments.loc
    assert lon == 23
    assert lat == 45
    
    arguments = parser.parse_args(['--no-browser', '-l', '23', '45'])
    assert arguments.interactive is False
    assert arguments.nobrowser is True
    assert arguments.loc is not None
    lon, lat = arguments.loc
    assert lon == 23
    assert lat == 45
    
    arguments = parser.parse_args(['-v'])
    captured = capsys.readouterr()
    assert arguments.version is True


def test_windvis_parser(capsys):
    parser = cli.windvis_parser()
    try:
        arguments = parser.parse_args(['-h'])
    except SystemExit:
        captured = capsys.readouterr()
    assert 'wind data visualization at' in captured.out

    arguments = parser.parse_args(['-s', 'innsbruck', '-d',
                                   '3', '--no-browser'])
    assert arguments.station == 'innsbruck'
    assert arguments.days == 3
    assert arguments.nobrowser is True

    arguments = parser.parse_args(['-v'])
    captured = capsys.readouterr()
    assert arguments.version is True
