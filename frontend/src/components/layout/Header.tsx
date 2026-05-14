import { Link, useLocation } from 'react-router-dom'
import { useMarketStatus } from '../../hooks/useMarketStatus'

const NAV = [
  { to: '/', label: 'Arena' },
  { to: '/trades', label: 'Trade Feed' },
  { to: '/cramer', label: 'Cramer Picks' },
  { to: '/tax', label: 'Tax Report' },
]

export function Header() {
  const { status } = useMarketStatus()
  const location = useLocation()

  return (
    <header className="bg-circus-tent border-b-4 border-circus-gold shadow-circus-lg">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-3xl">🤡</span>
          <div>
            <div className="font-carnival text-circus-gold text-2xl leading-none tracking-widest">
              CLOWN ARENA
            </div>
            <div className="text-circus-cream text-xs font-sub opacity-70 tracking-wider">
              CAN A CLOWN BEAT THE MACHINES?
            </div>
          </div>
        </Link>

        <nav className="flex items-center gap-1">
          {NAV.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`font-sub font-bold uppercase text-sm px-3 py-1.5 rounded tracking-wider transition-colors ${
                location.pathname === to
                  ? 'bg-circus-gold text-circus-dark'
                  : 'text-circus-cream hover:text-circus-gold'
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          {status && (
            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded font-sub font-bold text-sm uppercase tracking-wider ${
              status.is_open
                ? 'bg-gain-green text-white'
                : 'bg-circus-dark text-circus-gold border border-circus-gold'
            }`}>
              <span className={`w-2 h-2 rounded-full ${status.is_open ? 'bg-white animate-pulse' : 'bg-circus-gold'}`} />
              {status.is_open ? 'MARKET OPEN' : 'MARKET CLOSED'}
            </div>
          )}
          <div className="text-circus-cream text-xs font-mono opacity-60">
            {status?.current_time_et ?? '—'}
          </div>
        </div>
      </div>
    </header>
  )
}
