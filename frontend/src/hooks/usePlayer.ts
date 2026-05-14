import useSWR from 'swr'
import { api } from '../api/client'
import type { Player, Position, TaxSummary } from '../types'

export function usePlayer(id: string) {
  const { data, error, isLoading } = useSWR<Player>(
    id ? `/players/${id}` : null,
    () => api.getPlayer(id) as Promise<Player>,
    { refreshInterval: 30_000 }
  )
  return { player: data, error, isLoading }
}

export function usePlayerPositions(id: string) {
  const { data, error, isLoading } = useSWR<Position[]>(
    id ? `/players/${id}/positions` : null,
    () => api.getPlayerPositions(id) as Promise<Position[]>,
    { refreshInterval: 30_000 }
  )
  return { positions: data ?? [], error, isLoading }
}

export function usePlayerTax(id: string) {
  const { data, error, isLoading } = useSWR<TaxSummary>(
    id ? `/players/${id}/tax` : null,
    () => api.getPlayerTax(id) as Promise<TaxSummary>,
    { refreshInterval: 60_000 }
  )
  return { tax: data, error, isLoading }
}
