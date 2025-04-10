import importlib
from typing import Any, Callable
import importlib.util
import sys
import types

from typing import Any, Mapping, Tuple, List, Dict
import unittest


def map_args_to_function_outputs(
    module: types.ModuleType,
    function_args: Mapping[str, List[Tuple[Any, ...]]]
) -> Dict[str, Dict[Tuple[Any, ...], Any]]:
    """
    Executes multiple functions from a module with provided argument tuples.
    """
    return {
        func_name: {
            args: getattr(module, func_name)(*args) for args in arg_list
        }
        for func_name, arg_list in function_args.items()
    }

def load_function_args(function_args_path: str) -> Dict[str, List[Tuple[Any, ...]]]:
    """
    Dynamically loads the function_args dictionary from a Python file.
    
    Args:
        function_args_path: Path to the Python file containing `function_args`.

    Returns:
        function_args: The dictionary containing function names and argument tuples.
    """
    try:
        spec = importlib.util.spec_from_file_location("function_args_module", function_args_path)
        if spec is None:
            raise FileNotFoundError(f"Could not find the file: {function_args_path}")
        
        function_args_module = importlib.util.module_from_spec(spec)
        sys.modules["function_args_module"] = function_args_module
        
        if spec.loader:
            spec.loader.exec_module(function_args_module)
        else:
            raise ImportError(f"Could not load the module from {function_args_path}")
        
        if not hasattr(function_args_module, "function_args"):
            raise AttributeError(f"{function_args_path} must define a 'function_args' dictionary.")
        
        return function_args_module.function_args
    except Exception as e:
        print(f"Error loading function_args from file: {e}")
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


def make_test_func(
    func_name: str,
    cases: List[Tuple],
    module: object,
    stored_results: Dict[str, Dict[Tuple, Any]]
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

    Returns:
        Callable[[unittest.TestCase], None]: A test function that compares the actual output of the function
                                             with the expected output for each argument tuple.
    """
    def test(self: unittest.TestCase) -> None:
        for args in cases:
            with self.subTest(func=func_name, args=args):
                actual = getattr(module, func_name)(*args)
                expected = stored_results[func_name][args]
                self.assertEqual(
                    actual, expected,
                    msg=f"\nFunction: {func_name}\nArgs: {args}\nExpected: {expected}\nGot: {actual}"
                )

    return test