import { useState } from 'react'
import type { PersonalityType, FurColor } from '../types'

interface Props {
  onSetup: (name: string, personality: PersonalityType, furColor: FurColor) => void
  isLoading: boolean
}

const PERSONALITIES: { value: PersonalityType; label: string; desc: string }[] = [
  { value: 'tsundere', label: 'ツンデレ',   desc: 'なかなか懐かない。でも懐いたら可愛い' },
  { value: 'amaenbo',  label: '甘えん坊',   desc: 'すぐ好きになる。離れると寂しがる' },
  { value: 'maipace',  label: 'マイペース', desc: '変化が穏やか。いつも我が道を行く' },
]

const FUR_COLORS: { value: FurColor; label: string; emoji: string }[] = [
  { value: 'shiro',    label: 'しろ',     emoji: '⬜' },
  { value: 'kuro',     label: 'くろ',     emoji: '⬛' },
  { value: 'mike',     label: 'みけ',     emoji: '🔶' },
  { value: 'kijitora', label: 'キジトラ', emoji: '🟫' },
  { value: 'sabi',     label: 'サビ',     emoji: '🟤' },
]

export function SetupScreen({ onSetup, isLoading }: Props) {
  const [name, setName] = useState('')
  const [personality, setPersonality] = useState<PersonalityType>('maipace')
  const [furColor, setFurColor] = useState<FurColor>('mike')

  const canSubmit = name.trim().length > 0 && !isLoading

  return (
    <div
      className="min-h-svh flex flex-col items-center justify-center px-6 py-10"
      style={{ background: 'linear-gradient(180deg, #fde68a 0%, #fca5a5 100%)' }}
    >
      <div
        className="w-full max-w-sm rounded-3xl p-6 flex flex-col gap-5"
        style={{
          background: 'rgba(255,255,255,0.82)',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 4px 32px rgba(0,0,0,0.12)',
        }}
      >
        {/* タイトル */}
        <div className="text-center">
          <p className="text-4xl mb-1">🐱</p>
          <h1 className="text-2xl font-bold text-gray-800" style={{ letterSpacing: '-0.5px' }}>
            ネコスイ
          </h1>
          <p className="text-sm text-gray-500 mt-1">猫との距離感を育てるゲーム</p>
        </div>

        {/* 猫の名前 */}
        <div>
          <label className="block text-sm text-gray-600 mb-1 font-medium">猫の名前</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            maxLength={20}
            placeholder="ミル"
            className="w-full rounded-xl px-4 py-3 text-gray-800 outline-none transition"
            style={{
              background: 'rgba(0,0,0,0.05)',
              border: '1.5px solid rgba(0,0,0,0.08)',
              fontSize: 16,
            }}
          />
        </div>

        {/* 性格 */}
        <div>
          <label className="block text-sm text-gray-600 mb-2 font-medium">性格</label>
          <div className="flex flex-col gap-2">
            {PERSONALITIES.map(p => (
              <button
                key={p.value}
                onClick={() => setPersonality(p.value)}
                className="text-left rounded-xl px-4 py-3 transition-all"
                style={{
                  background: personality === p.value
                    ? 'rgba(251,146,60,0.18)'
                    : 'rgba(0,0,0,0.04)',
                  border: personality === p.value
                    ? '1.5px solid rgba(251,146,60,0.5)'
                    : '1.5px solid transparent',
                }}
              >
                <span className="text-sm font-semibold text-gray-800">{p.label}</span>
                <span className="text-xs text-gray-500 ml-2">{p.desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 毛色 */}
        <div>
          <label className="block text-sm text-gray-600 mb-2 font-medium">毛色</label>
          <div className="flex gap-2 flex-wrap">
            {FUR_COLORS.map(f => (
              <button
                key={f.value}
                onClick={() => setFurColor(f.value)}
                className="flex flex-col items-center gap-1 px-3 py-2 rounded-xl transition-all"
                style={{
                  background: furColor === f.value
                    ? 'rgba(251,146,60,0.18)'
                    : 'rgba(0,0,0,0.04)',
                  border: furColor === f.value
                    ? '1.5px solid rgba(251,146,60,0.5)'
                    : '1.5px solid transparent',
                }}
              >
                <span style={{ fontSize: 20 }}>{f.emoji}</span>
                <span className="text-xs text-gray-600">{f.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* はじめるボタン */}
        <button
          onClick={() => canSubmit && onSetup(name.trim(), personality, furColor)}
          disabled={!canSubmit}
          className="w-full py-4 rounded-2xl font-bold text-white transition-all active:scale-95"
          style={{
            background: canSubmit
              ? 'linear-gradient(135deg, #fb923c, #f97316)'
              : 'rgba(0,0,0,0.15)',
            fontSize: 16,
            cursor: canSubmit ? 'pointer' : 'not-allowed',
            boxShadow: canSubmit ? '0 4px 16px rgba(249,115,22,0.35)' : 'none',
          }}
        >
          {isLoading ? '準備中…' : 'はじめる'}
        </button>
      </div>
    </div>
  )
}
