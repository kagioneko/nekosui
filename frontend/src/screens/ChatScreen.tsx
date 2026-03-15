import { useRef, useEffect, useState } from 'react'
import type { GameState } from '../hooks/useGame'
import type { ActionType } from '../types'
import { Background } from '../components/Background'
import { CatSprite } from '../components/CatSprite'
import { DialogBubble } from '../components/DialogBubble'
import { HeartMeter } from '../components/HeartMeter'
import { ActionBar } from '../components/ActionBar'

interface Props {
  state: GameState
  onAction: (action: ActionType, text?: string) => void
}

const TIME_LABEL: Record<string, string> = {
  morning:  '🌅 朝',
  midday:   '☀️ 昼',
  evening:  '🌆 夕方',
  night:    '🌙 夜',
  midnight: '🌌 深夜',
}

export function ChatScreen({ state, onAction }: Props) {
  const prevFledRef = useRef(state.isFled)
  const [textInput, setTextInput] = useState('')

  useEffect(() => {
    prevFledRef.current = state.isFled
  })

  const handleText = () => {
    if (!textInput.trim()) return
    onAction('text', textInput.trim())
    setTextInput('')
  }

  const nightMode = state.timePeriod === 'night' || state.timePeriod === 'midnight'

  return (
    <Background period={state.timePeriod}>
      <div className="max-w-sm mx-auto min-h-svh flex flex-col">

        {/* ヘッダー */}
        <div className="flex items-center justify-between px-4 pt-4 pb-2">
          <span
            className="text-sm font-medium px-3 py-1 rounded-full"
            style={{
              background: 'rgba(255,255,255,0.4)',
              color: nightMode ? '#e2e8f0' : '#374151',
              backdropFilter: 'blur(8px)',
            }}
          >
            {TIME_LABEL[state.timePeriod]}
          </span>

          <HeartMeter level={state.relationshipLevel} />

          <span
            className="text-sm font-medium px-3 py-1 rounded-full"
            style={{
              background: 'rgba(255,255,255,0.4)',
              color: nightMode ? '#e2e8f0' : '#374151',
              backdropFilter: 'blur(8px)',
            }}
          >
            {state.cat.name}
          </span>
        </div>

        {/* 猫立ち絵エリア */}
        <div className="flex-1 flex flex-col items-center justify-end pb-2">
          <CatSprite
            pose={state.pose}
            expression={state.expression}
            isFled={state.isFled}
            prevFled={prevFledRef.current}
          />

          {/* セリフバブル */}
          <DialogBubble
            message={state.message}
            catName={state.cat.name}
            isFled={state.isFled}
          />
        </div>

        {/* アクションバー */}
        <div
          className="rounded-t-3xl pb-safe"
          style={{
            background: 'rgba(255,255,255,0.25)',
            backdropFilter: 'blur(12px)',
            borderTop: '1px solid rgba(255,255,255,0.4)',
          }}
        >
          <ActionBar
            onAction={onAction}
            disabled={state.isLoading}
            isFled={state.isFled}
          />

          {/* テキスト入力 */}
          <div className="flex gap-2 px-4 pb-4 pt-1">
            <input
              value={textInput}
              onChange={e => setTextInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleText()}
              placeholder="話しかける…"
              className="flex-1 rounded-xl px-4 py-2 text-sm outline-none"
              style={{
                background: 'rgba(255,255,255,0.7)',
                border: '1px solid rgba(255,255,255,0.5)',
                color: '#374151',
              }}
            />
            <button
              onClick={handleText}
              disabled={!textInput.trim() || state.isLoading}
              className="px-4 py-2 rounded-xl text-sm font-medium transition-all active:scale-95"
              style={{
                background: textInput.trim() ? 'rgba(249,115,22,0.85)' : 'rgba(0,0,0,0.1)',
                color: textInput.trim() ? 'white' : '#9ca3af',
              }}
            >
              送る
            </button>
          </div>
        </div>

      </div>
    </Background>
  )
}
