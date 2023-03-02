"""
Copyright © 2023 Brain Buffer

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import cmath
import math
from PIL import Image, ImageDraw
import random

##### START CONFIGURATION #####

# Image resolution parameters
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
IMAGE_SUPERSAMPLE_FACTOR = 5

# Ellipse a and b values for radii (https://www.mathopenref.com/coordparamellipse.html)
INNER_A_MIN = 450
INNER_A_MAX = 450
INNER_B_MIN = 350
INNER_B_MAX = 350

OUTER_A_MIN = 550
OUTER_A_MAX = 550
OUTER_B_MIN = 400
OUTER_B_MAX = 400

# Spike triangle parameters
INNER_WIDTH_MIN = 50
INNER_WIDTH_MAX = 70
INNER_HEIGHT_MIN = 400
INNER_HEIGHT_MAX = 600

OUTER_WIDTH_MIN = 40
OUTER_WIDTH_MAX = 60
OUTER_HEIGHT_MIN = 400
OUTER_HEIGHT_MAX = 500

# Spike angle parameters
INNER_ANGLE_MIN = 6 * math.pi / 180
INNER_ANGLE_MAX = 6 * math.pi / 180
OUTER_ANGLE_MIN = 6 * math.pi / 180
OUTER_ANGLE_MAX = 6 * math.pi / 180

OVERLAP_SPIKES = False
INNER_PERCENT = 40  # % - Expected percentage of all spike which are inner spikes (only if OVERLAP_SPIKES == False)

# Spike colour parameters
INNER_FILL = "#9c0a09"
OUTER_FILL = "#9c0a09"

# Export parameters
SAVE = True
SHOW = False
INCLUDE_INNER_ELLIPSE = False

##### END CONFIGURATION #####

# Multiply configuration by supersampling factor
IMAGE_WIDTH *= IMAGE_SUPERSAMPLE_FACTOR
IMAGE_HEIGHT *= IMAGE_SUPERSAMPLE_FACTOR
INNER_A_MIN *= IMAGE_SUPERSAMPLE_FACTOR
INNER_A_MAX *= IMAGE_SUPERSAMPLE_FACTOR
INNER_B_MIN *= IMAGE_SUPERSAMPLE_FACTOR
INNER_B_MAX *= IMAGE_SUPERSAMPLE_FACTOR
OUTER_A_MIN *= IMAGE_SUPERSAMPLE_FACTOR
OUTER_A_MAX *= IMAGE_SUPERSAMPLE_FACTOR
OUTER_B_MIN *= IMAGE_SUPERSAMPLE_FACTOR
OUTER_B_MAX *= IMAGE_SUPERSAMPLE_FACTOR
INNER_WIDTH_MIN *= IMAGE_SUPERSAMPLE_FACTOR
INNER_WIDTH_MAX *= IMAGE_SUPERSAMPLE_FACTOR
INNER_HEIGHT_MIN *= IMAGE_SUPERSAMPLE_FACTOR
INNER_HEIGHT_MAX *= IMAGE_SUPERSAMPLE_FACTOR
OUTER_WIDTH_MIN *= IMAGE_SUPERSAMPLE_FACTOR
OUTER_WIDTH_MAX *= IMAGE_SUPERSAMPLE_FACTOR
OUTER_HEIGHT_MIN *= IMAGE_SUPERSAMPLE_FACTOR
OUTER_HEIGHT_MAX *= IMAGE_SUPERSAMPLE_FACTOR

# Ensure outer radii parameters >= inner radii parameters
OUTER_A_MIN = max(OUTER_A_MIN, INNER_A_MIN)
OUTER_A_MAX = max(OUTER_A_MAX, INNER_A_MAX)
OUTER_B_MIN = max(OUTER_B_MIN, INNER_B_MIN)
OUTER_B_MAX = max(OUTER_B_MAX, INNER_B_MAX)


def generate_triangle_coords(
    radius: float,
    angle: float,
    width: float,
    height: float,
) -> tuple[tuple, tuple, tuple]:
    p1 = complex(IMAGE_WIDTH / 2, IMAGE_HEIGHT / 2) + cmath.rect(radius, angle)  # inner-most vertex
    base_midpoint = p1 + cmath.rect(height, angle)
    p2 = base_midpoint + cmath.rect(width / 2, angle + math.pi / 2)  # second vertex
    p3 = base_midpoint + cmath.rect(width / 2, angle - math.pi / 2)  # third vertex

    return ((p1.real, p1.imag), (p2.real, p2.imag), (p3.real, p3.imag))


def draw_inner_spike(angle: float, draw: ImageDraw) -> float:
    """Draw inner spike and return angle delta to next spike"""
    x1 = (
        (INNER_A_MIN * INNER_B_MIN)
        / (INNER_A_MIN**2 * math.tan(angle) ** 2 + INNER_B_MIN**2) ** 0.5
        if (angle % (2 * math.pi)) not in [math.pi / 2, math.pi * 3 / 2]
        else 0
    )
    y1 = INNER_B_MIN * (1 - (x1 / INNER_A_MIN) ** 2) ** 0.5
    r1 = abs(complex(x1, y1))

    x2 = (
        (INNER_A_MAX * INNER_B_MAX)
        / (INNER_A_MAX**2 * math.tan(angle) ** 2 + INNER_B_MAX**2) ** 0.5
        if (angle % (2 * math.pi)) not in [math.pi / 2, math.pi * 3 / 2]
        else 0
    )
    y2 = INNER_B_MAX * (1 - (x1 / INNER_A_MAX) ** 2) ** 0.5
    r2 = abs(complex(x2, y2))

    radius = r1 + random.random() * (r2 - r1)

    spike_width = INNER_WIDTH_MIN + random.random() * (INNER_WIDTH_MAX - INNER_WIDTH_MIN)
    spike_height = INNER_HEIGHT_MIN + random.random() * (INNER_HEIGHT_MAX - INNER_HEIGHT_MIN)

    draw.polygon(
        xy=generate_triangle_coords(radius, angle, spike_width, spike_height),
        fill=INNER_FILL,
    )

    angle_delta = INNER_ANGLE_MIN + random.random() * (INNER_ANGLE_MAX - INNER_ANGLE_MIN)
    return angle_delta


def draw_outer_spike(angle: float, draw: ImageDraw) -> float:
    """Draw outer spike and return angle delta to next spike"""
    x1 = (
        (OUTER_A_MIN * OUTER_B_MIN)
        / (OUTER_A_MIN**2 * math.tan(angle) ** 2 + OUTER_B_MIN**2) ** 0.5
        if (angle % (2 * math.pi)) not in [math.pi / 2, math.pi * 3 / 2]
        else 0
    )
    y1 = OUTER_B_MIN * (1 - (x1 / OUTER_A_MIN) ** 2) ** 0.5
    r1 = abs(complex(x1, y1))

    x2 = (
        (OUTER_A_MAX * OUTER_B_MAX)
        / (OUTER_A_MAX**2 * math.tan(angle) ** 2 + OUTER_B_MAX**2) ** 0.5
        if (angle % (2 * math.pi)) not in [math.pi / 2, math.pi * 3 / 2]
        else 0
    )
    y2 = OUTER_B_MAX * (1 - (x1 / OUTER_A_MAX) ** 2) ** 0.5
    r2 = abs(complex(x2, y2))

    radius = r1 + random.random() * (r2 - r1)

    spike_width = OUTER_WIDTH_MIN + random.random() * (OUTER_WIDTH_MAX - OUTER_WIDTH_MIN)
    spike_height = OUTER_HEIGHT_MIN + random.random() * (OUTER_HEIGHT_MAX - OUTER_HEIGHT_MIN)

    draw.polygon(
        xy=generate_triangle_coords(radius, angle, spike_width, spike_height),
        fill=OUTER_FILL,
    )

    angle_delta = OUTER_ANGLE_MIN + random.random() * (OUTER_ANGLE_MAX - OUTER_ANGLE_MIN)
    return angle_delta


def draw_thumbnail():
    img = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT))
    draw = ImageDraw.Draw(img)

    if OVERLAP_SPIKES:
        # Add inner triangles
        angle = random.random() * 2 * math.pi
        angle_processed = 0
        while angle_processed <= 2 * math.pi - INNER_ANGLE_MIN:
            angle_delta = draw_inner_spike(angle, draw)
            angle += angle_delta
            angle_processed += angle_delta

        # Add outer triangles
        angle = random.random() * 2 * math.pi
        angle_processed = 0
        while angle_processed <= 2 * math.pi - OUTER_ANGLE_MIN:
            angle_delta = draw_outer_spike(angle, draw)
            angle += angle_delta
            angle_processed += angle_delta

    else:
        # Add inner and outer triangles based on expected ratio
        angle = random.random() * 2 * math.pi
        angle_processed = 0
        while angle_processed <= 2 * math.pi:
            if random.random() < INNER_PERCENT / 100:
                angle_delta = draw_inner_spike(angle, draw)
            else:
                angle_delta = draw_outer_spike(angle, draw)

            angle += angle_delta
            angle_processed += angle_delta

    if INCLUDE_INNER_ELLIPSE:
        draw.ellipse(
            [
                (IMAGE_WIDTH / 2 - INNER_A_MIN, IMAGE_HEIGHT / 2 - INNER_B_MIN),
                (IMAGE_WIDTH / 2 + INNER_A_MIN, IMAGE_HEIGHT / 2 + INNER_B_MIN),
            ]
        )

    img = img.resize(
        (IMAGE_WIDTH // IMAGE_SUPERSAMPLE_FACTOR, IMAGE_HEIGHT // IMAGE_SUPERSAMPLE_FACTOR),
        resample=Image.LANCZOS,
    )

    if SAVE:
        img.save("spike.png")
    if SHOW:
        img.show()


if __name__ == "__main__":
    draw_thumbnail()
