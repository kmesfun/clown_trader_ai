export function TickerBadge({ ticker }: { ticker: string }) {
  return (
    <span className="ticker-chip">{ticker}</span>
  )
}

export function DirectionBadge({ direction }: { direction: string }) {
  const cls: Record<string, string> = {
    buy: 'direction-buy',
    sell: 'direction-sell',
    short: 'direction-short',
    cover: 'direction-cover',
    buy_to_open: 'direction-buy',
    sell_to_open: 'direction-sell',
    buy_to_close: 'direction-buy',
    sell_to_close: 'direction-sell',
  }
  const labels: Record<string, string> = {
    buy: 'BUY',
    sell: 'SELL',
    short: 'SHORT',
    cover: 'COVER',
    buy_to_open: 'BUY',
    sell_to_open: 'SELL',
    buy_to_close: 'CLOSE',
    sell_to_close: 'CLOSE',
  }
  return (
    <span className={cls[direction] ?? 'direction-buy'}>
      {labels[direction] ?? direction.toUpperCase()}
    </span>
  )
}
