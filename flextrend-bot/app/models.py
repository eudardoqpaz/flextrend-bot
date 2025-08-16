from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .db import Base

class KVSetting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(64), unique=True, index=True)
    value = Column(Text)
    is_secret = Column(Boolean, default=False)

class TradeLog(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20))
    side = Column(String(6))
    qty = Column(Float)
    entry_price = Column(Float)
    sl = Column(Float)
    tp1 = Column(Float, nullable=True)
    tp2 = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PositionSnap(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    side = Column(String(6))
    amount = Column(Float)
    entry_price = Column(Float)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class AppLog(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    level = Column(String(10))
    msg = Column(Text)
    ts = Column(DateTime(timezone=True), server_default=func.now())
