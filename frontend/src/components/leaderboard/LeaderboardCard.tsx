import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useLeaderboard } from '../../hooks/useLeaderboard'
import { PlayerAvatar } from '../ui/PlayerAvatar'
import { PnlBadge } from '../ui/PnlBadge'
import { LoadingClown } from '../ui/LoadingClown'

const RANK_ICONS = ['👑', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣']

function fmt(val: string | number, prefix = '$'): string {
  const n = typeof val === 'string' ? parseFloat(val) : val
  return `${prefix}${n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export function LeaderboardCard() {
  const { leaderboard, isLoading, refresh } = useLeaderboard()
  const [showAfterTax, setShowAfterTax] = useState(false)

  if (isLoading) return <LoadingClown message="Ranking the clowns..." />

  const sorted = [...leaderboard].sort((a, b) => {
    if (showAfterTax) return b.after_tax_return_pct - a.after_tax_return_pct
    return parseFloat(b.total_return_pct) - parseFloat(a.total_return_pct)
  })

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-carnival text-circus-red text-3xl tracking-wider">
          🏆 LEADERBOARD
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAfterTax(false)}
            className={`text-xs font-sub font-bold uppercase px-3 py-1 rounded tracking-wider ${!showAfterTax ? 'bg-circus-red text-white' : 'bg-circus-cream text-circus-dark border border-circus-red'}`}
          >
            Pre-Tax
          </button>
          <button
            onClick={() => setShowAfterTax(true)}
            className={`text-xs font-sub font-bold uppercase px-3 py-1 rounded tracking-wider ${showAfterTax ? 'bg-circus-red text-white' : 'bg-circus-cream text-circus-dark border border-circus-red'}`}
          >
            After-Tax
          </button>
          <button onClick={() => refresh()} className="btn-gold text-xs">
            ↻ Refresh
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-circus-gold">
              <th className="text-left py-2 px-2 font-sub text-circus-tent uppercase text-xs">Rank</th>
              <th className="text-left py-2 px-2 font-sub text-circus-tent uppercase text-xs">Player</th>
              <th className="text-right py-2 px-2 font-sub text-circus-tent uppercase text-xs">Portfolio</th>
              <th className="text-right py-2 px-2 font-sub text-circus-tent uppercase text-xs">Return %</th>
              <th className="text-right py-2 px-2 font-sub text-circus-tent uppercase text-xs">Unrealized P&L</th>
              <th className="text-right py-2 px-2 font-sub text-circus-tent uppercase text-xs">Positions</th>
              <th className="text-center py-2 px-2 font-sub text-circus-tent uppercase text-xs">PDT</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((entry, i) => {
              const returnPct = showAfterTax ? entry.after_tax_return_pct : parseFloat(entry.total_return_pct)
              const equity = showAfterTax ? entry.after_tax_equity : parseFloat(entry.total_equity)
              const isClown = entry.type === 'clown'

              return (
                <tr
                  key={entry.player_id}
                  className={`border-b border-circus-gold/20 hover:bg-circus-gold/10 transition-colors ${isClown ? 'bg-circus-red/5' : ''}`}
                >
                  <td className="py-3 px-2">
                    <span className="text-xl">{RANK_ICONS[i] ?? `${i + 1}`}</span>
                  </td>
                  <td className="py-3 px-2">
                    <Link to={`/player/${entry.player_id}`} className="flex items-center gap-2 hover:opacity-80">
                      <PlayerAvatar emoji={entry.avatar_emoji} name={entry.name} size="sm" />
                      <div>
                        <div className="font-sub font-bold text-circus-dark">{entry.name}</div>
                        <div className="text-xs text-circus-tent/70 max-w-[200px] truncate">{entry.strategy_description.slice(0, 50)}…</div>
                      </div>
                    </Link>
                  </td>
                  <td className="py-3 px-2 text-right font-mono font-bold text-circus-dark">
                    {fmt(equity)}
                  </td>
                  <td className="py-3 px-2 text-right">
                    <PnlBadge value={returnPct} suffix="%" />
                  </td>
                  <td className="py-3 px-2 text-right">
                    <PnlBadge value={parseFloat(entry.unrealized_pnl)} />
                  </td>
                  <td className="py-3 px-2 text-right font-mono text-circus-dark">
                    {entry.position_count ?? 0}
                  </td>
                  <td className="py-3 px-2 text-center">
                    {entry.pdt_triggered ? (
                      <span className="text-loss-red text-xs font-bold">⚠️ PDT</span>
                    ) : (
                      <span className="text-gain-green text-xs">✓</span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
