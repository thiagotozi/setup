
parameters = {
    'voltage_history': 300,
    'TESTING': False,
    'LOOP_PERIOD_SECONDS': 1,
    'TRIGGER_SLOPE': 0.0003,
    # Safe voltage range for stack.
    'SAFE_VOLTAGE_RANGE': [6, 9],
    'WAIT_TIME_SLOW_VALVE': 10
}


if parameters['TESTING']:
    # test settings.
    parameters['LOOP_PERIOD_SECONDS'] = 0.1
    parameters['WAIT_TIME_SLOW_VALVE'] = 0.01

DEMO = True


def set_demo():
    parameters['WAIT_TIME_SLOW_VALVE'] = 1.00
    parameters['voltage_history'] = 15


if DEMO:
    set_demo()
