import type { TimePeriod } from '../types'

const GRADIENTS: Record<TimePeriod, string> = {
  morning:  'linear-gradient(180deg, #fde68a 0%, #fca5a5 40%, #fcd5b0 100%)',
  midday:   'linear-gradient(180deg, #bae6fd 0%, #e0f2fe 60%, #f0f9ff 100%)',
  evening:  'linear-gradient(180deg, #f97316 0%, #fb923c 30%, #fcd34d 100%)',
  night:    'linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%)',
  midnight: 'linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%)',
}

interface Props {
  period: TimePeriod
  children: React.ReactNode
}

export function Background({ period, children }: Props) {
  return (
    <div
      className="min-h-svh transition-all duration-[2000ms]"
      style={{ background: GRADIENTS[period] }}
    >
      {children}
    </div>
  )
}
