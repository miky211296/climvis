import climvis
import climvis.cli as cli
from unittest.mock import patch


def test_print_version(capsys):

    cli.print_version()
    captured = capsys.readouterr()
    assert climvis.__version__ in captured.out


@patch('climvis.cli.input', side_effect=['o', 'y'])
def test_handle_interactive(capsys):
    cli.handle_interactive(23, 45)
    captured = capsys.readouterr()
    assert 'Warning: a blank plot might mean you are over ' in captured.out
        #assert cli.handle_interactive() == 'expected_output'


def test_cruvis_location(capsys):
    cli.cruvis_location(23, 45, nobrowser=True, interactive=False)
    captured = capsys.readouterr()
    assert 'File successfully generated at: ' in captured.out


def test_windvis_windrose(capsys):
    cli.windvis_windrose('innsbruck', '3', nobrowser=True)
    captured = capsys.readouterr()
    assert 'File successfully generated at: ' in captured.out
    
@patch('climvis.cli.input', side_effect=['-h']) 
def test_cruvis(capsys):
    cli.cruvis()
    captured = capsys.readouterr()
    assert 'CRU data visualization at' in captured.out
#def test_print_html(capsys):
#
#    cruvis_io(['-l', '12.1', '47.3', '--no-browser'])
#    captured = capsys.readouterr()
#    assert 'File successfully generated at:' in captured.out
#
#
#def test_error(capsys):
#
#    cruvis_io(['-l', '12.1'])
#    captured = capsys.readouterr()
#    assert 'cruvis --loc needs lon and lat parameters!' in captured.out
