from tradingbot.risk.atr import position_size


def test_position_size_scaling():
    eq = 1_000_000
    atr = 5.0
    qty = position_size(eq, atr, 0.003)
    assert qty == int((eq * 0.003) / (2 * atr))
