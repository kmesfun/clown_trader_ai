# 🤡 Clown Arena — The Clown vs. The Machines

A paper-trading battle arena where **"The Clown"** (a portfolio that mirrors Jim Cramer's public picks) competes against **6 AI trading bots**, each with a distinct strategy. Everyone starts with **$100,000** and must follow real trading rules — T+1 settlement, PDT restrictions, wash sales, and capital gains taxes.

**Core question: Can a clown beat the machines?**

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python + FastAPI + SQLAlchemy (async) + PostgreSQL |
| Market Data | yfinance (free, no key needed) |
| Scheduler | APScheduler (daily market cycle) |
| AI/LLM | Anthropic Claude API (Degen GPT bot) |
| Frontend | React + Vite + TypeScript + Tailwind CSS |
| Charts | Recharts |
| Infra | Docker Compose |

---

## Quick Start

### 1. Clone & configure

```bash
cp .env.example .env
# Fill in ANTHROPIC_API_KEY if you want Degen GPT to work
```

### 2. Start with Docker Compose

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
- Frontend: run separately (see below)

### 3. Start frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## The Players

| Player | Type | Strategy | Risk |
|---|---|---|---|
| 🤡 The Clown | Cramer Mirror | Buys/sells based on Cramer's public picks | Chaos |
| 📊 The Indexer | Bot | DCA into SPY/QQQ/VTI weekly, quarterly rebalance | Low |
| 🤖 The Quant | Bot | RSI(14) mean reversion + 200 SMA trend filter | Medium |
| 🎰 YOLO Bot | Bot | 3x simulated leverage on momentum breakouts | Extreme |
| 🧛 Theta Gang | Bot | Simulated premium selling (covered calls, CSPs) | Low-Med |
| 🔄 Inverse Clown | Bot | Takes exact opposite of every Cramer pick | Medium |
| 🦍 Degen GPT | Bot | Claude API sentiment + momentum decisions | High |

---

## Trading Rules Enforced

- **T+1 Settlement** — sale proceeds available next business day
- **PDT Rule** — max 3 day trades per rolling 5 business days if equity < $25k; violators locked for 90 days
- **Wash Sale Rule** — 30-day window detection, disallowed losses roll into cost basis
- **Short Selling** — simulated borrow rate (0.02%/day)
- **Slippage** — 0.05% on all equity trades
- **Market Hours** — 9:30 AM – 4:00 PM ET, Mon-Fri, US holidays respected

---

## Tax Engine

End-of-year (or on-demand) calculation:
- **Short-term gains** (< 1 year) → 37% rate
- **Long-term gains** (≥ 1 year) → 20% rate
- **NIIT** → 3.8% surtax
- **Wash sale adjustments** applied to cost basis

**The leaderboard shows after-tax returns — this is the real score.**

---

## Project Structure

```
clown_trader_ai/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── api/             # FastAPI route handlers
│   │   ├── engine/          # Portfolio manager, settlement, PDT, wash sale
│   │   ├── data/            # yfinance market data client
│   │   ├── bots/            # All 6 bot strategy implementations
│   │   ├── scheduler.py     # APScheduler daily market cycle
│   │   ├── seed.py          # Creates all 7 players with $100k portfolios
│   │   └── main.py          # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # Dashboard, PlayerDetail, TradeFeed, CramerPicks, TaxReport
│   │   ├── components/      # Leaderboard, TradeCard, PositionTable, EquityCurve, ...
│   │   ├── hooks/           # SWR data hooks
│   │   └── api/             # API client
│   └── package.json
└── docker-compose.yml
```

---

## Daily Bot Cycle

1. **9:00 AM ET** — Fetch latest Cramer picks (manual entry via UI)
2. **9:30 AM ET** — Execute all queued bot orders at open price + slippage
3. **Every 15 min** — Intraday mark-to-market; bots evaluate signals
4. **4:00 PM ET** — Final mark-to-market, daily P&L snapshot
5. **4:30 PM ET** — Process T+1 settlements, check margin/PDT

---

## Adding a Cramer Pick

1. Go to http://localhost:3000/cramer
2. Enter the ticker, direction (BUY/SELL/HOLD), and the quote
3. Click "Execute" to trigger The Clown's trade (and Inverse Clown's counter-trade)

---

## Dev Endpoints

The dashboard has two dev buttons:
- **↻ Mark to Market** — updates all positions with current prices
- **🤖 Run Bots Now** — triggers all bots outside of their normal schedule

Or hit the API directly:
```bash
POST /api/engine/mark-to-market
POST /api/engine/run-bots
POST /api/engine/process-settlements
```

---

## Legal Note

This is paper trading only. No real money. "The Clown" uses a generic clown character — not Cramer's likeness. Data from yfinance for personal/non-commercial use.

---

*"In the arena, there is only one clown — but who's really the joke?"*
