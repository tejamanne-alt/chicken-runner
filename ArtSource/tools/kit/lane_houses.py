"""The lane's houses, modelled from their paintings (ArtSource/cutouts/lane). See kitlib.py for the kit.

A house is a real building: its walls, plinth, cornice, parapet and pillars as solids running round all four sides,
its door and windows recessed into the wall, its steps, sunshades, pots and plants standing out in front, a roof you
could stand on. The front takes the painting itself; the sides and back are the same plaster, stone and paint, cut
from the painting, with a door or window repeated where a real house would have one.
"""
import math

import numpy as np

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
    lat = K.tile((50, 140, 80, 260), vary=0.06, soften=0.25)       # laterite with its pits and lime splashes
    lat2 = K.tile((290, 120, 310, 280), vary=0.06, soften=0.25)
    slab = K.tile((60, 18, 280, 34), vary=0.05, soften=0.2)
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
