#!/usr/bin/env python
# -*- coding: utf-8 -*-

import washing_state
import control_io
import logging
# import time

log = logging.getLogger(__name__)


def brine_interval_check():
    pass


# def rate_of_change():
#     v_hist = washing_state.voltage_history
#     voltages = zip(v_hist[1::2], v_hist[0::2])
#     delta = [x - y for x, y in voltages]
#     avg_delta = sum(delta) / len(delta)
#     return avg_delta


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
    voltage_history = washing_state.voltage_history
    hist_seconds = washing_state.settings['voltage_history']

    if len(voltage_history) < hist_seconds:
        # not enough data to do something.
        return

    avg_voltage = sum(voltage_history) / len(voltage_history)

    if avg_voltage < 6.0:
        # n0 action needed.
        # start cleaning.
        return False

    slope = least_square_slope(washing_state.voltage_history)

    log.debug("AVG DELTA VOLTAGE %s", avg_voltage)

    if slope > 0.0003:
        return True

    if len(voltage_history) > 300:
        voltage_history.pop(0)


def interval_check():
    interval = washing_state.current['interval']
    state = washing_state.current['name']

    log.debug('INTERVAL: %s', interval)

    if STATES[state]['interval'] > interval:
        return False

    return True


def check_brine_level():
    """
    Fill brine container if needed.

    always returns True.
    """
    value = control_io.get('brine level')
    bl = washing_state.brine_levels

    bl.append(value)

    if len(bl) > 10:
        bl.pop(0)

    if sum(bl) > 10:
        # stop
        control_io.set('p brine level', 0)
        control_io.set('p brine level speed', 0)
    else:
        # refill
        control_io.set('p brine level', 0)
        control_io.set('p brine level speed', 10)

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
            "p1 direction": 0,
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
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],
        "next": "FlushWithAirBrine",
    },

    "FlushWithAirBrine": {
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "LoadTheSoap",
    },

    "LoadTheSoap": {
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "FlushWithAirSoap",
    },


    "FlushWithAirSoap": {
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "LoadTheBrine",
    },

    "LoadTheBrine": {
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],

        "next": "GoToHappyFlow",
    },

    "GoToHappyFlow": {
        "state": {

        },
        "interval": 5,
        "actions": [
            interval_check,
        ],
        "next": "HappyFlow",
    }
}
