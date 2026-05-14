import { useParams, Link } from 'react-router-dom'
import { usePlayer, usePlayerPositions, usePlayerTax } from '../hooks/usePlayer'
import { usePlayerTrades } from '../hooks/useTrades'
import { PlayerAvatar } from '../components/ui/PlayerAvatar'
import { PnlBadge } from '../components/ui/PnlBadge'
import { PositionTable } from '../components/portfolio/PositionTable'
import { EquityCurve } from '../components/portfolio/EquityCurve'
import { TradeCard } from '../components/trades/TradeCard'
import { LoadingClown } from '../components/ui/LoadingClown'

function MetricBox({ label, value, sub }: { label: string; value: React.ReactNode; sub?: string }) {
  return (
    <div className="bg-circus-dark rounded-lg p-3 text-center">
      <div className="text-circus-gold/60 text-xs font-sub uppercase tracking-wider mb-1">{label}</div>
      <div className="text-circus-cream text-lg font-mono font-bold">{value}</div>
      {sub && <div className="text-circus-gold/40 text-xs font-mono mt-0.5">{sub}</div>}
    </div>
  )
}

export function PlayerDetail() {
  const { id } = useParams<{ id: string }>()
  const { player, isLoading } = usePlayer(id!)
  const { positions } = usePlayerPositions(id!)
  const { trades } = usePlayerTrades(id!)
  const { tax } = usePlayerTax(id!)

  if (isLoading || !player) return <LoadingClown message="Summoning the player..." />

  const equity = parseFloat(player.total_equity)
  const returnPct = parseFloat(player.total_return_pct)

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link to="/" className="text-circus-red font-sub font-bold text-sm hover:underline">
        ← Back to Arena
      </Link>

      {/* Player header */}
      <div className="card flex items-start gap-6">
        <PlayerAvatar emoji={player.avatar_emoji} name={player.name} size="lg" />
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="font-carnival text-circus-red text-5xl tracking-wider">{player.name}</h1>
            <span className={`text-xs font-sub font-bold uppercase px-2 py-1 rounded tracking-wider ${player.type === 'clown' ? 'bg-circus-red text-white' : 'bg-circus-dark text-circus-gold'}`}>
              {player.type}
            </span>
            {player.pdt_locked && (
              <span className="text-xs font-bold text-loss-red bg-loss-red/10 px-2 py-1 rounded">⚠️ PDT LOCKED</span>
            )}
          </div>
          <p className="text-circus-dark/70 font-sub mt-1">{player.strategy_description}</p>
        </div>
        <div className="text-right">
          <div className="font-mono text-3xl font-bold text-circus-dark">
            ${equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <PnlBadge value={returnPct} suffix="%" className="text-xl" />
        </div>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricBox
          label="Cash Available"
          value={`$${parseFloat(player.settled_cash).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`}
        />
        <MetricBox
          label="Unrealized P&L"
          value={<PnlBadge value={parseFloat(player.unrealized_pnl)} className="text-lg" />}
        />
        <MetricBox
          label="Realized P&L"
          value={<PnlBadge value={parseFloat(player.realized_pnl)} className="text-lg" />}
        />
        <MetricBox
          label="Open Positions"
          value={positions.length}
        />
      </div>

      {/* Chart */}
      <div className="card">
        <h2 className="font-carnival text-circus-red text-2xl tracking-wider mb-4">📈 MARKET REFERENCE (SPY)</h2>
        <EquityCurve ticker="SPY" height={280} />
      </div>

      {/* Positions */}
      <div className="card">
        <h2 className="font-carnival text-circus-red text-2xl tracking-wider mb-4">
          🎯 OPEN POSITIONS ({positions.length})
        </h2>
        <PositionTable positions={positions} />
      </div>

      {/* Tax Summary */}
      {tax && (
        <div className="card border-loss-red/30">
          <h2 className="font-carnival text-circus-red text-2xl tracking-wider mb-4">🏛️ TAX SUMMARY (YTD)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricBox label="Short-Term Gains" value={<PnlBadge value={tax.total_short_term_gains} />} />
            <MetricBox label="Long-Term Gains" value={<PnlBadge value={tax.total_long_term_gains} />} />
            <MetricBox label="Wash Sale Adj." value={<PnlBadge value={-tax.wash_sale_adjustments} />} />
            <MetricBox
              label="Est. Tax Owed"
              value={<span className="text-loss-red">${tax.total_tax_owed.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>}
              sub={`After-tax: $${tax.after_tax_equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            />
          </div>
        </div>
      )}

      {/* Trade history */}
      <div className="card">
        <h2 className="font-carnival text-circus-red text-2xl tracking-wider mb-4">
          📋 TRADE HISTORY ({trades.length})
        </h2>
        {trades.length === 0 ? (
          <div className="text-center py-8 text-circus-dark/50 font-sub">No trades yet</div>
        ) : (
          <div className="flex flex-col gap-2 max-h-[500px] overflow-y-auto">
            {trades.map((t) => (
              <TradeCard key={t.id} trade={t} showPlayer={false} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
