"""
ETA calculations
"""

import time
import datetime


class ETACalculator():
    """
    A wrapper class to time the execution of some statement
    and calculate the estimated time of arrival
    """

    def __init__(self, num_iterations):
        self.num_iterations = num_iterations
        self.reset()

    def reset(self):
        self.mean = 0
        self.n = 0

    def execute(self, i, func, args={}, verbose=True):
        # measure execution time
        start = time.clock()
        retval = func(**args)
        elapsed = time.clock() - start

        # calculate eta
        self.n += 1
        self.mean += (elapsed - self.mean) / self.n
        eta = self.mean * (self.num_iterations - self.n)

        if verbose:
            print("Execution took {} (ETA: {})"
                  .format(datetime.timedelta(seconds=elapsed), datetime.timedelta(seconds=eta)))

        return retval
