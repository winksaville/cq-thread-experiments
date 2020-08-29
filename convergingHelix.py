# from: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ
from math import cos, degrees, pi, sin
from typing import Callable, Tuple


def convergingHelix(
    radius: float,
    pitch: float,
    height: float,
    inset: float = 0,
    cvrgFactor: float = 0,
    horzOffset: float = 0,
    vertOffset: float = 0,
    firstT: float = 0,
    lastT: float = 1,
) -> Callable[[float], Tuple[float, float, float]]:
    """
    Returns a function which can be used to create helixes that are
    as simple as a single line to as complex as multifacited 3d solids
    that start at a point then smoothly expand to the solid and then
    smoothly converge back to a point.

    The initial use case is to create triangular or trapazoidal threads
    for nuts and bolts. Invoking convergingHelix multiple times with the
    same radius, pitch, inset, firstT, and lastT but with differing values
    for cvrgFactor, horzOffset and vertOffset the final solid will start
    at a point expand to the desired shape and then converge back to a
    point.

    Right now all "illegal parameters" will return Tuple[0, 0, 0]

    TODO: Should we throw an error on "illegal parameters" to convergingHelix
          such as, heightHelix != 0, pitch != 0, firstT >= cvrgFactor, cvrtFactor <= lastT

    TODO: Should "func" throw an error on "illegal parameters" such as t out of range
    """

    def func(t: float) -> Tuple[float, float, float]:

        x: float = 0
        y: float = 0
        z: float = 0

        # Reduce the height by 2 * inset. Threads start at inset
        # and end at height - inset.
        heightHelix: float = height - (2 * inset)
        if (
            heightHelix != 0
            and pitch != 0
            and t >= firstT
            and t <= lastT
            and firstT <= cvrgFactor
            and cvrgFactor <= lastT
        ):
            fadeAngle: float

            if (cvrgFactor > firstT) and (t <= cvrgFactor):
                # FadeIn, fadeAngle is 0 to 90deg so fadeScale is between 0 and 1
                fadeAngle = +(pi / 2 * t / cvrgFactor)
            elif (cvrgFactor == 0) or ((t > cvrgFactor) and (t < lastT - cvrgFactor)):
                # No fading set fadeAngle to 90deg so sin(fadeAngle) == 1
                fadeAngle = pi / 2
            else:
                # FadeOut, fadeAngle is 90 to 0deg so fadeScale is between 1 and 0
                fadeAngle = -((2 * pi) - (pi / 2 * (lastT - t) / cvrgFactor))
            fadeScale: float = sin(fadeAngle)

            r: float = radius + (horzOffset * fadeScale)
            a: float = 2 * pi / (pitch / heightHelix) * t
            x = r * sin(-a)
            y = r * cos(a)
            z = (heightHelix * t) + (vertOffset * fadeScale) + inset

            # print(f"cHelix.f: {t:.4f}: ({x:.4f}, {y:.4f}, {z:.4f})")
        else:
            # print(f"cHelix.f: {t:.4f}: (0, 0, 0)")
            pass

        return (x, y, z)

    return func
