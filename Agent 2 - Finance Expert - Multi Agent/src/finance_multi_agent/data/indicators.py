from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class IndicatorResult:
    latest: dict[str, float | str | None]
    score: float
    signals: list[str]
    risks: list[str]
    summary: str


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr_components = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1)
    tr = tr_components.max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()

    plus_di = 100 * (plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr.replace(0, np.nan))
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    adx = dx.ewm(alpha=1 / period, adjust=False).mean()
    return adx, plus_di, minus_di, atr


def _bollinger_bandwidth(close: pd.Series, period: int = 20, std_mult: int = 2) -> pd.Series:
    sma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = sma + std_mult * std
    lower = sma - std_mult * std
    return ((upper - lower) / sma.replace(0, np.nan)) * 100


def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff().fillna(0))
    return (direction * volume.fillna(0)).cumsum()


def _vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    pv = typical * df["Volume"]
    return pv.cumsum() / df["Volume"].replace(0, np.nan).cumsum()


def _stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14, smooth: int = 3):
    low_min = low.rolling(period).min()
    high_max = high.rolling(period).max()
    k = 100 * ((close - low_min) / (high_max - low_min).replace(0, np.nan))
    d = k.rolling(smooth).mean()
    return k, d


def _ichimoku_bias(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    conv = (high.rolling(9).max() + low.rolling(9).min()) / 2
    base = (high.rolling(26).max() + low.rolling(26).min()) / 2
    span_a = ((conv + base) / 2).shift(26)
    span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
    bias = pd.Series(index=close.index, dtype="object")
    bias[(close > span_a) & (close > span_b)] = "bullish"
    bias[(close < span_a) & (close < span_b)] = "bearish"
    bias = bias.fillna("neutral")
    return bias


def _supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
    high, low, close = df["High"], df["Low"], df["Close"]
    _, _, _, atr = _adx(high, low, close, period)
    hl2 = (high + low) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    supertrend.iloc[0] = upperband.iloc[0]
    direction.iloc[0] = 1

    for i in range(1, len(df)):
        curr_close = close.iloc[i]
        prev_super = supertrend.iloc[i - 1]
        curr_upper = upperband.iloc[i]
        curr_lower = lowerband.iloc[i]

        if curr_close > prev_super:
            direction.iloc[i] = 1
        elif curr_close < prev_super:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

        if direction.iloc[i] > 0:
            supertrend.iloc[i] = max(curr_lower, prev_super if direction.iloc[i - 1] > 0 else curr_lower)
        else:
            supertrend.iloc[i] = min(curr_upper, prev_super if direction.iloc[i - 1] < 0 else curr_upper)

    return supertrend, direction


def compute_indicators(df: pd.DataFrame) -> IndicatorResult:
    if df.empty or len(df) < 60:
        raise ValueError("Need at least 60 rows of price history to compute advanced indicators reliably.")

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    rsi = _rsi(close)
    ema12 = _ema(close, 12)
    ema26 = _ema(close, 26)
    macd = ema12 - ema26
    signal = _ema(macd, 9)
    hist = macd - signal
    adx, plus_di, minus_di, atr = _adx(high, low, close)
    bb_width = _bollinger_bandwidth(close)
    obv = _obv(close, volume)
    vwap = _vwap(df)
    stoch_k, stoch_d = _stochastic(high, low, close)
    ichi = _ichimoku_bias(high, low, close)
    supertrend, st_dir = _supertrend(df)

    latest = {
        "rsi": _safe_float(rsi.iloc[-1]),
        "macd": _safe_float(macd.iloc[-1]),
        "macd_signal": _safe_float(signal.iloc[-1]),
        "macd_histogram": _safe_float(hist.iloc[-1]),
        "adx": _safe_float(adx.iloc[-1]),
        "plus_di": _safe_float(plus_di.iloc[-1]),
        "minus_di": _safe_float(minus_di.iloc[-1]),
        "bollinger_bandwidth": _safe_float(bb_width.iloc[-1]),
        "atr": _safe_float(atr.iloc[-1]),
        "obv": _safe_float(obv.iloc[-1]),
        "vwap": _safe_float(vwap.iloc[-1]),
        "stoch_k": _safe_float(stoch_k.iloc[-1]),
        "stoch_d": _safe_float(stoch_d.iloc[-1]),
        "ichimoku_bias": str(ichi.iloc[-1]),
        "supertrend": _safe_float(supertrend.iloc[-1]),
    }

    score = 50.0
    signals: list[str] = []
    risks: list[str] = []

    if latest["rsi"] is not None:
        if 50 <= latest["rsi"] <= 70:
            score += 7
            signals.append("RSI is constructive without being deeply overbought.")
        elif latest["rsi"] > 75:
            score -= 5
            risks.append("RSI suggests overbought conditions.")
        elif latest["rsi"] < 35:
            score -= 4
            risks.append("RSI is weak and momentum remains fragile.")

    if latest["macd"] is not None and latest["macd_signal"] is not None:
        if latest["macd"] > latest["macd_signal"]:
            score += 8
            signals.append("MACD is above the signal line.")
        else:
            score -= 8
            risks.append("MACD remains below the signal line.")

    if latest["adx"] is not None and latest["plus_di"] is not None and latest["minus_di"] is not None:
        if latest["adx"] > 20 and latest["plus_di"] > latest["minus_di"]:
            score += 8
            signals.append("ADX confirms an improving uptrend.")
        elif latest["adx"] > 20 and latest["plus_di"] < latest["minus_di"]:
            score -= 8
            risks.append("ADX confirms trend strength, but downside pressure dominates.")

    if latest["stoch_k"] is not None and latest["stoch_d"] is not None:
        if latest["stoch_k"] > latest["stoch_d"] and latest["stoch_k"] < 80:
            score += 4
            signals.append("Stochastic oscillator is crossing up.")
        elif latest["stoch_k"] < latest["stoch_d"]:
            score -= 4
            risks.append("Stochastic oscillator is rolling over.")

    if latest["ichimoku_bias"] == "bullish":
        score += 6
        signals.append("Price structure is above the Ichimoku cloud.")
    elif latest["ichimoku_bias"] == "bearish":
        score -= 6
        risks.append("Price structure is below the Ichimoku cloud.")

    if latest["supertrend"] is not None and close.iloc[-1] > latest["supertrend"]:
        score += 7
        signals.append("Price is above Supertrend support.")
    else:
        score -= 7
        risks.append("Price is below Supertrend resistance.")

    if latest["vwap"] is not None and close.iloc[-1] > latest["vwap"]:
        score += 5
        signals.append("Current price is above VWAP.")
    else:
        score -= 5
        risks.append("Current price is below VWAP.")

    daily_return = ((close.iloc[-1] / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0.0
    avg_volume = volume.tail(20).mean()
    vol_ratio = float(volume.iloc[-1] / avg_volume) if avg_volume and not math.isnan(avg_volume) else 1.0
    if daily_return > 1.5 and vol_ratio > 1.2:
        score += 5
        signals.append("Positive price expansion is supported by volume.")
    elif daily_return < -1.5 and vol_ratio > 1.2:
        score -= 5
        risks.append("Heavy-volume selloff detected today.")

    score = max(0.0, min(100.0, score))
    summary = (
        f"Close {close.iloc[-1]:.2f}; day change {daily_return:.2f}%; volume ratio {vol_ratio:.2f}; "
        f"VWAP {latest['vwap'] if latest['vwap'] is not None else 'n/a'}; "
        f"supertrend {latest['supertrend'] if latest['supertrend'] is not None else 'n/a'}."
    )

    return IndicatorResult(latest=latest, score=score, signals=signals, risks=risks, summary=summary)


def _safe_float(value) -> float | None:
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None
