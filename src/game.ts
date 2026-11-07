import { GOAL, START } from './states'

export type Party = 'D' | 'R' | 'I-D' | 'I-R' | 'I' | '?'
export interface Official { name: string; party: Party; leader?: 'D' | 'R' }
export interface StateInfo {
  name: string
  governor: Official
  senators: Official[]
  house: { D: number; R: number; uncalled: number }
  notes?: string
  sources?: string[]
}
export interface Officials { asOf: string; note?: string; states: Record<string, StateInfo> }

export type Difficulty = 'easy' | 'normal' | 'hard'
export type Color = 'blue' | 'red' | 'purple'

export const DIFFICULTY: Record<Difficulty, { label: string; rule: string }> = {
  easy: { label: 'Easy', rule: 'Any Democrat counts: governor, U.S. senator or House member.' },
  normal: { label: 'Normal', rule: 'Needs a Democratic governor or U.S. senator.' },
  hard: { label: 'Hard', rule: 'Needs a Democratic governor or a Democratic House majority.' },
}

const isDem = (p: Party) => p === 'D' || p === 'I-D'
const isOpen = (p: Party) => p === '?'

/** The colour a state has under a rule; purple = depends on a race that is not called yet. */
export function stateColor(s: StateInfo, d: Difficulty): Color {
  const gov = s.governor.party
  const sens = s.senators.map((x) => x.party)
  const seats = s.house.D + s.house.R + s.house.uncalled
  if (d === 'hard') {
    if (isDem(gov) || s.house.D * 2 > seats) return 'blue'
    if (isOpen(gov) || (s.house.D + s.house.uncalled) * 2 > seats) return 'purple'
    return 'red'
  }
  if (isDem(gov) || sens.some(isDem)) return 'blue'
  if (d === 'easy' && s.house.D > 0) return 'blue'
  if (isOpen(gov) || sens.some(isOpen) || (d === 'easy' && s.house.uncalled > 0)) return 'purple'
  return 'red'
}

/** Human-readable list of the Democrats that make a state blue. */
export function democrats(s: StateInfo): string[] {
  const out: string[] = []
  if (isDem(s.governor.party)) out.push(`Gov. ${s.governor.name}`)
  for (const x of s.senators) if (isDem(x.party)) out.push(`Sen. ${x.name}${x.party === 'I-D' ? ' (I)' : ''}`)
  if (s.house.D > 0) out.push(`${s.house.D} of ${s.house.D + s.house.R + s.house.uncalled} House seats`)
  return out
}

function hash(str: string): number {
  let h = 2166136261
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619) }
  return h >>> 0
}

export type MoveKind = 'start' | 'step' | 'mail' | 'back'
export interface Move { to: string; kind: MoveKind; outcome: 'blue' | 'red'; gamble: boolean }

export interface GameState {
  difficulty: Difficulty
  seed: number
  status: 'start' | 'playing' | 'won' | 'lost'
  current: string | null
  visited: string[]
  revealed: Record<string, 'blue' | 'red'>
  peeked: string[]
  flags: string[]
  moves: Move[]
  powerups: { exitPoll: number; mailIn: number; recount: number }
  lostAt: string | null
}

export class Game {
  s: GameState
  constructor(private data: Officials, private adj: Record<string, string[]>, difficulty: Difficulty, seed = Date.now()) {
    this.s = {
      difficulty, seed, status: 'start', current: null, visited: [], revealed: {}, peeked: [], flags: [], moves: [],
      powerups: { exitPoll: 1, mailIn: 1, recount: 1 }, lostAt: null,
    }
  }

  info(code: string): StateInfo { return this.data.states[code] }
  color(code: string): Color { return stateColor(this.info(code), this.s.difficulty) }

  /** What the state really turns out to be in this game (purple resolves by a seeded coin flip). */
  outcome(code: string): 'blue' | 'red' {
    const c = this.color(code)
    if (c !== 'purple') return c
    return hash(`${this.s.seed}:${code}`) % 2 === 0 ? 'blue' : 'red'
  }

  neighbors(code: string): string[] { return this.adj[code] ?? [] }
  startOptions(): string[] { return START.filter((c) => this.outcome(c) === 'blue') }
  moveOptions(): string[] { return this.s.current ? this.neighbors(this.s.current) : [] }
  mailOptions(): string[] {
    if (!this.s.current || this.s.powerups.mailIn < 1) return []
    const near = new Set(this.moveOptions())
    const out = new Set<string>()
    for (const n of near) for (const m of this.neighbors(n)) if (m !== this.s.current && !near.has(m) && !this.s.visited.includes(m)) out.add(m)
    return [...out].sort()
  }
  peekOptions(): string[] {
    if (this.s.powerups.exitPoll < 1) return []
    return this.moveOptions().filter((c) => !this.s.revealed[c])
  }

  start(code: string): Move | null {
    if (this.s.status !== 'start' || !this.startOptions().includes(code)) return null
    this.s.status = 'playing'
    return this.land(code, 'start')
  }

  step(code: string): Move | null {
    if (this.s.status !== 'playing' || !this.moveOptions().includes(code)) return null
    return this.land(code, this.s.visited.includes(code) ? 'back' : 'step')
  }

  mail(code: string): Move | null {
    if (this.s.status !== 'playing' || !this.mailOptions().includes(code)) return null
    this.s.powerups.mailIn--
    return this.land(code, 'mail')
  }

  peek(code: string): 'blue' | 'red' | null {
    if (this.s.status !== 'playing' || !this.peekOptions().includes(code)) return null
    this.s.powerups.exitPoll--
    const o = this.outcome(code)
    this.s.revealed[code] = o
    if (!this.s.peeked.includes(code)) this.s.peeked.push(code)
    return o
  }

  recount(): boolean {
    if (this.s.status !== 'lost' || this.s.powerups.recount < 1) return false
    this.s.powerups.recount--
    this.s.status = 'playing'
    this.s.lostAt = null
    return true
  }

  toggleFlag(code: string) {
    const f = this.s.flags
    const i = f.indexOf(code)
    if (i >= 0) f.splice(i, 1)
    else f.push(code)
  }

  private land(code: string, kind: MoveKind): Move {
    const outcome = this.outcome(code)
    const move: Move = { to: code, kind, outcome, gamble: this.color(code) === 'purple' }
    this.s.moves.push(move)
    this.s.revealed[code] = outcome
    this.s.flags = this.s.flags.filter((c) => c !== code)
    if (outcome === 'red') {
      this.s.status = 'lost'
      this.s.lostAt = code
      return move
    }
    this.s.current = code
    if (!this.s.visited.includes(code)) this.s.visited.push(code)
    if (GOAL.includes(code)) this.s.status = 'won'
    return move
  }

  shareText(url: string): string {
    const sq = this.s.moves.map((m) => (m.outcome === 'red' ? '🟥' : m.kind === 'mail' ? '✉️' : m.gamble ? '🟪' : '🟦')).join('')
    const steps = this.s.moves.length
    const head = this.s.status === 'won'
      ? `Blue March (${DIFFICULTY[this.s.difficulty].label}): coast to coast in ${steps} moves 🌊`
      : `Blue March (${DIFFICULTY[this.s.difficulty].label}): lost in a landslide after ${steps} moves 🪨`
    return `${head}\n${sq}\n${url}`
  }
}
