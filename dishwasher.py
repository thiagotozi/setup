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

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def set_lamps(one, two, three, four):
    # set_io('one', one)
    control_io.set('two', two)
    control_io.set('three', three)
    control_io.set('four', four)


def run_forever(testloops=1):
    """
    Main Loop. Load plc state, execute state machine
    plan, exit on any deviation / error.
    """
    leds = [0, 0, 0, 0]
    last_state = None

    LOOP_PERIOD = washing_state.settings['LOOP_PERIOD_SECONDS']

    while testloops:

        washing_state.CURRENT_PLC_STATE = control_io.load_current_plc_state()
        state = state_machine.match_current_state()

        log.info('CURRENT %s', state)

        if state != last_state:
            log.info('STATE: %s', state)
            last_state = state
            washing_state.current['interval'] = 0
            washing_state.current['name'] = state
        else:
            washing_state.current['interval'] += 1

        if state:
            state_machine.action()
        else:
            msg = (
                "UNIPI is in a unknown STATE. please manualy put it",
                "in the desired state using the /index.html page"
            )
            log.error(msg)
            print(msg)
            sys.exit(1)

        time.sleep(LOOP_PERIOD)
        leds = [1 - x for x in leds]  # noqa
        set_lamps(*leds)

        if washing_state.settings['TESTING']:
            testloops -= 1

    return last_state


if __name__ == '__main__':
    run_forever()
