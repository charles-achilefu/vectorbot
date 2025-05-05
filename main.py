import asyncio
import pandas as pd
import vectorbt as vbt
import logging
from config import MODE, SYMBOL, TIMEFRAME, STRATEGY, BINANCE_API_KEY, BINANCE_API_SECRET
from connectors.exchanges import ExchangeConnector
import importlib
from typing import Optional, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def validate_config() -> None:
    """Validate configuration variables at startup."""
    if not SYMBOL or not isinstance(SYMBOL, list):
        raise ValueError("SYMBOL must be a non-empty list.")
    if not TIMEFRAME or not isinstance(TIMEFRAME, list):
        raise ValueError("TIMEFRAME must be a non-empty list.")
    if not STRATEGY:
        raise ValueError("STRATEGY must be set.")
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET must be set.")

async def fetch_data(symbol: str, timeframe: str, limit: int = 500, cache: dict = None) -> Optional[pd.DataFrame]:
    """Fetch OHLCV data for a symbol and timeframe, with optional caching."""
    cache_key = f"{symbol}_{timeframe}_{limit}"
    if cache is not None and cache_key in cache:
        logging.info(f"Using cached data for {symbol} {timeframe}")
        return cache[cache_key]
    connector = ExchangeConnector('binance', BINANCE_API_KEY, BINANCE_API_SECRET)
    try:
        ohlcv = await connector.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        if cache is not None:
            cache[cache_key] = df
        return df
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {str(e)}")
        return None
    finally:
        await connector.close()

def get_strategy_class(strategy_name: str) -> Any:
    """Dynamically import and return the strategy class by name."""
    module_name = f"strategies.{strategy_name}"
    class_name = "".join([part.capitalize() for part in strategy_name.split("_")]) + "Strategy"
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Unknown strategy: {strategy_name} ({e})")

def analyze_portfolio(pf: vbt.Portfolio, symbol: str, tf: str, strat_name: str) -> dict:
    """Analyze and log portfolio statistics, and return results."""
    stats = pf.stats()
    logging.info(f"Results for {symbol} {tf} {strat_name}:\n{stats}")
    return stats.to_dict() if hasattr(stats, 'to_dict') else dict(stats)

def store_results(results: List[dict]) -> None:
    """Store backtest results (placeholder for DB or file storage)."""
    # Implement actual storage logic as needed
    logging.info(f"Storing {len(results)} backtest results.")

async def main() -> None:
    """Main entry point for running backtests, live, or paper trading."""
    try:
        validate_config()
    except Exception as e:
        logging.error(f"Configuration error: {e}")
        return
    cache = {}
    results = []
    if MODE == 'backtest':
        strategies = STRATEGY if isinstance(STRATEGY, list) else [STRATEGY]
        for symbol in SYMBOL:
            for tf in TIMEFRAME:
                logging.info(f'Running backtest for {symbol} on timeframe: {tf}')
                df = await fetch_data(symbol, tf, limit=2000, cache=cache)
                if df is None:
                    continue
                for strat_name in strategies:
                    logging.info(f"  Using strategy: {strat_name}")
                    try:
                        strat_cls = get_strategy_class(strat_name)
                        strat = strat_cls(df['close'])
                        if not hasattr(strat, 'get_signals'):
                            raise ValueError(f"Strategy {strat_name} missing get_signals method.")
                        signals = strat.get_signals()
                        pf = vbt.Portfolio.from_signals(
                            close=df['close'],
                            entries=signals['long'],
                            exits=signals['short'],
                            freq=tf
                        )
                        stats = analyze_portfolio(pf, symbol, tf, strat_name)
                        results.append({
                            'symbol': symbol,
                            'timeframe': tf,
                            'strategy': strat_name,
                            'stats': stats
                        })
                        pf.plot().show()
                    except Exception as e:
                        logging.error(f"Backtest failed for {symbol} {tf} {strat_name}: {e}")
        store_results(results)
    elif MODE == 'live':
        await run_live()
    elif MODE == 'paper':
        await run_paper()
    else:
        logging.error(f'Unknown MODE: {MODE}')

if __name__ == '__main__':
    asyncio.run(main())