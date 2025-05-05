import numpy as np
import pandas as pd
import vectorbt as vbt

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def bbwp(series: pd.Series, window: int = 20, lookback: int = 252) -> pd.Series:
    """Calculate Bollinger Band Width Percentile (BBWP)."""
    # Calculate Bollinger Bands
    sma = series.rolling(window=window).mean()
    std_dev = series.rolling(window=window).std()
    upper_band = sma + (2 * std_dev)
    lower_band = sma - (2 * std_dev)

    # Calculate Bollinger Band Width (BBW)
    bbw = (upper_band - lower_band) / sma

    # Calculate Bollinger Band Width Percentile (BBWP)
    # Percentile rank of the current BBW compared to the lookback period
    bbwp_series = bbw.rolling(window=lookback).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=True)
    return bbwp_series

def stochrsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.rolling(window).mean()
    roll_down = down.rolling(window).mean()
    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs))
    stoch = (rsi - rsi.rolling(window).min()) / (rsi.rolling(window).max() - rsi.rolling(window).min())
    return stoch

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return pd.DataFrame({'macd': macd_line, 'signal': signal_line, 'hist': hist})

def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    high_low = high - low
    high_close = (high - close.shift()).abs()
    low_close = (low - close.shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=window, min_periods=window).mean()
    return atr