interface Props {
  value: number | string
  suffix?: string
  className?: string
}

export function PnlBadge({ value, suffix = '', className = '' }: Props) {
  const num = typeof value === 'string' ? parseFloat(value) : value
  const isPos = num > 0
  const isNeg = num < 0
  const formatted = Math.abs(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  return (
    <span className={`font-mono font-bold ${isPos ? 'text-gain-green' : isNeg ? 'text-loss-red' : 'text-circus-dark'} ${className}`}>
      {isPos ? '+' : isNeg ? '-' : ''}{formatted}{suffix}
    </span>
  )
}
