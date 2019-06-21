

UNIPI_IP = "192.168.0.127"


current = {
    'interval': 0,
    'name': '',
}


CURRENT_PLC_STATE = {}


voltage_history = []
brine_levels = []


def reset():
    voltage_history.clear()
    brine_levels.clear()


settings = {
    'voltage_history': 300,
    'TESTING': False,
    'LOOP_PERIOD_SECONDS': 1,
    'TRIGGER_SLOPE': 0.0003,
    # Safe voltage range for stack.
    'SAFE_VOLTAGE_RANGE': [6, 9],
    'WAIT_TIME_SLOW_VALVE': 10
}


if settings['TESTING']:
    # test settings.
    settings['LOOP_PERIOD_SECONDS'] = 0.1
    settings['WAIT_TIME_SLOW_VALVE'] = 0.01

    # settings['voltage_history'] = 0.1
