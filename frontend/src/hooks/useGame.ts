import { useState, useCallback, useEffect } from 'react'
import { api } from '../api/client'
import type { CatProfile, ActionType, Pose, Expression, TimePeriod } from '../types'

const SESSION_KEY = 'nekosui_session_id'

export function getSavedSessionId(): string | null {
  return localStorage.getItem(SESSION_KEY)
}

function saveSessionId(id: string) {
  localStorage.setItem(SESSION_KEY, id)
}

export function clearSavedSession() {
  localStorage.removeItem(SESSION_KEY)
}

export interface GameState {
  sessionId: string
  cat: CatProfile
  message: string
  pose: Pose
  expression: Expression
  sound: string | null
  isFled: boolean
  relationshipLevel: number
  timePeriod: TimePeriod
  isLoading: boolean
}

export function useGame() {
  const [state, setState] = useState<GameState | null>(null)

  const setup = useCallback(async (
    name: string,
    personality: 'tsundere' | 'amaenbo' | 'maipace',
    furColor: 'shiro' | 'kuro' | 'mike' | 'kijitora' | 'sabi',
  ) => {
    const res = await api.setup(name, personality, furColor)
    console.debug('[nekosui] setup', res.initial_state)

    saveSessionId(res.session_id)
    const status = await api.status(res.session_id)
    setState({
      sessionId: res.session_id,
      cat: res.cat,
      message: res.greeting,
      pose: 'sit',
      expression: 'normal',
      sound: null,
      isFled: false,
      relationshipLevel: 0,
      timePeriod: status.time_period,
      isLoading: false,
    })
  }, [])

  // 保存済みセッションを復元する
  const resume = useCallback(async (sessionId: string) => {
    try {
      const status = await api.status(sessionId)
      setState({
        sessionId,
        cat: status.cat,
        message: 'おかえり…（じっとこちらを見ている）',
        pose: 'sit',
        expression: 'normal',
        sound: null,
        isFled: status.is_fled,
        relationshipLevel: status.relationship_level,
        timePeriod: status.time_period,
        isLoading: false,
      })
      return true
    } catch {
      clearSavedSession()
      return false
    }
  }, [])

  const act = useCallback(async (action: ActionType, text?: string) => {
    if (!state || state.isLoading) return

    setState(s => s ? { ...s, isLoading: true } : s)

    try {
      const res = await api.chat(state.sessionId, action, text)
      console.debug('[nekosui] chat', { action, neuro: res.neuro_state, log: res.event_log })

      setState(s => s ? {
        ...s,
        message: res.message,
        pose: res.pose,
        expression: res.expression,
        sound: res.sound,
        isFled: res.is_fled,
        relationshipLevel: res.relationship_level,
        isLoading: false,
      } : s)
    } catch (err) {
      console.error('[nekosui] error', err)
      setState(s => s ? { ...s, isLoading: false } : s)
    }
  }, [state])

  // 定期ポーリング: 30秒ごとに状態を更新（時間帯変化・逃げ猫の自然回復を反映）
  useEffect(() => {
    if (!state?.sessionId || state.isLoading) return

    const timer = setInterval(async () => {
      try {
        const status = await api.status(state.sessionId)
        setState(s => s ? {
          ...s,
          timePeriod: status.time_period,
          isFled: status.is_fled,
          relationshipLevel: status.relationship_level,
        } : s)
      } catch (err) {
        console.error('[nekosui] poll error', err)
      }
    }, 30_000)

    return () => clearInterval(timer)
  }, [state?.sessionId, state?.isLoading])

  return { state, setup, resume, act }
}
