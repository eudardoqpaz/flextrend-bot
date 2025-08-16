from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .db import get_db, Base, engine
from .models import KVSetting, TradeLog, PositionSnap, AppLog
from .api import router as api_router
from config import SETTINGS
from .services.exchange import Exchange
from .services.risk import RISK

app = FastAPI(title=SETTINGS.app_name, version="1.0")
app.add_middleware(SessionMiddleware, secret_key=SETTINGS.secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Init DB
Base.metadata.create_all(bind=engine)

EX = Exchange()

def get_auth(req: Request):
    return req.session.get("auth")

@app.get("/", response_class=HTMLResponse)
def dashboard(req: Request, db: Session = Depends(get_db)):
    if not get_auth(req):
        return RedirectResponse("/login", status_code=302)
    positions = EX.positions()
    return templates.TemplateResponse("dashboard.html", {"request": req, "positions": positions, "settings": SETTINGS})

@app.get("/login", response_class=HTMLResponse)
def login_page(req: Request):
    return templates.TemplateResponse("base.html", {"request": req, "content": "login"})

@app.post("/login")
def login(req: Request, username: str = Form(...), password: str = Form(...)):
    if username == SETTINGS.admin_user and password == SETTINGS.admin_pass:
        req.session["auth"] = True
        return RedirectResponse("/", status_code=302)
    raise HTTPException(401, "Credenciales inválidas")

@app.get("/logout")
def logout(req: Request):
    req.session.clear()
    return RedirectResponse("/login", status_code=302)

@app.get("/settings", response_class=HTMLResponse)
def settings_page(req: Request):
    if not get_auth(req): return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("settings.html", {"request": req, "settings": SETTINGS})

@app.post("/settings")
def settings_save(req: Request,
                  watchlist: str = Form(None),
                  risk_per_trade: float = Form(None),
                  default_leverage: int = Form(None),
                  cooldown_sec: int = Form(None),
                  allow_all_symbols: str = Form("false")):
    if not get_auth(req): raise HTTPException(401, "Login requerido")
    # NOTE: Para simplicidad, actualizamos SETTINGS en caliente (no persistente al reiniciar)
    if watchlist is not None:
        SETTINGS.watchlist = [s.strip().upper() for s in watchlist.split(",") if s.strip()]
    if risk_per_trade is not None:
        SETTINGS.risk_per_trade = float(risk_per_trade)
    if default_leverage is not None:
        SETTINGS.default_leverage = int(default_leverage)
    if cooldown_sec is not None:
        SETTINGS.cooldown_sec = int(cooldown_sec)
    SETTINGS.allow_all_symbols = allow_all_symbols.lower() == "true"
    return RedirectResponse("/settings", status_code=302)

@app.get("/positions", response_class=HTMLResponse)
def positions_page(req: Request):
    if not get_auth(req): return RedirectResponse("/login", status_code=302)
    positions = EX.positions()
    return templates.TemplateResponse("positions.html", {"request": req, "positions": positions})

@app.get("/logs", response_class=HTMLResponse)
def logs_page(req: Request, db: Session = Depends(get_db)):
    if not get_auth(req): return RedirectResponse("/login", status_code=302)
    logs = db.query(AppLog).order_by(AppLog.ts.desc()).limit(200).all()
    return templates.TemplateResponse("logs.html", {"request": req, "logs": logs})

# API routes
app.include_router(api_router)
