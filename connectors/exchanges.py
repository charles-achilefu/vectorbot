import ccxt.async_support as ccxt
import asyncio

class ExchangeConnector:
    def __init__(self, exchange_name, api_key, api_secret):
        exchange_class = getattr(ccxt, exchange_name)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'timeout': 30000,  # 30 second timeout
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future' if 'dapi' in exchange_name else 'spot'
            }
        })

    async def fetch_ohlcv(self, symbol, timeframe, limit=500, retries=3):
        for attempt in range(retries):
            try:
                return await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            except (ccxt.NetworkError, ccxt.ExchangeError) as e:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # exponential backoff
        return None

    async def close(self):
        if hasattr(self, 'exchange'):
            await self.exchange.close()
            del self.exchange

# Example usage:
# connector = ExchangeConnector('binance', BINANCE_API_KEY, BINANCE_API_SECRET)
# ohlcv = asyncio.run(connector.fetch_ohlcv('BTC/USDT'))