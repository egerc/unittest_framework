import argparse
import pickle
from utils import load_function_args, load_module, map_args_to_function_outputs



def main(args):
    module = load_module(args.module)
    function_args = load_function_args(args.function_args)
    result = map_args_to_function_outputs(module, function_args)
    with open(args.output, "wb") as file:
        pickle.dump(result, file)
    print(f"Result written to {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map function outputs and save to pickle.")
    parser.add_argument("--module", required=True, help="Path to the Python file (e.g., /path/to/my_module.py)")
    parser.add_argument("--function_args", required=True, help="Path to the Python file containing the 'function_args' dictionary")
    parser.add_argument("--output", required=True, help="Output pickle file path")
    args = parser.parse_args()
    main(args)