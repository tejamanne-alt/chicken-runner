"""Cuts the neighbour asleep on his rope cot and the neighbour woken (pointing) from his sheet (B5) for level 1's yard.

    python ArtSource/tools/levels/cut_neighbour.py
Writes ArtSource/cutouts/people/neighbour_sleeping.png and neighbour_awake.png: the figures with their cot, on alpha
(the grey sheet keyed out, its soft contact shadow kept faint), as the other people cut-outs are.
"""
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[3]
SHEET = ROOT / "ArtSource" / "references" / "B5_neighbour_sheet.png"
OUT = ROOT / "ArtSource" / "cutouts" / "people"

# boxes on the sheet, as fractions of its width and height (the right half: asleep above, woken below)
BOXES = {"neighbour_sleeping": (0.475, 0.03, 0.99, 0.455), "neighbour_awake": (0.465, 0.395, 0.99, 0.875)}


def background(rgb):
    border = np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3),
                             rgb[:, -8:].reshape(-1, 3)])
    return np.median(border, axis=0)


def main():
    im = np.asarray(Image.open(SHEET).convert("RGB")).astype(np.float32)
    bg = background(im)
    H, W = im.shape[:2]
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (x0, y0, x1, y1) in BOXES.items():
        crop = im[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
        diff = np.linalg.norm(crop - bg, axis=2)
        mx, mn = crop.max(axis=2), crop.min(axis=2)
        sat = (mx - mn) / np.maximum(mx, 1)
        solid = np.clip((diff - 12) / 14, 0, 1)
        # the figure and his cot: the big connected shapes; specks and the other pose's edges dropped
        mask = solid > 0.5
        lab, n = ndimage.label(ndimage.binary_closing(mask, iterations=2))
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.15 * sizes.max()])
        keep = ndimage.binary_fill_holes(keep)
        alpha = np.where(keep, np.maximum(solid, ndimage.binary_erosion(keep, iterations=2)), 0.0)
        # the sheet's grey contact shadow under the cot: faint, as on the other cut-outs
        below = np.zeros(keep.shape, bool)
        below[int(keep.shape[0] * 0.72):] = True          # only under the cot, not stray marks above him
        shadow = (~keep) & below & (sat < 0.1) & (crop.mean(axis=2) < bg.mean() - 6)
        alpha = np.where(shadow, np.clip((bg.mean() - crop.mean(axis=2)) / bg.mean() * 1.2, 0, 0.45), alpha)
        rgb = np.where(shadow[..., None], 0, crop)
        ys, xs = np.nonzero(alpha > 0.02)
        b = (max(0, xs.min() - 6), max(0, ys.min() - 6), min(crop.shape[1], xs.max() + 7), min(crop.shape[0], ys.max() + 7))
        out = np.dstack([rgb, alpha * 255]).astype(np.uint8)[b[1]:b[3], b[0]:b[2]]
        Image.fromarray(out, "RGBA").save(OUT / f"{name}.png")
        print(name, out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()
