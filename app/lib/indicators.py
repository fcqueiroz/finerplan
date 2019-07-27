"""Tendency indicators helper functions"""
import numpy as np
from sklearn.exceptions import NotFittedError


class BaseExponentialSmoothing(object):
    """
    Base class for weighted moving averages with exponential smoothing.
    """
    _min_samples = None

    def __init__(self, alpha) -> None:
        self._alpha = alpha
        self.results = None

    def check_enough_data(self, data) -> None:
        length = len(data)
        if length == 0:
            raise ValueError(f"Data is empty!")
        elif length < self._min_samples:
            raise ValueError(f"There is not enough data to calculate {__class__.__name__}")

    def _recursive_calculation(self, samples):
        raise NotImplementedError

    def fit(self, data) -> None:
        self.check_enough_data(data)
        self._recursive_calculation(data)

    def last(self):
        if self.results is not None:
            return self.results[-1]
        else:
            raise NotFittedError


class ExponentialMovingAverage(BaseExponentialSmoothing):
    """
    Calculates Simple Exponential Moving Average.
    """
    _min_samples = 1

    def _recursive_calculation(self, samples):
        length = len(samples)
        self.results = np.empty(length, dtype=float)

        self.results[0] = samples[0]

        for t in range(self._min_samples, length):
            self.results[t] = self._alpha * samples[t] + (1 - self._alpha) * self.results[t-1]


class DoubleExponentialMovingAverage(BaseExponentialSmoothing):
    """
    Calculates Double Exponential Moving Average.
    """
    _min_samples = 2

    def __init__(self, alpha, beta):
        super().__init__(alpha)
        self._beta = beta

        self._b = None

    def _recursive_calculation(self, samples):
        length = len(samples)
        self.results = np.empty(length, dtype=float)
        self._b = np.empty(length, dtype=float)

        self.results = samples[1]
        self._b = samples[1] - samples[0]

        for t in range(self._min_samples, length):
            self.results[t] = self._alpha * samples[t] + (1 - self._alpha) * (self.results[t-1] + self._b[t-1])
            self._b = self._beta * (self.results[t] - self.results[t-1]) + (1 - self._beta) * self._b[t-1]

    def forecast(self, m):
        """Forecast 'm' periods ahead."""
        return self.last() + m * self._b[-1]
