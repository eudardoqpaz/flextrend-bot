from fastapi import APIRouter, HTTPException, Request, Depends, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
from config import SETTINGS
from .utils.symbols import normalize_symbol_from_tv
from .services.trading import place_entry, close_position, EX
from .services.risk import RISK
from .db import get_db
from .models import KVSetting, TradeLog, PositionSnap, AppLog
from sqlalchemy.orm import Session
from loguru import logger
import time

router = APIRouter()
LAST_FIRE: Dict[str, float] = {}

def allowed_symbol(sym: str) -> bool:
    return SETTINGS.allow_all_symbols or sym.upper() in SETTINGS.watchlist

class EntrySignal(BaseModel):
    event: str = "ENTRY"
    secret: str
    symbol: str
    side: str
    mode: Optional[str] = None
    reason: Optional[str] = None
    price: float
    sl: float
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    qty_override: Optional[float] = None

class UpdateSignal(BaseModel):
    event: str = "UPDATE"
    secret: str
    symbol: str
    valid_major: bool
    action: Optional[str] = None
    be_price: Optional[float] = None

class ExitSignal(BaseModel):
    event: str = "EXIT"
    secret: str
    symbol: str
    reason: Optional[str] = None

@router.post("/webhook")
def webhook(payload: Dict[str, Any], db: Session = Depends(get_db)):
    secret = payload.get("secret")
    if secret != SETTINGS.webhook_secret:
        raise HTTPException(401, "Secret incorrecto")

    event = str(payload.get("event", "ENTRY")).upper()
    raw_symbol = payload.get("symbol", "")
    symbol = normalize_symbol_from_tv(raw_symbol)

    if event == "ENTRY":
        now = time.time()
        if now - LAST_FIRE.get(symbol, 0) < SETTINGS.cooldown_sec:
            raise HTTPException(429, f"Cooldown activo {symbol}")
        if not allowed_symbol(symbol):
            raise HTTPException(403, f"{symbol} fuera de WATCHLIST")
        allowed, why = RISK.can_trade()
        if not allowed:
            raise HTTPException(403, why)

        model = EntrySignal(**payload)
        res = place_entry(symbol, model.side, model.sl, model.tp1, model.tp2)
        LAST_FIRE[symbol] = now
        db.add(TradeLog(symbol=symbol, side=model.side.upper(), qty=res["qty"], entry_price=res["entry"], sl=model.sl, tp1=model.tp1, tp2=model.tp2))
        db.commit()
        return {"ok": True, "event": "ENTRY", "detail": res}

    elif event == "UPDATE":
        model = UpdateSignal(**payload)
        if model.valid_major is False:
            closed = close_position(symbol)
            return {"ok": True, "event": "UPDATE", "closed": closed, "reason": "major_invalid"}
        if model.action:
            side = "sell"  # placeholder; management via separate logic
            # For MVP, allow only CLOSE/BE close via dynamic exit
            if model.action.upper() == "CLOSE":
                closed = close_position(symbol)
                return {"ok": True, "event": "UPDATE", "closed": closed, "reason": "force_close"}
        return {"ok": True, "event": "UPDATE"}

    elif event == "EXIT":
        closed = close_position(symbol)
        return {"ok": True, "event": "EXIT", "closed": closed}

    else:
        raise HTTPException(400, f"Evento no soportado: {event}")

@router.get("/status")
def status():
    return {
        "watchlist": SETTINGS.watchlist,
        "allow_all": SETTINGS.allow_all_symbols,
        "use_testnet": SETTINGS.use_testnet,
        "risk_per_trade": SETTINGS.risk_per_trade,
        "default_leverage": SETTINGS.default_leverage,
        "max_positions": SETTINGS.max_positions,
        "cooldown_sec": SETTINGS.cooldown_sec,
    }
