import sys
from functools import reduce
from math import radians, sqrt
from typing import List, Sequence, Tuple, Union, cast

# import cadquery as cq
import cadquery as cq

X: int = 0
Y: int = 1
Z: int = 2

_ctx = None


def setCtx(ctx) -> None:
    """
    Call setCtx() with globals() prior to using
    show or dbg methods when using cq-editor.
    """
    global _ctx
    _ctx = ctx


if "cq_editor" in sys.modules:
    # from __main__ import self as _cq_editor
    from logbook import info as _cq_log

    def show(o: object, name=None):
        if _ctx is None:
            raise ValueError("utils.setCtx was not called")
        if _ctx["show_object"] is None:
            raise ValueError("_ctx['show_object'] is not available")
        _ctx["show_object"](o, name=name)
        # _cq_editor.components["object_tree"].addObject(o) # Does not work

    def dbg(*args):
        _cq_log(*args)


else:

    def show(o: object, name=None):
        if name is None:
            name = str(id(o))
        if o is None:
            dbg(f"{name}: o=None")
        elif isinstance(o, cq.Workplane):
            wp: cq.Workplane = o
            if isinstance(wp.val(), cq.Shape):
                dbg(f"{name}: valid={cast(cq.Shape, wp.val()).isValid()} {vars(o)}")
            else:
                dbg(f"{name}: vars(o))")
        else:
            dbg(f"{name}: {o}")

    def dbg(*args):
        print(*args)


def xDist_2d(linePt1: Tuple[float, float], linePt2: Tuple[float, float]) -> float:
    xDist = linePt1[X] - linePt2[X]
    # print(f"xDist_2d:+- xDist={xDist}")
    return xDist


def yDist_2d(linePt1: Tuple[float, float], linePt2: Tuple[float, float]) -> float:
    yDist = linePt1[Y] - linePt2[Y]
    # print(f"yDist_2d:+- yDist={yDist}")
    return yDist


def sumPts(pt1: Tuple[float, float], pt2: Tuple[float, float]) -> Tuple[float, float]:
    """return pt1 + pt2"""
    return (pt1[X] + pt2[X], pt1[Y] + pt2[Y])


def diffPts(pt1: Tuple[float, float], pt2: Tuple[float, float]) -> Tuple[float, float]:
    """return pt1 - pt2"""
    return (pt1[X] - pt2[X], pt1[Y] - pt2[Y])


def prodPts(pt1: Tuple[float, float], pt2: Tuple[float, float]) -> Tuple[float, float]:
    """return pt1 * pt2"""
    return (pt1[X] * pt2[X], pt1[Y] * pt2[Y])


def crossProdPts(pt1: Tuple[float, float], pt2: Tuple[float, float]) -> float:
    """return (pt1[X] * pt2[Y]) - (pt1[Y] * pt2[X])"""
    prod = prodPts(pt1, (pt2[Y], pt2[X]))
    return prod[X] - prod[Y]


def translate_2d(
    lst: Sequence[Tuple[float, float]], t: Tuple[float, float]
) -> List[Tuple[float, float]]:
    """Translate a 2D obect to a different location on a plane"""
    return [sumPts(loc, t) for loc in lst]


def slope_2d(linePt1: Tuple[float, float], linePt2: Tuple[float, float]) -> float:
    xDist, yDist = diffPts(linePt1, linePt2)
    if xDist == 0:
        # What about nan's and -0 this is why there is no math.sign
        # See: https://stackoverflow.com/a/16726462
        slope = (1 if yDist >= 0.0 else -1) * radians(90)
    else:
        slope = yDist / xDist

    return slope


def slope_yIntercept_2d(
    linePt1: Tuple[float, float], linePt2: Tuple[float, float],
) -> Tuple[float, float]:
    """
    Return the two tuple (yIntercept, Slope) of line
    """

    # Line formula: y = (slope * x) + b
    # b = y - (slope * x)
    # yIntercept = b when x == 0
    slope = slope_2d(linePt1, linePt2)
    yIntercept = linePt1[Y] - (slope * linePt2[X])

    return (slope, yIntercept)


def lineToPtDirection_2d(
    linePt1: Tuple[float, float], linePt2: Tuple[float, float], pt: Tuple[float, float],
) -> float:
    """
    Return value is > 0 if pt is above the line, < 0 if below and 0 if on the line

    Use cross product to determine direction of rotation from the line to the point.

    A positive cross product means a counter clockwise rotation of the line
    is needed to intersect the point.

    A negative cross product means a counter clockwise rotation of the line
    is needed to intersect the point.

    A 0 means the point is on the line an no rotation is needed.

    See: https://www.geeksforgeeks.org/direction-point-line-segment
    """
    # translate linePt2 and pt1, pt2 to be relative to linePt1 at origin
    # i.e. substract linePt1 from the other points
    linePt2_o = diffPts(linePt2, linePt1)
    pt_o = diffPts(pt, linePt1)

    # Calculate crossProd of linePt2_o to pt1_o and pt2_o
    # If the a cross procduct is 0 then its on the line
    # if the signs are the same there both on the same side of the line
    return crossProdPts(linePt2_o, pt_o)


def intersectionLines_2d(
    line1Pt1: Tuple[float, float],
    line1Pt2: Tuple[float, float],
    line2Pt1: Tuple[float, float],
    line2Pt2: Tuple[float, float],
) -> Tuple[float, float]:
    """
    from: https://www.geeksforgeeks.org/program-for-point-of-intersection-of-two-lines/
    """
    # print(
    #     f"intersectionLines_2d:+ line1Pt1={line1Pt1} line1Pt2={line1Pt2} line2Pt1={line2Pt1} line2Pt2={line2Pt2}"
    # )
    # Line1 (a1 * x) + (b1 * y) = c1
    a1: float = yDist_2d(line1Pt2, line1Pt1)
    b1: float = xDist_2d(line1Pt1, line1Pt2)
    c1: float = (a1 * line1Pt1[X]) + (b1 * line1Pt1[Y])
    # print(f"intersectionLines_2d: a1={a1} b1={b1} c1={c1}")

    # Line2 (a2 * x) + (b2 * y) = c2
    a2: float = yDist_2d(line2Pt2, line2Pt1)
    b2: float = xDist_2d(line2Pt1, line2Pt2)
    c2: float = (a2 * line2Pt1[X]) + (b2 * line2Pt1[Y])
    # print(f"intersectionLines_2d: a2={a2} b2={b2} c2={c2}")

    determinant: float = (a1 * b2) - (a2 * b1)
    # print(f"intersectionLines_2d: determinant={determinant}")

    x: float
    y: float
    if determinant == 0:
        x = sys.float_info.max
        y = sys.float_info.max
    else:
        x = ((b2 * c1) - (b1 * c2)) / determinant
        y = ((a1 * c2) - (a2 * c1)) / determinant
    newPt: Tuple[float, float] = (x, y)

    # print(
    #     f"intersectionLines_2d:- newPt={newPt} line1Pt1={line1Pt1} line1Pt2={line1Pt2} line2Pt1={line2Pt1} line2Pt2={line2Pt2}"
    # )
    return newPt


def interpolatePt_2d(
    lst: Sequence[Tuple[float, float]],
    linePt1: Tuple[float, float],
    linePt2: Tuple[float, float],
    curIdx: int,
    curPt: Tuple[float, float],
    prvPt: Tuple[float, float],
) -> Tuple[float, float]:
    """
    Interpolate a point between curPt and prvPt that is
    on line defined by linePt1 and linePt2. An assumption is
    that a line drawn from curPt to prvPt crosses a line
    defined by linePt1 and linePt2.
    """
    # Linear interpolation for now, which will be the intersection
    # between the two lines
    # print(f"interpolatePt_2d:+ curPt={curPt} prvPt={prvPt}")

    newPt: Tuple[float, float] = intersectionLines_2d(linePt1, linePt2, curPt, prvPt)

    # print(f"interpolatePt_2d:- curPt={curPt} prvPt={prvPt} newPt={newPt}")
    return newPt


def split_2d(
    linePt1: Tuple[float, float],
    linePt2: Tuple[float, float],
    lst: Sequence[Tuple[float, float]],
    retAbove=True,
) -> List[Tuple[float, float]]:
    """
    Split the list defining a closed 2D object using line.
    If retAbove it True return all points >= line else all point <= line

    :param lst: is a sequence of 2D point tuples
    :param line: a two tuple of 2D point tuples
    :param retAbove:
    """
    # print(
    #     f"split_2d:+ lst={lst} linePt1={linePt1} linePt2={linePt2} retAbove={retAbove}"
    # )

    retBelow: bool = not retAbove

    # Formula for a 2d line is y = slope * x + yYntercept
    # Solve for lineY for each p[X]:
    #   lineY = ((slope * p[X]) + yIntercept)
    newList: List[Tuple[float, float]] = []
    # lineX = 0
    prvPt = lst[len(lst) - 1]
    # print(f"split_2d: prvPt={prvPt} len(lst)={len(lst)}")
    prvDir = lineToPtDirection_2d(linePt1, linePt2, prvPt)
    for i, curPt in enumerate(lst):
        curDir = lineToPtDirection_2d(linePt1, linePt2, curPt)
        # print(
        #     f"split_2d: tol {i}: prvPt={prvPt} prvDir={prvDir} curPt={curPt} curDir={curDir}"
        # )
        if ((curDir > 0) and (prvDir < 0)) or ((curDir < 0) and (prvDir > 0)):
            # points are on either side of the line, add an interpolated point
            intrPt = interpolatePt_2d(lst, linePt1, linePt2, i, curPt, prvPt)
            # print(f"split_2d: add intrPt={intrPt} at {len(newList)}")
            newList.append(intrPt)

        if (retAbove and (curDir >= 0)) or (retBelow and (curDir <= 0)):
            # This is a point we want, add to newList
            # print(f"split_2d: add curPt={curPt} at {len(newList)}")
            newList.append(curPt)

        prvPt = curPt
        prvDir = curDir

    # print(f"split_2d: newList={newList}")
    # print(
    #     f"slipt_2d:- lst={lst} linePt1={linePt1} linePt2={linePt2} retAbove={retAbove}"
    # )
    return newList


def perpendicular_distance_pt_to_line_2d(
    pt: Tuple[float, float], linePt1: Tuple[float, float], linePt2: Tuple[float, float],
) -> float:
    """
    Returns distance from pt to line define by linePt1 and linePt2.
    From: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    "Line defined by two points"
    """
    ydist: float = yDist_2d(linePt2, linePt1)
    xdist: float = xDist_2d(linePt2, linePt1)
    n: float = abs((ydist * pt[0]) - (xdist * pt[1]) + crossProdPts(linePt2, linePt1))
    d: float = sqrt((ydist * ydist) + (xdist * xdist))
    dist: float = n / d
    # print(f"dist={dist} ydist={ydist} xdist={xdist} n={n} d={d}")
    return dist


def valid(wp: Union[cq.Workplane, Sequence[cq.Workplane]]) -> bool:
    if isinstance(wp, Sequence):
        return reduce(
            lambda value, s: value and cast(cq.Shape, s.val()).isValid(), wp, True
        )
    else:
        return cast(cq.Shape, wp.val()).isValid()


def updatePending(wp: cq.Workplane) -> cq.Workplane:
    """
    Clear pendingWires and pendingEdges and then add
    objects that are wires or edges to the appropriate
    pending list. Another way to fix this would be to
    add a parameter to toPending which would do the
    clear before the extending operation.

    Fix cq bug https://github.com/CadQuery/cadquery/issues/421
    """
    wp.ctx.pendingWires = []
    wp.ctx.pendingEdges = []
    return wp.toPending()
