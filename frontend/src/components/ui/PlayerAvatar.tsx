interface Props {
  emoji: string
  name: string
  size?: 'sm' | 'md' | 'lg'
}

const SIZE_MAP = {
  sm: 'text-xl w-8 h-8',
  md: 'text-3xl w-12 h-12',
  lg: 'text-5xl w-16 h-16',
}

export function PlayerAvatar({ emoji, name, size = 'md' }: Props) {
  return (
    <div
      className={`${SIZE_MAP[size]} flex items-center justify-center rounded-full bg-circus-dark border-2 border-circus-gold shadow-circus`}
      title={name}
    >
      {emoji}
    </div>
  )
}
