import asyncio
import pandas as pd
import vectorbt as vbt
from config import MODE, SYMBOL, TIMEFRAME, STRATEGY, API_BINANCE, SECRET_BINANCE
from connectors.exchanges import ExchangeConnector
import importlib

async def fetch_data(symbol, timeframe, limit=500):
    connector = ExchangeConnector('binance', API_BINANCE, SECRET_BINANCE)
    ohlcv = await connector.fetch_ohlcv(symbol, timeframe, limit=limit)
    await connector.close()
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def get_strategy_class(strategy_name):
    """Dynamically import and return the strategy class by name."""
    module_name = f"strategies.{strategy_name}"
    # Always construct class name from strategy_name
    class_name = "".join([part.capitalize() for part in strategy_name.split("_")]) + "Strategy"
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Unknown strategy: {strategy_name} ({e})")

async def main():
    if MODE == 'backtest':
        # Allow STRATEGY to be a list of strategy names
        strategies = STRATEGY if isinstance(STRATEGY, list) else [STRATEGY]
        for symbol in SYMBOL:
            for tf in TIMEFRAME:
                print(f'\nRunning backtest for {symbol} on timeframe: {tf}')
                df = await fetch_data(symbol, tf, limit=2000)
                for strat_name in strategies:
                    print(f"  Using strategy: {strat_name}")
                    strat_cls = get_strategy_class(strat_name)
                    strat = strat_cls(df['close'])
                    signals = strat.get_signals()
                    pf = vbt.Portfolio.from_signals(
                        close=df['close'],
                        entries=signals['long'],
                        exits=signals['short'],
                        freq=tf
                    )
                    print(pf.stats())
                    pf.plot().show()
    elif MODE == 'live':
        await run_live()
    elif MODE == 'paper':
        await run_paper()
    else:
        print(f'Unknown MODE: {MODE}')

if __name__ == '__main__':
    # Override symbol for this test
    SYMBOL = 'SUIUSDT'
    asyncio.run(main())