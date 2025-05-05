import numpy as np
import pandas as pd
import vectorbt as vbt

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def bbwp(series: pd.Series, window: int = 13, lookback: int = 252) -> pd.Series:
    # Placeholder for BBWP calculation
    # Replace with actual BBWP logic as needed
    return (series.rolling(window).max() - series.rolling(window).min()) / series.rolling(lookback).std()

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