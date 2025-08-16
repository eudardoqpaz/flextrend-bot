from config import SETTINGS
from datetime import datetime, timezone

class RiskGuard:
    def __init__(self):
        self.day = None
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.equity_start = None

    def _roll_day(self):
        today = datetime.now(timezone.utc).date()
        if self.day != today:
            self.day = today
            self.daily_pnl = 0.0

    def set_equity_start(self, equity: float):
        if self.equity_start is None:
            self.equity_start = equity

    def add_pnl(self, pnl: float):
        self._roll_day()
        self.daily_pnl += pnl
        self.total_pnl += pnl

    def can_trade(self) -> tuple[bool, str]:
        self._roll_day()
        if self.equity_start is None:
            return True, "OK"
        if SETTINGS.max_daily_loss_pct > 0 and self.daily_pnl <= -self.equity_start * SETTINGS.max_daily_loss_pct / 100:
            return False, "Max daily loss alcanzado"
        if SETTINGS.max_total_loss_pct > 0 and self.total_pnl <= -self.equity_start * SETTINGS.max_total_loss_pct / 100:
            return False, "Max total loss alcanzado"
        return True, "OK"

RISK = RiskGuard()
