def add(x,y):
    return x + y

def add_1(x):
    return add(x, 1)

def map_dict(func, dict):
    return {key: func(value) for key, value in dict.items()}