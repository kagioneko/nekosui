import type { ActionType } from '../types'

interface Props {
  onAction: (action: ActionType) => void
  disabled: boolean
  isFled: boolean
}

const ACTIONS: { action: ActionType; label: string; emoji: string }[] = [
  { action: 'nekosui', label: '猫吸い',   emoji: '😤' },
  { action: 'naderu',  label: 'なでる',   emoji: '🤚' },
  { action: 'gohan',   label: 'ごはん',   emoji: '🍚' },
  { action: 'asobu',   label: '遊ぶ',     emoji: '🧶' },
  { action: 'dakko',   label: '抱っこ',   emoji: '🫂' },
  { action: 'namae',   label: '名前を呼ぶ', emoji: '📣' },
]

export function ActionBar({ onAction, disabled, isFled }: Props) {
  return (
    <div className="grid grid-cols-3 gap-2 px-4 pb-2">
      {ACTIONS.map(({ action, label, emoji }) => (
        <button
          key={action}
          onClick={() => onAction(action)}
          disabled={disabled}
          className="flex flex-col items-center gap-1 py-3 rounded-2xl transition-all active:scale-95"
          style={{
            background: 'rgba(255,255,255,0.75)',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255,255,255,0.5)',
            opacity: disabled ? 0.5 : isFled && action !== 'namae' ? 0.4 : 1,
            cursor: disabled ? 'not-allowed' : 'pointer',
            boxShadow: '0 1px 8px rgba(0,0,0,0.08)',
          }}
        >
          <span style={{ fontSize: 24 }}>{emoji}</span>
          <span className="text-xs text-gray-600">{label}</span>
        </button>
      ))}
    </div>
  )
}
