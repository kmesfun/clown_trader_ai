import useSWR from 'swr'
import { api } from '../api/client'
import type { LeaderboardEntry, TaxSummary } from '../types'
import { PlayerAvatar } from '../components/ui/PlayerAvatar'
import { PnlBadge } from '../components/ui/PnlBadge'
import { LoadingClown } from '../components/ui/LoadingClown'

export function TaxReport() {
  const { data: leaderboard, isLoading } = useSWR<LeaderboardEntry[]>(
    '/leaderboard',
    () => api.getLeaderboard() as Promise<LeaderboardEntry[]>
  )

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-loss-red border-4 border-circus-dark rounded-xl p-6 text-center">
        <div className="font-carnival text-white text-5xl tracking-widest">
          🏛️ THE IRS ALWAYS WINS 🏛️
        </div>
        <div className="text-white/80 font-sub mt-2 text-lg tracking-wide">
          Mock Schedule D — Paper Trading Tax Report · {new Date().getFullYear()} YTD
        </div>
        <div className="text-white/50 text-xs font-sub mt-1">
          Simulated at 37% short-term / 20% long-term / 3.8% NIIT. For entertainment only.
        </div>
      </div>

      {isLoading ? (
        <LoadingClown message="Calculating your losses..." />
      ) : (
        <div className="space-y-4">
          {/* Summary table */}
          <div className="card">
            <h2 className="font-carnival text-circus-red text-3xl tracking-wider mb-4">
              PRE-TAX vs. AFTER-TAX
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b-2 border-circus-gold">
                    {['Player', 'Pre-Tax Equity', 'Pre-Tax Return', 'After-Tax Equity', 'After-Tax Return', 'Rank Delta'].map((h) => (
                      <th key={h} className="text-left py-2 px-3 font-sub text-circus-tent uppercase text-xs">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {leaderboard?.map((entry, i) => {
                    const preTaxReturn = parseFloat(entry.total_return_pct)
                    const afterTaxReturn = entry.after_tax_return_pct
                    const rankDelta = 0

                    return (
                      <tr key={entry.player_id} className="border-b border-circus-gold/20 hover:bg-circus-gold/5">
                        <td className="py-3 px-3">
                          <div className="flex items-center gap-2">
                            <PlayerAvatar emoji={entry.avatar_emoji} name={entry.name} size="sm" />
                            <span className="font-sub font-bold">{entry.name}</span>
                          </div>
                        </td>
                        <td className="py-3 px-3 font-mono font-bold">
                          ${parseFloat(entry.total_equity).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </td>
                        <td className="py-3 px-3">
                          <PnlBadge value={preTaxReturn} suffix="%" />
                        </td>
                        <td className="py-3 px-3 font-mono font-bold">
                          ${(entry.after_tax_equity).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </td>
                        <td className="py-3 px-3">
                          <PnlBadge value={afterTaxReturn} suffix="%" />
                        </td>
                        <td className="py-3 px-3">
                          <span className="text-circus-dark/40 font-mono text-xs">—</span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Per-player tax cards */}
          <h2 className="font-carnival text-circus-red text-3xl tracking-wider">MOCK SCHEDULE D — PER PLAYER</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {leaderboard?.map((entry) => (
              <TaxCard key={entry.player_id} entry={entry} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function TaxCard({ entry }: { entry: LeaderboardEntry }) {
  const { data: tax } = useSWR<TaxSummary>(
    `/players/${entry.player_id}/tax`,
    () => api.getPlayerTax(entry.player_id) as Promise<TaxSummary>
  )

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <PlayerAvatar emoji={entry.avatar_emoji} name={entry.name} size="sm" />
        <div className="font-carnival text-circus-red text-xl tracking-wider">{entry.name}</div>
      </div>
      {tax ? (
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="bg-circus-dark/5 rounded p-2">
            <div className="text-xs text-circus-tent/60 font-sub uppercase">ST Gains</div>
            <PnlBadge value={tax.total_short_term_gains} className="font-bold" />
          </div>
          <div className="bg-circus-dark/5 rounded p-2">
            <div className="text-xs text-circus-tent/60 font-sub uppercase">LT Gains</div>
            <PnlBadge value={tax.total_long_term_gains} className="font-bold" />
          </div>
          <div className="bg-circus-dark/5 rounded p-2">
            <div className="text-xs text-circus-tent/60 font-sub uppercase">Wash Sales</div>
            <span className="font-mono font-bold text-clown-purple">${tax.wash_sale_adjustments.toFixed(2)}</span>
          </div>
          <div className="bg-loss-red/10 border border-loss-red/30 rounded p-2">
            <div className="text-xs text-loss-red font-sub uppercase">Est. Tax Owed</div>
            <span className="font-mono font-bold text-loss-red">${tax.total_tax_owed.toFixed(2)}</span>
          </div>
          <div className="col-span-2 bg-circus-dark rounded p-2 text-center">
            <div className="text-xs text-circus-gold/60 font-sub uppercase">After-Tax Portfolio</div>
            <span className="font-mono font-bold text-circus-gold text-lg">${tax.after_tax_equity.toFixed(2)}</span>
          </div>
        </div>
      ) : (
        <div className="text-circus-dark/40 font-sub text-sm text-center py-4">No realized gains yet</div>
      )}
    </div>
  )
}
