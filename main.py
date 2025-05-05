import asyncio
import pandas as pd
import vectorbt as vbt
from config import MODE, SYMBOL, TIMEFRAME, API_BINANCE, SECRET_BINANCE
from connectors.exchanges import ExchangeConnector
from strategies.bbwp_srs import BBWPStochRSIStrategy

async def fetch_data(symbol, timeframe, limit=500):
    connector = ExchangeConnector('binance', API_BINANCE, SECRET_BINANCE)
    ohlcv = await connector.fetch_ohlcv(symbol, timeframe, limit=limit)
    await connector.close()
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def run_backtest(df):
    strat = BBWPStochRSIStrategy(df['close'])
    signals = strat.get_signals()
    pf = vbt.Portfolio.from_signals(
        close=df['close'],
        entries=signals['long'],
        exits=signals['short'],
        freq=TIMEFRAME
    )
    print(pf.stats())
    pf.plot().show()

async def run_live():
    # Placeholder for live trading logic
    print('Live trading mode not yet implemented.')

async def run_paper():
    # Placeholder for paper trading logic
    print('Paper trading mode not yet implemented.')

async def main():
    if MODE == 'backtest':
        df = await fetch_data(SYMBOL, TIMEFRAME)
        run_backtest(df)
    elif MODE == 'live':
        await run_live()
    elif MODE == 'paper':
        await run_paper()
    else:
        print(f'Unknown MODE: {MODE}')

if __name__ == '__main__':
    asyncio.run(main())