import './style.css'
import officialsJson from './data/officials.json'
import { ADJ, LABEL_NUDGE, MAP_STATES } from './map'
import { DIFFICULTY, Game, democrats, type Difficulty, type Officials } from './game'
import { GOAL, NAME, START } from './states'
import { CLIPS, LOSS_CLIP, type Clip } from './clips'

const DATA = officialsJson as unknown as Officials
const SHARE_URL = location.origin + location.pathname
type Mode = 'move' | 'flag' | 'peek' | 'mail'

// ---------------------------------------------------------------- storage (best effort)
const store = {
  get<T>(k: string, d: T): T { try { const v = localStorage.getItem(k); return v ? (JSON.parse(v) as T) : d } catch { return d } },
  set(k: string, v: unknown) { try { localStorage.setItem(k, JSON.stringify(v)) } catch { /* private mode */ } },
}
let difficulty = store.get<Difficulty>('bm.difficulty', 'normal')
const unlocked = new Set(store.get<string[]>('bm.unlocked', []))
let game = new Game(DATA, ADJ, difficulty)
let mode: Mode = 'move'

// ---------------------------------------------------------------- dom
const $ = <T extends HTMLElement>(sel: string) => document.querySelector(sel) as T
const esc = (s: string) => s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`)

document.querySelector('#app')!.innerHTML = `
  <header class="top">
    <div class="brand"><h1>BLUE MARCH</h1><p>Pacific to Atlantic. Blue states only.</p></div>
    <div class="controls">
      <label class="diff">Rules
        <select id="difficulty">${(Object.keys(DIFFICULTY) as Difficulty[]).map((d) => `<option value="${d}">${DIFFICULTY[d].label}</option>`).join('')}</select>
      </label>
      <button id="new" class="ghost">New game</button>
      <button id="help" class="ghost" aria-label="How to play">?</button>
    </div>
  </header>
  <main class="board">
    <svg id="map" viewBox="0 0 975 610" role="img" aria-label="Map of the contiguous United States"></svg>
    <section class="panel">
      <div id="status" class="status"></div>
      <div id="powerups" class="powerups"></div>
      <div id="options" class="options"></div>
      <div class="meta"><span id="unlocked"></span><span id="moves"></span></div>
    </section>
  </main>
  <footer class="foot">
    Satire. Not affiliated with any campaign or party. Election data as of ${esc(DATA.asOf)}; races not yet called are purple.
  </footer>
  <div id="toast" class="toast" role="status" aria-live="polite"></div>
  <dialog id="modal"><div id="modal-body"></div></dialog>
`

const svg = $<HTMLElement>('#map') as unknown as SVGSVGElement
const NS = 'http://www.w3.org/2000/svg'
const paths: Record<string, SVGPathElement> = {}
const marks: Record<string, SVGTextElement> = {}
const gStates = document.createElementNS(NS, 'g')
const gLabels = document.createElementNS(NS, 'g')
gLabels.setAttribute('class', 'labels')
svg.append(gStates, gLabels)
for (const s of MAP_STATES) {
  const p = document.createElementNS(NS, 'path')
  p.setAttribute('d', s.d)
  p.dataset.code = s.code
  p.innerHTML = `<title>${s.name}</title>`
  p.addEventListener('click', () => onState(s.code))
  p.addEventListener('contextmenu', (e) => { e.preventDefault(); if (game.s.status === 'playing') { game.toggleFlag(s.code); render() } })
  gStates.append(p)
  paths[s.code] = p
  const [dx, dy] = LABEL_NUDGE[s.code] ?? [0, 0]
  const t = document.createElementNS(NS, 'text')
  t.setAttribute('x', String(s.cx + dx))
  t.setAttribute('y', String(s.cy + dy))
  t.setAttribute('class', s.area < 1500 ? 'small' : '')
  t.textContent = s.code
  gLabels.append(t)
  const m = document.createElementNS(NS, 'text')
  m.setAttribute('x', String(s.cx + dx))
  m.setAttribute('y', String(s.cy + dy - 14))
  m.setAttribute('class', 'mark')
  gLabels.append(m)
  marks[s.code] = m
}

// ---------------------------------------------------------------- actions
function onState(code: string) {
  const s = game.s
  if (s.status === 'start') return void (game.startOptions().includes(code) && arrive(game.start(code)))
  if (s.status !== 'playing') return
  if (mode === 'flag') { game.toggleFlag(code); return render() }
  if (mode === 'peek') {
    const o = game.peek(code)
    if (!o) return toast('Exit poll works on a neighbouring state you have not seen yet.')
    mode = 'move'
    toast(`Exit poll: ${NAME[code]} is ${o === 'blue' ? 'BLUE' : 'RED'}.`)
    return render()
  }
  if (mode === 'mail') {
    const m = game.mail(code)
    if (!m) return toast('Mail-in ballot lands two states away, skipping the one in between.')
    mode = 'move'
    return arrive(m)
  }
  if (!game.moveOptions().includes(code)) return toast(`${NAME[code]} does not border ${NAME[s.current!]}.`)
  if (s.revealed[code] === 'red' && !confirm(`${NAME[code]} is red. March in anyway?`)) return
  arrive(game.step(code))
}

function arrive(m: ReturnType<Game['step']>) {
  if (!m) return
  render()
  if (m.outcome === 'red') return showLoss(m.to)
  if (m.kind === 'back') return
  const isNew = !unlocked.has(m.to)
  unlocked.add(m.to)
  store.set('bm.unlocked', [...unlocked])
  showState(m.to, isNew, m.gamble)
}

function newGame(d = difficulty) {
  difficulty = d
  store.set('bm.difficulty', d)
  game = new Game(DATA, ADJ, d)
  mode = 'move'
  closeModal()
  render()
}

// ---------------------------------------------------------------- modal
const modal = $<HTMLDialogElement>('#modal')
const body = $<HTMLDivElement>('#modal-body')
function openModal(html: string) {
  body.innerHTML = html
  if (!modal.open) modal.showModal()
  body.querySelector<HTMLVideoElement>('video')?.play().catch(() => { /* autoplay blocked: controls stay visible */ })
}
function closeModal() {
  body.querySelector('video')?.pause()
  if (modal.open) modal.close()
}
modal.addEventListener('click', (e) => { if (e.target === modal && game.s.status === 'playing') closeModal() })

const clipHtml = (c: Clip) => `
  <video src="${c.src}" playsinline controls preload="auto"></video>
  <p class="quote">${esc(c.quote)}</p><p class="credit">${esc(c.credit)}</p>`

function showState(code: string, isNew: boolean, gamble: boolean) {
  const info = game.info(code)
  const clip = CLIPS[code]
  const won = game.s.status === 'won'
  openModal(`
    <h2>${esc(NAME[code])} <span class="tag blue">${gamble ? 'Called for the blues!' : 'Blue'}</span></h2>
    <p class="who">${democrats(info).map(esc).join(' · ') || 'Democrats on the ballot'}</p>
    ${clip ? clipHtml(clip) : `<div class="card-soon"><strong>${esc(NAME[code])}</strong><span>Puppet clip coming soon</span></div>`}
    ${isNew ? `<p class="unlock">Unlocked ${unlocked.size} / 48 states</p>` : ''}
    ${won ? winHtml() : '<div class="actions"><button class="primary" data-act="close">Keep marching</button></div>'}
  `)
  wire()
}

function winHtml() {
  return `<div class="result win"><h3>You reached the Atlantic!</h3>
    <p>Coast to coast in ${game.s.moves.length} moves on ${DIFFICULTY[game.s.difficulty].label}.</p>
    <div class="actions"><button class="primary" data-act="share">Share result</button><button data-act="again">Play again</button></div></div>`
}

function showLoss(code: string) {
  const canRecount = game.s.powerups.recount > 0
  openModal(`
    <h2>${esc(NAME[code])} <span class="tag red">Red</span></h2>
    <p class="who">No Democrats in the top jobs. You lost by a landslide.</p>
    ${clipHtml(LOSS_CLIP)}
    <div class="actions">
      ${canRecount ? '<button class="primary" data-act="recount">Demand a recount</button>' : ''}
      <button ${canRecount ? '' : 'class="primary"'} data-act="again">Try again</button>
      <button data-act="share">Share</button>
    </div>`)
  wire()
}

function showHelp() {
  openModal(`
    <h2>How to play</h2>
    <ol class="rules">
      <li>Start in a Pacific state and march to any Atlantic state, one neighbouring state at a time.</li>
      <li>You may only enter states with a Democrat in a top job. <em>${esc(DIFFICULTY[difficulty].rule)}</em></li>
      <li>The map is hidden. Step into a state with no Democrats and you lose.</li>
      <li>Purple states are too close to call. Entering one is a coin flip.</li>
      <li>Every blue state unlocks a clip. Collect all 48.</li>
    </ol>
    <h3>Help, once per game</h3>
    <ul class="rules">
      <li><b>Exit poll</b>: see the colour of one neighbouring state.</li>
      <li><b>Mail-in ballot</b>: jump two states, skipping the one between.</li>
      <li><b>Demand a recount</b>: undo the move that lost you the game.</li>
    </ul>
    <p class="small">Right-click (or use Flag mode) to mark states you think are red.</p>
    <div class="actions"><button class="primary" data-act="close">March!</button></div>`)
  wire()
  store.set('bm.seenHelp', true)
}

function wire() {
  body.querySelectorAll<HTMLButtonElement>('[data-act]').forEach((b) => b.addEventListener('click', () => {
    const a = b.dataset.act
    if (a === 'close') closeModal()
    if (a === 'again') newGame()
    if (a === 'share') share()
    if (a === 'recount' && game.recount()) { closeModal(); toast('Recount granted. Pick another route.'); render() }
  }))
}

async function share() {
  const text = game.shareText(SHARE_URL)
  try {
    if (navigator.share) await navigator.share({ text })
    else { await navigator.clipboard.writeText(text); toast('Result copied to clipboard.') }
  } catch { /* share sheet dismissed */ }
}

let toastTimer = 0
function toast(msg: string) {
  const t = $<HTMLDivElement>('#toast')
  t.textContent = msg
  t.classList.add('show')
  clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => t.classList.remove('show'), 2600)
}

// ---------------------------------------------------------------- render
function render() {
  const s = game.s
  const opts = s.status === 'start' ? game.startOptions()
    : mode === 'mail' ? game.mailOptions() : mode === 'peek' ? game.peekOptions() : game.moveOptions()
  for (const { code } of MAP_STATES) {
    const p = paths[code]
    const rev = s.revealed[code]
    const cls = ['st']
    if (rev) cls.push(rev === 'red' ? 'red' : 'blue')
    else if (game.color(code) === 'purple') cls.push('purple')
    else cls.push('hidden')
    if (s.peeked.includes(code) && !s.visited.includes(code)) cls.push('peeked')
    if (code === s.current) cls.push('current')
    if (code === s.lostAt) cls.push('lost')
    if (GOAL.includes(code) && !rev) cls.push('goal')
    if (s.status !== 'won' && s.status !== 'lost' && opts.includes(code)) cls.push('option', `opt-${s.status === 'start' ? 'start' : mode}`)
    p.setAttribute('class', cls.join(' '))
    marks[code].textContent = s.flags.includes(code) ? '🧢' : ''
  }

  const statusEl = $('#status')
  if (s.status === 'start') statusEl.innerHTML = `<h2>Pick your start</h2><p>Choose a Pacific state: ${START.map((c) => NAME[c]).join(', ')}.</p>`
  else if (s.status === 'playing') {
    const tip = mode === 'peek' ? 'Exit poll: tap a neighbouring state to see its colour.'
      : mode === 'mail' ? 'Mail-in ballot: tap a state two steps away.'
      : mode === 'flag' ? 'Flag mode: tap states you think are red.' : 'Where next?'
    statusEl.innerHTML = `<h2>${esc(NAME[s.current!])}</h2><p>${tip}</p>`
  } else if (s.status === 'won') statusEl.innerHTML = `<h2>You made it to ${esc(NAME[s.current!])}!</h2><p>Coast to coast in ${s.moves.length} moves.</p>`
  else statusEl.innerHTML = `<h2>Lost in ${esc(NAME[s.lostAt!])}</h2><p>Won by a landslide (not by you).</p>`

  const pu = s.powerups
  const playing = s.status === 'playing'
  $('#powerups').innerHTML = `
    <button data-mode="peek" ${!playing || pu.exitPoll < 1 ? 'disabled' : ''} class="${mode === 'peek' ? 'on' : ''}">Exit poll <b>${pu.exitPoll}</b></button>
    <button data-mode="mail" ${!playing || pu.mailIn < 1 ? 'disabled' : ''} class="${mode === 'mail' ? 'on' : ''}">Mail-in ballot <b>${pu.mailIn}</b></button>
    <button data-mode="flag" ${!playing ? 'disabled' : ''} class="${mode === 'flag' ? 'on' : ''}">Flag 🧢</button>
    <span class="recount" title="Used automatically from the game-over screen">Recount <b>${pu.recount}</b></span>`
  $('#powerups').querySelectorAll<HTMLButtonElement>('[data-mode]').forEach((b) => b.addEventListener('click', () => {
    const m = b.dataset.mode as Mode
    mode = mode === m ? 'move' : m
    render()
  }))

  const list = s.status === 'won' || s.status === 'lost' ? [] : opts
  $('#options').innerHTML = list.length
    ? `<p class="label">${s.status === 'start' ? 'Start in' : mode === 'move' ? 'March to' : mode === 'flag' ? 'Flag' : 'Target'}</p>` +
      list.map((c) => {
        const r = s.revealed[c]
        const hint = r === 'red' ? ' ⚠︎ red' : s.visited.includes(c) ? ' ✓' : game.color(c) === 'purple' && !r ? ' ?' : ''
        return `<button class="opt ${r ?? ''} ${s.flags.includes(c) ? 'flagged' : ''}" data-code="${c}">${NAME[c]}${hint}</button>`
      }).join('')
    : s.status === 'won' || s.status === 'lost' ? '<div class="actions"><button class="primary" data-again>New game</button><button data-share>Share</button></div>' : ''
  $('#options').querySelectorAll<HTMLButtonElement>('[data-code]').forEach((b) => b.addEventListener('click', () => onState(b.dataset.code!)))
  $('#options').querySelector('[data-again]')?.addEventListener('click', () => newGame())
  $('#options').querySelector('[data-share]')?.addEventListener('click', share)

  $('#unlocked').textContent = `Unlocked ${unlocked.size} / 48`
  $('#moves').textContent = s.moves.length ? `Moves ${s.moves.length}` : ''
}

// ---------------------------------------------------------------- boot
const sel = $<HTMLSelectElement>('#difficulty')
sel.value = difficulty
sel.addEventListener('change', () => newGame(sel.value as Difficulty))
$('#new').addEventListener('click', () => newGame())
$('#help').addEventListener('click', showHelp)
render()
if (!store.get('bm.seenHelp', false)) showHelp()
