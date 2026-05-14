import useSWR from 'swr'
import { api } from '../api/client'
import type { Trade } from '../types'

export function useTrades() {
  const { data, error, isLoading } = useSWR<Trade[]>(
    '/trades',
    () => api.getTrades() as Promise<Trade[]>,
    { refreshInterval: 15_000 }
  )
  return { trades: data ?? [], error, isLoading }
}

export function usePlayerTrades(playerId: string) {
  const { data, error, isLoading } = useSWR<Trade[]>(
    playerId ? `/players/${playerId}/trades` : null,
    () => api.getPlayerTrades(playerId) as Promise<Trade[]>,
    { refreshInterval: 30_000 }
  )
  return { trades: data ?? [], error, isLoading }
}
