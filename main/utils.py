import hashlib
import importlib
import pickle
from typing import Any, Callable, TypeVar
import importlib.util
import sys
import types

from typing import Any, Mapping, Tuple, List, Dict
import unittest


T = TypeVar("T")
def map_with_args(
    func: Callable[..., T],
    args_list: List[Tuple[Any, ...]]
) -> List[Tuple[Tuple[Any, ...], T]]:
    """
    Maps a list of argument tuples to the results of calling the function with those arguments.
    Args:
        func: The function to call with the arguments.
        args_list: A list of argument tuples to pass to the function.
    Returns:
        A list of tuples where each item is (args, result).
    """
    return [(args, func(*args)) for args in args_list]

def map_args_to_function_outputs(
        module: types.ModuleType,
        test_inputs: Dict[str, List[Tuple[Any, ...]]]
) -> Dict[str, List[Tuple[Tuple[Any, ...], Any]]]:
    """
    Applies a modules functions to the test inputs
    Args:
        module: The imported file storing the functions
        test_inputs: The dictionary planning the test cases
    Returns:
        A Dictionary of function names and the stored function arguments and results according to test_inputs
    """
    return {
        func_name: map_with_args(getattr(module, func_name), args_list)
        for func_name, args_list in test_inputs.items()
    }

def load_test_inputs(test_inputs_path: str) -> Dict[str, List[Tuple[Any, ...]]]:
    """
    Dynamically loads the test_inputs dictionary from a Python file.
    
    Args:
        test_inputs_path: Path to the Python file containing `test_inputs`.

    Returns:
        test_inputs: The dictionary containing function names and argument tuples.
    """
    try:
        spec = importlib.util.spec_from_file_location("test_inputs_module", test_inputs_path)
        if spec is None:
            raise FileNotFoundError(f"Could not find the file: {test_inputs_path}")
        
        test_inputs_module = importlib.util.module_from_spec(spec)
        sys.modules["test_inputs_module"] = test_inputs_module
        
        if spec.loader:
            spec.loader.exec_module(test_inputs_module)
        else:
            raise ImportError(f"Could not load the module from {test_inputs_path}")
        
        if not hasattr(test_inputs_module, "test_inputs"):
            raise AttributeError(f"{test_inputs_path} must define a 'test_inputs' dictionary.")
        
        return test_inputs_module.test_inputs
    except Exception as e:
        print(f"Error loading test_inputs from file: {e}")
        raise e

def load_module(module_path: str) -> types.ModuleType:
    """
    Loads a Python module from a given file path.
    
    Args:
        module_path: The path to the Python file.
    
    Returns:
        The loaded module.
    
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ImportError: If the module cannot be loaded.
    """
    try:
        module_spec = importlib.util.spec_from_file_location("module", module_path)
        if module_spec is None:
            raise FileNotFoundError(f"Module at {module_path} not found.")
        
        module = importlib.util.module_from_spec(module_spec)
        sys.modules["module"] = module
        
        if module_spec.loader:
            module_spec.loader.exec_module(module)
        else:
            raise ImportError(f"Could not load the module from {module_path}")
        
        return module
    except Exception as e:
        print(f"Error: Could not load the module from file '{module_path}'")
        raise e


def hash_object(obj: Any) -> str:
    """
    Returns an MD5 hash of a pickled Python object.

    Args:
        obj: The object to hash.

    Returns:
        A string representing the MD5 hash.
    """
    return hashlib.md5(pickle.dumps(obj)).hexdigest()

def make_test_func(
    func_name: str,
    cases: List[Tuple],
    module: object,
    stored_results: Dict[str, List[Tuple[Tuple[Any, ...], Any]]],
    fail_fast: bool
) -> Callable[[unittest.TestCase], None]:
    """
    Creates a test function for a specific function in the module that compares its output
    to stored results for a list of argument tuples.

    Args:
        func_name (str): The name of the function in the module to test.
        cases (List[Tuple]): A list of argument tuples to test the function with.
        module (object): The module that contains the function to test.
        stored_results (Dict[str, Dict[Tuple, Any]]): A dictionary containing expected outputs
                                                      for each function and argument tuple.
        fail_fast (bool): If True, stop running tests after the first failure.

    Returns:
        Callable[[unittest.TestCase], None]: A test function that compares the actual output of the function
                                             with the expected output for each argument tuple.
    """
    def test(self: unittest.TestCase) -> None:
        # Track if there were any assertion failures
        failures = []

        for args, expected in cases:
            with self.subTest(func=func_name, args=args):
                actual = getattr(module, func_name)(*args)

                try:
                    # Attempt to directly compare the actual and expected values
                    self.assertEqual(actual, expected,
                        msg=f"\nFunction: {func_name}\nArgs: {args}\nExpected: {expected}\nGot: {actual}")
                except AssertionError as e:
                    # If there's a failure, record it
                    failures.append(f"\nAssertion failed for {func_name} with args {args}: {e}")
                except NotImplementedError:
                    # If equality comparison is not implemented (e.g., for AnnData), compare hashes instead
                    try:
                        self.assertEqual(hash_object(actual), hash_object(expected),
                            msg=f"\nFunction: {func_name}\nArgs: {args}\nExpected hash: {hash_object(expected)}\nGot hash: {hash_object(actual)}")
                    except AssertionError as e:
                        # If hash comparison fails, record it
                        failures.append(f"Hash comparison failed for {func_name} with args {args}: {e}")

            if fail_fast and failures:
                # If we're failing fast, stop after the first failure
                break

        # If there were any failures, output them after all tests have run
        if failures:
            for failure in failures:
                print(failure)
            self.fail("One or more tests failed.")

    return test