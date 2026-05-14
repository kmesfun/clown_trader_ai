import useSWR from 'swr'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { api } from '../../api/client'

interface Props {
  ticker?: string
  playerId?: string
  height?: number
}

export function EquityCurve({ ticker = 'SPY', height = 300 }: Props) {
  const { data } = useSWR(
    `/market/history/${ticker}`,
    () => api.getMarketHistory(ticker, 30) as Promise<{ ticker: string; data: Array<{ date: string; close: number }> }>,
    { refreshInterval: 60_000 }
  )

  if (!data?.data?.length) {
    return (
      <div className="flex items-center justify-center h-32 bg-circus-dark/5 rounded">
        <span className="text-circus-dark/40 font-sub text-sm">No chart data available</span>
      </div>
    )
  }

  const minVal = Math.min(...data.data.map((d) => d.close))
  const maxVal = Math.max(...data.data.map((d) => d.close))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data.data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#F6C90E20" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10, fontFamily: 'JetBrains Mono', fill: '#1A0A0088' }}
          tickFormatter={(v: string) => v.slice(5)}
        />
        <YAxis
          domain={[minVal * 0.995, maxVal * 1.005]}
          tick={{ fontSize: 10, fontFamily: 'JetBrains Mono', fill: '#1A0A0088' }}
          tickFormatter={(v: number) => `$${v.toFixed(0)}`}
          width={60}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1A0A00',
            border: '2px solid #F6C90E',
            borderRadius: '6px',
            fontFamily: 'JetBrains Mono',
            color: '#FFF8E7',
          }}
          formatter={(v: number) => [`$${v.toFixed(2)}`, 'Price']}
        />
        <ReferenceLine y={data.data[0]?.close} stroke="#F6C90E" strokeDasharray="4 4" opacity={0.5} />
        <Line
          type="monotone"
          dataKey="close"
          stroke="#CC1F1A"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: '#F6C90E' }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
