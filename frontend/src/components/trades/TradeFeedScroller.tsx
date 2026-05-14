import { useTrades } from '../../hooks/useTrades'
import { TradeCard } from './TradeCard'
import { LoadingClown } from '../ui/LoadingClown'

export function TradeFeedScroller() {
  const { trades, isLoading } = useTrades()

  return (
    <div className="card h-full">
      <h3 className="font-carnival text-circus-red text-2xl tracking-wider mb-3">
        📡 LIVE TRADE FEED
      </h3>
      {isLoading ? (
        <LoadingClown message="Tuning in..." />
      ) : trades.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-5xl mb-2">🚗</div>
          <div className="font-sub text-circus-dark/50">No trades yet.<br />The clown car is empty.</div>
        </div>
      ) : (
        <div className="flex flex-col gap-2 overflow-y-auto max-h-[600px] pr-1">
          {trades.slice(0, 50).map((trade) => (
            <TradeCard key={trade.id} trade={trade} showPlayer />
          ))}
        </div>
      )}
    </div>
  )
}
