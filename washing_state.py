
LOOP_PERIOD_SECONDS = 1

UNIPI_IP = "192.168.0.127"


current = {
    'interval': 0,
    'name': '',
}


CURRENT_PLC_STATE = {}


voltage_history = []
brine_levels = []

TESTING = False

settings = {
    'voltage_history_seconds': 300,

}


if TESTING:
    # test settings.
    settings['voltage_history_seconds'] = 10
