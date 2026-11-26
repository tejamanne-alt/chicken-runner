"""The lane's houses, modelled from their paintings (ArtSource/cutouts/lane). See kitlib.py for the kit.

A house is a real building: its walls, plinth, cornice, parapet and pillars as solids running round all four sides,
its door and windows recessed into the wall, its steps, sunshades, pots and plants standing out in front, a roof you
could stand on. The front takes the painting itself; the sides and back are the same plaster, stone and paint, cut
from the painting, with a door or window repeated where a real house would have one.
"""
import math

import numpy as np
from scipy import ndimage
from mathutils import Matrix, Vector

from kitlib import model


def stairs(K, steps, mat_top, mat_side=None, tread=0.3, y0=0.0):
    """Steps coming out from the wall at y0 towards the camera: steps [(x0_px, x1_px, top_py), ...] from the top
    step (nearest the wall) down; each lower step reaches one tread further out."""
    P = K.paint
    for k, (x0, x1, top) in enumerate(steps):
        K.box(P.x(x0), P.x(x1), y0 - tread * (k + 1), y0, 0.0, P.z(top), mat_top, bevel=0.01, name=f"step{k}")


def flat_roof_house(K, x0, x1, body_top_py, depth, wall, plinth=None, plinth_top_py=None, cornice=None,
                    coping=None, pillars=(), back_door=None):
    """The shell of a flat-roofed house: walls x0..x1 px from the ground to body_top_py, `depth` m deep; a plinth band
    round it to plinth_top_py; a cornice (y0_py, y1_py, out m) round all four sides; a coping lip on the roof's edge
    (y0_py, y1_py); corner pillars [(x0_px, x1_px, top_py, cap_py), ...] at the front and repeated at the back; a door
    copied onto the back wall (box px). Returns the wall object (to cut doors into)."""
    P = K.paint
    X0, X1 = P.x(x0), P.x(x1)
    top = P.z(body_top_py)
    body = K.box(X0, X1, 0.0, depth, 0.0, top, wall, name="walls")
    if plinth is not None:
        K.box(X0 - 0.03, X1 + 0.03, -0.03, depth + 0.03, 0.0, P.z(plinth_top_py), plinth, bevel=0.01, name="plinth")
    if cornice is not None:
        y0, y1, out, mat = cornice
        K.box(X0 - out, X1 + out, -out, depth + out, P.z(y1), P.z(y0), mat, bevel=0.015, name="cornice")
    if coping is not None:
        y0, y1, mat = coping
        lip = 0.12
        z0, z1 = P.z(y1), P.z(y0) + 0.06
        K.box(X0 - 0.03, X1 + 0.03, -0.03, lip, z0, z1, mat, bevel=0.01, name="coping_f")
        K.box(X0 - 0.03, X1 + 0.03, depth - lip, depth + 0.03, z0, z1, mat, bevel=0.01, name="coping_b")
        K.box(X0 - 0.03, X0 + lip, 0.0, depth, z0, z1, mat, bevel=0.01, name="coping_l")
        K.box(X1 - lip, X1 + 0.03, 0.0, depth, z0, z1, mat, bevel=0.01, name="coping_r")
    for px0, px1, top_py, cap_py, mat, cap in pillars:
        for y in (0.0, depth - P.m(px1 - px0)):
            K.box(P.x(px0), P.x(px1), y, y + P.m(px1 - px0), P.z(cap_py), P.z(top_py) - 0.0, mat, name="pillar")
            K.box(P.x(px0) - 0.04, P.x(px1) + 0.04, y - 0.04, y + P.m(px1 - px0) + 0.04, P.z(cap_py), P.z(cap_py) + 0.1,
                  cap, bevel=0.015, name="pillar_cap")
    if back_door is not None:
        bx0, by0, bx1, by1 = back_door
        mat = K.decal(back_door)
        # the back wall faces +Y: mirror the picture's corners so it reads the right way round from behind
        K.quad([(P.x(bx1), depth + 0.004, P.z(by1)), (P.x(bx0), depth + 0.004, P.z(by1)),
                (P.x(bx0), depth + 0.004, P.z(by0)), (P.x(bx1), depth + 0.004, P.z(by0))], mat, name="back_door")
    return body


def side_window(K, body, side, y_mid, z0, z1, width, frame, bars, dark, depth=0.12):
    """A small barred window in a side wall (side -1 left, +1 right): a dark recess, a frame round it, iron bars."""
    P = K.paint
    bb = [v[0] for v in body.bound_box]
    x_wall = max(bb) if side > 0 else min(bb)
    y0, y1 = y_mid - width / 2, y_mid + width / 2
    xo = x_wall + side * 0.03
    xi = x_wall - side * depth
    K.cut(body, min(xi, x_wall + side * 0.05), max(xi, x_wall + side * 0.05), y0, y1, z0, z1)
    K.box(min(xi, xi - side * 0.02), max(xi, xi - side * 0.02), y0, y1, z0, z1, dark, name="window_back")
    f = 0.06
    for a, b, c, d in ((y0 - f, y0, z0 - f, z1 + f), (y1, y1 + f, z0 - f, z1 + f), (y0, y1, z0 - f, z0), (y0, y1, z1, z1 + f)):
        K.box(min(xo, x_wall - side * 0.02), max(xo, x_wall - side * 0.02), a, b, c, d, frame, bevel=0.008, name="window_frame")
    n = 4
    for i in range(1, n):
        y = y0 + (y1 - y0) * i / n
        xb = x_wall - side * 0.02
        K.tube([(xb, y, z0), (xb, y, z1)], 0.009, bars, segments=6, name="bar")


@model("house_pink", "lane", kind="building", atlas=2048)
def house_pink(K):
    """A narrow pink lime-washed house: a parapet with corner pillars and three vents, a cornice, a teal door frame
    with a carved double door under a red sunshade and a garland, red kolam steps, a jasmine vine and a hibiscus in a
    pot."""
    P = K.paint
    depth = 4.0
    K.front_exclude = [(0, 360, 24, 513)]                       # the neighbour's ladder at the left edge
    wall = K.tile((14, 150, 84, 425), vary=0.05, soften=0.55)   # pink plaster, stained: the left strip
    upper = K.tile((12, 22, 66, 88), vary=0.05, soften=0.4)     # the parapet's plaster, streaked (the left pillar)
    ledge = K.colour((60, 92, 240, 104), vary=0.06)
    red = K.tile((28, 460, 78, 510), vary=0.06, soften=0.3)     # the red-oxide plinth and steps, below the kolam
    teal = K.colour((88, 260, 97, 400), vary=0.05)
    wood = K.tile((110, 300, 140, 400), P.m(30))
    body = flat_roof_house(
        K, 8, 312, 22, depth, wall, plinth=red, plinth_top_py=428,
        cornice=(92, 110, 0.07, ledge), coping=(22, 33, upper),
        pillars=[(8, 70, 5, 18, upper, ledge), (248, 312, 5, 18, upper, ledge)], back_door=(85, 178, 207, 415))
    # a plain lime-washed roof deck, and a small barred window in each side wall
    K.box(P.x(70), P.x(250), 0.12, depth - 0.12, P.z(22), P.z(22) + 0.01, K.colour((20, 40, 60, 80), vary=0.08, pct=70),
          name="roof_deck")
    iron = K.colour((0.025, 0.02, 0.02), vary=0.05)
    dark = K.colour((0.03, 0.02, 0.025), vary=0.0)
    for side in (-1, 1):
        side_window(K, body, side, depth * 0.55, P.z(330), P.z(250), 0.7, teal, iron, dark)
    # the door: recessed 12 cm into the wall inside its teal frame
    K.cut(body, P.x(98), P.x(192), -0.05, 0.25, P.z(412), P.z(190))
    K.box(P.x(98), P.x(192), 0.12, 0.17, P.z(412), P.z(190), wood, name="door")
    for x0, x1 in ((87, 98), (192, 205)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(413), P.z(180), teal, bevel=0.008, name="jamb")
    K.box(P.x(87), P.x(205), -0.03, 0.12, P.z(190), P.z(180), teal, bevel=0.008, name="frame_head")
    # the vents in the parapet: three small recesses
    for x0, x1 in ((85, 98), (115, 128), (145, 157)):
        K.cut(body, P.x(x0), P.x(x1), -0.05, 0.1, P.z(62), P.z(38))
    # the sunshade over the door
    K.box(P.x(57), P.x(237), -0.16, 0.0, P.z(170), P.z(155), red, bevel=0.01, name="sunshade")
    # the garland: a swag of marigolds across the door and its two hanging strings
    flowers = K.colour((120, 205, 200, 225), vary=0.25, scale=40)
    pts = [P.pt(x, y, -0.05) for x, y in ((84, 192), (110, 205), (148, 215), (186, 205), (212, 192))]
    K.tube(pts, P.m(10), flowers, segments=8, name="garland")
    for x in (88, 207):
        K.tube([P.pt(x, 185, -0.05), P.pt(x, 245, -0.05)], P.m(8), flowers, segments=8, name="garland_string")
    # the steps
    stairs(K, [(80, 212, 413), (73, 222, 433), (63, 232, 460), (53, 247, 490)], red)
    # the hibiscus in its pot
    pot = K.projected(axis_x=P.x(275), squeeze=0.94, keep=[(238, 428, 314, 513)])
    prof = [(28, 513), (30, 505), (24, 495), (27, 480), (33, 445), (37, 432), (36, 427)]
    K.lathe([(P.m(r), P.z(y)) for r, y in prof], pot, segments=28, centre=(P.x(275), -0.35, 0.0), name="pot")
    K.leaves_only((205, 300, 335, 432))
    for i in range(14):
        cx, cy = K.rng.uniform(222, 318), K.rng.uniform(318, 418)
        K.card_from_painting((cx - 34, cy - 30, cx + 34, cy + 30), (P.x(cx), -0.35 + K.rng.uniform(-0.25, 0.25), P.z(cy)),
                             yaw=K.rng.uniform(-70, 70), pitch=K.rng.uniform(-20, 20), name="hibiscus")
    K.card_from_painting((205, 300, 335, 432), (P.x(270), -0.6, P.z(366)), name="hibiscus_front")
    # the jasmine vine over the wall's top right, standing a little off it
    K.leaves_only((150, 40, 340, 300))
    for i in range(22):
        cx, cy = K.rng.uniform(165, 325), K.rng.uniform(55, 285)
        if cx < 220 and cy > 140:
            continue
        K.card_from_painting((cx - 30, cy - 30, cx + 30, cy + 30), (P.x(cx), -K.rng.uniform(0.03, 0.18), P.z(cy)),
                             yaw=K.rng.uniform(-50, 50), pitch=K.rng.uniform(-25, 25), name="vine")
    # the vine comes round the corner onto the right side
    for i in range(10):
        cx, cy = K.rng.uniform(270, 320), K.rng.uniform(60, 260)
        K.card_from_painting((cx - 28, cy - 28, cx + 28, cy + 28), (P.x(312) + 0.03, K.rng.uniform(0.1, 1.2), P.z(cy)),
                             yaw=90 + K.rng.uniform(-25, 25), name="vine_side")


# ====================================================================== helpers for the rest of the lane
def scatter_cards(K, box, n, size, y_range, yaw=60, pitch=20, name="plant", skip=None, x_range=None, z_range=None):
    """n cards cut from the painting inside box (px), each placed where it is painted, at a depth in y_range (m);
    `skip(px, py)` leaves a spot out. Masked with leaves_only(box) by the caller."""
    P = K.paint
    x0, y0, x1, y1 = box
    xr = x_range or (x0, x1)
    zr = z_range or (y0, y1)
    alpha = P.rgba[..., 3]
    placed, tries = 0, 0
    while placed < n and tries < n * 30:
        tries += 1
        cx, cy = K.rng.uniform(*xr), K.rng.uniform(*zr)
        if alpha[int(min(P.h - 1, cy)), int(min(P.w - 1, cx))] < 0.5:
            continue
        if skip is not None and skip(cx, cy):
            continue
        w, h = size[0] * K.rng.uniform(0.8, 1.2), size[1] * K.rng.uniform(0.8, 1.2)
        K.card_from_painting((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2),
                             (P.x(cx), K.rng.uniform(*y_range), P.z(cy)), yaw=K.rng.uniform(-yaw, yaw),
                             pitch=K.rng.uniform(-pitch, pitch), name=name)
        placed += 1
    return placed


def side_cards(K, box, n, size, x_wall, side, y_range, name="vine_side"):
    """n cards from the painting inside box hung on a side wall (x_wall, facing side -1/+1), spread over y_range."""
    P = K.paint
    x0, y0, x1, y1 = box
    for i in range(n):
        cx, cy = K.rng.uniform(x0, x1), K.rng.uniform(y0, y1)
        K.card_from_painting((cx - size[0] / 2, cy - size[1] / 2, cx + size[0] / 2, cy + size[1] / 2),
                             (x_wall + side * K.rng.uniform(0.02, 0.08), K.rng.uniform(*y_range), P.z(cy)),
                             yaw=90 + K.rng.uniform(-25, 25), pitch=K.rng.uniform(-15, 15), name=name)


def pot(K, cx_px, prof_px, keep, y, exclude=(), name="pot", segments=28, mouth=True, squeeze=0.93, wobble=0.01):
    """A clay pot turned from its painted outline (radius px, y px from the foot up) at depth y, wearing its own
    painted bands all round; a dark mouth going into it."""
    P = K.paint
    mat = K.projected(axis_x=P.x(cx_px), squeeze=squeeze, keep=keep, exclude=exclude)
    ob = K.lathe([(P.m(r), P.z(py)) for r, py in prof_px], mat, segments=segments, centre=(P.x(cx_px), y, 0.0),
                 wobble=wobble, name=name)
    if mouth:
        r_top, z_top = P.m(prof_px[-1][0]), P.z(prof_px[-1][1])
        inside = K.colour((0.06, 0.03, 0.015), vary=0.1)
        K.lathe([(r_top * 0.92, z_top - 0.002), (r_top * 0.85, z_top - 0.05), (0.0, z_top - 0.07)], inside,
                segments=segments, centre=(P.x(cx_px), y, 0.0), name=name + "_mouth", cap=False)
    return ob


def back_decal(K, box, depth, x_shift=0.0, name="back_door"):
    """The painted thing inside box (px) repeated on the back wall (y = depth), mirrored so it reads right from
    behind; x_shift moves it along the wall (m)."""
    P = K.paint
    bx0, by0, bx1, by1 = box
    mat = K.decal(box)
    y = depth + 0.004
    return K.quad([(P.x(bx1) + x_shift, y, P.z(by1)), (P.x(bx0) + x_shift, y, P.z(by1)),
                   (P.x(bx0) + x_shift, y, P.z(by0)), (P.x(bx1) + x_shift, y, P.z(by0))], mat, name=name)


def side_decal(K, box, x_wall, side, y_mid, z0=None, width=None, name="side_decal"):
    """The painted thing inside box (px) put on a side wall at x_wall (side -1 left, +1 right), centred at y_mid,
    its bottom at z0 (default where it is painted), `width` m wide (default as painted)."""
    P = K.paint
    bx0, by0, bx1, by1 = box
    w = width or P.m(bx1 - bx0)
    h = P.m(by1 - by0) * (w / P.m(bx1 - bx0))
    z0 = P.z(by1) if z0 is None else z0
    x = x_wall + side * 0.004
    ya, yb = (y_mid - w / 2, y_mid + w / 2) if side < 0 else (y_mid + w / 2, y_mid - w / 2)
    # seen from outside: left side looks towards +x, its left hand is +y... keep the picture unmirrored
    ya, yb = (y_mid + w / 2, y_mid - w / 2) if side < 0 else (y_mid - w / 2, y_mid + w / 2)
    return K.quad([(x, ya, z0), (x, yb, z0), (x, yb, z0 + h), (x, ya, z0 + h)], K.decal(box), name=name)


# ====================================================================== house_limewash
@model("house_limewash", "lane", kind="building", atlas=2048)
def house_limewash(K):
    """A narrow cream lime-washed house: a parapet with three vents and a raised corner, a cornice, a teal door frame
    with a carved double door under a red kolam sunshade and a marigold garland, red kolam steps, a pot on a red
    platform, a hibiscus climbing over the left corner and a bush at the right."""
    P = K.paint
    depth = 4.0
    wall = K.tile((214, 215, 252, 400), size=0.5, vary=0.05, soften=0.6)   # cream plaster, right of the door
    upper = K.tile((132, 84, 198, 106), vary=0.05, soften=0.35)      # the parapet's plaster with its rust streaks
    ledge = K.colour((130, 112, 200, 122), vary=0.06)
    red = K.tile((30, 472, 90, 510), vary=0.06, soften=0.3)          # red-oxide platform, below its kolam border
    teal = K.colour((95, 250, 105, 400), vary=0.05)
    wood = K.tile((110, 300, 140, 400), P.m(30))
    X0, X1 = P.x(27), P.x(254)
    body = flat_roof_house(K, 27, 254, 41, depth, wall, plinth=red, plinth_top_py=440,
                           cornice=(108, 126, 0.08, ledge), coping=(41, 52, upper), back_door=(92, 181, 212, 425))
    # the raised right corner of the parapet, front and back
    for y in (0.0, depth - 0.45):
        K.box(P.x(200), X1 + 0.03, y - 0.03 * (y == 0), y + 0.45 + 0.03 * (y > 0), P.z(52), P.z(26), upper, bevel=0.02,
              name="corner_block")
    K.box(X0 + 0.12, X1 - 0.12, 0.12, depth - 0.12, P.z(41), P.z(41) + 0.01,
          K.colour((140, 60, 196, 76), vary=0.08, pct=70), name="roof_deck")
    iron = K.colour((0.025, 0.02, 0.02), vary=0.05)
    dark = K.colour((0.03, 0.02, 0.025), vary=0.0)
    for side in (-1, 1):
        side_window(K, body, side, depth * 0.55, P.z(330), P.z(250), 0.7, teal, iron, dark)
    # the vents: three recesses with a dark back
    for x0, x1 in ((118, 130), (147, 158), (175, 186)):
        K.cut(body, P.x(x0), P.x(x1), -0.05, 0.14, P.z(82), P.z(57))
        K.box(P.x(x0), P.x(x1), 0.1, 0.12, P.z(82), P.z(57), dark, name="vent_back")
    # the door, recessed in its teal frame
    K.cut(body, P.x(106), P.x(200), -0.05, 0.25, P.z(426), P.z(197))
    K.box(P.x(106), P.x(200), 0.12, 0.17, P.z(426), P.z(197), wood, name="door")
    for x0, x1 in ((93, 106), (200, 212)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(426), P.z(181), teal, bevel=0.008, name="jamb")
    K.box(P.x(93), P.x(212), -0.03, 0.12, P.z(197), P.z(181), teal, bevel=0.008, name="frame_head")
    # the sunshade with its kolam edge
    K.box(P.x(77), P.x(228), -0.2, 0.0, P.z(181), P.z(165), red, bevel=0.01, name="sunshade")
    # the garland across the door and its two strings
    flowers = K.colour((120, 205, 180, 225), vary=0.25, scale=40)
    strings = K.colour((88, 210, 100, 245), vary=0.25, scale=40)
    pts = [P.pt(x, y, -0.06) for x, y in ((96, 196), (118, 214), (152, 228), (188, 214), (208, 196))]
    K.tube(pts, P.m(10), flowers, segments=8, name="garland")
    for x in (98, 208):
        K.tube([P.pt(x, 190, -0.05), P.pt(x, 248, -0.05)], P.m(7), strings, segments=8, name="garland_string")
    # the steps, and the red platforms either side of them
    stairs(K, [(93, 215, 425), (83, 220, 445), (75, 229, 467), (65, 237, 490)], red)
    K.box(X0 - 0.03, P.x(93), -0.45, 0.0, 0.0, P.z(440), red, bevel=0.012, name="platform_l")
    K.box(P.x(215), X1 + 0.03, -0.45, 0.0, 0.0, P.z(446), red, bevel=0.012, name="platform_r")
    # the pot on the left platform
    pot(K, 64, [(13, 440), (20, 436), (27, 426), (31, 410), (30, 400), (26, 390), (17, 384), (14, 382), (15, 379),
                (18, 376), (16, 374)], keep=[(30, 372, 98, 441)], y=-0.22)
    # the hibiscus climbing over the left corner: cards where it is painted, standing a little off the wall, round
    # the corner onto the left side and over the parapet onto the roof
    K.leaves_only((0, 0, 150, 335))
    scatter_cards(K, (0, 0, 150, 335), 30, (60, 60), (-0.2, -0.02), yaw=45, pitch=25, name="vine")
    K.card_from_painting((0, 0, 150, 335), (P.x(75), -0.21, P.z(167.5)), name="vine_front")
    side_cards(K, (0, 40, 60, 320), 12, (55, 55), X0, -1, (0.05, 1.3))
    scatter_cards(K, (20, 0, 120, 60), 6, (50, 45), (0.1, 0.9), yaw=30, pitch=70, name="vine_roof")
    # the bush at the bottom right
    K.leaves_only((216, 395, 254, 512))
    scatter_cards(K, (216, 395, 254, 512), 10, (40, 45), (-0.45, -0.1), yaw=70, name="bush")
    K.card_from_painting((216, 395, 254, 512), (P.x(235), -0.47, P.z(453.5)), name="bush_front")


def raised_parapet(K, x0_px, x1_px, top_py, base_py, depth, mat, rim=0.3, left=False, right=False, back=True):
    """A raised stretch of parapet x0..x1 px from base_py up to top_py: a rim `rim` m thick along the front, and along
    the back and the outer sides if asked (so from behind it is the same raised wall)."""
    P = K.paint
    X0, X1, Z0, Z1 = P.x(x0_px), P.x(x1_px), P.z(base_py), P.z(top_py)
    K.box(X0, X1, -0.03, rim, Z0, Z1, mat, bevel=0.02, name="parapet_raised")
    if back:
        K.box(X0, X1, depth - rim, depth + 0.03, Z0, Z1, mat, bevel=0.02, name="parapet_raised_b")
    if left:
        K.box(X0, X0 + rim, 0.0, depth, Z0, Z1, mat, bevel=0.02, name="parapet_raised_l")
    if right:
        K.box(X1 - rim, X1, 0.0, depth, Z0, Z1, mat, bevel=0.02, name="parapet_raised_r")


def barred_window(K, body, frame_box, opening_box, bars_x, bars_y, frame, iron, dark, depth=0.2, out=0.05):
    """A window in the front wall: its wooden frame (frame_box px) standing out `out` m, the opening (px) recessed
    `depth` m to a dark back, iron bars at bars_x (vertical) and bars_y (horizontal) px."""
    P = K.paint
    fx0, fy0, fx1, fy1 = frame_box
    ox0, oy0, ox1, oy1 = opening_box
    K.cut(body, P.x(ox0), P.x(ox1), -0.1, depth + 0.02, P.z(oy1), P.z(oy0))
    K.box(P.x(ox0), P.x(ox1), depth - 0.03, depth, P.z(oy1), P.z(oy0), dark, name="window_back")
    for a, b, c, d in ((fx0, ox0, fy0, fy1), (ox1, fx1, fy0, fy1), (ox0, ox1, fy0, oy0), (ox0, ox1, oy1, fy1)):
        K.box(P.x(a), P.x(b), -out, 0.04, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    r = P.m(2.2)
    yb = depth * 0.35
    for x in bars_x:
        K.tube([P.pt(x, oy1, yb), P.pt(x, oy0, yb)], r, iron, segments=6, name="bar")
    for y in bars_y:
        K.tube([P.pt(ox0, y, yb - 0.02), P.pt(ox1, y, yb - 0.02)], r, iron, segments=6, name="bar")


def shutter(K, hinge_px, width_m, py0, py1, angle, mat, side=-1, name="shutter"):
    """A wooden shutter hinged at hinge_px, swung open `angle` degrees out from the wall towards the camera, to the
    left (side -1) or right (+1)."""
    P = K.paint
    a = math.radians(angle)
    hx = P.x(hinge_px)
    tx, ty = hx + side * width_m * math.cos(a), -width_m * math.sin(a)
    rot = math.degrees(math.atan2(ty, tx - hx))
    return K.block((hx + tx) / 2, ty / 2, (P.z(py0) + P.z(py1)) / 2, width_m, 0.03, abs(P.z(py0) - P.z(py1)), mat,
                   rot=(0, 0, rot), bevel=0.005, name=name)


@model("house_turmeric_ladder", "lane", kind="building", atlas=2048)
def house_turmeric_ladder(K):
    """A turmeric-yellow house: a stepped parapet with five vents, a cornice, a barred window with an open shutter, a
    teal door frame with a carved double door under a red kolam sunshade and a garland, red kolam steps, a pot on a
    red thinnai platform, bushes either side. (Its ladder is a separate 3D prop in the game.)"""
    P = K.paint
    depth = 4.5
    K.front_exclude = [(0, 96, 25, 152), (384, 0, 422, 477), (0, 0, 3, 400)]   # the neighbours' bits at the edges
    wall = K.tile((135, 280, 172, 355), size=0.6, vary=0.05, soften=0.7)    # turmeric plaster between window and door
    upper = K.tile((190, 18, 300, 74), vary=0.05, soften=0.3)                # the parapet's cream with orange streaks
    ledge = K.colour((100, 82, 280, 92), vary=0.06)
    red = K.tile((35, 405, 120, 470), vary=0.06, soften=0.35)               # the thinnai's red oxide, below its kolam
    teal = K.colour((178, 250, 186, 380), vary=0.05)
    wood = K.tile((190, 300, 230, 380), P.m(30))
    frame = K.colour((56, 185, 68, 268), vary=0.08)
    X0, X1 = P.x(3), P.x(383)
    body = flat_roof_house(K, 3, 383, 25, depth, wall, plinth=red, plinth_top_py=455,
                           cornice=(78, 97, 0.09, ledge), coping=(25, 34, upper), back_door=(175, 162, 293, 390))
    raised_parapet(K, 3, 70, 5, 34, depth, upper, rim=0.32, left=True)
    raised_parapet(K, 180, 383, 4, 34, depth, upper, rim=0.32, right=True)
    K.box(X0 + 0.12, X1 - 0.12, 0.12, depth - 0.12, P.z(25), P.z(25) + 0.01,
          K.colour((120, 30, 175, 40), vary=0.08, pct=70), name="roof_deck")
    iron = K.colour((0.05, 0.04, 0.035), vary=0.05)
    bars = K.colour((96, 199, 120, 204), vary=0.05)
    dark = K.colour((0.03, 0.02, 0.015), vary=0.0)
    # side windows, and the front window repeated on the back
    for side in (-1, 1):
        side_window(K, body, side, depth * 0.5, P.z(274), P.z(185), 0.7, frame, iron, dark)
    back_decal(K, (52, 180, 132, 274), depth, x_shift=P.m(-20), name="back_window")
    # the vents in the low stretch of parapet
    for x0, x1 in ((72, 80), (93, 101), (118, 127), (145, 153), (168, 176)):
        K.cut(body, P.x(x0), P.x(x1), -0.05, 0.14, P.z(62), P.z(42))
        K.box(P.x(x0), P.x(x1), 0.1, 0.12, P.z(62), P.z(42), dark, name="vent_back")
    # the window: frame, bars, the shutter swung open
    barred_window(K, body, (52, 180, 132, 274), (72, 188, 126, 269), (85.5, 99, 111.5),
                  (201.5, 214.5, 227.5, 241, 254.5), frame, bars, dark)
    shutter(K, 72, 0.3, 183, 272, 56, frame, side=-1)
    # the door, recessed in its teal frame
    K.cut(body, P.x(186), P.x(280), -0.05, 0.25, P.z(391), P.z(174))
    K.box(P.x(186), P.x(280), 0.12, 0.17, P.z(391), P.z(174), wood, name="door")
    for x0, x1 in ((175, 186), (280, 292)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(391), P.z(162), teal, bevel=0.008, name="jamb")
    K.box(P.x(175), P.x(292), -0.03, 0.12, P.z(174), P.z(162), teal, bevel=0.008, name="frame_head")
    K.box(P.x(147), P.x(320), -0.22, 0.0, P.z(152), P.z(137), red, bevel=0.01, name="sunshade")
    flowers = K.colour((222, 186, 246, 196), vary=0.25, scale=40)
    strings = K.colour((178, 185, 183, 225), vary=0.25, scale=40)
    pts = [P.pt(x, y, -0.06) for x, y in ((183, 172), (207, 192), (233, 202), (259, 192), (285, 172))]
    K.tube(pts, P.m(11), flowers, segments=8, name="garland")
    for x in (178, 290):
        K.tube([P.pt(x, 166, -0.05), P.pt(x, 228, -0.05)], P.m(6), strings, segments=8, name="garland_string")
    stairs(K, [(171, 294, 390), (154, 308, 410), (143, 320, 431), (135, 332, 456)], red)
    # the thinnai on the left with its pot, a low platform on the right behind the bush
    K.box(P.x(26), P.x(174), -0.55, 0.0, 0.0, P.z(362), red, bevel=0.012, name="thinnai")
    K.box(P.x(294), X1 + 0.03, -0.4, 0.0, 0.0, P.z(440), red, bevel=0.012, name="platform_r")
    pot(K, 110.3, [(16.8, 364), (20, 357), (26, 348.5), (29.6, 336), (25.7, 321), (20.5, 315), (14, 311),
                   (16.5, 305.5), (14.5, 303.5)], keep=[(78, 302, 143, 366)], y=-0.3)
    # bushes at both feet of the wall
    K.leaves_only((0, 398, 72, 477))
    scatter_cards(K, (0, 398, 72, 477), 10, (40, 40), (-0.5, -0.05), yaw=70, name="bush_l")
    K.card_from_painting((0, 398, 72, 477), (P.x(36), -0.57, P.z(437.5)), name="bush_l_front")
    K.leaves_only((298, 355, 384, 477))
    scatter_cards(K, (298, 355, 384, 477), 14, (45, 45), (-0.42, -0.05), yaw=70, name="bush_r")
    K.card_from_painting((298, 355, 384, 477), (P.x(341), -0.44, P.z(416)), name="bush_r_front")


def country_roof(K, x0_px, x1_px, y_eave, y_top, z_eave, z_top, mat, courses, col_px, tile_r=0.035, lip=0.025,
                 hip_px=(0, 0), thickness=0.03, name="roof", x0_top_px=None, x1_top_px=None):
    """A country-tile roof slope from the eave (y_eave, z_eave) up to (y_top, z_top): `courses` rows of half-round
    tiles (so each painted row lands on a modelled row when the painting is projected from the front), columns
    col_px wide as painted, each course's lower end standing proud by `lip`; hip_px pulls the two ends in by that
    many px at the top (a hipped end)."""
    P = K.paint
    X0, X1 = P.x(x0_px), P.x(x1_px)
    T0 = P.x(x0_top_px if x0_top_px is not None else x0_px + hip_px[0])
    T1 = P.x(x1_top_px if x1_top_px is not None else x1_px - hip_px[1])
    ncol = max(2, int(round(P.m(x1_px - x0_px) / P.m(col_px))))
    jitter = K.rng.normal(0, 1, (courses + 2, ncol + 2))

    def surf(u, v):
        xa, xb = X0 + (T0 - X0) * v, X1 + (T1 - X1) * v
        x = xa + (xb - xa) * u
        col = u * ncol
        ripple = tile_r * abs(math.sin(math.pi * col))
        c = min(courses - 1, int(v * courses))
        frac = v * courses - c
        z = z_eave + (z_top - z_eave) * v + ripple + lip * (1 - frac) ** 2 + 0.006 * jitter[c, int(col)]
        y = y_eave + (y_top - y_eave) * v
        return (x, y, z)
    return K.sheet(surf, ncol * 8, courses * 8, mat, name=name, smooth=False, thickness=thickness)


def turned_post(K, cx_px, prof_px, y, keep, name="post", segments=20, squeeze=0.9):
    """A turned wooden pillar from its painted outline [(radius px, y px), ...] bottom up, at depth y, its own
    painted bands all round."""
    P = K.paint
    mat = K.projected(axis_x=P.x(cx_px), squeeze=squeeze, keep=keep)
    return K.lathe([(P.m(r), P.z(py)) for r, py in prof_px], mat, segments=segments, centre=(P.x(cx_px), y, 0.0),
                   name=name)


PILLAR_IV = [(10.5, 405), (12, 400), (14, 390), (14.5, 380), (13.5, 368), (11, 362), (13, 357), (13, 350),
             (13.3, 340), (12, 300), (10, 240), (11, 235), (13, 232), (13, 228), (11, 224), (13.5, 218), (13.5, 208),
             (12.5, 204), (12.5, 199)]


@model("house_indigo_veranda", "lane", kind="building", atlas=2048)
def house_indigo_veranda(K):
    """An indigo-washed house with a stepped parapet and six vents, a veranda under a lean-to of country tiles on
    three turned wooden pillars, a barred window with open shutters, a teal-framed carved door with a garland, a
    brass lantern, a hanging fern, a cot with a striped bolster, a pot, a red kolam plinth and steps."""
    P = K.paint
    depth, ver = 4.5, 1.5                       # the house behind its front wall; the veranda in front of it
    py_ = -1.3                                  # the pillars' line
    K.front_min = 0.0                           # the lean-to faces the camera only at a slant: let it take the painting
    K.front_exclude = [(0, 0, 10, 100), (532, 0, 546, 100)]
    wall = K.tile((427, 275, 490, 400), size=0.6, vary=0.05, soften=0.6)      # indigo plaster right of the door
    upper = K.tile((120, 66, 230, 86), vary=0.05, soften=0.3)                 # the parapet's indigo, streaked
    ledge = K.colour((120, 90, 400, 98), vary=0.06)
    red = K.tile((300, 470, 420, 500), vary=0.06, soften=0.35)                # red-oxide plinth below the kolam
    floor = K.colour((60, 434, 230, 440), vary=0.08)
    teal = K.colour((295, 260, 303, 400), vary=0.05)
    wood = K.tile((320, 300, 360, 400), P.m(30))
    timber = K.tile((5, 162, 200, 178), vary=0.05)                            # the veranda beam
    tiles = K.tile((60, 104, 220, 160), vary=0.04)
    stone = K.colour((25, 412, 58, 436), vary=0.08)
    iron = K.colour((0.05, 0.04, 0.035), vary=0.05)
    dark = K.colour((0.025, 0.02, 0.03), vary=0.0)
    frame = K.colour((152, 233, 215, 240), vary=0.08)
    zf = P.z(438)                                                              # the veranda floor
    # the walls: the lower storey wide (to the veranda's ends), the parapet above the roof a little narrower
    body = K.box(P.x(8), P.x(538), 0.0, depth, 0.0, P.z(100), wall, name="walls")
    top = K.box(P.x(22), P.x(520), 0.0, depth, P.z(100), P.z(20), upper, name="parapet_walls")
    K.box(P.x(18), P.x(527), -0.08, depth + 0.08, P.z(102), P.z(88), ledge, bevel=0.015, name="cornice")
    for y0, y1, xa, xb in ((-0.03, 0.12, 22, 520), (depth - 0.12, depth + 0.03, 22, 520)):
        K.box(P.x(xa) - 0.03, P.x(xb) + 0.03, y0, y1, P.z(28), P.z(20) + 0.05, upper, bevel=0.01, name="coping")
    raised_parapet(K, 22, 112, 5, 28, depth, upper, rim=0.32, left=True)
    raised_parapet(K, 436, 520, 5, 28, depth, upper, rim=0.32, right=True)
    K.box(P.x(30), P.x(512), 0.12, depth - 0.12, P.z(20), P.z(20) + 0.01, K.colour((120, 40, 180, 50), vary=0.08,
          pct=70), name="roof_deck")
    for x0, x1 in ((188, 202), (222, 236), (258, 272), (300, 314), (336, 350), (372, 386)):
        K.cut(top, P.x(x0), P.x(x1), -0.05, 0.14, P.z(63), P.z(38))
        K.box(P.x(x0), P.x(x1), 0.1, 0.12, P.z(63), P.z(38), dark, name="vent_back")
    # the plinth under the house and the veranda, its floor
    K.box(P.x(18), P.x(520), -ver, depth + 0.04, 0.0, zf, red, bevel=0.012, name="plinth")
    K.box(P.x(20), P.x(518), -ver + 0.02, -0.0, zf, zf + 0.008, floor, name="veranda_floor")
    # the door, recessed in its teal frame, a threshold step before it
    K.cut(body, P.x(305), P.x(412), -0.05, 0.25, P.z(428), P.z(208))
    K.box(P.x(305), P.x(412), 0.12, 0.17, P.z(428), P.z(208), wood, name="door")
    for x0, x1 in ((293, 305), (412, 423)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(428), P.z(196), teal, bevel=0.008, name="jamb")
    K.box(P.x(293), P.x(423), -0.03, 0.12, P.z(208), P.z(196), teal, bevel=0.008, name="frame_head")
    K.box(P.x(292), P.x(427), -0.32, 0.0, zf, P.z(425), red, bevel=0.01, name="threshold")
    # the steps down from the veranda's edge
    stairs(K, [(283, 433, 440), (262, 448, 456), (245, 463, 479)], red, tread=0.28, y0=-ver)
    # the window: frame, bars, both shutters open
    barred_window(K, body, (150, 232, 218, 322), (157, 240, 211, 316), (168, 180, 192, 203), (253, 268, 283, 298),
                  frame, iron, dark)
    shutter(K, 157, 0.27, 237, 318, 60, frame, side=-1)
    shutter(K, 211, 0.27, 237, 318, 60, frame, side=1)
    # garland
    flowers = K.colour((330, 225, 345, 235), vary=0.25, scale=40)
    strings = K.colour((296, 220, 304, 260), vary=0.25, scale=40)
    pts = [P.pt(x, y, -0.06) for x, y in ((298, 205), (325, 226), (358, 236), (392, 226), (418, 205))]
    K.tube(pts, P.m(10), flowers, segments=8, name="garland")
    for x in (297, 420):
        K.tube([P.pt(x, 200, -0.05), P.pt(x, 265, -0.05)], P.m(7), strings, segments=8, name="garland_string")
    # the pillars on their stone blocks, capitals and brackets, the beam over them with its rafter ends
    for cx in (42, 257, 512):
        turned_post(K, cx, PILLAR_IV, py_, keep=[(cx - 16, 198, cx + 16, 408)], name="pillar")
        K.box(P.x(cx - 17.5), P.x(cx + 17.5), py_ - 0.15, py_ + 0.15, zf, P.z(405), stone, bevel=0.01, name="base")
        K.box(P.x(cx - 14), P.x(cx + 14), py_ - 0.12, py_ + 0.12, P.z(200), P.z(176), timber, bevel=0.006, name="capital")
        K.box(P.x(cx - 22), P.x(cx + 22), py_ - 0.14, py_ + 0.14, P.z(178), P.z(168), timber, bevel=0.006, name="bracket")
    K.box(P.x(0), P.x(546), py_ - 0.11, py_ + 0.11, P.z(178), P.z(162), timber, bevel=0.008, name="beam")
    slope = math.degrees(math.atan2(P.z(100) - P.z(168), -py_ + 0.1))
    for x in range(5, 546, 38):
        L = math.hypot(-py_ + 0.12, P.z(100) - P.z(168))
        K.block(P.x(x + 4), py_ / 2 - 0.02, (P.z(103) + P.z(170)) / 2, P.m(8), L, P.m(9), timber, rot=(slope, 0, 0),
                name="rafter")
    # the lean-to of country tiles, hipped at its ends
    country_roof(K, 0, 546, -1.62, 0.0, P.z(163), P.z(100), tiles, courses=3, col_px=33, tile_r=0.04, lip=0.03,
                 hip_px=(25, 25))
    # the lantern on its bracket
    brass = K.projected(axis_x=P.x(470), squeeze=0.9, keep=[(455, 195, 486, 260)], inset=2)
    K.lathe([(P.m(r), P.z(y)) for r, y in ((1, 259), (5, 255), (11, 248), (12.5, 240), (12.5, 220), (13, 214),
                                           (9, 208), (4, 204), (2, 198))], brass, segments=16,
            centre=(P.x(470), -0.22, 0.0), name="lantern")
    K.tube([P.pt(470, 182, 0.0), P.pt(470, 182, -0.22), P.pt(470, 198, -0.22)], 0.008, iron, segments=6, name="hook")
    # the hanging fern: its pot on ropes from the beam, leaves as cards
    pot(K, 104, [(5, 266), (11, 262), (14, 252), (14.5, 242), (15, 234), (14, 232)], keep=[(88, 230, 120, 268)],
        y=-1.0, mouth=False)
    rope = K.colour((0.35, 0.2, 0.08), vary=0.1)
    for dx, dy in ((-11, 0.0), (11, 0.0), (0, -0.07), (0, 0.07)):
        K.tube([P.pt(104, 196, -1.0), P.pt(104 + dx, 233, -1.0 + dy)], 0.005, rope, segments=5, name="rope")
    K.tube([P.pt(104, 170, -1.0), P.pt(104, 196, -1.0)], 0.006, rope, segments=5, name="rope")
    K.leaves_only((62, 205, 142, 312))
    scatter_cards(K, (62, 205, 142, 312), 14, (35, 35), (-1.15, -0.85), yaw=80, pitch=30, name="fern")
    K.card_from_painting((62, 205, 142, 312), (P.x(102), -1.17, P.z(258.5)), name="fern_front")
    # the cot by the wall with its striped bolster
    cotw = K.tile((160, 385, 235, 397), vary=0.05)
    legm = K.projected(axis_x=P.x(144), squeeze=0.9, keep=[(136, 360, 153, 436)], inset=2)
    cy0, cy1 = -0.85, -0.15
    for lx in (144, 287):
        for ly in (cy0 + 0.04, cy1 - 0.04):
            K.lathe([(P.m(r), P.z(y)) for r, y in ((5, 437), (6, 425), (7.5, 410), (6, 398), (7, 385), (5, 372),
                                                   (6, 365), (4, 360))], legm, segments=10,
                    centre=(P.x(lx), ly, 0.0), name="cot_leg")
    K.box(P.x(148), P.x(284), cy0, cy1, P.z(396), P.z(380), cotw, bevel=0.01, name="cot_frame")
    weave = K.colour((175, 378, 230, 383), vary=0.15, scale=60)
    K.box(P.x(150), P.x(282), cy0 + 0.03, cy1 - 0.03, P.z(381), P.z(378), weave, name="cot_weave")
    bolster = K.projected(axis_x=P.x(208), squeeze=1.0, keep=[(168, 355, 248, 380)], inset=2)
    K.tube([P.pt(x, 368, -0.6) for x in (170, 190, 208, 226, 246)], [P.m(7), P.m(11), P.m(12), P.m(11), P.m(7)],
           bolster, segments=14, name="bolster")
    # the pot on the floor, behind the left pillar
    pot(K, 88, [(17, 433), (24, 428), (29, 418), (31.5, 400), (30, 388), (25, 376), (15, 368), (13, 364), (16, 360),
                (15, 358)], keep=[(56, 356, 122, 436)], exclude=[(20, 405, 62, 440)], y=-0.75)
    # side windows and the back
    for side in (-1, 1):
        side_window(K, body, side, depth * 0.5, P.z(322), P.z(232), 0.7, frame, iron, dark)
    back_decal(K, (293, 196, 423, 428), depth)
    back_decal(K, (130, 232, 238, 322), depth, x_shift=P.m(-40), name="back_window")
    # bushes at the plinth's ends
    K.leaves_only((0, 395, 20, 506))
    scatter_cards(K, (0, 395, 20, 506), 6, (25, 35), (-1.6, -0.2), yaw=70, name="bush_l")
    K.leaves_only((526, 410, 546, 506))
    scatter_cards(K, (526, 410, 546, 506), 6, (25, 35), (-1.6, -0.2), yaw=70, name="bush_r")


def leaf_pixels(rgb):
    """Leaves of a thoranam or a bush: green, yellow and orange (not red laterite, brown wood or plaster)."""
    from kitlib import plant_pixels
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    warm = (g > 110) & (b < 0.62 * g) & (r - g < 120)
    return plant_pixels(rgb) | warm


@model("doorway_garland", "lane", kind="building", atlas=2048)
def doorway_garland(K):
    """A doorway of red laterite: two pillars and a heavy lintel slab with yellow corner blocks, a wooden frame and a
    double plank door with its bar and ring, a thoranam of mango leaves on two strings, a laterite threshold and step
    with a kolam, grass at its feet."""
    P = K.paint
    d = 0.9                                                       # the doorway's depth through the wall
    lat = K.tile((50, 140, 80, 260), size=0.3, vary=0.06, soften=0.25)   # laterite with its pits and lime splashes
    lat2 = K.tile((285, 120, 310, 280), size=0.3, vary=0.06, soften=0.25)
    slab = K.tile((90, 14, 150, 42), size=0.5, vary=0.05, soften=0.2)
    wood = K.tile((120, 120, 170, 190), vary=0.05)
    frame_w = K.colour((86, 120, 100, 300), vary=0.08)
    ochre = K.colour((50, 45, 70, 72), vary=0.08)
    step = K.tile((40, 372, 80, 395), vary=0.05, soften=0.2)
    # the pillars and the lintel
    K.box(P.x(47), P.x(82), 0.0, d, P.z(366), P.z(40), lat, bevel=0.01, name="pillar_l")
    K.box(P.x(280), P.x(311), 0.0, d, P.z(366), P.z(40), lat2, bevel=0.01, name="pillar_r")
    K.box(P.x(28), P.x(330), -0.12, d + 0.12, P.z(42), P.z(8), slab, bevel=0.02, name="lintel")
    K.box(P.x(82), P.x(280), 0.0, d, P.z(56), P.z(42), lat, name="head_wall")
    for x0, x1 in ((45, 74), (283, 312)):
        for y0, y1 in ((-0.08, 0.16), (d - 0.16, d + 0.08)):
            K.box(P.x(x0), P.x(x1), y0, y1, P.z(77), P.z(42), ochre, bevel=0.01, name="corner_block")
    # the wooden frame, set back, and the door set back again in it
    fy = 0.08
    for x0, x1 in ((82, 106), (251, 280)):
        K.box(P.x(x0), P.x(x1), fy, d - 0.1, P.z(363), P.z(56), frame_w, bevel=0.006, name="jamb")
    K.box(P.x(82), P.x(280), fy, d - 0.1, P.z(70), P.z(56), frame_w, bevel=0.006, name="frame_head")
    door = K.box(P.x(106), P.x(251), 0.2, 0.26, P.z(363), P.z(70), wood, name="door")
    # the door's back: planks with three battens and a bar
    bat = K.colour((0.17, 0.07, 0.025), vary=0.1)
    for py in (110, 215, 320):
        K.box(P.x(110), P.x(247), 0.26, 0.3, P.z(py + 12), P.z(py), bat, bevel=0.005, name="batten")
    iron = K.colour((0.06, 0.035, 0.02), vary=0.05)
    K.tube([P.pt(158, 207, 0.32), P.pt(205, 207, 0.32)], 0.012, iron, segments=6, name="back_bar")
    K.tube([P.pt(160, 207, 0.195), P.pt(205, 207, 0.195)], 0.009, iron, segments=6, name="bar")
    # threshold platform and the step before it
    K.box(P.x(35), P.x(322), -0.35, d + 0.1, 0.0, P.z(366), step, bevel=0.012, name="platform")
    K.box(P.x(82), P.x(278), -0.68, -0.35, 0.0, P.z(394), step, bevel=0.012, name="step")
    # the thoranam: two strings sagging between the corner blocks, mango leaves hanging off them
    rope = K.colour((0.55, 0.36, 0.06), vary=0.1)
    for pts in (((75, 45), (130, 56), (180, 62), (230, 56), (285, 45)), ((78, 54), (130, 76), (180, 84), (230, 76),
                                                                           (282, 54))):
        K.tube([P.pt(x, y, -0.04) for x, y in pts], 0.008, rope, segments=6, name="string")
    K.leaves_only((70, 44, 292, 140), leaf_pixels)
    K.card_from_painting((70, 44, 292, 140), (P.x(181), -0.06, P.z(92)), name="thoranam")
    for cx in (95, 135, 160, 180, 210, 225, 245, 270):
        K.card_from_painting((cx - 25, 60, cx + 25, 138), (P.x(cx), -0.06 + K.rng.uniform(-0.04, 0.03), P.z(99)),
                             yaw=K.rng.uniform(-40, 40), pitch=K.rng.uniform(-10, 10), name="leaf")
    # grass at its feet
    K.leaves_only((0, 335, 75, 437))
    K.leaves_only((275, 335, 353, 437))
    for box in ((0, 335, 75, 437), (275, 335, 353, 437)):
        cx = (box[0] + box[2]) / 2
        for yaw in (0, 55, -55):
            K.card_from_painting(box, (P.x(cx), K.rng.uniform(-0.5, -0.05), P.z(386)), yaw=yaw, name="grass")
        for i in range(3):
            K.card_from_painting(box, (P.x(cx) + K.rng.uniform(-0.05, 0.05), K.rng.uniform(0.2, 0.9), P.z(386)),
                                 yaw=K.rng.uniform(-80, 80), name="grass_side")


def hip_tin_roof(K, eave, ridge, ze, zr, mat, pitch=0.08, amp=0.018, cap=None, name="tin"):
    """A hipped roof of corrugated tin: eave = (x0, x1, y0, y1) m at height ze, the ridge (x0, x1) m at height zr
    over the middle; four slopes whose corrugations run down the fall, hip caps on the four hip lines and a ridge
    cap (mat `cap`)."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    ym = (ey0 + ey1) / 2
    parts = []

    def slope(front):
        def f(u, v):
            xa, xb = ex0 + (rx0 - ex0) * v, ex1 + (rx1 - ex1) * v
            x = xa + (xb - xa) * u
            y0 = ey0 if front else ey1
            y = y0 + (ym - y0) * v
            z = ze + (zr - ze) * v + amp * math.sin(2 * math.pi * (x - ex0) / pitch)
            return (x, y, z)
        n = int((ex1 - ex0) / pitch * (4 if front else 3))
        return K.sheet(f, n, 6, mat, name=name + ("_front" if front else "_back"), smooth=False, thickness=0.01)

    def hip(left):
        def f(u, v):
            ya, yb = ey0 + (ym - ey0) * v, ey1 + (ym - ey1) * v
            y = ya + (yb - ya) * u
            x0 = ex0 if left else ex1
            r = rx0 if left else rx1
            x = x0 + (r - x0) * v
            z = ze + (zr - ze) * v + amp * math.sin(2 * math.pi * (y - ey0) / pitch)
            return (x, y, z)
        n = int((ey1 - ey0) / pitch * 3)
        return K.sheet(f, n, 4, mat, name=name + "_hip", smooth=False, thickness=0.01)
    parts += [slope(True), slope(False), hip(True), hip(False)]
    cap = cap or mat
    for (xa, ya), xr in (((ex0, ey0), rx0), ((ex0, ey1), rx0), ((ex1, ey0), rx1), ((ex1, ey1), rx1)):
        K.tube([(xa, ya, ze + 0.02), (xr, ym, zr + 0.02)], 0.035, cap, segments=6, name="hip_cap")
    K.tube([(rx0, ym, zr + 0.02), (rx1, ym, zr + 0.02)], 0.05, cap, segments=8, name="ridge_cap")
    return parts


def slope_y(y_eave, y_ridge, z_eave, z_ridge, z):
    """Where a straight roof slope from (y_eave, z_eave) to (y_ridge, z_ridge) is at height z."""
    return y_eave + (z - z_eave) / (z_ridge - z_eave) * (y_ridge - y_eave)


def tyre(K, cx_px, cy_px, r_px, tube_px, y, tilt, mat, segments=28, name="tyre"):
    """An old tyre: a torus (a tube bent round in a ring) lying on a surface tilted `tilt` degrees towards the camera,
    centred where it is painted."""
    P = K.paint
    R, r = P.m(r_px), P.m(tube_px)
    t = math.radians(tilt)
    cx, cz = P.x(cx_px), P.z(cy_px)
    pts = []
    for i in range(segments + 1):
        a = 2 * math.pi * i / segments
        lx, ly = R * math.cos(a), R * math.sin(a)
        pts.append((cx + lx, y + ly * math.cos(t), cz + ly * math.sin(t)))
    return K.tube(pts, r, mat, segments=12, name=name, cap=False)


@model("house_mud_tin", "lane", kind="building", atlas=2048)
def house_mud_tin(K):
    """A mud-walled house under a hipped roof of rusting corrugated tin held down with stones and an old tyre: a blue
    plank door, a window with its plank flap propped open on a stick, a lime-washed skirting, an earth plinth."""
    P = K.paint
    depth = 4.0
    K.front_min = 0.1                                    # the front slope of the roof faces the camera at a slant
    mud = K.tile((180, 520, 520, 960), size=1.2, vary=0.05, soften=0.5)
    tin = K.tile((380, 110, 560, 240), size=0.6, vary=0.05, soften=0.25)
    lime = K.tile((200, 1012, 520, 1085), size=0.8, vary=0.04, soften=0.4)
    earth = K.tile((200, 1100, 520, 1140), size=0.8, vary=0.06)
    blue = K.tile((600, 520, 820, 980), size=0.7, vary=0.04)
    frame = K.colour((560, 600, 585, 900), vary=0.06)
    plank = K.tile((1040, 560, 1150, 640), vary=0.05)
    dark = K.colour((0.04, 0.025, 0.025), vary=0.0)
    X0, X1 = P.x(122), P.x(1312)
    ze, zr = P.z(368), P.z(36)
    body = K.box(X0, X1, 0.0, depth, 0.0, ze + 0.05, mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, depth + 0.015, P.z(1095), P.z(1000), lime, name="skirting")
    K.box(P.x(85), P.x(1350), -0.15, depth + 0.15, 0.0, P.z(1095), earth, bevel=0.03, name="plinth")
    # the roof: hipped tin with an overhang all round, its eave over the wall's shadow band
    ov = 0.38
    hip_tin_roof(K, (P.x(8), P.x(1425), -ov, depth + ov), (P.x(200), P.x(1235)), ze, zr, tin,
                 cap=K.colour((300, 26, 900, 44), vary=0.06))
    # rafters under the overhang, front and back
    timber = K.colour((0.16, 0.08, 0.04), vary=0.1)
    for x in np.linspace(X0 + 0.2, X1 - 0.2, 7):
        for y0, y1 in ((-ov + 0.05, 0.0), (depth, depth + ov - 0.05)):
            K.box(x - 0.03, x + 0.03, y0, y1, ze - 0.06, ze - 0.01, timber, name="rafter")
    # stones weighting the tin, and the tyre
    stone = K.projected(squeeze=1.0, keep=[(298, 52, 382, 98), (556, 40, 648, 80), (856, 42, 915, 78),
                                           (128, 260, 268, 333), (916, 252, 1012, 303), (1248, 282, 1338, 328),
                                           (952, 5, 1012, 32)], inset=2)
    ys = lambda z: slope_y(-ov, depth / 2, ze, zr, z)
    tilt = math.degrees(math.atan2(zr - ze, depth / 2 + ov))
    lift = 1.0 / math.sin(math.radians(tilt))        # at a fixed height, how far forward a thing must sit per m off the tin
    for px, py, w, h in ((340, 76, 82, 40), (602, 60, 90, 38), (885, 60, 58, 32), (198, 298, 138, 70),
                         (964, 280, 94, 48), (1293, 306, 88, 44), (982, 20, 58, 26), (285, 90, 22, 12),
                         (270, 320, 30, 14)):
        z = P.z(py)
        hh = P.m(h) * 0.35
        K.boulder(P.x(px), ys(z) - hh * lift * 0.8, z, P.m(w), P.m(w) * 0.7, P.m(h) * 1.05, stone, name="stone")
    tyre_m = K.projected(axis_x=P.x(1107), squeeze=0.95, keep=[(990, 176, 1224, 313)], inset=2)
    tyre(K, 1107, 244, 88, 28, ys(P.z(244)) - P.m(28) * lift, tilt, tyre_m)
    # the door: a plank door recessed in its frame
    K.cut(body, P.x(588), P.x(830), -0.05, 0.22, P.z(1080), P.z(475))
    K.box(P.x(588), P.x(830), 0.1, 0.15, P.z(1080), P.z(475), blue, name="door")
    for x0, x1 in ((553, 590), (828, 866)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.1, P.z(1085), P.z(442), frame, bevel=0.008, name="jamb")
    K.box(P.x(553), P.x(866), -0.03, 0.1, P.z(476), P.z(442), frame, bevel=0.008, name="frame_head")
    # the window: a dark opening in a plank frame, its flap hinged at the top and propped out on a stick
    K.cut(body, P.x(1000), P.x(1170), -0.05, 0.25, P.z(716), P.z(526))
    K.box(P.x(1000), P.x(1170), 0.2, 0.23, P.z(716), P.z(526), dark, name="window_back")
    for a, b, c, d in ((983, 1000, 511, 724), (1162, 1185, 511, 724), (983, 1185, 511, 526), (983, 1185, 712, 724)):
        K.box(P.x(a), P.x(b), -0.03, 0.06, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    fy = -0.42
    corners = [(P.x(1000), -0.03, P.z(526)), (P.x(1178), -0.03, P.z(526)), (P.x(1225), fy, P.z(664)),
               (P.x(1040), fy, P.z(667))]
    def flap(u, v):
        a = [corners[0][k] + (corners[1][k] - corners[0][k]) * u for k in range(3)]
        b = [corners[3][k] + (corners[2][k] - corners[3][k]) * u for k in range(3)]
        return tuple(a[k] + (b[k] - a[k]) * v for k in range(3))
    K.sheet(flap, 4, 4, plank, name="flap", smooth=False, thickness=0.03)
    K.tube([P.pt(1057, 791, -0.02), P.pt(1135, 645, fy * 0.95)], 0.013, frame, segments=6, name="stick")
    # the side walls: a window each side with its plank flap shut; the back: the door again
    for side in (-1, 1):
        xw = X1 if side > 0 else X0
        yc = depth * 0.55
        K.cut(body, xw - 0.25, xw + 0.25, yc - 0.3, yc + 0.3, P.z(716), P.z(526))
        K.box(min(xw, xw - side * 0.06), max(xw, xw - side * 0.06), yc - 0.3, yc + 0.3, P.z(716), P.z(526), plank,
              name="side_flap")
        for a0, a1, z0, z1 in ((-0.36, -0.3, 724, 511), (0.3, 0.36, 724, 511), (-0.36, 0.36, 526, 511),
                               (-0.36, 0.36, 724, 712)):
            K.box(min(xw, xw + side * 0.02), max(xw, xw + side * 0.02), yc + a0, yc + a1, P.z(z0), P.z(z1), frame,
                  bevel=0.004, name="side_window_frame")
        for zz in (560, 640):
            K.box(min(xw, xw + side * 0.015), max(xw, xw + side * 0.015), yc - 0.28, yc + 0.28, P.z(zz + 8), P.z(zz),
                  frame, name="flap_batten")
    back_decal(K, (553, 442, 866, 1085), depth)


def tin_panel(K, plane, a0, a1, z0, z1, mat, pitch=0.1, amp=0.015, name="tin_panel", wave_top=0.0):
    """A corrugated tin sheet nailed on a wall, its corrugations running up and down: plane ('y', y, side) for a
    front/back wall (spanning x a0..a1) or ('x', x, side) for a side wall (spanning y a0..a1); side -1/+1 is which
    way it faces. wave_top lets its top edge sag a little (an old sheet)."""
    kind, c, side = plane

    def f(u, v):
        a = a0 + (a1 - a0) * u
        z = z0 + (z1 - z0) * v - wave_top * math.sin(math.pi * u) * v
        off = c + side * (0.012 + amp * (1 + math.sin(2 * math.pi * (a - a0) / pitch)))
        return (a, off, z) if kind == "y" else (off, a, z)
    n = max(4, int(abs(a1 - a0) / pitch * 4))
    return K.sheet(f, n, 2, mat, name=name, smooth=False, thickness=0.006)


def plank_panel(K, plane, a0, a1, z0, z1, mat, name="planks", out=0.02):
    """A patch of boards nailed over a wall: a slab `out` m proud of the plane ('x'|'y', coordinate, side)."""
    kind, c, side = plane
    o0, o1 = sorted((c, c + side * out))
    if kind == "y":
        return K.box(a0, a1, o0, o1, z0, z1, mat, bevel=0.004, name=name)
    return K.box(o0, o1, a0, a1, z0, z1, mat, bevel=0.004, name=name)


def hip_tin_courses(K, eave, ridge, ze, zr, mats, split=0.5, pitch=0.12, amp=0.024, lap=0.035, name="tin"):
    """A hipped tin roof laid in two courses of sheets (the lower one from the eave, the upper one lapping over it
    from `split` of the way up), each course a run of sheets of different tins (mats, cycled): front and back
    slopes, two hip ends, caps on the hips and ridge."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    ym = (ey0 + ey1) / 2

    def course(front, v0, v1, lift, x_cuts, mat, k):
        def f(u, v):
            vv = v0 + (v1 - v0) * v
            xa, xb = ex0 + (rx0 - ex0) * vv, ex1 + (rx1 - ex1) * vv
            ua, ub = x_cuts
            x = xa + (xb - xa) * (ua + (ub - ua) * u)
            y0 = ey0 if front else ey1
            y = y0 + (ym - y0) * vv
            z = ze + (zr - ze) * vv + lift + amp * math.sin(2 * math.pi * (x - ex0) / pitch) + 0.004 * k
            return (x, y - (lift if front else -lift) * 0.3, z)
        n = max(4, int((ex1 - ex0) * (x_cuts[1] - x_cuts[0]) / pitch * 4))
        return K.sheet(f, n, 3, mat, name=name, smooth=False, thickness=0.008)
    cuts = [0.0, 0.23, 0.45, 0.62, 0.8, 1.0]
    for front in (True, False):
        for row, (v0, v1, lift) in enumerate(((0.0, split + 0.06, 0.0), (split, 1.0, lap))):
            off = 1 if row else 0
            for k in range(len(cuts) - 1):
                course(front, v0, v1, lift, (cuts[k], cuts[k + 1]), mats[(k + off + (0 if front else 2)) % len(mats)], k)

    def hip(left):
        def f(u, v):
            ya, yb = ey0 + (ym - ey0) * v, ey1 + (ym - ey1) * v
            y = ya + (yb - ya) * u
            x0 = ex0 if left else ex1
            r = rx0 if left else rx1
            z = ze + (zr - ze) * v + amp * math.sin(2 * math.pi * (y - ey0) / pitch)
            return (x0 + (r - x0) * v, y, z)
        return K.sheet(f, int((ey1 - ey0) / pitch * 3), 3, mats[0 if left else 1], name=name + "_hip", smooth=False,
                       thickness=0.008)
    hip(True)
    hip(False)
    cap = mats[0]
    for (xa, ya), xr in (((ex0, ey0), rx0), ((ex0, ey1), rx0), ((ex1, ey0), rx1), ((ex1, ey1), rx1)):
        K.tube([(xa, ya, ze + 0.03), (xr, ym, zr + 0.05)], 0.035, cap, segments=6, name="hip_cap")


@model("house_plank_sheet", "lane", kind="building", atlas=2048)
def house_plank_sheet(K):
    """A shack of old planks and patched corrugated tin under a hipped roof of mismatched tin sheets in two courses: a
    doorway hung with a saree for a curtain, a window with three pots of chillies on its sill, corner posts, a
    plastic basin by the door."""
    P = K.paint
    D = 3.4
    K.front_min = 0.05
    orange = K.tile((110, 290, 370, 640), size=0.9, vary=0.04)
    grey = K.tile((110, 670, 370, 990), size=0.9, vary=0.04)
    blue = K.tile((770, 290, 950, 990), size=0.6, vary=0.04)
    rust = K.tile((1262, 700, 1428, 990), size=0.6, vary=0.04)
    brown = K.tile((965, 755, 1240, 990), size=0.9, vary=0.04)
    post = K.colour((84, 300, 100, 600), vary=0.08)
    frame = K.colour((380, 500, 405, 900), vary=0.08)
    dark = K.colour((0.035, 0.025, 0.03), vary=0.0)
    earth = K.colour((300, 1004, 800, 1022), vary=0.12, scale=10)
    roof_mats = [K.tile((470, 60, 640, 150), size=0.7, vary=0.04), K.tile((110, 60, 300, 140), size=0.7, vary=0.04),
                 K.tile((900, 175, 1080, 250), size=0.7, vary=0.04), K.tile((1150, 60, 1380, 130), size=0.7, vary=0.04),
                 K.tile((60, 165, 280, 250), size=0.7, vary=0.04)]
    X0, X1 = P.x(84), P.x(1448)
    ze, zr = P.z(268), P.z(32)
    zg = P.z(1002)
    body = K.box(X0 + 0.02, X1 - 0.02, 0.02, D - 0.02, 0.0, ze + 0.04, orange, name="walls")
    K.box(P.x(78), P.x(1455), -0.12, D + 0.12, 0.0, zg, earth, bevel=0.02, name="floor_slab")
    # corner posts
    for x in (X0 + 0.04, X1 - 0.04):
        for y in (0.04, D - 0.04):
            K.box(x - 0.045, x + 0.045, y - 0.045, y + 0.045, 0.0, ze + 0.02, post, bevel=0.008, name="post")
    # the front's patches stand proud of the frame where they are painted (the painting lands on them)
    plank_panel(K, ("y", 0.0, -1), P.x(762), P.x(955), zg, ze, blue, name="front_tin")
    plank_panel(K, ("y", 0.0, -1), P.x(1300), P.x(1432), P.z(632), P.z(400), grey, name="torn_sheet", out=0.03)
    # the side walls and the back: the same planks and tin, patched
    for side, x in ((-1, X0), (1, X1)):
        segs = ((0.0, 1.2, orange if side < 0 else blue), (1.2, 2.3, grey if side < 0 else brown), (2.3, D, rust))
        for a0, a1, m in segs:
            if m in (grey, blue):
                tin_panel(K, ("x", x, side), a0 + 0.05, a1, zg, ze, m, wave_top=0.03)
            else:
                plank_panel(K, ("x", x, side), a0 + 0.05, a1, zg, ze, m)
    for a0, a1, m in ((X0, X0 + 1.1, grey), (X0 + 1.1, X0 + 2.5, brown), (X0 + 2.5, X1, rust)):
        if m is grey:
            tin_panel(K, ("y", D, 1), a0 + 0.05, a1, zg, ze, m, wave_top=0.04)
        else:
            plank_panel(K, ("y", D, 1), a0 + 0.05, a1, zg, ze, m)
    # a side window on the right (boarded), a back door
    for a, b, c, d in ((1.45, 2.15, P.z(720), P.z(700)), (1.45, 2.15, P.z(420), P.z(400)), (1.45, 1.5, P.z(720), P.z(400)),
                       (2.1, 2.15, P.z(720), P.z(400))):
        K.box(X1 + 0.02, X1 + 0.06, a, b, c, d, frame, bevel=0.004, name="side_window_frame")
    K.box(X1 + 0.015, X1 + 0.03, 1.5, 2.1, P.z(700), P.z(420), dark, name="side_window")
    for a0, a1 in ((X0 + 1.45, X0 + 1.5), (X0 + 2.25, X0 + 2.3)):
        K.box(a0, a1, D + 0.02, D + 0.07, zg, P.z(380), frame, bevel=0.004, name="back_door_frame")
    K.box(X0 + 1.45, X0 + 2.3, D + 0.02, D + 0.07, P.z(380), P.z(350), frame, bevel=0.004, name="back_door_frame")
    K.box(X0 + 1.5, X0 + 2.25, D + 0.02, D + 0.045, zg, P.z(380), brown, name="back_door")
    # the roof
    hip_tin_courses(K, (P.x(20), P.x(1530), -0.3, D + 0.3), (P.x(102), P.x(1445)), ze, zr, roof_mats)
    K.box(P.x(100), P.x(1447), D / 2 - 0.12, D / 2 + 0.12, zr, zr + 0.09, roof_mats[2], bevel=0.01, name="ridge_board")
    # the doorway: frame, a dark room, the saree on its rod
    K.cut(body, P.x(410), P.x(727), -0.05, 0.7, zg, P.z(380))
    K.box(P.x(410), P.x(727), 0.65, 0.7, zg, P.z(380), dark, name="room")
    for x0, x1 in ((372, 410), (727, 762)):
        K.box(P.x(x0), P.x(x1), -0.04, 0.08, zg, P.z(345), frame, bevel=0.006, name="door_post")
    K.box(P.x(372), P.x(762), -0.04, 0.08, P.z(380), P.z(345), frame, bevel=0.006, name="door_head")
    K.box(P.x(372), P.x(762), -0.06, 0.02, P.z(345), P.z(290), K.tile((400, 295, 740, 340)), bevel=0.006, name="lintel")
    cloth = K.projected(axis_x=P.x(600), squeeze=1.0, keep=[(505, 395, 735, 975), (430, 385, 735, 520)], inset=3)
    def xl(py):
        pts = ((382, 425), (520, 450), (650, 485), (800, 510), (975, 510))
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= py <= b:
                return xa + (xb - xa) * (py - a) / (b - a)
        return 510
    def curtain(u, v):
        py = 382 + (975 - 382) * v
        x0 = xl(py)
        px = x0 + (735 - x0) * u
        fold = 0.035 * math.sin(u * math.pi * 7 + v * 1.5) * (0.3 + 0.7 * v)
        return (P.x(px), 0.1 + fold, P.z(py))
    K.sheet(curtain, 28, 20, cloth, name="saree", thickness=0.006)
    K.tube([P.pt(412, 384, 0.08), P.pt(725, 384, 0.08)], 0.012, frame, segments=6, name="rod")
    # the window: frame, mullion, dark panes, its sill with three pots of chillies
    K.cut(body, P.x(983), P.x(1227), -0.05, 0.35, P.z(717), P.z(427))
    K.box(P.x(983), P.x(1227), 0.3, 0.33, P.z(717), P.z(427), dark, name="window_back")
    wf = K.colour((960, 400, 1250, 425), vary=0.08)
    for a, b, c, d in ((953, 983, 393, 720), (1227, 1257, 393, 720), (983, 1227, 393, 427), (1093, 1120, 427, 717)):
        K.box(P.x(a), P.x(b), -0.04, 0.06, P.z(d), P.z(c), wf, bevel=0.006, name="window_frame")
    K.box(P.x(937), P.x(1277), -0.2, 0.04, P.z(747), P.z(720), wf, bevel=0.008, name="sill")
    for cx, x0, x1, top, r_top, r_bot in ((1017, 977, 1057, 660, 40, 26), (1107, 1072, 1143, 677, 35, 24),
                                          (1196, 1157, 1235, 660, 39, 26)):
        pot(K, cx, [(r_bot, 720), (r_top * 0.85, 690), (r_top, 668), (r_top, top)], keep=[(x0, top - 2, x1, 721)],
            y=-0.09, mouth=False, segments=20)
    K.leaves_only((925, 500, 1280, 690))
    for cx, cy in ((1015, 600), (1105, 640), (1195, 590)):
        for yaw in (0, 60, -60):
            K.card_from_painting((cx - 80, cy - 100, cx + 80, cy + 85), (P.x(cx), -0.09 + K.rng.uniform(-0.03, 0.03),
                                 P.z(cy - 7)), yaw=yaw + K.rng.uniform(-10, 10), name="chilli")
    # the plastic basin by the door
    basin = K.projected(axis_x=P.x(902), squeeze=0.95, keep=[(820, 986, 984, 1036)], inset=2)
    K.lathe([(P.m(66), 0.0), (P.m(72), P.m(15)), (P.m(80), P.m(44)), (P.m(82), P.m(48)), (P.m(76), P.m(46))], basin,
            segments=28, centre=(P.x(902), -0.45, 0.0), name="basin")
    K.lathe([(P.m(74), P.m(44)), (P.m(60), P.m(20)), (0.0, P.m(16))], K.colour((0.05, 0.25, 0.25), vary=0.05),
            segments=28, centre=(P.x(902), -0.45, 0.0), name="basin_water", cap=False)


def straw_pixels(rgb):
    """Straw and dry palm leaf (tan, ochre, olive), not the shadowed mud wall behind a thatch's fringe."""
    from kitlib import plant_pixels
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    straw = (r > 120) & (g > 0.6 * r) & (g > 90)
    dark = np.maximum(np.maximum(r, g), b) < 70
    keep = straw | plant_pixels(rgb)
    return keep | (dark & ndimage.binary_dilation(keep, iterations=2))


def hip_thatch(K, eave, ridge, ze, zr, mat, thickness=0.22, shag=0.05, fringe=0.1, ends=True, name="thatch"):
    """A hipped thatch: eave = (x0, x1, y0, y1) m at height ze, ridge (x0, x1) m at height zr over the middle; front
    and back slopes and (ends=True) the two hip ends, each a thick lumpy straw mat whose lowest edge hangs as a
    ragged fringe `fringe` m deep."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    ym = (ey0 + ey1) / 2
    rng = K.rng
    nu, nv = 48, 14

    def lumps(n_u):
        noise = ndimage.gaussian_filter(rng.normal(0, 1, (nv + 1, n_u + 1)), 1.2)
        tips = ndimage.gaussian_filter(rng.normal(0, 1, n_u + 1), 0.7)
        return noise, tips

    def slope(front):
        noise, tips = lumps(nu)
        def f(u, v):
            xa, xb = ex0 + (rx0 - ex0) * v, ex1 + (rx1 - ex1) * v
            x = xa + (xb - xa) * u
            y0 = ey0 if front else ey1
            y = y0 + (ym - y0) * v
            iu, iv = int(round(u * nu)), int(round(v * nv))
            z = ze + (zr - ze) * v + shag * noise[iv, iu]
            if v < 0.09:
                z -= fringe * (0.6 + 0.8 * abs(tips[iu]))
            return (x, y, z)
        return K.sheet(f, nu, nv, mat, name=name, smooth=True, thickness=thickness)

    def end(left):
        n_u = 24
        noise, tips = lumps(n_u)
        def f(u, v):
            ya, yb = ey0 + (ym - ey0) * v, ey1 + (ym - ey1) * v
            y = ya + (yb - ya) * u
            x0, r = (ex0, rx0) if left else (ex1, rx1)
            iu, iv = int(round(u * n_u)), int(round(v * nv))
            z = ze + (zr - ze) * v + shag * noise[iv, iu]
            if v < 0.09:
                z -= fringe * (0.6 + 0.8 * abs(tips[iu]))
            return (x0 + (r - x0) * v, y, z)
        return K.sheet(f, n_u, nv, mat, name=name + "_end", smooth=True, thickness=thickness)
    slope(True)
    slope(False)
    if ends:
        end(True)
        end(False)


def round_pot(K, cx_px, top_py, bot_py, r_px, y, mat, segments=20, name="pot", rim=0.64, open_mouth=True):
    """A round-bellied clay pot with a short neck and rolled rim, its outline fitted to the painted one (centre x,
    top and bottom py, belly radius px), standing at depth y."""
    P = K.paint
    h = bot_py - top_py
    prof = [(0.45, 0.0), (0.8, 0.08), (0.98, 0.3), (1.0, 0.45), (0.93, 0.65), (0.74, 0.82), (rim - 0.04, 0.9),
            (rim + 0.02, 0.95), (rim, 1.0)]
    pts = [(P.m(r_px * a), P.z(bot_py - h * b)) for a, b in prof]
    ob = K.lathe(pts, mat, segments=segments, centre=(P.x(cx_px), y, 0.0), wobble=0.015, name=name)
    if open_mouth:
        inside = K.colour((0.05, 0.03, 0.02), vary=0.1)
        K.lathe([(P.m(r_px * (rim - 0.06)), P.z(top_py) - 0.003), (P.m(r_px * 0.3), P.z(top_py) - 0.06),
                 (0.0, P.z(top_py) - 0.07)], inside, segments=segments, centre=(P.x(cx_px), y, 0.0), cap=False,
                name=name + "_mouth")
    return ob


def halo_exclude(K, boxes, cell=6, near=12, white=205):
    """The cut-out's white sticker halo (near-white pixels within `near` px of its transparent edge) inside the
    given boxes, kept off the model: excluded from the front projection in small cells, so the part's own material
    shows where the geometry reaches into it."""
    a = (K.paint.rgba * 255).astype(np.int32)
    op = a[..., 3] > 127
    halo = (a[..., :3].min(axis=2) > white) & op & ndimage.binary_dilation(~op, iterations=near)
    m = np.zeros_like(halo)
    for x0, y0, x1, y1 in boxes:
        m[int(y0):int(y1), int(x0):int(x1)] = True
    halo &= m
    h, w = halo.shape
    cells = halo[:h // cell * cell, :w // cell * cell].reshape(h // cell, cell, w // cell, cell).any(axis=(1, 3))
    for cy, cx in zip(*np.nonzero(cells)):
        K.front_exclude.append((cx * cell, cy * cell, (cx + 1) * cell, (cy + 1) * cell))


@model("house_potter", "lane", kind="building", atlas=2048)
def house_potter(K):
    """A potter's mud hut under a hipped thatch with palm fronds laid on it, a carved plank door and a shuttered
    window, a lime skirting; at its side a thatched lean-to on bamboo posts over the potter's wheel in its frame,
    stacks of red pots, a heap of clay and a painted pot; rows of grey pots drying along the front."""
    P = K.paint
    D = 4.5
    K.front_min = 0.15
    halo_exclude(K, [(300, 0, 1520, 540), (1430, 200, 2195, 1010)])
    # inside the wheel's frame the cut-out is painted solid white: not the frame's back rails
    K.front_exclude += [(1570, 822, 1672, 876), (1709, 822, 1814, 876), (1570, 924, 1673, 955), (1707, 924, 1814, 955)]
    mud = K.tile((480, 640, 660, 900), size=1.2, vary=0.05, soften=0.5)
    lime = K.tile((500, 930, 970, 980), size=1.0, vary=0.04, soften=0.4)
    thatch_m = K.tile((420, 250, 500, 440), size=0.6, vary=0.06, soften=0.3)   # clean golden straw, left of the fronds
    earth = K.tile((300, 1110, 1300, 1128), size=1.0, vary=0.08)
    wood = K.tile((1010, 660, 1220, 900), size=0.6, vary=0.04)
    frame = K.colour((985, 700, 1000, 1000), vary=0.06)
    dark = K.colour((0.05, 0.03, 0.025), vary=0.0)
    X0, X1 = P.x(467), P.x(1427)
    body = K.box(X0, X1, 0.0, D, 0.0, P.z(470), mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(921), lime, name="skirting")
    K.box(P.x(0), P.x(2190), -1.25, D + 0.4, 0.0, P.z(1108), earth, bevel=0.03, name="ground")
    # the hut's thatch, its ridge pole, palm fronds weighting it front (painted) and back (cards)
    hip_thatch(K, (P.x(334), P.x(1500), -0.55, D + 0.55), (P.x(506), P.x(1414)), P.z(474), P.z(40), thatch_m,
               thickness=0.25, shag=0.05, fringe=0.1)
    K.tube([P.pt(506, 28, D / 2), P.pt(1414, 28, D / 2)], P.m(17), K.colour((560, 15, 1300, 40), vary=0.06),
           segments=10, name="ridge_pole")
    K.leaves_only((440, 40, 1310, 470), olive_leaf_pixels)
    zr, ze = P.z(40), P.z(474)
    ang = math.degrees(math.atan2(zr - ze, D / 2 + 0.55))
    for i, (cx, cy) in enumerate(((640, 250), (860, 260), (1040, 240), (1180, 230))):
        u = 0.35 + 0.2 * (i % 2)
        z = ze + (zr - ze) * u
        y = D + 0.55 - (D / 2 + 0.55) * u + 0.14
        K.card_from_painting((cx - 130, cy - 200, cx + 130, cy + 200), (P.x(cx) + K.rng.uniform(-0.3, 0.3), y, z),
                             yaw=180, pitch=-(90 - ang) * 0.95, name="frond_back")
    # straw fringe cards round the sides and back, cut from the painted fringe
    K.leaves_only((560, 400, 1300, 520), straw_pixels)
    for i in range(16):
        side = i % 4
        cx = K.rng.uniform(600, 1260)
        box = (cx - 60, 410, cx + 60, 518)
        if side == 0:
            pos, yaw = (K.rng.uniform(X0 + 0.3, X1 - 0.3), D + 0.58, P.z(464)), 180
        elif side == 1:
            pos, yaw = (K.rng.uniform(X0 + 0.3, X1 - 0.3), D + 0.58, P.z(464)), 180
        elif side == 2:
            pos, yaw = (P.x(334) - 0.02, K.rng.uniform(-0.3, D + 0.3), P.z(464)), 90
        else:
            pos, yaw = (P.x(1500) + 0.02, K.rng.uniform(1.0, D + 0.3), P.z(464)), -90
        K.card_from_painting(box, pos, yaw=yaw + K.rng.uniform(-8, 8), pitch=K.rng.uniform(-10, 10), name="fringe")
    # the door, the shuttered window
    K.cut(body, P.x(1003), P.x(1230), -0.05, 0.25, P.z(1071), P.z(647))
    K.box(P.x(1003), P.x(1230), 0.12, 0.17, P.z(1071), P.z(647), wood, name="door")
    for x0, x1 in ((981, 1003), (1230, 1251)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(1071), P.z(615), frame, bevel=0.008, name="jamb")
    K.box(P.x(981), P.x(1251), -0.03, 0.12, P.z(647), P.z(615), frame, bevel=0.008, name="frame_head")
    K.cut(body, P.x(699), P.x(797), -0.05, 0.12, P.z(771), P.z(638))
    K.box(P.x(699), P.x(797), 0.07, 0.1, P.z(771), P.z(638), wood, name="shutters")
    for a, b, c, d in ((681, 699, 621, 784), (797, 813, 621, 784), (699, 797, 621, 638), (699, 797, 771, 784)):
        K.box(P.x(a), P.x(b), -0.03, 0.07, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    back_decal(K, (981, 615, 1251, 1071), D)
    side_decal(K, (681, 621, 813, 784), X0, -1, D * 0.5, name="side_window")
    side_decal(K, (681, 621, 813, 784), X1, 1, D * 0.6, name="side_window")
    # the lean-to: a thatch slab falling away from the hut's side, its thick cut end at the front as painted
    # traced on the straw's own edge, inside the white halo the cut-out has round the shed
    top = [(1430, 225), (1480, 238), (1550, 258), (1600, 273), (1650, 288), (1700, 318), (1750, 343), (1800, 368),
           (1850, 386), (1900, 413), (1950, 433), (2000, 458), (2050, 483), (2100, 508), (2150, 560)]
    bottom = [(2140, 578), (2100, 587), (2050, 582), (2000, 572), (1950, 558), (1880, 557), (1850, 552),
              (1800, 527), (1750, 517), (1700, 507), (1650, 497), (1600, 478), (1550, 497), (1500, 487), (1430, 487)]
    lean = thatch_m
    yb = 3.0
    K.prism([(P.x(x), P.z(y)) for x, y in top + bottom], -0.5, -0.22, lean, name="lean_to_end")
    th = 0.24
    def lean_top(x):
        for (xa, za), (xb, zb) in zip(top, top[1:]):
            if xa <= x <= xb:
                return P.z(za + (zb - za) * (x - xa) / (xb - xa))
        return P.z(top[-1][1])
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (13, 31)), 1.0)
    def lean_surf(u, v):
        px = 1430 + (2130 - 1430) * u
        return (P.x(px), -0.22 + (yb + 0.22) * v, lean_top(px) - 0.06 + 0.02 * noise[int(v * 12), int(u * 30)])
    K.sheet(lean_surf, 30, 12, lean, name="lean_to", thickness=th)
    bamboo = K.projected(axis_x=P.x(2010), squeeze=0.9, keep=[(1985, 600, 2034, 1030)], inset=2)
    bamboo2 = K.projected(axis_x=P.x(1918), squeeze=0.9, keep=[(1903, 600, 1932, 965)], inset=2)
    for y in (-0.1, 0.9, 1.9, 2.8):
        K.tube([(P.x(1430), y, lean_top(1430) - th - 0.03), (P.x(2120), y, lean_top(2120) - th - 0.03)], 0.035, bamboo,
               segments=8, name="rafter")
    # posts: the two painted at the front (one behind the clay heap), two more at the back
    for x, y, top_py, m in ((2010, -0.3, 529, bamboo), (1918, 0.35, 560, bamboo2), (2010, yb - 0.25, 560, bamboo),
                            (1918, yb - 0.25, 560, bamboo2)):
        K.tube([P.pt(x, 1105, y), P.pt(x, top_py, y)], P.m(21 if x == 2010 else 15), m, segments=10, name="post")
    K.tube([P.pt(1891, 563, 0.35), P.pt(2042, 563, -0.3)], P.m(11), bamboo, segments=8, name="beam")
    K.tube([P.pt(1891, 575, yb - 0.25), P.pt(2042, 575, yb - 0.25)], P.m(11), bamboo, segments=8, name="beam")
    K.tube([P.pt(2010, 560, -0.3), P.pt(2010, 560, yb - 0.25)], P.m(11), bamboo, segments=8, name="plate")
    K.tube([P.pt(1972, 562, -0.25), P.pt(2008, 654, -0.28)], P.m(7), bamboo, segments=6, name="brace")
    # the potter's wheel: a frame of posts and rails, the stone flywheel, spindle, head and a lump of clay
    yw = 0.55
    tw = K.colour((1540, 820, 1565, 950), vary=0.08)
    for x0, x1 in ((1536, 1569), (1815, 1858)):
        for y in (yw - 0.6, yw + 0.6):
            K.box(P.x(x0), P.x(x1), y - 0.05, y + 0.05, P.z(1105), P.z(759), tw, bevel=0.006, name="frame_post")
    for y in (yw - 0.6, yw + 0.6):
        K.box(P.x(1526), P.x(1881), y - 0.045, y + 0.045, P.z(821), P.z(798), tw, bevel=0.006, name="rail")
        K.box(P.x(1536), P.x(1858), y - 0.04, y + 0.04, P.z(976), P.z(956), tw, bevel=0.006, name="rail_low")
    for x0, x1 in ((1536, 1569), (1815, 1858)):
        K.box(P.x(x0), P.x(x1), yw - 0.6, yw + 0.6, P.z(821), P.z(798), tw, bevel=0.006, name="rail_side")
    K.box(P.x(1600), P.x(1800), yw - 0.6, yw + 0.6, P.z(976), P.z(958), tw, bevel=0.006, name="cross_bar")
    stone = K.projected(axis_x=P.x(1699), squeeze=0.95, keep=[(1572, 876, 1826, 925)], inset=2)
    K.lathe([(P.m(128), P.z(923)), (P.m(130), P.z(905)), (P.m(126), P.z(880)), (P.m(40), P.z(877))], stone,
            segments=40, centre=(P.x(1699), yw, 0.0), name="flywheel")
    clay = K.projected(axis_x=P.x(1690), squeeze=0.95, keep=[(1640, 730, 1755, 890)], inset=2)
    K.lathe([(P.m(15), P.z(949)), (P.m(15), P.z(923))], tw, segments=12, centre=(P.x(1690), yw, 0.0), name="axle")
    K.lathe([(P.m(18), P.z(880)), (P.m(14), P.z(850)), (P.m(10), P.z(810)), (P.m(52), P.z(801)), (P.m(54), P.z(793)),
             (P.m(20), P.z(789))], clay, segments=24, centre=(P.x(1692), yw, 0.0), name="head")
    K.boulder(P.x(1697), yw, P.z(760), P.m(70), P.m(60), P.m(58), clay, name="clay_lump")
    K.box(P.x(1674), P.x(1730), yw - 0.08, yw + 0.08, P.z(1105), P.z(976), tw, name="foot")
    # rows of grey pots drying along the front: a back row against the wall, a front row before it
    grey = K.colour((60, 1000, 110, 1060), vary=0.1, scale=8)
    for cx, top_, bot, r in ((106, 967, 1077, 47), (238, 967, 1085, 45), (371, 967, 1085, 53), (476, 975, 1089, 47),
                             (595, 999, 1089, 45), (700, 1003, 1089, 43), (804, 1009, 1089, 38)):
        round_pot(K, cx, top_, bot, r, -0.32, grey, name="pot_back")
    for cx, top_, bot, r in ((72, 987, 1109, 65), (208, 987, 1109, 63), (342, 987, 1109, 63), (457, 1018, 1109, 47),
                             (561, 1024, 1109, 44), (663, 1030, 1109, 43), (787, 1030, 1105, 39),
                             (890, 1005, 1097, 41)):
        round_pot(K, cx, top_, bot, r, -0.82, grey, name="pot_front")
    # stacks of red pots by the wheel
    red = K.colour((1400, 1030, 1450, 1080), vary=0.1, scale=8)
    for cx, y, pots in ((1351, 0.0, ((936, 1010, 30), (1010, 1094, 32))),
                        (1421, -0.6, ((877, 945, 45), (940, 1020, 48), (1020, 1107, 52))),
                        (1528, -0.25, ((916, 1000, 48), (995, 1097, 50)))):
        for t, b, r in pots:
            round_pot(K, cx, t, b, r, y, red, name="red_pot", rim=0.8, open_mouth=t == pots[0][0])
    # the heap of clay and the painted pot
    heap = K.projected(squeeze=1.0, keep=[(1766, 972, 2049, 1100)], inset=2)
    for px, py, w, h in ((1830, 1060, 130, 80), (1920, 1040, 150, 110), (2000, 1065, 90, 70), (1880, 1085, 120, 40),
                         (1960, 1080, 110, 45)):
        K.boulder(P.x(px), -0.5 + K.rng.uniform(-0.15, 0.15), P.z(py), P.m(w), P.m(w) * 0.9, P.m(h), heap, name="clay")
    deco = K.projected(axis_x=P.x(2116), squeeze=0.93, keep=[(2045, 959, 2187, 1104)])
    K.lathe([(P.m(r), P.z(y)) for r, y in ((40, 1104), (58, 1095), (69, 1070), (71, 1045), (64, 1010), (48, 985),
                                           (40, 975), (46, 966), (44, 960))], deco, segments=28,
            centre=(P.x(2116), -0.55, 0.0), name="painted_pot")


def hip_front_y(eave, ridge, ze, zr, x, z):
    """How far back (y) the front of a hipped roof is at (x, z) as seen from the front: on the front slope, or, past
    its end at that height, on the hip line."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    ym = (ey0 + ey1) / 2
    v = min(1.0, max(0.0, (z - ze) / (zr - ze)))
    xa, xb = ex0 + (rx0 - ex0) * v, ex1 + (rx1 - ex1) * v
    if xa <= x <= xb:
        return ey0 + (ym - ey0) * v
    ve = (x - ex1) / (rx1 - ex1) if x > xb else (x - ex0) / (rx0 - ex0)
    ve = min(1.0, max(v, ve))
    return ey0 + (ym - ey0) * ve


def pumpkin(K, px, py, rx_px, ry_px, y, mat, stalk, ribs=8, name="pumpkin"):
    """A ribbed pumpkin where it is painted: a squashed sphere with `ribs` grooves, a stalk on top."""
    P = K.paint
    rx, ry = P.m(rx_px), P.m(ry_px)
    cx, cz = P.x(px), P.z(py)

    def f(u, v):
        a = 2 * math.pi * u
        t = math.pi * (v - 0.5)
        rib = 1 - 0.07 * abs(math.sin(ribs * a / 2)) ** 0.5
        r = rx * math.cos(t) * rib
        return (cx + r * math.cos(a), y + r * math.sin(a) * 0.95, cz + ry * math.sin(t) * (1 - 0.15 * (v > 0.85)))
    ob = K.sheet(f, 32, 12, mat, name=name, smooth=True)
    K.tube([(cx, y, cz + ry * 0.8), (cx + 0.02, y, cz + ry * 1.15)], 0.012, stalk, segments=6, name="pumpkin_stalk")
    return ob


def cover_cards(K, box, keep, step, size, place, thresh=0.2, jitter=0.25, name="leaf"):
    """Cards over every cell of a step-px grid inside box where the painting's plant (keep(rgb) -> bool) covers more
    than `thresh` of the cell, so from the front nothing of it is missing; place(cx, cy) -> (y, yaw, pitch) puts
    each one (on the roof, off its edge, on the wall)."""
    P = K.paint
    x0, y0, x1, y1 = [int(v) for v in box]
    rgb = (P.rgba[y0:y1, x0:x1, :3] * 255).astype(np.uint8)
    m = keep(rgb) & (P.rgba[y0:y1, x0:x1, 3] > 0.5)
    n = 0
    for cy in np.arange(y0 + step / 2, y1, step):
        for cx in np.arange(x0 + step / 2, x1, step):
            a, b = int(cy - y0 - step / 2), int(cx - x0 - step / 2)
            if m[max(0, a):a + step, max(0, b):b + step].mean() < thresh:
                continue
            jx, jy = K.rng.uniform(-jitter, jitter) * step, K.rng.uniform(-jitter, jitter) * step
            px, py = cx + jx, cy + jy
            y, yaw, pitch = place(px, py)
            K.card_from_painting((px - size / 2, py - size / 2, px + size / 2, py + size / 2), (P.x(px), y, P.z(py)),
                                 yaw=yaw, pitch=pitch, name=name)
            n += 1
    return n


def olive_leaf_pixels(rgb):
    """Leaves painted in olive and khaki greens (a gourd vine, palm fronds), which plant_pixels takes for straw: by
    hue (yellow-green and greener, saturated, not near-white), with the dark ink round them."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    span = np.maximum(1, mx - mn)
    hue = np.where(mx == r, 60.0 * (g - b) / span, np.where(mx == g, 120 + 60.0 * (b - r) / span, 240.0))
    leaf = (hue > 36) & (hue < 160) & ((mx - mn) > 35) & (mx < 240)
    leaf = ndimage.binary_opening(ndimage.binary_closing(leaf, iterations=2), iterations=1)
    return leaf | ((mx < 80) & ndimage.binary_dilation(leaf, iterations=3))


@model("house_thatched_hut", "lane", kind="building", atlas=2048)
def house_thatched_hut(K):
    """A mud hut under a deep hipped thatch with a ridge pole, a pumpkin vine climbing over its right side with five
    pumpkins, a plank door between painted kolam motifs, a shuttered window, a lime skirting, a painted pot."""
    P = K.paint
    D = 4.6
    K.front_min = 0.15
    halo_exclude(K, [(0, 0, 1522, 660), (1222, 600, 1460, 910)])
    mud = K.tile((200, 880, 560, 1020), size=1.2, vary=0.05, soften=0.45)
    lime = K.tile((180, 1040, 590, 1120), size=1.0, vary=0.04, soften=0.4)
    thatch_m = K.tile((180, 280, 420, 520), size=0.7, vary=0.06, soften=0.25)
    earth = K.tile((200, 1140, 1000, 1175), size=1.0, vary=0.08)
    wood = K.tile((660, 720, 860, 1060), size=0.6, vary=0.04)
    frame = K.colour((622, 700, 645, 1100), vary=0.06)
    X0, X1 = P.x(165), P.x(1353)
    body = K.box(X0, X1, 0.0, D, 0.0, P.z(605), mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(1032), lime, name="skirting")
    K.box(P.x(125), P.x(1396), -0.45, D + 0.25, 0.0, P.z(1132), earth, bevel=0.04, name="ground")
    eave = (P.x(15), P.x(1508), -0.62, D + 0.62)
    ridge = (P.x(305), P.x(1220))
    ze, zr = P.z(598), P.z(82)
    hip_thatch(K, eave, ridge, ze, zr, thatch_m, thickness=0.26, shag=0.05, fringe=0.11)
    K.tube([P.pt(305, 77, D / 2), P.pt(1220, 77, D / 2)], P.m(18), K.colour((500, 62, 1000, 90), vary=0.06),
           segments=10, name="ridge_pole")
    fy = lambda px, py: hip_front_y(eave, ridge, ze, zr, P.x(px), P.z(py))
    # the door between its kolam motifs, the shuttered window
    K.cut(body, P.x(650), P.x(874), -0.05, 0.25, P.z(1119), P.z(697))
    K.box(P.x(650), P.x(874), 0.12, 0.17, P.z(1119), P.z(697), wood, name="door")
    for x0, x1 in ((619, 650), (874, 908)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(1119), P.z(666), frame, bevel=0.008, name="jamb")
    K.box(P.x(619), P.x(908), -0.03, 0.12, P.z(697), P.z(666), frame, bevel=0.008, name="frame_head")
    K.cut(body, P.x(340), P.x(445), -0.05, 0.12, P.z(840), P.z(715))
    K.box(P.x(340), P.x(445), 0.07, 0.1, P.z(840), P.z(715), wood, name="shutters")
    for a, b, c, d in ((327, 340, 702, 852), (445, 458, 702, 852), (340, 445, 702, 715), (340, 445, 840, 852)):
        K.box(P.x(a), P.x(b), -0.03, 0.07, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    back_decal(K, (619, 666, 908, 1119), D)
    side_decal(K, (327, 702, 458, 852), X0, -1, D * 0.5, name="side_window")
    side_decal(K, (327, 702, 458, 852), X1, 1, D * 0.45, name="side_window")
    # the pot
    pot(K, 1130.5, [(40, 1150), (62, 1140), (78, 1115), (82, 1085), (76, 1055), (60, 1030), (44, 1018), (48, 1008),
                    (53, 995), (50, 991)], keep=[(1046, 988, 1215, 1152)], y=-0.3)
    # the pumpkins, lying on the thatch where they are painted (and one hanging over the wall)
    pk = K.projected(squeeze=1.0, keep=[(787, 190, 895, 270), (1180, 235, 1290, 305), (1003, 325, 1130, 435),
                                        (1300, 487, 1415, 572), (1130, 628, 1250, 710)], inset=3)
    stalk = K.colour((0.12, 0.16, 0.05), vary=0.1)
    for px, py, rx, ry in ((841, 230, 54, 40), (1235, 270, 55, 36), (1066, 380, 63, 52), (1357, 530, 57, 43)):
        pumpkin(K, px, py, rx, ry, fy(px, py + ry * 0.6) - P.m(rx) * 0.8, pk, stalk)
    pumpkin(K, 1190, 669, 60, 41, -0.2, pk, stalk)
    for px, py, rx, ry in ((1150, 300, 55, 40), (930, 210, 50, 38)):     # more on the back slope, mirrored
        pumpkin(K, px, py, rx, ry, D - fy(px, py + ry * 0.6) + P.m(rx) * 0.8, pk, stalk)
    # the vine: leaves cut from the painting (not the pumpkins), each laid just off the roof where it is painted,
    # down the wall below the eave, round the right corner, and over the ridge onto the back
    vine_keep = olive_leaf_pixels
    K.leaves_only((460, 10, 1455, 905), vine_keep)
    def place(cx, cy):
        v = min(1.0, max(0.0, (P.z(cy) - ze) / (zr - ze)))
        xa, xb = P.px(eave[0] + (ridge[0] - eave[0]) * v), P.px(eave[1] + (ridge[1] - eave[1]) * v)
        on_roof = cy < 600 and xa + 30 < cx < xb - 30
        if cy > 615:
            y = -0.1 if cx < 1353 else -0.05
        else:
            y = fy(cx, cy) - (0.06 if on_roof else 0.03)
        return y, K.rng.uniform(-30, 30), K.rng.uniform(-15, 15) - (35 if on_roof else 0)
    cover_cards(K, (460, 10, 1455, 905), vine_keep, 70, 110, place, name="vine")
    side_cards(K, (1222, 640, 1450, 880), 8, (100, 100), X1, 1, (0.1, 1.4))
    for i in range(10):
        cx, cy = K.rng.uniform(800, 1250), K.rng.uniform(40, 330)
        z = P.z(cy)
        yb = D + 0.62 - (fy(cx, cy) + 0.62) + 0.06
        K.card_from_painting((cx - 55, cy - 55, cx + 55, cy + 55), (P.x(cx), yb, z), yaw=180 + K.rng.uniform(-30, 30),
                             pitch=40 + K.rng.uniform(-20, 20), name="vine_back")
    for i in range(10):
        cx, cy = K.rng.uniform(900, 1300), K.rng.uniform(120, 560)
        v = (P.z(K.rng.uniform(250, 560)) - ze) / (zr - ze)
        xh = eave[1] + (ridge[1] - eave[1]) * v
        ya, yb2 = eave[2] + (D / 2 - eave[2]) * v, eave[3] + (D / 2 - eave[3]) * v
        K.card_from_painting((cx - 55, cy - 55, cx + 55, cy + 55), (xh + 0.06, K.rng.uniform(ya + 0.2, yb2 - 0.2),
                             ze + (zr - ze) * v), yaw=90 + K.rng.uniform(-30, 30), pitch=K.rng.uniform(-20, 20) + 35,
                             name="vine_hip")


def ribbon(K, top, bottom, width_px, y_top, y_bot, mat, sag=0.0, name="ribbon", n=10):
    """A band of cloth or yarn hanging from top (px, py) to bottom (px, py), width_px wide, at depths y_top..y_bot,
    bellying out `sag` m in the middle."""
    P = K.paint
    (tx, ty), (bx, by) = top, bottom

    def f(u, v):
        px = tx + (bx - tx) * v + (u - 0.5) * width_px
        py = ty + (by - ty) * v
        y = y_top + (y_bot - y_top) * v - sag * math.sin(math.pi * v)
        return (P.x(px), y, P.z(py))
    return K.sheet(f, 3, n, mat, name=name, thickness=0.01)


@model("house_weaver", "lane", kind="building", atlas=2048)
def house_weaver(K):
    """A weaver's lime-washed house under a tall hipped thatch, an indigo skirting, its front opened as a workshop
    alcove holding a pit loom with a pink saree on it; outside, a drying rack hung with hanks of dyed yarn and a
    spinning wheel."""
    P = K.paint
    D = 4.6
    K.front_min = 0.15
    halo_exclude(K, [(0, 0, 1671, 480), (1340, 590, 1671, 1143)])
    halo_exclude(K, [(1346, 600, 1660, 1080)], near=400)          # the white the cut-out filled in behind the rack
    white = K.tile((200, 560, 440, 900), size=1.0, vary=0.04, soften=0.45)
    indigo = K.tile((200, 950, 450, 1070), size=1.0, vary=0.05, soften=0.35)
    thatch_m = K.tile((500, 120, 800, 380), size=0.8, vary=0.06, soften=0.25)
    earth = K.tile((200, 1092, 1300, 1130), size=1.0, vary=0.08)
    brown = K.colour((495, 560, 520, 700), vary=0.06)
    timber = K.colour((560, 600, 568, 750), vary=0.08)
    X0, X1 = P.x(152), P.x(1345)
    body = K.box(X0, X1, 0.0, D, 0.0, P.z(452), white, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(925), indigo, name="skirting")
    K.box(P.x(150), P.x(1665), -0.9, D + 0.25, 0.0, P.z(1090), earth, bevel=0.04, name="ground")
    eave = (P.x(5), P.x(1495), -0.62, D + 0.62)
    ridge = (P.x(375), P.x(1125))
    hip_thatch(K, eave, ridge, P.z(436), P.z(30), thatch_m, thickness=0.26, shag=0.05, fringe=0.09)
    K.tube([P.pt(375, 26, D / 2), P.pt(1125, 26, D / 2)], P.m(16), K.colour((600, 15, 900, 38), vary=0.06),
           segments=10, name="ridge_pole")
    # the workshop alcove, lined with its dark mud plaster, and its floor
    ad = 1.7
    zt = P.z(452)
    K.cut(body, P.x(491), P.x(1001), -0.05, ad, 0.0, zt + 0.02)
    xa, xb = P.x(491), P.x(1001)
    K.box(xa, xa + 0.03, 0.0, ad, 0.0, zt, brown, name="alcove_l")
    K.box(xb - 0.03, xb, 0.0, ad, 0.0, zt, brown, name="alcove_r")
    K.box(xa, xb, ad - 0.03, ad, 0.0, zt, brown, name="alcove_back")
    K.box(xa, xb, 0.0, ad, zt - 0.03, zt, brown, name="alcove_ceiling")
    K.box(xa, xb, -0.02, ad, P.z(1090), P.z(989), K.colour((520, 960, 980, 985), vary=0.08), name="alcove_floor")
    # the loom: front legs, back posts, top beam, breast beam with the saree over it, reed and sley, heddle cords,
    # the cloth beam, a crossbar and the treadle
    yf, yb = 0.45, 1.35
    for x0, x1, y, top in ((525, 548, yf, 772), (947, 973, yf, 772), (545, 569, yb, 507), (937, 955, yb, 507)):
        K.box(P.x(x0), P.x(x1), y - 0.04, y + 0.04, P.z(989), P.z(top), timber, bevel=0.005, name="loom_post")
    K.box(P.x(535), P.x(970), yb - 0.05, yb + 0.05, P.z(544), P.z(525), timber, bevel=0.005, name="top_beam")
    for x in (545, 955):
        K.box(P.x(x) - 0.03, P.x(x) + 0.03, yf, yb, P.z(544), P.z(530), timber, name="top_rail")
        K.box(P.x(x) - 0.03, P.x(x) + 0.03, yf, yb, P.z(925), P.z(909), timber, name="low_rail")
    K.box(P.x(522), P.x(975), yf - 0.05, yf + 0.05, P.z(782), P.z(761), timber, bevel=0.005, name="breast_beam")
    K.box(P.x(577), P.x(924), yf + 0.25, yf + 0.3, P.z(743), P.z(725), timber, bevel=0.004, name="sley")
    K.box(P.x(592), P.x(908), yf + 0.26, yf + 0.29, P.z(725), P.z(699), K.colour((600, 705, 900, 720), vary=0.1),
          name="reed")
    for x in (600, 903):
        K.box(P.x(x) - 0.012, P.x(x) + 0.012, yf + 0.26, yf + 0.29, P.z(720), P.z(554), timber, name="sley_sword")
    cord = K.colour((0.55, 0.45, 0.32), vary=0.1)
    for x in (613, 640, 658, 856, 882):
        K.tube([P.pt(x, 489, yf + 0.5), P.pt(x, 699, yf + 0.5)], 0.007, cord, segments=5, name="heddle_cord")
    warp = K.colour((0.6, 0.12, 0.25), vary=0.1)
    K.box(P.x(610), P.x(877), yf, yb - 0.1, P.z(764), P.z(760), warp, name="warp")
    saree = K.projected(axis_x=P.x(745), squeeze=1.0, keep=[(612, 756, 875, 871)], inset=2)
    def cloth(u, v):
        px = 610 + 267 * u
        if v < 0.25:
            t = v / 0.25
            return (P.x(px), yf + 0.06 - 0.12 * t, P.z(758) + 0.03 * math.sin(math.pi * t))
        t = (v - 0.25) / 0.75
        return (P.x(px), yf - 0.07 + 0.01 * math.sin(u * 9), P.z(762) - (P.z(762) - P.z(873)) * t)
    K.sheet(cloth, 16, 12, saree, name="saree", thickness=0.006)
    K.tube([P.pt(550, 842, yf + 0.05), P.pt(947, 842, yf + 0.05)], P.m(12), timber, segments=10, name="cloth_beam")
    K.box(P.x(545), P.x(952), yf - 0.03, yf + 0.03, P.z(925), P.z(909), timber, name="crossbar")
    K.box(P.x(719), P.x(812), yf + 0.1, yf + 0.6, P.z(940), P.z(924), timber, name="treadle")
    K.panel((931, 634, 965, 663), yb - 0.06, name="note")
    # the drying rack outside, with its hanks of dyed yarn, and the spinning wheel
    yr = -0.55
    rack = K.colour((1188, 700, 1205, 1000), vary=0.08)
    for x0, x1, top in ((1183, 1211, 598), (1582, 1605, 619)):
        for y in (yr - 0.3, yr + 0.3):
            K.box(P.x(x0), P.x(x1), y - 0.035, y + 0.035, P.z(1074), P.z(top), rack, bevel=0.005, name="rack_post")
        K.box(P.x(x0) - 0.04, P.x(x1) + 0.04, yr - 0.45, yr + 0.45, P.z(1114), P.z(1074), rack, bevel=0.008,
              name="rack_foot")
    for py, xl in ((659, 1150), (816, 1072), (970, 1153)):
        K.tube([P.pt(xl, py, yr - 0.3), P.pt(1658, py, yr - 0.3)], P.m(8), rack, segments=8, name="rod")
    K.tube([P.pt(1150, 659, yr + 0.3), P.pt(1658, 659, yr + 0.3)], P.m(8), rack, segments=8, name="rod_back")
    K.box(P.x(1211), P.x(1582), yr - 0.03, yr + 0.03, P.z(1074), P.z(1053), rack, name="base_rail")
    yarn = K.projected(squeeze=1.0, keep=[(1222, 650, 1575, 995)], inset=2)
    for top, bot, w, dy in (((1335, 700), (1305, 955), 45, 0.08), ((1300, 662), (1245, 960), 55, -0.02),
                            ((1345, 662), (1395, 985), 60, -0.04), ((1387, 665), (1430, 975), 60, -0.05),
                            ((1440, 665), (1480, 970), 45, -0.06), ((1487, 665), (1540, 970), 55, -0.07)):
        ribbon(K, top, bot, w, yr - 0.3 + dy * 0.3, yr - 0.3 + dy, yarn, sag=0.04, name="yarn")
        ribbon(K, top, (bot[0], bot[1] - 10), w * 0.9, yr - 0.24, yr + 0.15, yarn, sag=-0.05, name="yarn_back")
    wheel = K.colour((1120, 760, 1140, 900), vary=0.08)
    hub = P.pt(1132, 827, yr - 0.45)
    for ex, ey in ((1077, 767), (1135, 725), (1158, 733), (1227, 754), (1056, 851), (1103, 943), (1145, 956),
                   (1227, 890)):
        K.tube([hub, P.pt(ex, ey, yr - 0.45)], P.m(5), wheel, segments=6, name="spoke")
        K.tube([(hub[0], hub[1] + 0.14, hub[2]), P.pt(1132 + (ex - 1132) * 0.95, 827 + (ey - 827) * 0.95, yr - 0.31)],
               P.m(5), wheel, segments=6, name="spoke_back")
    pts = [P.pt(1132 + 88 * math.cos(a), 827 + 88 * math.sin(a), yr - 0.38) for a in np.linspace(0, 2 * math.pi, 25)]
    K.tube(pts, 0.006, cord, segments=4, cap=False, name="drive_string")
    K.tube([P.pt(1053, 824, yr - 0.38), P.pt(1192, 824, yr - 0.38)], P.m(8), wheel, segments=8, name="axle_beam")
    for y in (yr - 0.5, yr - 0.26):
        K.box(P.x(1072), P.x(1098), y - 0.025, y + 0.025, P.z(1074), P.z(820), wheel, name="wheel_leg")
    K.box(P.x(1060), P.x(1110), yr - 0.55, yr - 0.2, P.z(1090), P.z(1074), wheel, name="wheel_base")
    # the back and the sides: a plank back door, small barred windows
    door = K.colour((0.2, 0.1, 0.045), vary=0.1)
    K.box(P.x(700), P.x(880), D - 0.02, D + 0.03, P.z(925), P.z(560), door, name="back_door")
    for x0, x1 in ((688, 700), (880, 892)):
        K.box(P.x(x0), P.x(x1), D - 0.02, D + 0.05, P.z(925), P.z(548), timber, name="back_door_frame")
    K.box(P.x(688), P.x(892), D - 0.02, D + 0.05, P.z(560), P.z(548), timber, name="back_door_frame")
    iron = K.colour((0.04, 0.03, 0.03), vary=0.05)
    dark = K.colour((0.04, 0.03, 0.03), vary=0.0)
    for side in (-1, 1):
        side_window(K, body, side, D * 0.55, P.z(820), P.z(640), 0.6, timber, iron, dark)


def wall_disc(K, x, y, z, r, thick, mat, facing="-y", name="disc", wobble=0.08):
    """A lumpy disc (a dung cake slapped on a wall to dry, a plate, a lid) of radius r m and `thick` m, its back on
    the wall at (x, y, z), facing -y (the front), +y, -x or +x."""
    prof = [(0.0, 0.0), (r, 0.0), (r * 0.97, thick * 0.45), (r * 0.75, thick * 0.9), (0.0, thick)]
    ob = K.lathe(prof, mat, segments=14, wobble=wobble, name=name)
    R = {"-y": Matrix.Rotation(math.radians(90), 4, "X"), "+y": Matrix.Rotation(math.radians(-90), 4, "X"),
         "-x": Matrix.Rotation(math.radians(-90), 4, "Y"), "+x": Matrix.Rotation(math.radians(90), 4, "Y")}[facing]
    ob.data.transform(Matrix.Translation((x, y, z)) @ R)
    return ob


def rope_cot(K, x0_px, x1_px, top_py, foot_py, y0, y1, legs_mat, frame_mat, weave_mat, leg_prof=None):
    """A rope cot (kattil): four turned legs, a frame of four rails, its woven rope bed, x0..x1 px wide, y0..y1 m deep,
    the bed at top_py, standing on foot_py."""
    P = K.paint
    prof = leg_prof or [(0.035, 0.0), (0.04, 0.08), (0.05, 0.18), (0.035, 0.3), (0.045, 0.36), (0.035, 0.42)]
    zt, zf = P.z(top_py), P.z(foot_py)
    h = zt - zf
    for x in (P.x(x0_px) + 0.05, P.x(x1_px) - 0.05):
        for y in (y0 + 0.05, y1 - 0.05):
            K.lathe([(r, zf + h * t / 0.42) for r, t in prof] + [(0.03, zt + 0.06)], legs_mat, segments=10,
                    centre=(x, y, 0.0), name="cot_leg")
    K.box(P.x(x0_px), P.x(x1_px), y0, y0 + 0.06, zt - 0.06, zt, frame_mat, bevel=0.008, name="cot_rail")
    K.box(P.x(x0_px), P.x(x1_px), y1 - 0.06, y1, zt - 0.06, zt, frame_mat, bevel=0.008, name="cot_rail")
    K.box(P.x(x0_px), P.x(x0_px) + 0.06, y0, y1, zt - 0.06, zt, frame_mat, bevel=0.008, name="cot_rail")
    K.box(P.x(x1_px) - 0.06, P.x(x1_px), y0, y1, zt - 0.06, zt, frame_mat, bevel=0.008, name="cot_rail")
    K.sheet(lambda u, v: (P.x(x0_px) + 0.06 + (P.x(x1_px) - P.x(x0_px) - 0.12) * u, y0 + 0.06 + (y1 - y0 - 0.12) * v,
                          zt - 0.025 - 0.03 * math.sin(math.pi * u) * math.sin(math.pi * v)), 10, 4, weave_mat,
            name="cot_weave", thickness=0.012)


@model("house_hut_porch", "lane", kind="building", atlas=2048)
def house_hut_porch(K):
    """A mud hut under a tall hipped thatch, with a porch of woven palm matting on a bamboo frame across its front;
    dung cakes drying on the walls, a carved plank door between kolam motifs, a shuttered window, a rope cot on the
    porch and a pile of firewood, a lime skirting."""
    P = K.paint
    D = 4.6
    K.front_min = 0.15
    halo_exclude(K, [(0, 0, 1659, 1139)])
    mud = K.tile((532, 690, 600, 830), size=0.7, vary=0.05, soften=0.45)    # clean mud between window and post
    lime = K.tile((1000, 990, 1060, 1060), size=0.6, vary=0.04, soften=0.4)
    thatch_m = K.tile((500, 100, 800, 400), size=0.8, vary=0.06, soften=0.25)
    mat_m = K.tile((280, 462, 560, 532), size=0.7, vary=0.05)
    earth = K.tile((300, 1100, 1300, 1130), size=1.0, vary=0.08)
    wood = K.tile((720, 660, 940, 1040), size=0.6, vary=0.04)
    frame = K.colour((688, 700, 700, 1000), vary=0.06)
    X0, X1 = P.x(130), P.x(1525)
    body = K.box(X0, X1, 0.0, D, 0.0, P.z(480), mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(985), lime, name="skirting")
    K.box(P.x(78), P.x(1580), -1.85, D + 0.25, 0.0, P.z(1100), earth, bevel=0.04, name="ground")
    hip_thatch(K, (P.x(100), P.x(1545), -0.5, D + 0.5), (P.x(370), P.x(1290)), P.z(468), P.z(30), thatch_m,
               thickness=0.26, shag=0.05, fringe=0.09)
    K.tube([P.pt(370, 27, D / 2), P.pt(1290, 27, D / 2)], P.m(16), K.colour((600, 12, 1000, 40), vary=0.06),
           segments=10, name="ridge_pole")
    # the porch: a woven mat on bamboo rafters, a beam along its front on four posts
    yb, yfp = -0.42, -1.62
    bamboo = K.projected(axis_x=P.x(615), squeeze=0.9, keep=[(606, 560, 625, 1095)], inset=2)
    def mat_surf(u, v):
        x = P.x(48) + (P.x(1585) - P.x(48)) * u
        y = yb + (yfp - 0.06 - yb) * v
        z = P.z(452) + (P.z(540) - P.z(452)) * v - 0.025 * math.sin(math.pi * u * 3) ** 2 * math.sin(math.pi * v)
        return (x, y, z)
    K.sheet(mat_surf, 30, 6, mat_m, name="porch_mat", thickness=0.02)
    K.tube([P.pt(50, 547, yfp), P.pt(1650, 547, yfp)], P.m(10), bamboo, segments=10, name="front_beam")
    K.tube([P.pt(60, 458, yb + 0.05), P.pt(1580, 458, yb + 0.05)], P.m(8), bamboo, segments=8, name="back_beam")
    for x in (95, 615, 1053, 1560):
        K.tube([P.pt(x, 1100, yfp), P.pt(x, 552, yfp)], P.m(10), bamboo, segments=10, name="post")
        K.tube([P.pt(x, 458, yb + 0.1), P.pt(x, 549, yfp - 0.15)], P.m(9), bamboo, segments=8, name="rafter")
    # dung cakes drying on the front wall where they are painted, and round the sides and back
    dung = K.tile((300, 850, 360, 905), size=P.m(84), vary=0.08)          # one painted cake, its rim and its straw
    r = P.m(42)
    cakes = [(175, 588), (250, 588), (345, 588), (448, 588), (545, 588), (230, 678), (330, 678), (240, 778),
             (330, 778), (180, 878), (275, 878), (375, 878), (470, 878), (560, 878), (1165, 588), (1255, 588),
             (1355, 588), (1455, 588), (1075, 675), (1165, 675), (1265, 675), (1355, 675), (1455, 675), (1085, 775),
             (1170, 775), (1265, 775), (1360, 775), (1460, 775), (1080, 878), (1180, 878), (1275, 878), (1370, 878),
             (1465, 878)]
    for cx, cy in cakes:
        wall_disc(K, P.x(cx), -0.002, P.z(cy), r * K.rng.uniform(0.92, 1.05), 0.035, dung, name="dung_cake")
    for side, xw in ((-1, X0), (1, X1)):
        for row, z in enumerate((P.z(600), P.z(700), P.z(800), P.z(900))):
            for k in range(6):
                if K.rng.uniform() < 0.25:
                    continue
                y = 0.45 + k * 0.62 + (0.3 if row % 2 else 0) + K.rng.uniform(-0.05, 0.05)
                if y > D - 0.3:
                    continue
                wall_disc(K, xw, y, z + K.rng.uniform(-0.04, 0.04), r * K.rng.uniform(0.9, 1.05), 0.035, dung,
                          facing="+x" if side > 0 else "-x", name="dung_cake")
    for row, z in enumerate((P.z(650), P.z(760), P.z(870))):
        for k in range(9):
            if K.rng.uniform() < 0.3:
                continue
            x = X0 + 0.4 + k * 0.62 + (0.3 if row % 2 else 0)
            if x > X1 - 0.3 or abs(x - P.x(830)) < 0.7:
                continue
            wall_disc(K, x, D, z, r * K.rng.uniform(0.9, 1.05), 0.035, dung, facing="+y", name="dung_cake")
    # the door, the window
    K.cut(body, P.x(700), P.x(960), -0.05, 0.25, P.z(1068), P.z(632))
    K.box(P.x(700), P.x(960), 0.12, 0.17, P.z(1068), P.z(632), wood, name="door")
    for x0, x1 in ((683, 700), (960, 975)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(1068), P.z(615), frame, bevel=0.008, name="jamb")
    K.box(P.x(683), P.x(975), -0.03, 0.12, P.z(632), P.z(615), frame, bevel=0.008, name="frame_head")
    K.cut(body, P.x(410), P.x(512), -0.05, 0.12, P.z(790), P.z(665))
    K.box(P.x(410), P.x(512), 0.07, 0.1, P.z(790), P.z(665), wood, name="shutters")
    for a, b, c, d in ((395, 410, 652, 802), (512, 527, 652, 802), (410, 512, 652, 665), (410, 512, 790, 802)):
        K.box(P.x(a), P.x(b), -0.03, 0.07, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    back_decal(K, (683, 615, 975, 1068), D, x_shift=0.0)
    side_decal(K, (395, 652, 527, 802), X0, -1, D * 0.5, name="side_window")
    side_decal(K, (395, 652, 527, 802), X1, 1, D * 0.5, name="side_window")
    # the rope cot on the porch
    cotleg = K.projected(axis_x=P.x(140), squeeze=0.9, keep=[(128, 990, 152, 1105)], inset=2)
    rope_cot(K, 125, 660, 955, 1100, -0.95, -0.15, cotleg, K.colour((150, 990, 600, 1000), vary=0.08),
             K.tile((300, 955, 600, 985), vary=0.06))
    # the firewood: logs end-on at the bottom, sticks piled across them
    logs = K.projected(squeeze=1.0, keep=[(1065, 945, 1555, 1100)], inset=2)
    bark = K.colour((1200, 1000, 1300, 1040), vary=0.12)
    for cx, cy, rr in ((1110, 1078, 18), (1150, 1080, 19), (1195, 1078, 18), (1240, 1080, 18), (1290, 1078, 19),
                       (1335, 1080, 18), (1380, 1078, 18), (1425, 1080, 18), (1470, 1078, 19), (1515, 1082, 17),
                       (1130, 1045, 17), (1175, 1045, 18), (1220, 1044, 17), (1310, 1046, 18), (1355, 1044, 17),
                       (1400, 1045, 18), (1445, 1046, 17), (1490, 1048, 17)):
        y0 = -1.25 + K.rng.uniform(-0.05, 0.05)
        K.tube([P.pt(cx, cy, y0), P.pt(cx + K.rng.uniform(-8, 8), cy + K.rng.uniform(-4, 4), y0 + 0.95)], P.m(rr),
               logs, segments=8, name="log")
    for (ax, ay), (bx, by) in (((1080, 1020), (1290, 1000)), ((1120, 995), (1360, 960)), ((1210, 1010), (1480, 985)),
                               ((1260, 990), (1530, 1030)), ((1300, 975), (1450, 955)), ((1350, 1000), (1550, 1060)),
                               ((1150, 1030), (1420, 1015))):
        yy = -0.75 + K.rng.uniform(-0.35, 0.35)
        K.tube([P.pt(ax, ay, yy - 0.2), P.pt(bx, by, yy + 0.2)], P.m(13), logs, segments=8, name="stick")


def tiled_quad(K, corners, mat, courses, nu=24, lip=0.03, thickness=0.04, name="tiles"):
    """A slope of country tiles through four corners (eave left, eave right, top right, top left; a triangle when
    the two top corners are the same point): `courses` rows of tiles, each row's lower end standing proud by `lip`
    (the tile columns themselves are in the painted texture)."""
    c = [Vector(p) for p in corners]

    def f(u, v):
        a = c[0].lerp(c[1], u)
        b = c[3].lerp(c[2], u)
        p = a.lerp(b, v)
        k = min(courses - 1, int(v * courses))
        frac = v * courses - k
        return (p.x, p.y, p.z + lip * (1 - frac) ** 2)
    return K.sheet(f, nu, courses * 3, mat, name=name, smooth=False, thickness=thickness)


def finial(K, px, top_py, base_py, y, mat, r_px=10, name="finial"):
    """A turned clay finial on a ridge: a pot-and-spire profile from base_py up to top_py."""
    P = K.paint
    h = base_py - top_py
    prof = [(1.0, 0.0), (1.2, 0.1), (0.9, 0.22), (1.1, 0.35), (0.7, 0.5), (0.5, 0.62), (0.75, 0.7), (0.35, 0.82),
            (0.12, 1.0)]
    return K.lathe([(P.m(r_px * a), P.z(base_py - h * t)) for a, t in prof], mat, segments=12,
                   centre=(P.x(px), y, 0.0), name=name)


PILLAR_VH = [(33, 1172), (32, 1163), (22, 1146), (22, 1140), (18, 1135), (18, 1125), (25, 1118), (28, 1100),
             (27, 1075), (25, 1058), (23, 1000), (20, 950), (18, 920), (21.5, 915), (20, 895), (19.5, 890),
             (19.5, 882), (18, 878), (18, 862)]
BRACKET_VH = [(-78, 806), (78, 806), (76, 822), (66, 831), (48, 828), (36, 840), (27, 862), (-27, 862), (-36, 840),
              (-48, 828), (-66, 831), (-76, 822)]


@model("house_village_head", "lane", kind="building", atlas=2048)
def house_village_head(K):
    """The village head's two-storey house: a hipped roof of country tiles with clay finials over a cream upper
    storey with three shuttered windows, a tiled veranda roof with a gable over the door on six turned wooden
    pillars with carved brackets, thinnai platforms at its ends, a studded carved door between two niches, a brass
    lamp, an easy chair, a kolam-bordered plinth with steps, a tulsi planter before it."""
    P = K.paint
    D, Du = 7.0, 4.2                                   # the ground floor's depth; the upper storey's
    yv, yp = -2.6, -2.3                                # the veranda's edge; the pillars' line
    K.front_min = 0.0
    halo_exclude(K, [(0, 0, 2325, 1377)])
    cream = K.tile((800, 400, 1000, 560), size=1.2, vary=0.04, soften=0.5)
    maroon = K.colour((250, 420, 290, 600), vary=0.05)
    dado = K.tile((620, 1060, 880, 1140), size=1.0, vary=0.04, soften=0.4)
    tiles = K.tile((700, 120, 1000, 280), size=1.4, vary=0.04, soften=0.15)
    tiles_low = K.tile((620, 660, 900, 760), size=1.4, vary=0.04, soften=0.15)
    fascia = K.colour((400, 308, 800, 326), vary=0.06)
    plinth = K.colour((500, 1182, 900, 1196), vary=0.06)
    floor = K.colour((600, 1150, 900, 1165), vary=0.06)
    thin = K.tile((150, 1100, 380, 1170), size=0.8, vary=0.05, soften=0.3)
    bracket_m = K.colour((545, 815, 560, 845), vary=0.08)
    clay = K.colour((560, 90, 600, 100), vary=0.06)
    dark = K.colour((0.03, 0.02, 0.02), vary=0.0)
    wood = K.colour((470, 450, 500, 600), vary=0.08)
    X0, X1 = P.x(240), P.x(2085)
    zf = P.z(1172)
    # the storeys: the ground floor (deeper), the upper storey over its front, a maroon band between them
    lower = K.box(X0, X1, 0.0, Du, 0.0, P.z(640), cream, name="ground_floor")
    K.box(X0, X1, Du - 0.01, D, 0.0, P.z(790), cream, name="ground_floor_back")
    upper = K.box(X0, X1, 0.0, Du, P.z(640), P.z(330), cream, name="upper_floor")
    K.box(X0 - 0.03, X1 + 0.03, -0.03, Du + 0.03, P.z(645), P.z(620), maroon, name="band")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, zf, P.z(1035), dado, name="dado")
    for x0, x1 in ((240, 292), (2033, 2085)):
        for z0, z1 in ((zf, P.z(800)), (P.z(620), P.z(330))):
            K.box(P.x(x0) - 0.02, P.x(x1) + 0.02 * 0, -0.02, 0.05, z0, z1, maroon, name="pilaster")
    # the plinth: its kolam face where painted, a plain base course down to the ground, the veranda floor
    K.box(P.x(137), P.x(2190), yv, D + 0.1, 0.0, zf, plinth, bevel=0.015, name="plinth")
    K.box(P.x(140), P.x(2187), yv + 0.02, 0.0, zf, zf + 0.008, floor, name="veranda_floor")
    stairs(K, [(990, 1335, 1201), (985, 1340, 1261), (980, 1345, 1305), (975, 1350, 1345)], plinth, tread=0.28,
           y0=yv)
    # the thinnai at both ends
    for (a0, a1), (b0, b1) in (((138, 311), (311, 467)), ((2014, 2187), (1858, 2014))):
        K.box(P.x(a0), P.x(a1), yv, 0.0, zf, P.z(1025), thin, bevel=0.012, name="thinnai")
        K.box(P.x(b0), P.x(b1), yv, -1.1, zf, P.z(1083), thin, bevel=0.012, name="thinnai_seat")
    # the door, recessed in its carved frame, a niche either side
    K.cut(lower, P.x(1030), P.x(1295), -0.05, 0.3, zf, P.z(812))
    K.box(P.x(1073), P.x(1251), 0.2, 0.26, zf, P.z(845), K.tile((1090, 870, 1230, 1100), vary=0.04), name="door")
    K.box(P.x(1030), P.x(1295), 0.12, 0.2, zf, P.z(812), wood, name="door_frame")
    K.cut(lower, P.x(1060), P.x(1265), 0.05, 0.25, zf, P.z(840))
    for x0, x1 in ((955, 1000), (1320, 1365)):
        K.cut(lower, P.x(x0), P.x(x1), -0.05, 0.12, P.z(962), P.z(888))
        K.box(P.x(x0), P.x(x1), 0.08, 0.1, P.z(962), P.z(888), dark, name="niche_back")
    # the upper windows, shutters open
    iron = K.colour((0.05, 0.03, 0.025), vary=0.05)
    for cx in (592, 1163, 1732):
        dx = cx - 592
        barred_window(K, upper, (510 + dx, 381, 677 + dx, 587), (527 + dx, 400, 660 + dx, 575),
                      [x + dx for x in (545, 562, 578, 607, 623, 640)], (487,), wood, iron, dark)
        shutter(K, 510 + dx, 0.38, 385, 585, 62, wood, side=-1)
        shutter(K, 677 + dx, 0.38, 385, 585, 62, wood, side=1)
    for side in (-1, 1):
        side_window(K, upper, side, Du * 0.5, P.z(587), P.z(400), 0.8, wood, iron, dark)
        side_window(K, lower, side, Du * 0.6, P.z(1000), P.z(880), 0.7, wood, iron, dark)
    back_decal(K, (456, 381, 729, 590), Du, x_shift=P.m(570), name="back_window")
    back_decal(K, (1030, 812, 1295, 1150), D, name="back_door")
    # the pillars on the veranda floor and the thinnai, their carved brackets, the beam
    for cx in (563, 922, 1423, 1782):
        turned_post(K, cx, PILLAR_VH, yp, keep=[(cx - 34, 860, cx + 34, 1175)], name="pillar")
    short = [(r, 1027 - (1172 - y) * (1027 - 870) / (1172 - 862)) for r, y in PILLAR_VH]
    for cx in (184, 2158):
        turned_post(K, cx, short, yp, keep=[(cx - 34, 860, cx + 34, 1030)], name="pillar_end")
    for cx in (184, 563, 922, 1423, 1782, 2158):
        K.prism([(P.x(cx + dx), P.z(py)) for dx, py in BRACKET_VH], yp - 0.08, yp + 0.08, bracket_m, name="bracket")
    K.box(P.x(45), P.x(2280), yp - 0.12, yp + 0.12, P.z(806), P.z(790), fascia, bevel=0.01, name="veranda_beam")
    # the veranda roof: a lean-to from the band, hipped at its ends, a gable over the door
    zt, ze = P.z(640), P.z(782)
    eY = yv - 0.15
    tiled_quad(K, [(P.x(13), eY, ze), (P.x(2312), eY, ze), (P.x(2068), 0.0, zt), (P.x(257), 0.0, zt)], tiles_low,
               courses=5, nu=40, name="veranda_roof")
    for xe, xt in ((13, 257), (2312, 2068)):
        tiled_quad(K, [(P.x(xe), 0.0, ze), (P.x(xe), eY, ze), (P.x(xt), 0.0, zt), (P.x(xt), 0.0, zt)], tiles_low,
                   courses=5, nu=8, name="veranda_hip")
    zg = P.z(603)
    gY = eY - 0.12
    K.prism([(P.x(895), P.z(806)), (P.x(1431), P.z(806)), (P.x(1163), P.z(590))], gY, gY + 0.16,
            K.colour((1100, 700, 1220, 760), vary=0.06), name="pediment")
    for xe in (905, 1421):
        tiled_quad(K, [(P.x(xe), gY + 0.1, P.z(796)), (P.x(xe), -0.6, P.z(796)), (P.x(1163), -0.3, zg),
                       (P.x(1163), gY + 0.1, zg)], tiles_low, courses=5, nu=6, name="gable_slope")
    finial(K, 1163, 565, 605, gY + 0.08, clay, r_px=9)
    # the upper roof: hipped country tiles, ridge and hip caps, three finials, its fascia
    zeU, zrU = P.z(300), P.z(86)
    ov = 0.8
    ex0, ex1, rx0, rx1 = P.x(129), P.x(2195), P.x(566), P.x(1760)
    ym = Du / 2
    tiled_quad(K, [(ex0, -ov, zeU), (ex1, -ov, zeU), (rx1, ym, zrU), (rx0, ym, zrU)], tiles, courses=8, nu=40,
               name="roof_front")
    tiled_quad(K, [(ex1, Du + ov, zeU), (ex0, Du + ov, zeU), (rx0, ym, zrU), (rx1, ym, zrU)], tiles, courses=8,
               nu=40, name="roof_back")
    tiled_quad(K, [(ex0, Du + ov, zeU), (ex0, -ov, zeU), (rx0, ym, zrU), (rx0, ym, zrU)], tiles, courses=8, nu=10,
               name="roof_hip")
    tiled_quad(K, [(ex1, -ov, zeU), (ex1, Du + ov, zeU), (rx1, ym, zrU), (rx1, ym, zrU)], tiles, courses=8, nu=10,
               name="roof_hip")
    K.box(P.x(155), P.x(2170), -ov + 0.02, -ov + 0.08, P.z(330), P.z(300), fascia, name="fascia")
    K.box(P.x(155), P.x(2170), Du + ov - 0.08, Du + ov - 0.02, P.z(330), P.z(300), fascia, name="fascia")
    K.tube([(rx0, ym, zrU + 0.06), (rx1, ym, zrU + 0.06)], P.m(12), clay, segments=8, name="ridge_cap")
    for x in np.arange(620, 1720, 70):
        K.lathe([(P.m(13), zrU), (P.m(15), zrU + 0.1), (P.m(12), zrU + 0.16), (0.0, zrU + 0.17)], clay, segments=10,
                centre=(P.x(x), ym, 0.0), name="ridge_tile")
    for (xa, ya), xr in (((ex0, -ov), rx0), ((ex0, Du + ov), rx0), ((ex1, -ov), rx1), ((ex1, Du + ov), rx1)):
        K.tube([(xa, ya, zeU + 0.06), (xr, ym, zrU + 0.06)], P.m(10), clay, segments=8, name="hip_cap")
    for x in (566, 1163, 1750):
        finial(K, x, 9, 80, ym, clay, r_px=14)
    # back lean-to over the ground floor's back rooms
    zb = P.z(790) - 0.05
    tiled_quad(K, [(X1 + 0.5, D + 0.55, zb), (X0 - 0.5, D + 0.55, zb), (X0 - 0.2, Du, P.z(645)),
                   (X1 + 0.2, Du, P.z(645))], tiles_low, courses=7, nu=30, name="back_roof")
    for xe, xt in ((X0 - 0.5, X0 - 0.2), (X1 + 0.5, X1 + 0.2)):
        tiled_quad(K, [(xe, Du, zb), (xe, D + 0.55, zb), (xt, Du, P.z(645)), (xt, Du, P.z(645))], tiles_low,
                   courses=7, nu=6, name="back_hip")
    # the brass lamp, the easy chair
    brass = K.projected(axis_x=P.x(1340), squeeze=0.9, keep=[(1308, 980, 1372, 1166)], inset=2)
    K.lathe([(P.m(r), P.z(y)) for r, y in ((30, 1166), (30, 1160), (18, 1152), (8, 1145), (6, 1120), (10, 1100),
                                           (6, 1085), (6, 1052), (12, 1046), (30, 1040), (28, 1034), (8, 1030),
                                           (8, 1010), (5, 995), (1, 983))], brass, segments=18,
            centre=(P.x(1340), -0.5, 0.0), name="lamp")
    chair = K.colour((1590, 1120, 1610, 1140), vary=0.08)
    slats = K.projected(squeeze=1.0, keep=[(1560, 990, 1720, 1120)], inset=2)
    for y in (-1.25, -0.7):
        for (ax, ay), (bx, by) in (((1712, 990), (1600, 1150)), ((1520, 1100), (1505, 1172)),
                                   ((1655, 1100), (1690, 1172)), ((1510, 1070), (1690, 1060)),
                                   ((1535, 1118), (1660, 1110))):
            K.tube([P.pt(ax, ay, y), P.pt(bx, by, y)], P.m(5), chair, segments=6, name="chair_frame")
    def seat(u, v):
        top, low, front = P.pt(1700, 1000, 0), P.pt(1610, 1125, 0), P.pt(1530, 1105, 0)
        if v < 0.6:
            t = v / 0.6
            x, z = top[0] + (low[0] - top[0]) * t, top[2] + (low[2] - top[2]) * t
        else:
            t = (v - 0.6) / 0.4
            x, z = low[0] + (front[0] - low[0]) * t, low[2] + (front[2] - low[2]) * t
        return (x, -1.22 + 0.49 * u, z - 0.04 * math.sin(math.pi * u))
    K.sheet(seat, 4, 10, slats, name="chair_seat", thickness=0.01)
    # the tulsi planter before the steps, the plant on it
    tp = K.projected(axis_x=P.x(790), squeeze=0.95, keep=[(705, 1148, 877, 1370)], inset=2)
    yt = yv - 1.0
    for x0, x1, t, b in ((705, 876, 1331, 1377), (720, 872, 1305, 1331), (731, 850, 1198, 1305),
                         (712, 865, 1178, 1198)):
        hw = P.m(x1 - x0) / 2
        K.box(P.x(x0), P.x(x1), yt - hw, yt + hw, P.z(b), P.z(t), tp, bevel=0.008, name="tulsi_maadam")
    hw = P.m(865 - 712) / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.block(P.x(788.5) + sx * (hw - 0.04), yt + sy * (hw - 0.04), P.z(1165), 0.07, 0.07, P.m(26), tp,
                    bevel=0.01, name="horn")
    K.box(P.x(716), P.x(861), yt - hw + 0.03, yt + hw - 0.03, P.z(1180), P.z(1176), K.colour((0.12, 0.06, 0.03)),
          name="soil")
    from kitlib import plant_pixels
    K.leaves_only((695, 990, 895, 1176), plant_pixels)
    for yaw in (0, 45, -45, 90):
        K.card_from_painting((695, 990, 895, 1176), (P.x(795), yt + K.rng.uniform(-0.04, 0.04), P.z(1083)),
                             yaw=yaw, name="tulsi")
