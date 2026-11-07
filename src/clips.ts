export interface Clip { src: string; quote: string; credit: string }

/** One puppet clip per state. States without one get a quote card instead. */
export const CLIPS: Record<string, Clip> = {
  TX: { src: 'clips/tx.mp4', quote: '“So, I’m asking you to pretend that I’m on the ballot.”', credit: 'Audio: C-SPAN' },
}

// TODO: replace credit with the original broadcaster once the source of the clip is confirmed.
export const LOSS_CLIP: Clip = { src: 'clips/loss.mp4', quote: '“…we win in a landslide.”', credit: 'Audio: press remarks' }
