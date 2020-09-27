#!/usr/bin/env python3
from typing import cast

import cadquery as cq

from cq_threads import ext_threads
from helicalthreads import HelicalThreads
from utils import dbg, setCtx, show

setCtx(globals())


def cq_bolt(
    hts: HelicalThreads, head_size: float, head_height: float, wall_thickness: float
) -> cq.Workplane:
    bolt_threads: cq.Solid = ext_threads(hts)
    # show(bolt_threads, "bolt_threads-0")
    # bolt_threads_bb: cq.BoundBox = bolt_threads.BoundingBox()
    # dbg(f"bolthreads_bb={vars(bolt_threads_bb)}")

    bolt_core_radius: float = hts.ext_helix_radius
    # dbg(f"bolt_core_radius={bolt_core_radius} boltRadius={boltRadius:.3f})

    boltHead: cq.Workplane = (
        cq.Workplane("XY", origin=(0, 0, 0)).polygon(6, head_size).extrude(head_height)
    )
    # show(boltHead, "boltHead-0")

    bolt_core: cq.Workplane = (
        cq.Workplane("XY", origin=(0, 0, head_height))
        .circle(bolt_core_radius)
        .circle(bolt_core_radius - wall_thickness)
        .extrude(hts.htd.height)
    )
    # show(bolt_core, "bolt_core-0")

    bolt: cq.Workplane = boltHead.union(bolt_core).union(
        # TODO: What is the "right" way to allow a moved Shape to something
        # acceptable to .union? I'm using cast to convert the Shape returned
        # by .move back to Solid to satisfy mypy.
        cast(cq.Solid, bolt_threads.move(cq.Location(cq.Vector(0, 0, head_height))))
    )
    # show(bolt, "bolt-0")

    return bolt
