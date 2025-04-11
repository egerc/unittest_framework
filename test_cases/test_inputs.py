# This dict named function_args is mandatory
# the two .py files you want to test need to have identically named functions to those in the function_args dict
whatever = {
    "a": [1,2,3],
    "b": [5,4],
}
whatever1 = {
    "a": [1,2,3],
    "b": [5,4],
    "c": [5,4],
    "d": [5,4],
}


test_inputs = {
    'add': [
        (1, 2), 
        (5, 9)
    ],
    'add_1': [
        (5,), 
        (6,),
        (9,)
    ],
    "map_dict": [
        (sum, whatever),
        (sum, whatever1),
    ]
}