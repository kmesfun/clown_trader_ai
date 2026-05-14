import { api } from '../api/client'
import { LeaderboardCard } from '../components/leaderboard/LeaderboardCard'
import { TradeFeedScroller } from '../components/trades/TradeFeedScroller'

export function Dashboard() {
  const handleMarkToMarket = async () => {
    try {
      await api.triggerMarkToMarket()
      alert('Mark-to-market complete!')
    } catch {
      alert('Failed to trigger mark-to-market')
    }
  }

  const handleRunBots = async () => {
    try {
      const result = await api.runBots() as { summary: Record<string, unknown> }
      alert(`Bots run!\n${JSON.stringify(result.summary, null, 2)}`)
    } catch {
      alert('Failed to run bots')
    }
  }

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="relative bg-circus-tent border-4 border-circus-gold rounded-xl p-8 text-center overflow-hidden shadow-circus-lg">
        <div className="absolute inset-0 opacity-10 text-[20rem] flex items-center justify-center select-none pointer-events-none leading-none">
          🤡
        </div>
        <div className="relative">
          <h1 className="font-carnival text-circus-gold text-7xl md:text-9xl tracking-widest drop-shadow-lg">
            CLOWN ARENA
          </h1>
          <p className="text-circus-cream text-xl font-sub mt-2 opacity-90 tracking-wide">
            "The Clown" vs. The Machines — $100,000 each. Real rules. Real pain.
          </p>
          <div className="mt-4 flex justify-center gap-3 flex-wrap">
            <div className="bg-circus-gold/20 border border-circus-gold text-circus-gold text-xs font-sub font-bold uppercase px-3 py-1 rounded tracking-wider">
              T+1 Settlement
            </div>
            <div className="bg-circus-gold/20 border border-circus-gold text-circus-gold text-xs font-sub font-bold uppercase px-3 py-1 rounded tracking-wider">
              PDT Rules
            </div>
            <div className="bg-circus-gold/20 border border-circus-gold text-circus-gold text-xs font-sub font-bold uppercase px-3 py-1 rounded tracking-wider">
              Wash Sale Tracking
            </div>
            <div className="bg-circus-gold/20 border border-circus-gold text-circus-gold text-xs font-sub font-bold uppercase px-3 py-1 rounded tracking-wider">
              After-Tax Returns
            </div>
          </div>
        </div>
      </div>

      {/* Dev controls */}
      <div className="flex gap-2 justify-end">
        <button onClick={handleMarkToMarket} className="btn-gold text-xs">
          ↻ Mark to Market
        </button>
        <button onClick={handleRunBots} className="btn-primary text-xs">
          🤖 Run Bots Now
        </button>
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2">
          <LeaderboardCard />
        </div>
        <div className="xl:col-span-1">
          <TradeFeedScroller />
        </div>
      </div>
    </div>
  )
}
