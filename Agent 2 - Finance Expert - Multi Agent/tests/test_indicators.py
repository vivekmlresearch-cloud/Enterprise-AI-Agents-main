import numpy as np
import pandas as pd

from finance_multi_agent.data.indicators import compute_indicators


def test_compute_indicators_basic():
    rows = 120
    base = np.linspace(100, 140, rows)
    df = pd.DataFrame(
        {
            "Open": base,
            "High": base + 1,
            "Low": base - 1,
            "Close": base + 0.5,
            "Volume": np.linspace(100000, 200000, rows),
        }
    )
    result = compute_indicators(df)
    assert 0 <= result.score <= 100
    assert "rsi" in result.latest
    assert "supertrend" in result.latest
