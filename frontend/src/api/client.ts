const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? '/api'

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`)
  return res.json() as Promise<T>
}

export const api = {
  getLeaderboard: () => req('/leaderboard'),
  getPlayers: () => req('/players'),
  getPlayer: (id: string) => req(`/players/${id}`),
  getPlayerTrades: (id: string) => req(`/players/${id}/trades`),
  getPlayerPositions: (id: string) => req(`/players/${id}/positions`),
  getPlayerTax: (id: string) => req(`/players/${id}/tax`),
  getTrades: () => req('/trades'),
  getCramerPicks: () => req('/cramer-picks'),
  createCramerPick: (data: unknown) =>
    req('/cramer-picks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),
  executeCramerPick: (id: string) =>
    req(`/cramer-picks/${id}/execute`, { method: 'POST' }),
  getMarketStatus: () => req('/market/status'),
  getMarketPrice: (ticker: string) => req(`/market/price/${ticker}`),
  getMarketHistory: (ticker: string, days = 30) =>
    req(`/market/history/${ticker}?days=${days}`),
  triggerMarkToMarket: () => req('/engine/mark-to-market', { method: 'POST' }),
  runBots: () => req('/engine/run-bots', { method: 'POST' }),
  processSettlements: () => req('/engine/process-settlements', { method: 'POST' }),
}
