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


function squareArea (ann) {
    let sq = dg.square(2).stroke(color("hl4"))
    let side1 = dg.annotation.length(dg.V2(-1,-1), dg.V2(1,-1), ann, 0.2, 0.2).stroke(color("pc1")).fontsize(20)
    let side2 = dg.annotation.length(dg.V2(1,-1), dg.V2(1,1), ann, 0.2, 0.2).stroke(color("pc1")).fontsize(20)
    let ques = dg.textvar("?").position(dg.V2(0,0)).fontsize(32)
    return [bounding(2.5,3.5), sq, side1, side2, ques]
}

export function squareArea1() {return squareArea('a')}

export function squareArea2() {return squareArea('b')}

export function squareArea3() {return squareArea('c')}


function converse(scale,a,b,c=null) {
    let offset = (Math.PI/4)-Math.acos(((a**2)+(b**2)-Math.sqrt(a**2+b**2)))/(2*a*b)
    let tri = dg.polygon([dg.V2(0,0), dg.V2(b,0), dg.V2(b-a*Math.sin(offset),a*Math.cos(offset))]).stroke(color("hl4")).position(dg.V2(-b/2,-a/2))
    let a1 = dg.textvar(''+a*scale).position(dg.V2(((2*b-a*Math.sin(offset)+0.2)/2)-b/2,0)).fontsize(20)
    let b1 = dg.textvar(''+b*scale).position(dg.V2(0,a*Math.cos(offset)*-0.7)).fontsize(20)
    if (c) {
        let c1 = dg.textvar(''+c*scale).position(dg.V2(((-a*Math.sin(offset))*0.25)-0.2,0)).fontsize(20)
        return [bounding(1.5,1.5), tri, a1, b1, c1]
    }
    return [bounding(1.5,1.5), tri, a1, b1]
}

export function converse1() {return converse(4,0.75,1,1.25)}

export function converse2() {return converse(5,1,1.2,1.4)}

export function converse3() {return converse(4,1.25,1)}
