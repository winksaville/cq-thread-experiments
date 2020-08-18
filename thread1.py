# from: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ
from math import cos, pi, sin

import cadquery as cq

from wing_utils import show


def helix(r0, r_eps, p, h, depth=0, frac=1e-1):
    def func(t):

        if t > frac and t < 1 - frac:
            z = h * t + depth
            r = r0 + r_eps
        elif t <= frac:
            z = h * t + depth * sin(pi / 2 * t / frac)
            r = r0 + r_eps * sin(pi / 2 * t / frac)
        else:
            z = h * t - depth * sin(2 * pi - pi / 2 * (1 - t) / frac)
            r = r0 - r_eps * sin(2 * pi - pi / 2 * (1 - t) / frac)

        x = r * sin(-2 * pi / (p / h) * t)
        y = r * cos(2 * pi / (p / h) * t)

        return x, y, z

    return func


def thread(radius, pitch, height, depth, radius_eps, aspect=10):

    e1_bottom = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, 0, pitch, height, -depth))
        .val()
    )
    e1_top = (
        cq.Workplane("XY").parametricCurve(helix(radius, 0, pitch, height, depth)).val()
    )

    e2_bottom = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, radius_eps, pitch, height, -depth / aspect))
        .val()
    )
    e2_top = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, radius_eps, pitch, height, depth / aspect))
        .val()
    )

    f1 = cq.Face.makeRuledSurface(e1_bottom, e1_top)
    f2 = cq.Face.makeRuledSurface(e2_bottom, e2_top)
    f3 = cq.Face.makeRuledSurface(e1_bottom, e2_bottom)
    f4 = cq.Face.makeRuledSurface(e1_top, e2_top)

    sh = cq.Shell.makeShell([f1, f2, f3, f4])
    rv = cq.Solid.makeSolid(sh)

    return rv


radius = 4
pitch = 2
height = 4
depth = pitch / 4
radius_eps = 0.5
eps = 1e-3

core = (
    cq.Workplane("XY", origin=(0, 0, -depth))
    .circle(radius - 1 - eps)
    .circle(radius + eps)
    .extrude(height + 1.75 * depth)
)
th1 = thread(radius, pitch, height, depth, radius_eps)
th2 = thread(radius - 1, pitch, height, depth, -radius_eps)

res = core.union(cq.Compound.makeCompound([th1, th2]))

show(res)

tolerance = 1e-3
fname = f"thread1-radius_{radius}-pitch_{pitch}-depth_{depth}-height_{height}-tol_{tolerance}.stl"
cq.exporters.export(res, fname, tolerance=tolerance)
