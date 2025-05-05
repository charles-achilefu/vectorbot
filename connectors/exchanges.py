import ccxt.async_support as ccxt
import asyncio

class ExchangeConnector:
    def __init__(self, exchange_name, api_key, api_secret):
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange = self._init_exchange()

    def _init_exchange(self):
        exchange_class = getattr(ccxt, self.exchange_name)
        return exchange_class({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True
        })

    async def fetch_ohlcv(self, symbol, timeframe='1h', since=None, limit=1000):
        return await self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)

    async def create_order(self, symbol, side, amount, order_type='market', price=None, params={}):
        return await self.exchange.create_order(symbol, order_type, side, amount, price, params)

    async def close(self):
        await self.exchange.close()

# Example usage:
# connector = ExchangeConnector('binance', API_BINANCE, SECRET_BINANCE)
# ohlcv = asyncio.run(connector.fetch_ohlcv('BTC/USDT'))