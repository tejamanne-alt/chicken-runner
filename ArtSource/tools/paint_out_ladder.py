"""Paints the bamboo ladder out of the turmeric house's cut-out, leaving the wall behind it.

    python ArtSource/tools/paint_out_ladder.py [CUTOUT.png]

The kid climbs a real 3D ladder (ArtSource/tools/models/ladder_model.py) that the game stands where the painting had
one, so the card must not carry a second, painted ladder. cutouts.py calls this right after it cuts the house out of C4;
running it again on a house already painted out does no harm. Needs opencv (cv2).

The ladder's rails and rungs are found by eye in the 422 x 477 px cut-out (before the game mirrors it): the rails run
from about x 318 and 341 at the top (y 34) to 368 and 405 at the foot, nine rungs between them. What the plant at its
foot covers stays; what stuck out past the wall's edge becomes transparent; the wall's outline is drawn back in there.
"""
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

SIZE = (422, 477)
RAILS = (((318, 34), (368, 477)), ((341, 34), (405, 477)))
RUNGS = (73, 115, 156, 213, 256, 298, 352, 394, 434)
PARAPET = 86            # rows above this are the parapet, which reaches a little further right
EDGE = (390, 384)       # the wall's right edge: parapet, then wall
OUTLINE = (52, 36, 24)


def rail_x(rail, y):
    (x0, y0), (x1, y1) = rail
    return x0 + (x1 - x0) * (y - y0) / (y1 - y0)


def paint_out(rgba):
    """The cut-out (H x W x 4 uint8) with its ladder painted out."""
    h, w = rgba.shape[:2]
    sx, sy = w / SIZE[0], h / SIZE[1]
    mask = np.zeros((h, w), np.uint8)
    for (x0, y0), (x1, y1) in RAILS:
        cv2.line(mask, (int(x0 * sx), int(y0 * sy)), (int(x1 * sx), int(y1 * sy)), 255, max(3, int(15 * sx)))
    for y in RUNGS:
        left, right = rail_x(RAILS[0], y), rail_x(RAILS[1], y)
        cv2.rectangle(mask, (int((left - 14) * sx), int((y - 11) * sy)), (int((right + 14) * sx), int((y + 11) * sy)), 255, -1)
    rgb, alpha = rgba[..., :3].copy(), rgba[..., 3].copy()
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(int)
    leaves = (hsv[..., 0] > 35) & (hsv[..., 0] < 90) & (hsv[..., 1] > 80)       # the plant stands in front: keep it
    leaves = cv2.morphologyEx(leaves.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
    hole = (mask > 0) & ~leaves
    # Give the transparent background its nearest wall colour first, so the fill never pulls in its stray grey.
    _, (iy, ix) = ndimage.distance_transform_edt(alpha < 128, return_indices=True)
    bgr = cv2.inpaint(cv2.cvtColor(rgb[iy, ix], cv2.COLOR_RGB2BGR), hole.astype(np.uint8) * 255, 6, cv2.INPAINT_TELEA)
    filled = cv2.inpaint(alpha, hole.astype(np.uint8) * 255, 6, cv2.INPAINT_TELEA)
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.where(yy < PARAPET * sy, EDGE[0] * sx, EDGE[1] * sx)
    alpha = np.where(hole, np.where((filled > 140) & (xx <= edge), 255, 0), alpha).astype(np.uint8)
    out = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    # Where the ladder hung over the wall's edge the edge lost its outline: draw it back.
    for y in range(h):
        if hole[y].any():
            solid = np.nonzero(alpha[y] > 128)[0]
            if len(solid) and hole[y, max(0, solid[-1] - 3):solid[-1] + 4].any():
                out[y, max(0, solid[-1] - 1):solid[-1] + 1] = OUTLINE
    return np.dstack([out, alpha])


def paint_out_file(path):
    rgba = np.asarray(Image.open(path).convert("RGBA"))
    Image.fromarray(paint_out(rgba), "RGBA").save(path)


if __name__ == "__main__":
    root = pathlib.Path(__file__).resolve().parents[2]
    paint_out_file(sys.argv[1] if len(sys.argv) > 1 else root / "ArtSource" / "cutouts" / "lane" / "house_turmeric_ladder.png")
