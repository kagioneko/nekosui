import { useState } from 'react'
import { useGame } from './hooks/useGame'
import { SetupScreen } from './screens/SetupScreen'
import { ChatScreen } from './screens/ChatScreen'
import type { PersonalityType, FurColor } from './types'

export default function App() {
  const { state, setup, act } = useGame()
  const [isSetupLoading, setIsSetupLoading] = useState(false)

  const handleSetup = async (name: string, personality: PersonalityType, furColor: FurColor) => {
    setIsSetupLoading(true)
    try {
      await setup(name, personality, furColor)
    } finally {
      setIsSetupLoading(false)
    }
  }

  if (!state) {
    return <SetupScreen onSetup={handleSetup} isLoading={isSetupLoading} />
  }

  return <ChatScreen state={state} onAction={act} />
}
