import { useState, useEffect } from 'react'
import { useGame, getSavedSessionId, clearSavedSession } from './hooks/useGame'
import { SetupScreen } from './screens/SetupScreen'
import { ChatScreen } from './screens/ChatScreen'
import type { PersonalityType, FurColor } from './types'
import { api } from './api/client'

type AppPhase = 'checking' | 'resume_prompt' | 'setup' | 'playing'

export default function App() {
  const { state, setup, resume, act } = useGame()
  const [phase, setPhase] = useState<AppPhase>('checking')
  const [isSetupLoading, setIsSetupLoading] = useState(false)
  const [savedCatName, setSavedCatName] = useState<string | null>(null)

  // 起動時: 保存済みセッションの確認
  useEffect(() => {
    const sessionId = getSavedSessionId()
    if (!sessionId) {
      setPhase('setup')
      return
    }
    api.status(sessionId)
      .then(status => {
        setSavedCatName(status.cat.name)
        setPhase('resume_prompt')
      })
      .catch(() => {
        clearSavedSession()
        setPhase('setup')
      })
  }, [])

  const handleResume = async () => {
    const sessionId = getSavedSessionId()
    if (!sessionId) return
    setIsSetupLoading(true)
    const ok = await resume(sessionId)
    setIsSetupLoading(false)
    if (ok) setPhase('playing')
    else setPhase('setup')
  }

  const handleNewCat = () => {
    clearSavedSession()
    setPhase('setup')
  }

  const handleSetup = async (name: string, personality: PersonalityType, furColor: FurColor) => {
    setIsSetupLoading(true)
    try {
      await setup(name, personality, furColor)
      setPhase('playing')
    } finally {
      setIsSetupLoading(false)
    }
  }

  if (phase === 'checking') {
    return (
      <div className="flex items-center justify-center min-h-screen bg-sky-100">
        <p className="text-gray-400 text-sm">読み込み中...</p>
      </div>
    )
  }

  if (phase === 'resume_prompt') {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-sky-100 gap-6 px-6">
        <div className="text-5xl">🐱</div>
        <p className="text-gray-700 text-lg font-medium">
          {savedCatName} が待っています
        </p>
        <div className="flex flex-col gap-3 w-full max-w-xs">
          <button
            onClick={handleResume}
            disabled={isSetupLoading}
            className="w-full py-3 rounded-2xl bg-orange-400 text-white font-bold text-base shadow active:scale-95 transition"
          >
            {isSetupLoading ? '読み込み中...' : `${savedCatName} のところへ戻る`}
          </button>
          <button
            onClick={handleNewCat}
            className="w-full py-3 rounded-2xl bg-white text-gray-400 text-sm shadow active:scale-95 transition"
          >
            新しい猫を作る
          </button>
        </div>
      </div>
    )
  }

  if (phase === 'setup' || !state) {
    return <SetupScreen onSetup={handleSetup} isLoading={isSetupLoading} />
  }

  return <ChatScreen state={state} onAction={act} />
}
