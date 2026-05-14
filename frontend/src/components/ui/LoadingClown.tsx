export function LoadingClown({ message = 'Loading the Arena...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <div className="text-6xl animate-bounce">🤡</div>
      <div className="font-carnival text-circus-red text-2xl tracking-widest">{message}</div>
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 bg-circus-gold rounded-full animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  )
}
