from typing import Callable, List, Tuple, cast

import cadquery as cq
from helical_thread import ThreadHelixes
from taperable_helix import HelixLocation

from utils import dbg, setCtx, show

setCtx(globals())


def _threads(external_threads: bool, ths: ThreadHelixes) -> cq.Solid:
    """
    Create a thread helix which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters when construction ThreadHelixes.

    :returns: Solid representing the threads
    """

    # dbg(f"_threads: external_threads={external_threads} ht={vars(ht)}")

    helixes: List[HelixLocation] = ths.int_helixes if (
        not external_threads
    ) else ths.ext_helixes

    # Create the helix functions
    helix_funcs: List[Callable[[float], Tuple[float, float, float]]] = [
        ths.ht.helix(hl) for hl in helixes
    ]

    # Create the wires
    wires: List[cq.Wire] = [
        (cast(cq.Wire, cq.Workplane("XY").parametricCurve(helix_funcs[i]).val(),))
        for i, hl in enumerate(helixes)
    ]

    lenWires = len(wires)
    assert (lenWires == 3) or (lenWires == 4)
    # dbg(f"threads: wires.len={len(wires)}")

    # Create the faces of the thread
    # faces: cq.Faces = []
    faces: List[cq.Face] = []
    faces.append(cq.Face.makeRuledSurface(wires[0], wires[1]))
    faces.append(cq.Face.makeRuledSurface(wires[1], wires[2]))
    if lenWires == 4:
        faces.append(cq.Face.makeRuledSurface(wires[2], wires[3]))
    faces.append(cq.Face.makeRuledSurface(wires[-1], wires[0]))

    # Add end caps if either taper_{in|out}_rpos is 0
    out_face_locs: List[cq.Vector] = []
    out_face_edges: List[cq.Edge] = []
    out_face_wire: cq.Wire
    out_face: cq.Face
    if ths.ht.taper_out_rpos == 0:
        out_face_locs = [cq.Vector(hf(ths.ht.first_t)) for hf in helix_funcs]
        # print(f"out_face_locs={out_face_locs}")
        out_face_edges = [
            cq.Edge.makeLine(
                out_face_locs[i],
                out_face_locs[(i + 1) if (i < len(out_face_locs) - 1) else 0],
            )
            for i in range(0, len(out_face_locs))
        ]
        # print(f"out_face_edges={out_face_edges}")
        out_face_wire = cq.Wire.assembleEdges(out_face_edges)
        # print(f"out_face_wire={out_face_wire}")
        out_face = cq.Face.makeFromWires(out_face_wire)
        # print(f"out_face={out_face}")
        faces.insert(0, out_face)

    in_face_locs: List[cq.Vector] = []
    in_face_edges: List[cq.Edge] = []
    in_face_wire: cq.Wire
    in_face: cq.Face
    if ths.ht.taper_in_rpos == 1:
        in_face_locs = [cq.Vector(hf(ths.ht.last_t)) for hf in helix_funcs]
        # print(f"in_face_locs={in_face_locs}")
        in_face_edges = [
            cq.Edge.makeLine(
                in_face_locs[i],
                in_face_locs[(i + 1) if (i < len(in_face_locs) - 1) else 0],
            )
            for i in range(0, len(in_face_locs))
        ]
        # print(f"in_face_edges={in_face_edges}")
        in_face_wire = cq.Wire.assembleEdges(in_face_edges)
        # print(f"in_face_wire={in_face_wire}")
        in_face = cq.Face.makeFromWires(in_face_wire)
        # print(f"in_face={in_face}")
        faces.insert(0, in_face)

    # print(f"faces={faces}")

    # Create the shell
    sh: cq.Shell = cq.Shell.makeShell(faces)

    # Create the solid
    rv: cq.Solid = cq.Solid.makeSolid(sh)

    # show(rv, "rv")

    # print("done")
    # print("")
    return rv


def int_threads(ths: ThreadHelixes) -> cq.Solid:
    """
    Create internal threads which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters when construction ThreadHelixes.

    :param ht: ThreadHelixes
    :returns: Solid representing the threads
    """
    return _threads(False, ths)


def ext_threads(ths: ThreadHelixes) -> cq.Solid:
    """
    Create external threads which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters when construction ThreadHelixes.

    :param ht: ThreadHelixes
    :returns: Solid representing the threads
    """
    return _threads(True, ths)
