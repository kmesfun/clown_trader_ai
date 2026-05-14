import { useState } from 'react'
import { useTrades } from '../hooks/useTrades'
import { TradeCard } from '../components/trades/TradeCard'
import { LoadingClown } from '../components/ui/LoadingClown'

export function TradeFeed() {
  const { trades, isLoading } = useTrades()
  const [filter, setFilter] = useState<string>('all')

  const players = Array.from(new Set(trades.map((t) => t.player_name)))
  const filtered = filter === 'all' ? trades : trades.filter((t) => t.player_name === filter)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="font-carnival text-circus-red text-5xl tracking-wider">📡 TRADE FEED</h1>
        <div className="text-xs text-circus-dark/50 font-mono">Auto-refreshes every 15s</div>
      </div>

      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setFilter('all')}
          className={`text-xs font-sub font-bold uppercase px-3 py-1.5 rounded tracking-wider ${filter === 'all' ? 'bg-circus-red text-white' : 'bg-circus-cream border border-circus-red text-circus-red'}`}
        >
          All Players
        </button>
        {players.map((p) => (
          <button
            key={p}
            onClick={() => setFilter(p)}
            className={`text-xs font-sub font-bold uppercase px-3 py-1.5 rounded tracking-wider ${filter === p ? 'bg-circus-red text-white' : 'bg-circus-cream border border-circus-red text-circus-red'}`}
          >
            {p}
          </button>
        ))}
      </div>

      {isLoading ? (
        <LoadingClown message="Loading trades..." />
      ) : filtered.length === 0 ? (
        <div className="text-center py-24">
          <div className="text-6xl mb-4">🎪</div>
          <div className="font-carnival text-circus-red text-3xl">NO TRADES YET</div>
          <div className="font-sub text-circus-dark/50 mt-2">The arena is silent. Add a Cramer pick to get things started.</div>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {filtered.map((trade) => (
            <TradeCard key={trade.id} trade={trade} showPlayer />
          ))}
        </div>
      )}
    </div>
  )
}
