export type PersonalityType = 'tsundere' | 'amaenbo' | 'maipace'
export type FurColor = 'shiro' | 'kuro' | 'mike' | 'kijitora' | 'sabi'
export type ActionType = 'nekosui' | 'naderu' | 'gohan' | 'asobu' | 'dakko' | 'namae' | 'mushi' | 'text'
export type Pose = 'sit' | 'lie' | 'curl' | 'stand' | 'nuzzle' | 'groom'
export type Expression = 'normal' | 'happy' | 'annoyed'
export type TimePeriod = 'morning' | 'midday' | 'evening' | 'night' | 'midnight'

export interface CatProfile {
  cat_id: string
  name: string
  personality: PersonalityType
  fur_color: FurColor
  birthday: string
}

export interface NeuroState {
  D: number; S: number; C: number
  O: number; G: number; E: number
  corruption: number
}

export interface SetupResponse {
  session_id: string
  cat: CatProfile
  initial_state: NeuroState
  greeting: string
}

export interface CatResponse {
  message: string
  pose: Pose
  expression: Expression
  sound: string | null
  is_fled: boolean
  neuro_state: NeuroState
  relationship_level: number
  event_log: string[]
}

export interface SessionStatus {
  session_id: string
  cat: CatProfile
  neuro_state: NeuroState
  relationship_level: number
  is_fled: boolean
  time_period: TimePeriod
  consecutive_nekosui: number
}
