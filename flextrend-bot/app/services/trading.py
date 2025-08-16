import math
from loguru import logger
from config import SETTINGS
from .exchange import Exchange
from .notifier import tg_send

EX = Exchange()

def _precision(symbol):
    mk = EX.market(symbol)
    step = float(mk["info"].get("stepSize") or 10 ** (-mk["precision"]["amount"]))
    tick = float(mk["info"].get("tickSize") or 10 ** (-mk["precision"]["price"]))
    return step, tick

def _round_qty(symbol, qty):
    step, _ = _precision(symbol)
    return math.floor(qty / step) * step

def _round_price(symbol, price):
    _, tick = _precision(symbol)
    return math.floor(price / tick) * tick

def calc_qty(symbol: str, entry: float, sl: float, balance_usdt: float) -> float:
    risk_usdt = max(0.0, balance_usdt * SETTINGS.risk_per_trade)
    if SETTINGS.max_notional_per_trade > 0:
        risk_usdt = min(risk_usdt, SETTINGS.max_notional_per_trade)
    delta = abs(entry - sl)
    if delta <= 0: raise ValueError("SL inválido (delta=0)")
    qty = risk_usdt / delta
    return _round_qty(symbol, qty)

def place_entry(symbol: str, side: str, sl: float, tp1: float | None, tp2: float | None):
    EX.set_leverage(symbol, SETTINGS.default_leverage)
    last = _round_price(symbol, EX.ticker(symbol)["last"])
    bal = EX.balance_usdt()
    qty = calc_qty(symbol, last, sl, bal)
    if qty <= 0: raise Exception("qty<=0")

    side_ex = "buy" if side.upper() == "LONG" else "sell"
    opp = "sell" if side_ex == "buy" else "buy"

    logger.info(f"ENTRY {side} {symbol} qty={qty} ~{last} SL={sl} TP1={tp1} TP2={tp2}")
    tg_send(f"ENTRY {side} {symbol} qty={qty} ~{last} SL={sl} TP1={tp1} TP2={tp2}")

    EX.create_order(symbol=symbol, type="market", side=side_ex, amount=qty)

    EX.create_order(symbol, type="stop_market", side=opp, amount=qty,
                    params={"stopPrice": _round_price(symbol, sl),
                            "reduceOnly": True, "workingType": "CONTRACT_PRICE"})

    if tp1:
        tp1_qty = _round_qty(symbol, qty * (0.6 if tp2 else 1.0))
        EX.create_order(symbol, type="take_profit_market", side=opp, amount=tp1_qty,
                        params={"stopPrice": _round_price(symbol, tp1),
                                "reduceOnly": True, "workingType": "CONTRACT_PRICE"})
    if tp2:
        rest = _round_qty(symbol, qty - _round_qty(symbol, qty * 0.6))
        if rest > 0:
            EX.create_order(symbol, type="take_profit_market", side=opp, amount=rest,
                            params={"stopPrice": _round_price(symbol, tp2),
                                    "reduceOnly": True, "workingType": "CONTRACT_PRICE"})
    return {"qty": qty, "entry": last}

def close_position(symbol: str):
    # Close entire position by placing market reduceOnly opposite
    risk = EX.positions()
    mk = EX.market(symbol)["id"]
    for p in risk:
        if p["symbol"] == mk:
            amt = float(p["positionAmt"])
            if amt == 0:
                return False
            side = "sell" if amt > 0 else "buy"
            EX.create_order(symbol, type="market", side=side, amount=abs(amt), params={"reduceOnly": True})
            EX.cancel_all(symbol)
            tg_send(f"CLOSE {symbol} by dynamic-exit")
            return True
    return False
