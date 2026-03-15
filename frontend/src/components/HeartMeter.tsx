import { useEffect, useRef } from 'react'

interface Props {
  level: number  // 0.0 - 1.0
}

const HEARTS = 5

export function HeartMeter({ level }: Props) {
  const filled = Math.round(level * HEARTS * 2) / 2  // 0.5刻み
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.classList.remove('heart-pop')
    void el.offsetWidth
    el.classList.add('heart-pop')
    setTimeout(() => el.classList.remove('heart-pop'), 500)
  }, [Math.round(level * 10)])  // 0.1ずつ変化したら反応

  return (
    <div ref={ref} className="flex gap-1 justify-center py-2">
      {Array.from({ length: HEARTS }).map((_, i) => {
        const fillAmount = Math.min(1, Math.max(0, filled - i))
        return (
          <span
            key={i}
            style={{
              fontSize: 20,
              opacity: fillAmount === 0 ? 0.2 : fillAmount < 1 ? 0.6 : 1,
              filter: fillAmount === 1 ? 'drop-shadow(0 0 4px rgba(255,100,150,0.5))' : 'none',
              transition: 'all 0.3s ease',
            }}
          >
            {fillAmount === 0 ? '🤍' : '❤️'}
          </span>
        )
      })}
    </div>
  )
}
