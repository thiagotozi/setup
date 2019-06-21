

UNIPI_IP = "192.168.0.127"


current = {
    'interval': 0,
    'name': '',
}


CURRENT_PLC_STATE = {}


voltage_history = []
brine_levels = []


settings = {
    'voltage_history': 300,
    'TESTING': False,
    'LOOP_PERIOD_SECONDS': 1,
}


if settings['TESTING']:
    # test settings.
    settings['voltage_history'] = 10
    settings['LOOP_PERIOD_SECONDS'] = 0.1
