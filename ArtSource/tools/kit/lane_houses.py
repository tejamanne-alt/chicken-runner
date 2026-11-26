"""The lane's houses, modelled from their paintings (ArtSource/cutouts/lane). See kitlib.py for the kit.

A house is a real building: its walls, plinth, cornice, parapet and pillars as solids running round all four sides,
its door and windows recessed into the wall, its steps, sunshades, pots and plants standing out in front, a roof you
could stand on. The front takes the painting itself; the sides and back are the same plaster, stone and paint, cut
from the painting, with a door or window repeated where a real house would have one.
"""
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
