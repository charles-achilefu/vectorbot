import pandas as pd
from utils.indicators import macd, rsi, ema
from utils.builder import StrategyBuilder, IndicatorBlock, SignalBlock

def macd_block(close):
    return macd(close)

def rsi_block(close):
    return rsi(close, 14)

def ema_21_block(close):
    return ema(close, 21)

def ema_55_block(close):
    return ema(close, 55)

def long_signal(indicators, price):
    macd_df = indicators['macd']
    rsi_val = indicators['rsi']
    ema_21 = indicators['ema_21']
    ema_55 = indicators['ema_55']
    return (
        (macd_df['macd'] > macd_df['signal']) &
        (macd_df['macd'].shift(1) <= macd_df['signal'].shift(1)) &
        (rsi_val > 50) &
        (price > ema_21) & (price > ema_55)
    )

def short_signal(indicators, price):
    macd_df = indicators['macd']
    rsi_val = indicators['rsi']
    ema_21 = indicators['ema_21']
    ema_55 = indicators['ema_55']
    return (
        (macd_df['macd'] < macd_df['signal']) &
        (macd_df['macd'].shift(1) >= macd_df['signal'].shift(1)) &
        (rsi_val < 50) &
        (price < ema_21) & (price < ema_55)
    )

class MACDRSIEMAStrategy_Builder:
    def __init__(self, close: pd.Series):
        self.builder = StrategyBuilder()
        self.builder.add_indicator(IndicatorBlock('macd', macd_block))
        self.builder.add_indicator(IndicatorBlock('rsi', rsi_block))
        self.builder.add_indicator(IndicatorBlock('ema_21', ema_21_block))
        self.builder.add_indicator(IndicatorBlock('ema_55', ema_55_block))
        self.builder.add_signal(SignalBlock('long', long_signal))
        self.builder.add_signal(SignalBlock('short', short_signal))
        # Removed backtest execution from constructor
        self.indicators = None
        self.signals = None

    def run_backtest(self, close):
        self.indicators, self.signals = self.builder.backtest(close)
        return self.indicators, self.signals

    def get_signals(self):
        return self.signals

    def get_indicators(self):
        return self.indicators