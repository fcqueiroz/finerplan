from pytest import approx

from app.lib.indicators import ExponentialMovingAverage, DoubleExponentialMovingAverage

from tests.data.time_series import hours_worked, hours_worked_ema_smoothed


def test_ema_last():
    for my_alpha in hours_worked_ema_smoothed().keys():
        ema = ExponentialMovingAverage(alpha=my_alpha)

        ema.fit(data=hours_worked())
        assert approx(ema.last(), rel=1e-5) == hours_worked_ema_smoothed()[my_alpha][-1]


def test_dema_last():
    for my_alpha in hours_worked_ema_smoothed().keys():
        ema = DoubleExponentialMovingAverage(alpha=my_alpha, beta=my_beta)

        ema.fit(data=hours_worked())
        assert approx(ema.last(), rel=1e-5) == hours_worked_ema_smoothed()[my_alpha][-1]
