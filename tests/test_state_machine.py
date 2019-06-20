


# tests.

# import time
import unittest
from unittest import mock
#

from state_machine import least_square_slope


class TestDBWriting(unittest.TestCase):
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


