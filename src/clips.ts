export interface Clip { src: string; quote: string; credit: string }

/** One puppet clip per state. States without one get a quote card instead. */
export const CLIPS: Record<string, Clip> = {
  TX: { src: 'clips/tx.mp4', quote: '“So, I’m asking you to pretend that I’m on the ballot.”', credit: 'Audio: C-SPAN' },
  MI: { src: 'clips/mi.mp4', quote: '“J.D. … Habibi. There is this delicious irony in the fact that you’re constitutionally obligated to swear me in in January.”', credit: 'Audio: C-SPAN (Abdul El-Sayed, election night)' },
  OH: { src: 'clips/oh.mp4', quote: '“Then I looked at his hands. Look at his hands. He’s got these, like… claws.”', credit: 'Audio: C-SPAN (Trump on Sen. Jon Husted, Youngstown rally)' },
  KY: { src: 'clips/ky.mp4', quote: '“It’s garbage day in Kentucky… So I know a little bit about garbage.”', credit: 'Audio: Nate Morris for Senate launch ad, 2025' },
  CA: { src: 'clips/ca.mp4', quote: '“Close your eyes, and I’ll do all the work.”', credit: 'Audio: “Just Try It, California” (Steve Hilton for Governor ad)' },
}

// TODO: replace credit with the original broadcaster once the source of the clip is confirmed.
export const LOSS_CLIP: Clip = { src: 'clips/loss.mp4', quote: '“…we win in a landslide.”', credit: 'Audio: press remarks' }
