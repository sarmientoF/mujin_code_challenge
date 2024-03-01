import unittest
import argparse
from pathPlanning import calculatePath


class TestAdd(unittest.TestCase):
    def test_success(self):
        args = argparse.Namespace(inputyaml='test/configuration_file_success.yaml',
                                  output='test/solution_success.txt', plot=False)

        self.assertEqual(calculatePath(args=args), [[2.0, 2.0], [8.0, 12.0], [
                         60.0, 80.0], [80.0, 90.0], [98.0, 98.0]])

    def test_no_path(self):
        args = argparse.Namespace(inputyaml='test/configuration_file_fail.yaml',
                                  output='test/solution_fail.txt', plot=False)
        with self.assertRaises(ValueError):
            calculatePath(args=args)

    def test_intersect(self):
        args = argparse.Namespace(inputyaml='test/configuration_file_fail_intersect.yaml',
                                  output='test/solution_fail_intersect.txt', plot=False)
        with self.assertRaises(ValueError):
            calculatePath(args=args)


if __name__ == '__main__':
    unittest.main()
