# FlexTrend Bot (FastAPI + Web Monitor + Binance Futures USDT-M)

Bot de trading para Linux que ejecuta órdenes SOLO cuando tus indicadores **FLEX + TREND** confirman **todas** las condiciones. Incluye:

- API de **webhook** para recibir señales de TradingView (ENTRY/UPDATE/EXIT)
- **Salida dinámica**: cierra posiciones al invalidarse la condición mayor (tendencia/ADX)
- **Gestión de riesgo** configurable (x3 leverage, % riesgo, límites diarios/totales)
- **Web Monitor** (FastAPI + Jinja2): dashboard, posiciones, settings (watchlist, riesgo, cooldown, etc.)
- **Soporte Telegram** para notificaciones (opcional)
- Persistencia en **SQLite**

## 🚀 Instalación rápida

```bash
sudo apt update && sudo apt install -y python3-pip python3-venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env (API keys, etc.)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Web Monitor: http://localhost:8000 (user: `admin`, pass en `.env`)

Webhook TV: `http://TU_IP_PUBLICA:8000/webhook`

## 🧩 TradingView → JSON ejemplo

Configura alertas cuando tu indicador cumpla TODO al cierre de vela.

```json
{
  "event": "ENTRY",
  "secret": "supersecreto",
  "symbol": "BINANCE:ADAUSDT.P",
  "side": "LONG",
  "mode": "CONTINUACION",
  "reason": "PB_SANO",
  "price": 0.987,
  "sl": 0.972,
  "tp1": 0.997,
  "tp2": 1.012
}
```

Para salida dinámica (invalidación mayor):
```json
{
  "event": "UPDATE",
  "secret": "supersecreto",
  "symbol": "BINANCE:ADAUSDT.P",
  "valid_major": false
}
```

Mover SL a BE:
```json
{
  "event": "UPDATE",
  "secret": "supersecreto",
  "symbol": "BINANCE:ADAUSDT.P",
  "valid_major": true,
  "action": "BE",
  "be_price": 0.987
}
```

## ⚙️ Variables clave
- `USE_TESTNET=true|false`
- `DEFAULT_LEVERAGE=3`
- `RISK_PER_TRADE=0.01` (1%)
- `MAX_POSITIONS=3`
- `COOLDOWN_SEC=180`
- `WATCHLIST=BTC/USDT,ETH/USDT,...`
- `ALLOW_ALL_SYMBOLS=false` (si `true`, opera cualquier símbolo entrante)

## 🧪 Systemd (servicio)

```bash
sudo cp scripts/systemd/flextrend-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now flextrend-bot
```

## 🐳 Docker
```bash
cd scripts/docker
docker compose up -d --build
```
