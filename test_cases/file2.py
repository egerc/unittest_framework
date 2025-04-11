def add(x,y):
    return x + y + 1 

def add_1(x):
    return add(x, 2)

def map_dict(func, dict):
    return {key: func(value) + 1 for key, value in dict.items()}