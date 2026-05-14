import { formatDistanceToNow } from 'date-fns'
import type { Trade } from '../../types'
import { TickerBadge, DirectionBadge } from '../ui/TickerBadge'
import { PnlBadge } from '../ui/PnlBadge'

interface Props {
  trade: Trade
  showPlayer?: boolean
}

export function TradeCard({ trade, showPlayer = true }: Props) {
  const timeAgo = formatDistanceToNow(new Date(trade.executed_at), { addSuffix: true })
  const totalValue = parseFloat(trade.total_value)
  const hasPnl = trade.realized_pnl !== null

  return (
    <div className="flex items-start gap-3 p-3 bg-circus-cream border border-circus-gold/30 rounded-lg hover:border-circus-gold transition-colors">
      {showPlayer && (
        <div className="text-2xl flex-shrink-0 w-9 h-9 flex items-center justify-center bg-circus-dark rounded-full border border-circus-gold">
          {trade.player_avatar_emoji}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <TickerBadge ticker={trade.ticker} />
          <DirectionBadge direction={trade.direction} />
          {trade.wash_sale_flag && (
            <span className="text-xs bg-clown-purple/20 text-clown-purple px-1.5 py-0.5 rounded font-bold">
              ♻️ WASH
            </span>
          )}
        </div>
        <div className="mt-1 text-xs text-circus-dark/70 font-mono">
          {parseFloat(trade.quantity).toLocaleString()} shares @ ${parseFloat(trade.price).toFixed(2)}
          {' · '}
          <span className="font-bold">${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        </div>
        {hasPnl && (
          <div className="mt-0.5 text-xs">
            P&L: <PnlBadge value={parseFloat(trade.realized_pnl!)} />
          </div>
        )}
        {trade.notes && (
          <div className="mt-0.5 text-xs text-circus-dark/50 truncate">{trade.notes}</div>
        )}
      </div>
      <div className="text-right flex-shrink-0">
        {showPlayer && (
          <div className="text-xs font-sub font-bold text-circus-tent">{trade.player_name}</div>
        )}
        <div className="text-xs text-circus-dark/50 font-mono">{timeAgo}</div>
        <div className="text-xs text-circus-dark/40">{trade.source.replace('bot_', '').replace('_', ' ')}</div>
      </div>
    </div>
  )
}
