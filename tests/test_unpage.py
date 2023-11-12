import unittest
import doctest
import unpage

class TestDoctests(unittest.TestCase):
    def test_doctests(self):
        failures, _ = doctest.testmod(unpage, verbose=False)
        self.assertEqual(failures, 0)

if __name__ == "__main__":
    unittest.main()
