import { Outlet } from 'react-router-dom'
import { Header } from './Header'

export function Layout() {
  return (
    <div className="min-h-screen circus-bg">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>
      <footer className="border-t-4 border-circus-gold bg-circus-tent text-center py-3 mt-12">
        <span className="text-circus-cream text-xs font-sub opacity-60 tracking-widest uppercase">
          🤡 Paper Trading Only — No Real Money · The Clown Always Loses Eventually · Past Performance Means Nothing 🤡
        </span>
      </footer>
    </div>
  )
}
