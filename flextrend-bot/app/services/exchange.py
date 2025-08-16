import ccxt
from loguru import logger
from config import SETTINGS

class Exchange:
    def __init__(self):
        self.ex = ccxt.binance({
            "apiKey": SETTINGS.binance_key,
            "secret": SETTINGS.binance_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "future"},
        })
        if SETTINGS.use_testnet:
            self.ex.set_sandbox_mode(True)
        self.ex.load_markets()

    def set_leverage(self, symbol: str, lev: int):
        try:
            self.ex.set_leverage(lev, symbol)
        except Exception as e:
            logger.warning(f"set_leverage fallback {symbol}: {e}")
            try:
                mk = self.ex.market(symbol)
                self.ex.fapiPrivate_post_leverage({"symbol": mk["id"], "leverage": int(lev)})
            except Exception as e2:
                logger.error(f"No pude fijar leverage {symbol}: {e2}")

    def balance_usdt(self) -> float:
        bal = self.ex.fetch_balance({"type": "future"})
        return float(bal["total"].get(SETTINGS.quote, 0.0))

    def ticker(self, symbol: str):
        return self.ex.fetch_ticker(symbol)

    def market(self, symbol: str):
        return self.ex.market(symbol)

    def create_order(self, **kwargs):
        return self.ex.create_order(**kwargs)

    def cancel_all(self, symbol: str):
        try:
            self.ex.cancel_all_orders(symbol)
        except Exception:
            pass

    def positions(self):
        return self.ex.fapiPrivateGetPositionRisk()
