

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
