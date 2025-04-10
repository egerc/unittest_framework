import argparse
import pickle
import unittest
from utils import load_module, make_test_func


def main(args):
    module = load_module(args.module)
    with open(args.input, "rb") as file:
        stored_results = pickle.load(file)
    class TestFunctionOutputMapping(unittest.TestCase):
        pass
    for func_name, args_list in stored_results.items():
        test_func = make_test_func(func_name, args_list, module, stored_results)
        test_func.__name__ = f"test_{func_name}"
        setattr(TestFunctionOutputMapping, test_func.__name__, test_func)
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestFunctionOutputMapping))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unit test loaded func results")
    parser.add_argument("--module", required=True, help="Path to the Python file (e.g., /path/to/my_module.py)")
    parser.add_argument("--input", required=True, help="Input pickle file path")
    args = parser.parse_args()
    main(args)