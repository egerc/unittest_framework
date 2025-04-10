import argparse
import pickle
import unittest
from utils import load_module, make_test_func


def main(args):
    module = load_module(args.module)
    with open(args.input, "rb") as file:
        stored_results = pickle.load(file)
    
    # Create the TestCase dynamically
    class TestFunctionOutputMapping(unittest.TestCase):
        pass
    
    # Define test functions for each function name and its cases
    for func_name, args_list in stored_results.items():
        test_func = make_test_func(func_name, args_list, module, stored_results, args.fail_fast)
        test_func.__name__ = f"test_{func_name}"
        setattr(TestFunctionOutputMapping, test_func.__name__, test_func)
    
    # Run the tests with the option to stop on the first failure
    unittest.TextTestRunner(failfast=args.fail_fast).run(unittest.TestLoader().loadTestsFromTestCase(TestFunctionOutputMapping))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unit test loaded func results")
    parser.add_argument("--module", required=True, help="Path to the Python file (e.g., /path/to/my_module.py)")
    parser.add_argument("--input", required=True, help="Input pickle file path")
    parser.add_argument("--fail-fast", action="store_true", default=False, help="Stop testing after the first failure")
    
    args = parser.parse_args()
    main(args)