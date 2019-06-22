"""
Dishwasher-edstack

A washing program for an Electric Dialysis to prevent cloggage and keep
equiment in working conditions.

We are using a unipi plc with an evok interface to program the cleaning
procedure.

Python 2.7 compatibility.
"""

import sys
import state_machine
import control_io
import time
import logging
import washing_state

logging.getLogger("urllib3").setLevel(logging.WARNING)

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M:%S',
        level=logging.INFO
)

log = logging.getLogger(__name__)


def set_lamps(one, two, three, four):
    control_io.set('one', one)
    # control_io.set('two', two)
    # control_io.set('three', three)
    # control_io.set('four', four)


def run_state_machine(last_state):
    """Run a single iteration of statemachine.

    - load current plc io status.
    - decide whih state we are in.
    - log changes
    - apply actions / checks for current state.
    """
    washing_state.CURRENT_PLC_STATE = control_io.load_current_plc_state()
    state = state_machine.match_current_state()
    error_count = 0

    # log.info('CURRENT %s', state)

    if state != last_state:
        log.info('STATE: %s', state)
        last_state = state
        washing_state.current['interval'] = 0
        washing_state.current['name'] = state
    else:
        washing_state.current['interval'] += 1

    if state:
        state_machine.action()
        error_count += 0
    else:
        error_count += 1
        msg = (
            "UNIPI is in a unknown STATE. please manualy put it",
            "in the desired state using the /index.html page"
            "retying.. %s" % error_count
        )
        log.error(msg)
        print(msg)
        if error_count > 5:
            sys.exit(1)

    return state


def run_forever():
    """
    Main Loop. Load plc state, execute state machine
    plan, exit on any deviation / error.
    """
    leds = [0, 0, 0, 0]
    last_state = None

    LOOP_PERIOD = washing_state.settings['LOOP_PERIOD_SECONDS']

    while True:
        new_state = run_state_machine(last_state)
        last_state = new_state
        # waiting time before continuing.
        time.sleep(LOOP_PERIOD)
        leds = [1 - x for x in leds]  # noqa
        set_lamps(*leds)


if __name__ == '__main__':
    run_forever()
