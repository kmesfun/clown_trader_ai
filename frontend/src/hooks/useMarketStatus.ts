import useSWR from 'swr'
import { api } from '../api/client'
import type { MarketStatus } from '../types'

export function useMarketStatus() {
  const { data, error } = useSWR<MarketStatus>(
    '/market/status',
    () => api.getMarketStatus() as Promise<MarketStatus>,
    { refreshInterval: 60_000 }
  )
  return { status: data, error }
}
