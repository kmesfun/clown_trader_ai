import useSWR from 'swr'
import { api } from '../api/client'
import type { LeaderboardEntry } from '../types'

export function useLeaderboard() {
  const { data, error, isLoading, mutate } = useSWR<LeaderboardEntry[]>(
    '/leaderboard',
    () => api.getLeaderboard() as Promise<LeaderboardEntry[]>,
    { refreshInterval: 30_000 }
  )
  return { leaderboard: data ?? [], error, isLoading, refresh: mutate }
}
