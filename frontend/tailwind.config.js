/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'circus-red': '#CC1F1A',
        'circus-red-dark': '#9B1713',
        'circus-gold': '#F6C90E',
        'circus-gold-dark': '#C9A50B',
        'circus-cream': '#FFF8E7',
        'circus-dark': '#1A0A00',
        'circus-tent': '#8B1A1A',
        'gain-green': '#00C853',
        'loss-red': '#FF1744',
        'clown-purple': '#7B1FA2',
      },
      fontFamily: {
        carnival: ['"Bebas Neue"', 'Impact', 'sans-serif'],
        sub: ['Oswald', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'monospace'],
      },
      backgroundImage: {
        'circus-stripes': 'repeating-linear-gradient(45deg, #FFF8E7 0px, #FFF8E7 20px, #fef3d0 20px, #fef3d0 40px)',
      },
      boxShadow: {
        'circus': '0 4px 0 #C9A50B, 0 6px 12px rgba(0,0,0,0.2)',
        'circus-lg': '0 6px 0 #9B1713, 0 8px 24px rgba(0,0,0,0.3)',
      },
      keyframes: {
        ticker: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(-100%)' },
        },
        honk: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.1)' },
        },
      },
      animation: {
        ticker: 'ticker 30s linear infinite',
        honk: 'honk 0.3s ease-in-out',
      },
    },
  },
  plugins: [],
}
