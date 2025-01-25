import time
import numpy as np
from statistics import mean, stdev
from functools import wraps

class TimerDecorator:
    def __init__(self):
        self.times = []

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            self.times.append(elapsed_time)
            return result
        return wrapper

    def stats(self):
        if not self.times:
            raise ValueError('No recordings')
        print('Time stats:')
        print(f'{len(self.times) = }')
        print(f'{mean(self.times) = }')
        print(f'{min(self.times) = }')
        print(f'{max(self.times) = }')
        print(f'{stdev(self.times) = }')
        

timer = TimerDecorator()

@timer
def long_time_function():
    np.random.seed(123)
    matrix = np.random.rand(1000, 1000)
    return np.linalg.svd(matrix)

for _ in range(13):
    long_time_function()

timer.stats()