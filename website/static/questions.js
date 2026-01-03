import * as dg from 'https://cdn.jsdelivr.net/npm/diagramatics@1.5/dist/diagramatics.min.js'
let color = (colorVar) => window.getComputedStyle(document.documentElement).getPropertyValue('--'+colorVar)
let bounding = (x,y) => dg.rectangle(x,y).strokewidth(1)

export function hypotenuse1() {
    let tri = dg.polygon([dg.V2(0,0), dg.V2(0,1.3), dg.V2(2,0)]).stroke(color("hl4"))
    let ang = dg.square(0.2).position(dg.V2(0.1,0.1)).stroke(color("hl3"))
    let x = dg.textvar("x").position(dg.V2(-1.2,0.6))
    let y = dg.textvar("y").position(dg.V2(-0.2,0.9))
    let z = dg.textvar("z").position(dg.V2(-0.5,-0.4))
    let tri2 = tri.combine(ang).rotate(2)
    return [tri2, x, y, z]
}