/**
 * 猫立ち絵コンポーネント
 * 現状はプレースホルダー（emoji + CSSアニメーション）
 * v1.5以降は PNG/Live2D に差し替える
 */
import { useEffect, useRef } from 'react'
import type { Pose, Expression } from '../types'

interface Props {
  pose: Pose
  expression: Expression
  isFled: boolean
  prevFled: boolean
}

const POSE_EMOJI: Record<Pose, string> = {
  sit:    '🐱',
  lie:    '😺',
  curl:   '😴',
  stand:  '🙀',
  nuzzle: '😻',
  groom:  '🐈',
}

const EXPRESSION_FILTER: Record<Expression, string> = {
  normal:  '',
  happy:   'drop-shadow(0 0 8px rgba(255,180,100,0.6))',
  annoyed: 'drop-shadow(0 0 8px rgba(200,80,80,0.5)) grayscale(0.2)',
}

export function CatSprite({ pose, expression, isFled, prevFled }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  // 逃げる・戻るアニメーション
  useEffect(() => {
    const el = ref.current
    if (!el) return
    if (!prevFled && isFled) {
      el.classList.remove('cat-slide-in')
      el.classList.add('cat-slide-out')
    } else if (prevFled && !isFled) {
      el.classList.remove('cat-slide-out')
      void el.offsetWidth
      el.classList.add('cat-slide-in')
      setTimeout(() => el.classList.remove('cat-slide-in'), 500)
    }
  }, [isFled, prevFled])

  return (
    <div
      ref={ref}
      className="flex items-end justify-center select-none"
      style={{ minHeight: 180 }}
    >
      <span
        className="transition-all duration-300"
        style={{
          fontSize: 120,
          filter: EXPRESSION_FILTER[expression],
          opacity: isFled ? 0 : 1,
        }}
        role="img"
        aria-label={`${pose} ${expression}`}
      >
        {POSE_EMOJI[pose]}
      </span>
    </div>
  )
}
