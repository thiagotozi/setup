# test happy flow.

# import time
import os
import json
import unittest
from unittest import mock
#
import dishwasher

from state_machine import least_square_slope

from washing_state import settings


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
    }
}


class MockResponse():
    """Request Session object mocked

    Gives fixtures as response.
    """
    _response_data = {}

    status_code = 200

    def json(self):
        assert self._response_data
        return self._response_data


class TestWasMachine(unittest.TestCase):
    """Test slope test"""

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

    #@mock.patch("requests.post")
    @mock.patch("requests.get")
    def test_happy_flow(self, get_mock):
        """
        test the happy flow situation
        """
        mr1 = MockResponse()
        # post_mr1 = MockResponse()
        get_mock.side_effect = [mr1, mr1]
        # get_mock.side_effect = [mr1]
        filepath = os.path.join('tests', 'fixtures', 'happystate.json')
        with open(filepath) as bla:
            hp_json = json.load(bla)
        mr1._response_data = hp_json
        last_state = dishwasher.run_forever(testloops=1)
        self.assertEqual(last_state, 'HappyFlow')

    def test_voltage_trigger(self, get_mock):

        mr1 = MockResponse()
        # post_mr1 = MockResponse()
        get_mock.side_effect = 10 * [mr1,]
        # get_mock.side_effect = [mr1]
        filepath = os.path.join('tests', 'fixtures', 'happystate.json')
        with open(filepath) as bla:
            hp_json = json.load(bla)
        mr1._response_data = hp_json
        last_state = dishwasher.run_forever(testloops=30)
        self.assertEqual(last_state, 'HappyFlow')


    #def test_washing_procedure(self, get_mock):
    #    """
    #    test trigering of happy flow.
    #    """
    #    mr1 = MockResponse()
    #    mr2 = MockResponse()
    #    mr1.
    #    get_mock.side_effect = [mr, mr]
    #    #
