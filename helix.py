# from: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ
from math import cos, degrees, pi, sin
from typing import Callable, Tuple


def helix(
    radius: float,
    pitch: float,
    height: float,
    threadDepth: float,
    threadHalfHeight: float,
    inset: float = 0,
    frac: float = 1e-1,
) -> Callable[[float], Tuple[float, float, float]]:
    def func(t: float) -> Tuple[float, float, float]:

        x: float = 0
        y: float = 0
        z: float = 0

        # Reduce the height by 2 * inset. Threads start at inset
        # and end at height - inset.
        heightThreads = height - (2 * inset)
        if heightThreads > 0 and pitch > 0:
            fadeAngle: float

            if (frac > 0) and (t <= frac):
                # FadeIn, fadeAngle is 0 to 90deg so fadeScale is between 0 and 1
                fadeAngle = +(pi / 2 * t / frac)
            elif (frac == 0) or ((t > frac) and (t < 1 - frac)):
                # No fading set fadeAngle to 90deg so sin(fadeAngle) == 1
                fadeAngle = pi / 2
            else:
                # FadeOut, fadeAngle is 90 to 0deg so fadeScale is betwen 1 and 0
                fadeAngle = -((2 * pi) - (pi / 2 * (1 - t) / frac))
            fadeScale: float = sin(fadeAngle)

            r: float = radius + (threadDepth * fadeScale)
            a: float = 2 * pi / (pitch / heightThreads) * t
            x = r * sin(-a)
            y = r * cos(a)
            z = (heightThreads * t) + (threadHalfHeight * fadeScale) + inset

            # print(f"helix.f: {t:.4f}: ({x:.4f}, {y:.4f}, {z:.4f})")
        else:
            # print(f"helix.f: {t:.4f}: (0, 0, 0)")
            pass

        return (x, y, z)

    return func
