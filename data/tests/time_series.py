def hours_worked():
    return [7, 2.5, 0, 1.5, 7.5, 1.5]


def hours_worked_ema_smoothed():
    # dict(alpha: [smoothed_values])
    values = {
        0.1: [7.00000, 6.55000, 5.89500, 5.45550, 5.65995, 5.24396],
        0.25: [7.00000, 5.87500, 4.40625, 3.67969, 4.63477, 3.85107]
    }
    return values
