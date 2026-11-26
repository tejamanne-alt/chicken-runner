"""Trees, modelled from their paintings. See kitlib.py for the kit.

A tree is its trunk, limbs and roots as real tapering tubes traced along the painted ones (taking the painted bark
from the front, the same bark round the back), a crown of leaf cards cut from the painting's own foliage and spread
through the crown's depth (so it is the painting from the front and a leafy volume from every other side), its fruit
as real fruit, and the rocks and undergrowth at its foot.
"""
import math

from kitlib import foliage_pixels, model


def limb(K, pts, mat, y=0.0, depth_wobble=0.0, segments=12, name="limb"):
    """A tapering tube along painted points [(px, py, radius_px), ...] at depth y (or a list of y per point)."""
    P = K.paint
    ys = y if isinstance(y, (list, tuple)) else [y + K.rng.uniform(-depth_wobble, depth_wobble) * (i > 0) for i in range(len(pts))]
    return K.tube([P.pt(px, py, yy) for (px, py, _), yy in zip(pts, ys)], [P.m(r) for _, _, r in pts], mat,
                  segments=segments, name=name)


def fruit(K, px, py, rx_px, ry_px, y, mat, stalk=None):
    """A fruit (mango, coconut, papaya) hanging where it is painted: a turned egg shape rx by ry px at depth y."""
    P = K.paint
    rx, ry = P.m(rx_px), P.m(ry_px)
    prof = [(0.0, -ry), (rx * 0.55, -ry * 0.85), (rx * 0.92, -ry * 0.45), (rx, 0.0), (rx * 0.9, ry * 0.5),
            (rx * 0.55, ry * 0.88), (0.0, ry)]
    ob = K.lathe(prof, mat, segments=16, centre=(P.x(px), y, P.z(py)), name="fruit")
    if stalk is not None:
        K.tube([(P.x(px), y, P.z(py) + ry * 0.9), (P.x(px) + 0.01, y, P.z(py) + ry * 1.6)], 0.008, stalk, segments=5,
               name="stalk")
    return ob


def rock(K, px, py, w_px, h_px, y, mat):
    """A boulder where the painting has one: px, py its bottom middle, w by h px."""
    P = K.paint
    return K.boulder(P.x(px), y, P.z(py) + P.m(h_px) * 0.5, P.m(w_px), P.m(w_px) * 0.75, P.m(h_px) * 1.1, mat)


@model("tree_mango_2", "lane", kind="prop", atlas=2048, leaves=1024)
def tree_mango_2(K):
    """A mango tree: a thick, twisting trunk on buttress roots, five big limbs, a broad dome of leaves with mangoes
    hanging in it, two rocks and low plants at its foot."""
    P = K.paint
    bark = K.projected(axis_x=P.x(365), squeeze=0.9, keep=[(200, 240, 560, 712)], exclude=[(100, 540, 280, 712), (500, 560, 640, 712)])
    bark_tile = K.tile((300, 450, 420, 560), vary=0.06, soften=0.2)
    crown_d = P.m(720) * 0.78
    # the trunk, from its flared foot up to the fork, its roots and limbs, melted into one surface
    wood = []
    wood.append(limb(K, [(365, 712, 120), (365, 660, 108), (362, 600, 92), (360, 540, 80), (356, 480, 72),
                         (356, 430, 66), (358, 395, 60)], bark, segments=18, name="trunk"))
    # buttress roots, round the whole foot (the painted ones at the sides; the rest towards the front and back)
    for pts in ([(330, 640, 40), (280, 690, 26), (225, 712, 12)], [(400, 640, 40), (460, 690, 26), (520, 712, 12)],
                [(345, 650, 36), (300, 705, 20), (270, 714, 8)], [(385, 650, 36), (430, 705, 20), (470, 714, 8)]):
        wood.append(limb(K, pts, bark, y=[0.0, 0.0, 0.0], name="root"))
    for yy, dx in ((-0.9, -40), (-0.8, 50), (0.9, 30), (0.85, -50)):
        wood.append(limb(K, [(365 + dx * 0.3, 640, 38), (365 + dx * 0.8, 700, 22), (365 + dx, 714, 8)], bark,
                         y=[0.0, yy * 0.6, yy], name="root_back"))
    # the limbs, as painted, and more going into the crown's depth behind them
    painted = [
        [(335, 410, 46), (290, 375, 36), (230, 352, 26), (170, 340, 18), (115, 330, 11)],
        [(390, 405, 48), (450, 378, 36), (520, 355, 26), (575, 340, 18), (625, 325, 11)],
        [(340, 390, 36), (310, 330, 28), (275, 275, 20), (245, 225, 12)],
        [(362, 390, 38), (352, 310, 30), (345, 235, 20), (340, 170, 12)],
        [(385, 390, 34), (420, 315, 26), (455, 255, 18), (515, 205, 10)],
    ]
    for pts in painted:
        wood.append(limb(K, pts, bark, y=0.0, depth_wobble=0.12, name="limb"))
    for side in (-1, 1):
        for pts in painted[2:]:
            pts2 = [(x + K.rng.uniform(-30, 30), y, r * 0.85) for x, y, r in pts]
            ys = [0.0] + [side * crown_d * 0.32 * (i / (len(pts2) - 1)) for i in range(1, len(pts2))]
            wood.append(limb(K, pts2, bark, y=ys, name="limb_depth"))
    K.fuse(wood, voxel=0.035, faces=9000)
    # the crown: leaves only (not the bark painted in its gaps), cards spread through its depth
    K.leaves_only((0, 0, 743, 450), foliage_pixels)
    K.canopy((10, 10, 735, 445), crown_d, n=170, size_px=(120, 100), yaw=40, pitch=25, bulge=0.35, centre_px=(372, 300))
    # a denser front layer, so from the front the painting is whole
    K.canopy((10, 10, 735, 445), crown_d * 0.25, n=60, size_px=(130, 110), yaw=20, pitch=10, centre_y=-crown_d * 0.3,
             bulge=1.0, centre_px=(372, 300))
    # mangoes where they hang, and more round the back
    mango = K.projected(squeeze=1.0, keep=[(300, 135, 360, 250), (520, 225, 575, 290), (140, 280, 180, 330),
                                           (100, 380, 140, 435), (620, 380, 662, 430)], inset=2)
    stalk = K.colour((0.1, 0.18, 0.03))
    for px, py, rx, ry in ((327, 162, 16, 22), (350, 195, 16, 22), (350, 230, 14, 20), (535, 250, 15, 22),
                           (555, 265, 16, 24), (162, 305, 15, 22), (120, 410, 15, 22), (640, 405, 15, 22)):
        fruit(K, px, py, rx, ry, -crown_d * 0.36, mango, stalk)
        fruit(K, px + K.rng.uniform(-40, 40), py + K.rng.uniform(-30, 30), rx, ry, crown_d * K.rng.uniform(0.0, 0.4),
              mango, stalk)
    # rocks and the low plants at the foot
    stone = K.projected(squeeze=1.0, keep=[(140, 645, 220, 705), (465, 640, 585, 705)], inset=2)
    rock(K, 180, 690, 80, 55, -0.5, stone)
    rock(K, 525, 690, 120, 65, -0.35, stone)
    rock(K, 300, 700, 70, 40, 1.1, stone)
    K.leaves_only((90, 550, 640, 712))
    for i in range(26):
        cx, cy = K.rng.uniform(110, 620), K.rng.uniform(600, 690)
        y = K.rng.uniform(-1.2, 1.2)
        K.card_from_painting((cx - 45, cy - 40, cx + 45, cy + 40), (P.x(cx), y, P.z(cy)), yaw=K.rng.uniform(-80, 80),
                             name="undergrowth")
    # the patch of earth
    earth = K.colour((0.30, 0.13, 0.05), vary=0.2, scale=6)
    K.lathe([(0.0, 0.0), (P.m(270), 0.0), (P.m(255), 0.025), (0.0, 0.04)], earth, segments=32, centre=(P.x(365), 0.0, 0.0),
            scale_y=0.7, wobble=0.12, name="earth")
