import pandas as pd
from utils.indicators import bbwp, stochrsi, ema
from utils.builder import StrategyBuilder, IndicatorBlock, SignalBlock

def bbwp_s_block(close):
    return bbwp(close, 13, 252)

def stochrsi_block(close):
    return stochrsi(close, 14)

def ema_9_block(close):
    return ema(close, 9)

def ema_21_block(close):
    return ema(close, 21)

def ema_55_block(close):
    return ema(close, 55)

def long_signal(indicators, price):
    ema_9 = indicators['ema_9']
    ema_21 = indicators['ema_21']
    ema_55 = indicators['ema_55']
    stoch = indicators['stochrsi']
    return (price > ema_9) & (ema_9 > ema_21) & (ema_21 > ema_55) & (stoch > 0.8)

def short_signal(indicators, price):
    ema_9 = indicators['ema_9']
    ema_21 = indicators['ema_21']
    ema_55 = indicators['ema_55']
    stoch = indicators['stochrsi']
    return (price < ema_9) & (ema_9 < ema_21) & (ema_21 < ema_55) & (stoch < 0.2)

class BBWPSRSStrategy_Builder:
    def __init__(self, close: pd.Series):
        self.builder = StrategyBuilder()
        self.builder.add_indicator(IndicatorBlock('bbwp_s', bbwp_s_block))
        self.builder.add_indicator(IndicatorBlock('stochrsi', stochrsi_block))
        self.builder.add_indicator(IndicatorBlock('ema_9', ema_9_block))
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

    def get_indicators(self):
        return self.indicators