#!/usr/bin/env python
# -*- coding: utf-8 -*-

import washing_state
import control_io
import logging
# import time
from washing_state import settings

log = logging.getLogger(__name__)


def brine_interval_check():
    pass


def least_square_slope(v_hist):
    """
    find slope of change in voltage in last
    ~ 300 seconds.

             N Σ(xy) − Σx Σy
     slope = ---------------
             N Σ(x2) − (Σx)2

    source:

    https://www.mathsisfun.com/data/least-squares-regression.html

    to avoid numpy dependency and general geek interest
    """
    N = len(v_hist)
    time = range(1, N+1)
    sumtime = sum(time)

    sumv = sum(v_hist)
    sumxy = sum([t * v for t, v in zip(time, v_hist)])

    sumx2 = sum([x*x for x in time])
    sumtime2 = sumtime * sumtime

    slope = (
        (N * sumxy - sumtime * sumv) /
        (N * sumx2 - sumtime2)
    )

    return slope


def voltage_check():
    """
    Check if voltage history to decide cleaning action
    is needed.

    We take the average of the delta over a period of time.
    """
    # add_current voltage.
    v = control_io.get('measured_stack_voltage')
    voltage_history = washing_state.voltage_history
    voltage_history.append(v)

    hist_seconds = settings['voltage_history']

    if len(voltage_history) < hist_seconds:
        # not enough data to do something.
        return False

    avg_voltage = sum(voltage_history) / len(voltage_history)

    min_voltage = settings['SAFE_VOLTAGE_RANGE'][0]
    if avg_voltage < min_voltage:
        # n0 action needed.
        # start cleaning.
        return False

    max_voltage = settings['SAFE_VOLTAGE_RANGE'][1]
    if avg_voltage > max_voltage:
        # way to high voltage.
        # clean the brine!
        return True

    slope = least_square_slope(washing_state.voltage_history)

    log.debug("AVG DELTA VOLTAGE %s SLOPE %s", avg_voltage, slope)

    if len(voltage_history) > hist_seconds:
        voltage_history.pop(0)

    if slope > 0.0003:
        return True

    return False


def interval_check():
    interval = washing_state.current['interval']
    state = washing_state.current['name']

    # log.debug('INTERVAL: %s', interval)

    if washing_state.settings['TESTING']:
        interval = interval / 10

    if STATES[state]['interval'] > interval:
        return False

    return True


def check_brine_level():
    """
    Fill brine container if needed.

    always returns True.
    """
    value = control_io.get('brine_level')
    bl = washing_state.brine_levels

    bl.append(value)

    if len(bl) < 10:
        return

    if len(bl) > 10:
        bl.pop(0)

    if sum(bl) > 10:
        # stop
        control_io.set('p_brine_level', 0)
        control_io.set('p_brine_level_speed', 0)
    else:
        # refill
        control_io.set('p_brine_level', 0)
        control_io.set('p_brine_level_speed', 10)

    return True


def match_io(possible_io_state):
    for alias, value in possible_io_state.items():
        matched = control_io.match(alias, value)
        if not matched:
            return False

    return True


def match_current_state():
    """
    See a possible state matches the PLC state.
    """
    for state in STATES.keys():
        possible_io_state = STATES[state]['expected']
        if not possible_io_state:
            log.error('NOTHING IN EXPECTED', state)
        if match_io(possible_io_state):
            log.debug('BINGO matched %s', state)
            return state


def change_to(next_state):
    assert next_state
    to_do_io_state = STATES[next_state]['expected']

    for alias, value in to_do_io_state.items():
        control_io.set(alias, value)


def action():
    """
    Decide if all actions condition are OK

    If so, move to next condition.
    """

    state = washing_state.current['name']
    assert type(state) == str
    results = []

    for action in STATES[state]['actions']:
        result_of_action = action()
        results.append(result_of_action)

    log.debug('ACTIONS RESULT %s', results)

    if all(results):
        next_state = STATES[state]["next"]
        log.debug('Change to %s', next_state)
        change_to(next_state)


STATES = {
    "HappyFlow": {
        "expected": {
            "p1": 1,
            "p1_direction": 0,
            "v1": 0,
            "v1-1": 0,
            "v2": 0,
            "v2-1": 0,
            "PSU": 0,   # ON
        },
        "interval": 2,
        "actions": [
            interval_check,
            check_brine_level,
            voltage_check,

        ],
        "next": "StartCleaning"
    },

    "StartCleaning": {
        "expected": {
            "p1": 0,
            "v1": 0,
            "v1-1": 0,
        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "SaveTheBrine",
    },

    "SaveTheBrine": {
        "expected": {},
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],
        "next": "FlushWithAirBrine",
    },

    "FlushWithAirBrine": {
        "expected": {},
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "LoadTheSoap",
    },

    "LoadTheSoap": {
        "expected": {},
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "FlushWithAirSoap",
    },


    "FlushWithAirSoap": {
        "expected": {},
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "LoadTheBrine",
    },

    "LoadTheBrine": {
        "expected": {},
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "GoToHappyFlow",
    },

    "GoToHappyFlow": {
        "expected": {},
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],
        "next": "HappyFlow",
    }
}
