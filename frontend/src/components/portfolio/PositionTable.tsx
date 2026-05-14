import type { Position } from '../../types'
import { TickerBadge } from '../ui/TickerBadge'
import { PnlBadge } from '../ui/PnlBadge'

interface Props {
  positions: Position[]
}

function fmt(val: string | number): string {
  const n = typeof val === 'string' ? parseFloat(val) : val
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function PositionTable({ positions }: Props) {
  if (positions.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-4xl mb-2">🎪</div>
        <div className="font-sub text-circus-dark/50">No open positions</div>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b-2 border-circus-gold">
            {['Ticker', 'Qty', 'Avg Cost', 'Current', 'Market Value', 'P&L', 'P&L %', 'Type'].map((h) => (
              <th key={h} className="text-left py-2 px-2 font-sub text-circus-tent uppercase text-xs">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {positions.map((pos) => (
            <tr key={pos.id} className="border-b border-circus-gold/20 hover:bg-circus-gold/5">
              <td className="py-2 px-2">
                <div className="flex items-center gap-1.5">
                  <TickerBadge ticker={pos.ticker} />
                  {pos.is_short && <span className="text-xs text-clown-purple font-bold">SHORT</span>}
                </div>
              </td>
              <td className="py-2 px-2 font-mono">{parseFloat(pos.quantity).toFixed(4)}</td>
              <td className="py-2 px-2 font-mono">${fmt(pos.avg_cost_basis)}</td>
              <td className="py-2 px-2 font-mono">${fmt(pos.current_price)}</td>
              <td className="py-2 px-2 font-mono font-bold">${fmt(pos.market_value)}</td>
              <td className="py-2 px-2">
                <PnlBadge value={parseFloat(pos.unrealized_pnl)} />
              </td>
              <td className="py-2 px-2">
                <PnlBadge value={parseFloat(pos.unrealized_pnl_pct)} suffix="%" />
              </td>
              <td className="py-2 px-2 text-xs text-circus-dark/60">equity</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
