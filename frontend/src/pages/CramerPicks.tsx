import { useState } from 'react'
import useSWR from 'swr'
import { format } from 'date-fns'
import { api } from '../api/client'
import type { CramerPick } from '../types'
import { TickerBadge, DirectionBadge } from '../components/ui/TickerBadge'
import { LoadingClown } from '../components/ui/LoadingClown'

export function CramerPicks() {
  const { data: picks, isLoading, mutate } = useSWR<CramerPick[]>(
    '/cramer-picks',
    () => api.getCramerPicks() as Promise<CramerPick[]>,
    { refreshInterval: 30_000 }
  )

  const [form, setForm] = useState({
    parsed_ticker: '',
    direction: 'buy' as 'buy' | 'sell' | 'hold',
    raw_text: '',
    source_url: '',
    confidence: 1.0,
  })
  const [submitting, setSubmitting] = useState(false)
  const [executing, setExecuting] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.createCramerPick({ ...form, parsed_ticker: form.parsed_ticker.toUpperCase() })
      setForm({ parsed_ticker: '', direction: 'buy', raw_text: '', source_url: '', confidence: 1.0 })
      await mutate()
    } catch (err) {
      alert(`Error: ${err}`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleExecute = async (pickId: string) => {
    setExecuting(pickId)
    try {
      const result = await api.executeCramerPick(pickId) as { ticker: string; direction: string }
      alert(`Executed! ${result.direction} ${result.ticker}`)
      await mutate()
    } catch (err) {
      alert(`Error: ${err}`)
    } finally {
      setExecuting(null)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="font-carnival text-circus-red text-5xl tracking-wider">🤡 CRAMER PICKS</h1>

      {/* Add pick form */}
      <div className="card">
        <h2 className="font-carnival text-circus-dark text-2xl tracking-wider mb-4">ADD A CRAMER PICK</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-sub font-bold uppercase tracking-wider text-circus-tent mb-1">
              Ticker *
            </label>
            <input
              type="text"
              required
              value={form.parsed_ticker}
              onChange={(e) => setForm({ ...form, parsed_ticker: e.target.value.toUpperCase() })}
              placeholder="AAPL"
              className="w-full border-2 border-circus-red rounded px-3 py-2 font-mono bg-circus-cream focus:outline-none focus:border-circus-gold"
            />
          </div>
          <div>
            <label className="block text-xs font-sub font-bold uppercase tracking-wider text-circus-tent mb-1">
              Direction *
            </label>
            <select
              value={form.direction}
              onChange={(e) => setForm({ ...form, direction: e.target.value as 'buy' | 'sell' | 'hold' })}
              className="w-full border-2 border-circus-red rounded px-3 py-2 font-sub bg-circus-cream focus:outline-none focus:border-circus-gold"
            >
              <option value="buy">BUY BUY BUY</option>
              <option value="sell">SELL</option>
              <option value="hold">HOLD</option>
            </select>
          </div>
          <div className="sm:col-span-2">
            <label className="block text-xs font-sub font-bold uppercase tracking-wider text-circus-tent mb-1">
              Quote / Raw Text
            </label>
            <input
              type="text"
              value={form.raw_text}
              onChange={(e) => setForm({ ...form, raw_text: e.target.value })}
              placeholder="I like this stock! Buy buy buy!"
              className="w-full border-2 border-circus-red rounded px-3 py-2 font-sub bg-circus-cream focus:outline-none focus:border-circus-gold"
            />
          </div>
          <div className="sm:col-span-2 lg:col-span-4 flex justify-end">
            <button type="submit" disabled={submitting} className="btn-primary">
              {submitting ? '🤡 Adding...' : '+ ADD PICK'}
            </button>
          </div>
        </form>
      </div>

      {/* Picks list */}
      <div className="card">
        <h2 className="font-carnival text-circus-dark text-2xl tracking-wider mb-4">
          PICK HISTORY ({picks?.length ?? 0})
        </h2>
        {isLoading ? (
          <LoadingClown message="Loading picks..." />
        ) : !picks?.length ? (
          <div className="text-center py-12 text-circus-dark/50 font-sub">
            No picks yet. Cramer hasn't spoken.
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {picks.map((pick) => (
              <div key={pick.id} className={`flex items-center gap-4 p-3 rounded-lg border-2 ${pick.executed ? 'border-gain-green/30 bg-gain-green/5' : 'border-circus-gold/30 bg-circus-cream'}`}>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <TickerBadge ticker={pick.parsed_ticker} />
                  <DirectionBadge direction={pick.direction} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-sub text-circus-dark truncate">{pick.raw_text || '(no quote)'}</div>
                  <div className="text-xs text-circus-dark/50 font-mono mt-0.5">
                    Aired: {format(new Date(pick.aired_at), 'MMM d, yyyy HH:mm')}
                    {' · '}
                    Confidence: {Math.round(pick.confidence * 100)}%
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {pick.executed ? (
                    <span className="text-gain-green text-xs font-bold font-sub">✓ EXECUTED</span>
                  ) : (
                    <button
                      onClick={() => handleExecute(pick.id)}
                      disabled={executing === pick.id}
                      className="btn-primary text-xs"
                    >
                      {executing === pick.id ? '...' : '▶ Execute'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
