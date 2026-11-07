// Checks that every difficulty has a Pacific-to-Atlantic route, with purple states counted as blue (best case) and red (worst case).
import { createServer } from 'vite'
const vite = await createServer({ server: { middlewareMode: true }, appType: 'custom', logLevel: 'error' })
const { stateColor } = await vite.ssrLoadModule('/src/game.ts')
const { ADJ } = await vite.ssrLoadModule('/src/map.ts')
const { START, GOAL } = await vite.ssrLoadModule('/src/states.ts')
const data = (await vite.ssrLoadModule('/src/data/officials.json')).default
await vite.close()

let bad = false
for (const d of ['easy', 'normal', 'hard']) {
  const col = Object.fromEntries(Object.entries(data.states).map(([k, s]) => [k, stateColor(s, d)]))
  const count = (c) => Object.values(col).filter((x) => x === c).length
  const route = (purpleOk) => {
    const ok = (c) => col[c] === 'blue' || (purpleOk && col[c] === 'purple')
    const prev = {}, q = START.filter(ok)
    q.forEach((c) => (prev[c] = null))
    while (q.length) {
      const c = q.shift()
      if (GOAL.includes(c)) { const p = []; for (let x = c; x; x = prev[x]) p.unshift(x); return p }
      for (const n of ADJ[c]) if (ok(n) && !(n in prev)) { prev[n] = c; q.push(n) }
    }
    return null
  }
  // BFS over (state, mail-in used); a mail-in jump lands two steps away, skipping the middle state unseen.
  const routeMail = (purpleOk) => {
    const ok = (c) => col[c] === 'blue' || (purpleOk && col[c] === 'purple')
    const key = (c, m) => c + m, prev = {}, q = []
    for (const c of START.filter(ok)) { prev[key(c, 0)] = null; q.push([c, 0]) }
    while (q.length) {
      const [c, m] = q.shift()
      if (GOAL.includes(c)) { const p = []; for (let k = key(c, m); k; k = prev[k]) p.unshift(k.slice(0, 2) + (k.endsWith('1') && !(prev[k] ?? '').endsWith('1') ? '(mail)' : '')); return p }
      const next = ADJ[c].filter(ok).map((n) => [n, m])
      if (!m) for (const n of ADJ[c]) for (const n2 of ADJ[n]) if (n2 !== c && !ADJ[c].includes(n2) && ok(n2)) next.push([n2, 1])
      for (const [n, mm] of next) if (!(key(n, mm) in prev)) { prev[key(n, mm)] = key(c, m); q.push([n, mm]) }
    }
    return null
  }
  const mailBest = routeMail(true), mailWorst = routeMail(false)
  const best = route(true), worst = route(false)
  console.log(`${d.padEnd(6)} blue ${count('blue')} red ${count('red')} purple ${count('purple')}`)
  console.log(`  red: ${Object.keys(col).filter((k) => col[k] === 'red').join(' ') || '-'}`)
  console.log(`  shortest route (purple as blue): ${best ? best.join(' > ') + ` (${best.length})` : 'NONE'}`)
  console.log(`  route without purple gambles:   ${worst ? worst.join(' > ') + ` (${worst.length})` : 'NONE'}`)
  console.log(`  with one mail-in ballot:         ${mailWorst ? mailWorst.join(' > ') : mailBest ? 'only with purple luck: ' + mailBest.join(' > ') : 'NONE'}`)
  if (!mailBest) bad = true
}
process.exit(bad ? 1 : 0)
