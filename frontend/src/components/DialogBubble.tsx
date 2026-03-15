import { useEffect, useRef } from 'react'

interface Props {
  message: string
  catName: string
  isFled: boolean
}

export function DialogBubble({ message, catName, isFled }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el || !message) return
    el.classList.remove('bubble-in')
    void el.offsetWidth
    el.classList.add('bubble-in')
  }, [message])

  if (!message) return null

  return (
    <div
      ref={ref}
      className="bubble-in mx-4 mb-4 rounded-2xl px-5 py-3 text-center max-w-xs mx-auto"
      style={{
        background: 'rgba(255,255,255,0.85)',
        backdropFilter: 'blur(8px)',
        boxShadow: '0 2px 16px rgba(0,0,0,0.10)',
        border: '1px solid rgba(255,255,255,0.6)',
      }}
    >
      <p className="text-xs text-gray-400 mb-1">{catName}</p>
      <p
        className="text-gray-800 leading-relaxed"
        style={{ fontFamily: "'Hiragino Sans', 'Noto Sans JP', sans-serif", fontSize: 15 }}
      >
        {isFled ? '（どこかへ行ってしまった……）' : message}
      </p>
    </div>
  )
}
