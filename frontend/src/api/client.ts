import type { SetupResponse, CatResponse, SessionStatus, PersonalityType, FurColor, ActionType } from '../types'

const BASE = '/api'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

async function del<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export const api = {
  setup(name: string, personality: PersonalityType, furColor: FurColor): Promise<SetupResponse> {
    return post('/cat/setup', { name, personality, fur_color: furColor })
  },

  chat(sessionId: string, action: ActionType, text?: string): Promise<CatResponse> {
    return post('/chat', { session_id: sessionId, action, text })
  },

  status(sessionId: string): Promise<SessionStatus> {
    return get(`/cat/status/${sessionId}`)
  },

  savedSession(): Promise<{ session_id: string; cat_name: string }> {
    return get('/saved-session')
  },

  clearSavedSession(): Promise<{ status: string }> {
    return del('/saved-session')
  },
}
