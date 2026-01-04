import * as dg from 'https://cdn.jsdelivr.net/npm/diagramatics@1.5/dist/diagramatics.min.js'
let color = (colorVar) => window.getComputedStyle(document.documentElement).getPropertyValue('--'+colorVar)
let bounding = (x,y) => dg.rectangle(x,y).strokewidth(0)

function hypotenuse (sides, posX, posY, posZ, rot, bound=null) {
    let tri = dg.polygon([dg.V2(0,0), dg.V2(0,sides[0]), dg.V2(sides[1],0)]).stroke(color("hl4"))
    let ang = dg.square(0.2).position(dg.V2(0.1,0.1)).stroke(color("hl3"))
    let x = dg.textvar("x").position(dg.V2(posX[0],posX[1])).fontsize(20)
    let y = dg.textvar("y").position(dg.V2(posY[0],posY[1])).fontsize(20)
    let z = dg.textvar("z").position(dg.V2(posZ[0],posZ[1])).fontsize(20)
    let tri2 = tri.combine(ang).rotate(rot)
    if (bound) {return [bounding(bound[0],bound[1]), tri2, x, y, z]}
    return [tri2, x, y, z]
}

export function hypotenuse1() {return hypotenuse([1.3,2], [-1.2,0.6], [-0.2,0.9], [-0.5,-0.4], 2)}

export function hypotenuse2() {return hypotenuse([1.5,1.5], [-0.6,-0.4], [0.6,-0.4], [0,-1.2], Math.PI*-0.75, [2.5, 2.5])}

export function hypotenuse3() {return hypotenuse([1,2], [0.4,0.35], [1,-0.5], [0.3,-0.9], Math.PI*-0.35)}