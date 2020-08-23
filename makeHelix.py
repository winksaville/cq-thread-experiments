# From: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/crpn7H05CQAJ
# and: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/Z_iW1cc8CQAJ

import cadquery as cq

pitch = 6
depth = 3
radius = 20.0
height = 20.0

profile_points = (
    (radius + depth, 0.1),
    (radius + 0.1, 0.1),
    (radius - depth, pitch / 2),
    (radius + 0.1, pitch + 0.1),
    (radius + depth, pitch + 0.1),
)

wire = cq.Wire.makeHelix(pitch, height, radius)
cut_path = cq.Workplane("XY").newObject([wire]).translate((0, 0, pitch))

profile = (
    cq.Workplane("XZ").polyline(profile_points).close().sweep(cut_path, isFrenet=True)
)

body = cq.Workplane("XY").circle(radius).extrude(height + pitch)

result = body.cut(profile)
