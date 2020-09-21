from dataclasses import dataclass
from math import atan, cos, degrees, pi, radians, sin, tan
from typing import List, Tuple, cast

import cadquery as cq
from helicalthreads import HelicalThreads, HelixLocation
from taperable_helix import helix

from wing_utils import perpendicular_distance_pt_to_line_2d, setCtx, show

setCtx(globals())


def _threads(external_threads: bool, ht: HelicalThreads) -> cq.Solid:
    """
    Create a thread helix which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters to ThreadDimensions.

    :returns: Solid representing the threads and float dept
    """

    # print(f"_threads: external_threads={external_threads} ht={vars(ht)}")

    helix_locations: List[HelixLocation] = ht.int_helixes if (
        not external_threads
    ) else ht.ext_helixes

    wires: cq.Wire = [
        (
            cq.Workplane("XY")
            .parametricCurve(
                helix(
                    radius=hl.radius,
                    pitch=ht.pitch,
                    height=ht.height,
                    taper_rpos=ht.taper_rpos,
                    inset_offset=ht.inset,
                    horz_offset=hl.horz_offset,
                    vert_offset=hl.vert_offset,
                )
            )
            .val()
        )
        for hl in helix_locations
    ]

    lenWires = len(wires)
    assert (lenWires == 3) or (lenWires == 4)
    # print(f"threads: wires.len={len(wires)}")

    # Create the faces of the thread
    faces: cq.Faces = []
    faces.append(cq.Face.makeRuledSurface(wires[0], wires[1]))
    faces.append(cq.Face.makeRuledSurface(wires[1], wires[2]))
    if lenWires == 4:
        faces.append(cq.Face.makeRuledSurface(wires[2], wires[3]))
    faces.append(cq.Face.makeRuledSurface(wires[-1], wires[0]))

    # TODO: if taper_rpos == 0 we need to create end faces

    # Create the solid
    sh: cq.Shell = cq.Shell.makeShell(faces)
    rv: cq.Solid = cq.Solid.makeSolid(sh)

    # show(rv, "rv")

    return rv


def int_threads(ht: HelicalThreads) -> cq.Solid:
    """
    Create internal threads which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters to HelicalThreads.

    :param ht: HelicalThreads
    :returns: Solid representing the threads and float dept
    """
    return _threads(False, ht)


def ext_threads(ht: HelicalThreads) -> cq.Solid:
    """
    Create external threads which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters to HelicalThreads.

    :param ht: HelicalThreads
    :returns: Solid representing the threads and float dept
    """
    return _threads(True, ht)

