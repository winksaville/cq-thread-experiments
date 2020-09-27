#!/usr/bin/env python3
import cadquery as cq

from cq_threads import int_threads
from helicalthreads import HelicalThreads
from utils import dbg, setCtx, show

setCtx(globals())


def cq_nut(hts: HelicalThreads, head_size: float) -> cq.Workplane:
    nut_core: cq.Workplane = (
        cq.Workplane("XY", origin=(0, 0, 0))
        .circle(hts.int_helix_radius)
        .polygon(6, head_size)
        .extrude(hts.htd.height)
    )
    # show(nut_core, "nut_core-0")

    nut_threads: cq.Solid = int_threads(hts)
    # nut_threads_bb: cq.BoundBox = nut_threads.BoundingBox()
    # dbg(f"nut_threads_bb={vars(nut_threads_bb)}")
    # show(nut_threads, "nut_threads-0")

    nut: cq.Workplane = nut_core.union(nut_threads)
    # show(nut, "nut-0")
    return nut
