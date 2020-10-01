#!/usr/bin/env python3
import cadquery as cq
from helical_thread import ThreadHelixes

from cq_threads import int_threads
from utils import dbg, setCtx, show

setCtx(globals())


def cq_nut(ths: ThreadHelixes, head_size: float) -> cq.Workplane:
    nut_core: cq.Workplane = (
        cq.Workplane("XY", origin=(0, 0, 0))
        .circle(ths.int_helix_radius)
        .polygon(6, head_size)
        .extrude(ths.ht.height)
    )
    # show(nut_core, "nut_core-0")

    nut_threads: cq.Solid = int_threads(ths)
    # nut_threads_bb: cq.BoundBox = nut_threads.BoundingBox()
    # dbg(f"nut_threads_bb={vars(nut_threads_bb)}")
    # show(nut_threads, "nut_threads-0")

    nut: cq.Workplane = nut_core.union(nut_threads)
    # show(nut, "nut-0")
    return nut
