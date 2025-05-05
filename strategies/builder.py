import pandas as pd

class IndicatorBlock:
    def __init__(self, name, func):
        self.name = name
        self.func = func
    def compute(self, close):
        return self.func(close)

class SignalBlock:
    def __init__(self, name, func):
        self.name = name
        self.func = func
    def compute(self, indicators, price):
        return self.func(indicators, price)

class StrategyBuilder:
    def __init__(self):
        self.indicator_blocks = []
        self.signal_blocks = []
    def add_indicator(self, block):
        self.indicator_blocks.append(block)
        return self
    def add_signal(self, block):
        self.signal_blocks.append(block)
        return self
    def compute_indicators(self, close):
        indicators = {}
        for block in self.indicator_blocks:
            indicators[block.name] = block.compute(close)
        return indicators
    def compute_signals(self, indicators, price):
        signals = {}
        for block in self.signal_blocks:
            signals[block.name] = block.compute(indicators, price)
        return signals
    def backtest(self, close):
        indicators = self.compute_indicators(close)
        signals = self.compute_signals(indicators, close)
        return indicators, signals