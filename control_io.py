"""
Helper function to control unipi io's.
"""
import logging
import requests
import sys
import washing_state
from washing_state import UNIPI_IP

log = logging.getLogger(__name__)


def load_current_plc_state():
    """
    Load the current state of the PLC.
    """
    url = 'http://{ip}/rest/all'
    url = url.format(ip=UNIPI_IP)
    response = requests.get(url)

    if response.status_code != 200:
        log.debug('unipi could not be found! wrong IP / OFF')
        sys.exit()

    all_values = response.json()
    return all_values


def find_io_by_alias(alias):
    """
    Our program works with aliases

    On the unipi / index.html page there is a configuration tab
    where you can map aliases to the available io's

    This function checks whether the PLC state has been retrieved,
    and that data entries are valid.

    It then returns the io object for the requested alias
    """
    assert washing_state.CURRENT_PLC_STATE

    for unipi_io in washing_state.CURRENT_PLC_STATE:

        if not type(unipi_io) == dict:
            log.error('unipi io %S should be dict, but is not', unipi_io)
            sys.exit(1)

        a = unipi_io.get('alias')
        if a:
            if a == 'al_%s' % alias:
                return unipi_io

    log.debug('unipi alias %s not configured in unipi', alias)
    sys.exit(1)


def set(alias, value):
    io = find_io_by_alias(alias)
    _set_value(io, value)


def _set_value(io, value):
    """

    """
    device = io['dev']
    circuit = io['circuit']

    url = "http://{ip}/rest/{device}/{circuit}"
    url = url.format(ip=UNIPI_IP, device=device, circuit=circuit)

    response = requests.post(url, {'value': value})

    if response.status_code != 200:
        log.debug('io state change failed!! %s %s', value, io)
        sys.exit(1)

    result = response.json().get('result')
    if not result and not result['success']:
        log.debug('unpi fails to act !! %s %s', value, io)
        sys.exit(1)


def _compare_value(io, value):
    return round(value, 0) == round(io['value'], 0)


def match(alias, value):
    io = find_io_by_alias(alias)
    return _compare_value(io, value)


def get(alias):
    """
    Retrieves the variable value for a given alias
    """
    io = find_io_by_alias(alias)
    return io['value']
