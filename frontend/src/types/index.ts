export interface Player {
  id: string
  name: string
  slug: string
  type: 'clown' | 'bot'
  strategy_description: string
  avatar_emoji: string
  cash_balance: string
  settled_cash: string
  total_equity: string
  unrealized_pnl: string
  realized_pnl: string
  total_return_pct: string
  position_count: number
  pdt_locked: boolean
}

export interface LeaderboardEntry {
  rank: number
  player_id: string
  name: string
  slug: string
  type: 'clown' | 'bot'
  strategy_description: string
  avatar_emoji: string
  cash_balance: string
  settled_cash: string
  total_equity: string
  unrealized_pnl: string
  realized_pnl: string
  total_return_pct: string
  position_count: number
  after_tax_equity: number
  after_tax_return_pct: number
  pdt_locked: boolean
  pdt_triggered: boolean
}

export interface Position {
  id: string
  ticker: string
  quantity: string
  avg_cost_basis: string
  current_price: string
  market_value: string
  unrealized_pnl: string
  unrealized_pnl_pct: string
  is_short: boolean
  opened_at: string
}

export interface Trade {
  id: string
  player_id: string
  player_name: string
  player_avatar_emoji: string
  ticker: string
  direction: 'buy' | 'sell' | 'short' | 'cover' | 'buy_to_open' | 'sell_to_open' | 'buy_to_close' | 'sell_to_close'
  quantity: string
  price: string
  total_value: string
  realized_pnl: string | null
  wash_sale_flag: boolean
  source: string
  notes: string
  executed_at: string
}

export interface CramerPick {
  id: string
  parsed_ticker: string
  direction: 'buy' | 'sell' | 'hold'
  raw_text: string
  source_url: string
  confidence: number
  aired_at: string
  ingested_at: string
  executed: boolean
  trade_id: string | null
}

export interface MarketStatus {
  is_open: boolean
  next_open: string | null
  current_time_et: string
}

export interface TaxSummary {
  player_id: string
  total_short_term_gains: number
  total_long_term_gains: number
  wash_sale_adjustments: number
  short_term_tax: number
  long_term_tax: number
  niit: number
  total_tax_owed: number
  pre_tax_equity: number
  after_tax_equity: number
}

export interface OHLCVBar {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}
