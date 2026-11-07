import { geoPath } from 'd3-geo'
import { feature, neighbors } from 'topojson-client'
import type { Topology, GeometryCollection } from 'topojson-specification'
import us from 'us-atlas/states-albers-10m.json'
import { STATES } from './states'

export interface MapState { code: string; name: string; d: string; cx: number; cy: number; area: number }

const topo = us as unknown as Topology<{ states: GeometryCollection }>
const geoms = topo.objects.states.geometries
const nb = neighbors(geoms as never)
const path = geoPath()

export const MAP_STATES: MapState[] = []
export const ADJ: Record<string, string[]> = {}

geoms.forEach((g, i) => {
  const st = STATES[String(g.id)]
  if (!st) return // Alaska, Hawaii, DC
  const f = feature(topo, g as never) as never
  const [cx, cy] = path.centroid(f)
  MAP_STATES.push({ code: st.code, name: st.name, d: path(f) ?? '', cx, cy, area: path.area(f) })
  ADJ[st.code] = nb[i].map((j) => STATES[String(geoms[j].id)]?.code).filter((c): c is string => !!c).sort()
})

/** Label nudges for states whose centroid sits awkwardly. */
export const LABEL_NUDGE: Record<string, [number, number]> = {
  FL: [18, 10], LA: [-12, 0], MI: [14, 26], KY: [6, 4], VA: [8, 2], MD: [-4, -2], NJ: [6, 2], DE: [8, 4],
  CT: [2, 2], RI: [6, 4], MA: [0, -2], NH: [0, 6], VT: [-2, -6], WV: [-2, 4], ID: [0, 20], CA: [-12, 0],
}
