import pandas as pd
from utils.indicators import macd, rsi, ema

class MACDRSIEMAStrategy:
    def __init__(self, close: pd.Series):
        self.close = close
        self.indicators = {}
        self.signals = {}
        self.compute_indicators()
        self.compute_signals()

    def compute_indicators(self):
        self.indicators['macd'] = macd(self.close)
        self.indicators['rsi'] = rsi(self.close, 14)
        self.indicators['ema_21'] = ema(self.close, 21)
        self.indicators['ema_55'] = ema(self.close, 55)

    def compute_signals(self):
        macd_df = self.indicators['macd']
        rsi_val = self.indicators['rsi']
        ema_21 = self.indicators['ema_21']
        ema_55 = self.indicators['ema_55']
        price = self.close
        # Long: MACD line crosses above signal, RSI > 50, price above both EMAs
        self.signals['long'] = (
            (macd_df['macd'] > macd_df['signal']) &
            (macd_df['macd'].shift(1) <= macd_df['signal'].shift(1)) &
            (rsi_val > 50) &
            (price > ema_21) & (price > ema_55)
        )
        # Short: MACD line crosses below signal, RSI < 50, price below both EMAs
        self.signals['short'] = (
            (macd_df['macd'] < macd_df['signal']) &
            (macd_df['macd'].shift(1) >= macd_df['signal'].shift(1)) &
            (rsi_val < 50) &
            (price < ema_21) & (price < ema_55)
        )

    def get_signals(self):
        return self.signals

    def get_indicators(self):
        return self.indicators