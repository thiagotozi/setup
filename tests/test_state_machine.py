# test happy flow.

# import time
import os
import json
import unittest
import random
from unittest import mock
#
import dishwasher

from state_machine import least_square_slope
from state_machine import voltage_check

from washing_state import settings
import washing_state


settings['TESTING'] = True

default_io_ok = {
    "result": {
        # "glob_dev_id": 1,
        # "unit": "V",
        # "value": -0.0003083001356571913,
        # "circuit": "3_04",
        # "alias": "al_TEST_VOLTAGE_INPUT",
        # "range_modes": ["0.0", "2.5", "10.0"],
        # "modes": ["Voltage", "Current", "Resistance"],
        # "range": "10.0", "dev": "ai", "mode": "Voltage"},
        "success": True,
    },
}

UNI_PI_STATE = {}


class GetResponse():
    """Unipi Respone object mocked

    Gives fixtures as response.

    - can simulate voltage change.
    """
    _response_data = []
    v_slope_increase = 0.0125
    status_code = 200
    voltage_increase = False
    voltage_io = None
    command_count = 0

    def _set_voltage_io(self):
        for item in self._response_data:
            alias = item.get('alias')
            if alias == 'al_measured_stack_voltage':
                self.voltage_io = item

    def load_fixture(self, name='happystate.json'):
        # Load fixtures in mocks.
        filepath = os.path.join('tests', 'fixtures', name)

        with open(filepath) as bla:
            hp_json = json.load(bla)
        self._response_data = hp_json

    def json(self):
        assert self._response_data

        if self.voltage_increase:
            self.update_voltage()

        return self._response_data

    def update_voltage(self):
        """Update voltage with randomish slope"""
        if not self.voltage_io:
            self._set_voltage_io()

        mv = self.voltage_io['value']
        self.voltage_io['value'] = \
            mv + self.v_slope_increase * random.random()

    def set_post_mock(self, post_mock):
        """
        post mock recieves commands send to the plc
        from the state machine.
        """
        self.post_mock = post_mock

    def handle_commands(self):
        """Execute new commands recieved on the post_mock"""
        if not self.post_mock:
            raise Exception('self.post_mock is not set')

        call_list = self.post_mock.call_args_list
        new_commands = call_list[self.command_count:]
        for call in new_commands:
            url = call[0][0]
            value = call[0][1]['value']
            self.handle_update(url, value)
            self.command_count += 1

    def handle_update(self, url, value):
        device, circuit = url.split('rest/')[1].split('/')
        for io_item in self._response_data:
            if io_item['dev'] != device:
                continue
            if io_item['circuit'] != circuit:
                continue
            # we found our device!
            io_item['value'] = value
            return


class PostResponse():
    """Default response when of unipi when changeing a value.
    """

    status_code = 200
    _response_data = default_io_ok

    def json(self):
        # check what we where called with last
        # and change the value?
        return self._response_data


class TestWasMachine(unittest.TestCase):
    """Test statemachine"""

    def test_least_square_slope(self):
        """Test slope function
        """

        test_array_0 = [1, 1.1, 0.9, 1.4, 1.2]
        self.assertEqual(
            round(least_square_slope(test_array_0), 2),
            0.07
        )

        test_array_3 = [0, 3.1, 6.9, 8.4, 12.2]
        self.assertEqual(
            round(least_square_slope(test_array_3), 2),
            2.97
        )

    @mock.patch("requests.get")
    def test_happy_flow(self, get_mock):
        """
        test the happy flow situation
        """
        unipi = GetResponse()
        get_mock.side_effect = [unipi, unipi]
        # get_mock.side_effect = [unipi]
        filepath = os.path.join('tests', 'fixtures', 'happystate.json')
        with open(filepath) as bla:
            hp_json = json.load(bla)
        unipi._response_data = hp_json
        last_state = dishwasher.run_state_machine(None)
        self.assertEqual(last_state, 'HappyFlow')

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_voltage_trigger(self, post_mock, get_mock):

        test_loops = settings['voltage_history'] + 1

        v_slope = 4.8 * settings['TRIGGER_SLOPE']
        # class variable.

        unipi = GetResponse()
        unipi.v_slope_increase = v_slope
        unipi.voltage_increase = True

        unipost = PostResponse()
        post_mock.return_value = unipost
        unipost._response_data = default_io_ok
        get_mock.return_value = unipi
        # load default fixture. io / unipi begin state.
        unipi.load_fixture()
        unipi.set_post_mock(post_mock)

        for i in range(test_loops):
            last_state = dishwasher.run_state_machine('HappyFlow')
            # process commands loaded in unipost
            unipi.handle_commands()

        v_hist = washing_state.voltage_history
        self.assertTrue(
            least_square_slope(v_hist) > settings['TRIGGER_SLOPE']
        )

        self.assertTrue(voltage_check())
        assert(last_state == 'StartCleaning')

        washing_state.reset()

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_no_trigger(self, post_mock, get_mock):
        test_loops = settings['voltage_history'] + 1

        assert len(washing_state.voltage_history) == 1
        # should be to low to ever trigger
        v_slope = 0.00001
        unipi = GetResponse()
        unipi.v_slope_increase = v_slope
        unipi.voltage_increase = True

        unipost = PostResponse()
        post_mock.return_value = unipost
        unipost._response_data = default_io_ok
        get_mock.return_value = unipi
        # load default fixture. io / unipi begin state.
        unipi.load_fixture()
        unipi.set_post_mock(post_mock)

        for i in range(test_loops):
            last_state = dishwasher.run_state_machine('HappyFlow')
            # process commands loaded in unipost
            unipi.handle_commands()

        v_hist = washing_state.voltage_history

        # nothing should be triggered.
        assert least_square_slope(v_hist) < settings['TRIGGER_SLOPE']
        self.assertFalse(voltage_check())
        self.assertEqual(last_state, 'HappyFlow')

        washing_state.reset()

        # def test_washing_procedure(self, get_mock):
    #    """
    #    test trigering of happy flow.
    #    """
    #    mr1 = MockResponse()
    #    mr2 = MockResponse()
    #    mr1.
    #    get_mock.side_effect = [mr, mr]
    #    #
