import pandas as pd
from utils.indicators import bbwp, stochrsi, ema

class BBWPStochRSIStrategy:
    def __init__(self, close: pd.Series):
        self.close = close
        self.indicators = {}
        self.signals = {}
        self.compute_indicators()
        self.compute_signals()

    def compute_indicators(self):
        self.indicators['bbwp_s'] = bbwp(self.close, 13, 252)
        self.indicators['stochrsi'] = stochrsi(self.close, 14)
        self.indicators['ema_9'] = ema(self.close, 9)
        self.indicators['ema_21'] = ema(self.close, 21)
        self.indicators['ema_55'] = ema(self.close, 55)

    def compute_signals(self):
        # Example signal: price above all EMAs and stochrsi > 0.8
        price = self.close
        ema_9 = self.indicators['ema_9']
        ema_21 = self.indicators['ema_21']
        ema_55 = self.indicators['ema_55']
        stoch = self.indicators['stochrsi']
        self.signals['long'] = (price > ema_9) & (ema_9 > ema_21) & (ema_21 > ema_55) & (stoch > 0.8)
        self.signals['short'] = (price < ema_9) & (ema_9 < ema_21) & (ema_21 < ema_55) & (stoch < 0.2)

    def get_signals(self):
        return self.signals

    def get_indicators(self):
        return self.indicators