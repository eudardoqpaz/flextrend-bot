from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "FlexTrend Bot")
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8000"))
    admin_user: str = os.getenv("APP_ADMIN_USER", "admin")
    admin_pass: str = os.getenv("APP_ADMIN_PASS", "changeme")
    secret_key: str = os.getenv("SECRET_KEY", "please_change_me")

    use_testnet: bool = os.getenv("USE_TESTNET", "true").lower() == "true"
    binance_key: str | None = os.getenv("BINANCE_API_KEY")
    binance_secret: str | None = os.getenv("BINANCE_API_SECRET")
    default_leverage: int = int(os.getenv("DEFAULT_LEVERAGE", "3"))
    risk_per_trade: float = float(os.getenv("RISK_PER_TRADE", "0.01"))
    max_positions: int = int(os.getenv("MAX_POSITIONS", "3"))
    cooldown_sec: int = int(os.getenv("COOLDOWN_SEC", "180"))
    quote: str = os.getenv("QUOTE", "USDT").upper()
    watchlist: list[str] = [s.strip().upper() for s in os.getenv("WATCHLIST", "BTC/USDT,ETH/USDT").split(",") if s.strip()]
    allow_all_symbols: bool = os.getenv("ALLOW_ALL_SYMBOLS", "false").lower() == "true"
    max_notional_per_trade: float = float(os.getenv("MAX_NOTIONAL_PER_TRADE", "0"))
    max_daily_loss_pct: float = float(os.getenv("MAX_DAILY_LOSS_PCT", "5"))
    max_total_loss_pct: float = float(os.getenv("MAX_TOTAL_LOSS_PCT", "10"))
    telegram_bot_token: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = os.getenv("TELEGRAM_CHAT_ID")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "supersecreto")

SETTINGS = Settings()
