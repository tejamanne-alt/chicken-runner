"""Trees, modelled from their paintings. See kitlib.py for the kit.

A tree is its trunk, limbs and roots as real tapering tubes traced along the painted ones (taking the painted bark
from the front, the same bark round the back), a crown of leaf cards cut from the painting's own foliage and spread
through the crown's depth (so it is the painting from the front and a leafy volume from every other side), its fruit
as real fruit, and the rocks and undergrowth at its foot.
"""
import collections
import math

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

from kitlib import Mat, _image, foliage_pixels, model, plant_pixels


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


# ====================================================================== the tracing kit for the other trees
# A painted tree's wood is traced, not guessed: its bark pixels become a mask, the mask's medial axis (skeleton) the
# centre lines of its trunk, limbs, twigs and roots, the distance to the mask's edge their radius. Each line is a
# tapering round tube at its painted place (so from the front the silhouette is the painting's); along the tree, from
# the root out, every limb leans a little forwards or back into the crown's depth (thin ones more than thick ones),
# and copies of the big limbs turned about the trunk carry the crown round the sides and back.
_NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def chan(rgb):
    """r, g, b (int arrays), max, min of an HxWx3 array of 0..255 colours."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    return r, g, b, np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)


def box_mask(shape, boxes, value=True):
    m = np.zeros(shape, bool) if value else np.ones(shape, bool)
    for x0, y0, x1, y1 in boxes:
        m[int(max(0, y0)):int(y1), int(max(0, x0)):int(x1)] = value
    return m


def wood_mask(K, rule, boxes=None, exclude=(), close=2, open_=1, hole=400, min_area=40, extra=None):
    """The painting's wood (bark) pixels: rule(rgb 0..255) -> bool, inside `boxes` (default everywhere), not in
    `exclude`; its ink lines closed, small holes filled, specks dropped. extra: a bool mask OR'd in (hand-painted)."""
    P = K.paint
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    m = rule(rgb) & (P.rgba[..., 3] > 0.5)
    if boxes:
        m &= box_mask(m.shape, boxes)
    if exclude:
        m &= ~box_mask(m.shape, exclude)
    if close:
        m = ndimage.binary_closing(m, iterations=close)
    if hole:
        holes = ndimage.binary_fill_holes(m) & ~m
        lab, n = ndimage.label(holes)
        if n:
            sizes = ndimage.sum(holes, lab, range(1, n + 1))
            m |= np.isin(lab, 1 + np.nonzero(sizes <= hole)[0])
    if open_:
        m = ndimage.binary_opening(m, iterations=open_)
    if extra is not None:
        m |= extra
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.nonzero(sizes >= min_area)[0])
    return m


def _skel_graph(sk):
    """A skeleton's paths between its nodes (ends and forks), as lists of (y, x); and each pixel's degree."""
    pix = set(zip(*[a.tolist() for a in np.nonzero(sk)]))

    def nbrs(p):
        y, x = p
        out = []
        for dy, dx in _NB:
            q = (y + dy, x + dx)
            if q not in pix:
                continue
            if dy and dx and ((y + dy, x) in pix or (y, x + dx) in pix):
                continue                                   # m-connectivity: no diagonal short-cuts round a corner
            out.append(q)
        return out
    nb = {p: nbrs(p) for p in pix}
    deg = {p: len(v) for p, v in nb.items()}
    nodes = {p for p, d in deg.items() if d != 2}
    seen = set()
    paths = []
    for n0 in nodes:
        for q0 in nb[n0]:
            if (n0, q0) in seen:
                continue
            path = [n0, q0]
            seen.add((n0, q0))
            seen.add((q0, n0))
            prev, cur = n0, q0
            while cur not in nodes:
                nxt = [q for q in nb[cur] if q != prev and (cur, q) not in seen]
                if not nxt:
                    break
                q = nxt[0]
                seen.add((cur, q))
                seen.add((q, cur))
                path.append(q)
                prev, cur = cur, q
            paths.append(path)
    return paths, deg


def wood_paths(mask, spur=1.5, min_len=5, smooth=1.2, iters=4):
    """The centre lines of the wood in `mask`: [(points [(x, y)], radii px)], with spurs (stubs shorter than their
    fork's radius x spur + min_len) pruned; plus the distance map."""
    m = mask
    if smooth:
        m = ndimage.gaussian_filter(m.astype(np.float32), smooth) > 0.5
    dt = ndimage.distance_transform_edt(m)
    sk = skeletonize(m)
    for _ in range(iters):
        paths, deg = _skel_graph(sk)
        keep = np.zeros_like(sk)
        changed = False
        for p in paths:
            a, b = p[0], p[-1]
            ea, eb = deg[a] <= 1, deg[b] <= 1
            if ea and eb and len(p) < min_len * 2:
                changed = True
                continue
            if ea != eb:
                j = b if ea else a
                if len(p) < spur * dt[j] + min_len:
                    keep[j] = True
                    changed = True
                    continue
            for q in p:
                keep[q] = True
        sk = skeletonize(keep)
        if not changed:
            break
    paths, deg = _skel_graph(sk)
    return paths, deg, dt


class Wood:
    """A painted tree's traced wood as a graph of paths (pixel centre lines with radii) and the depth (y, metres) of
    every point, grown out from the root."""

    def __init__(self, K, mask, root_px, spur=1.5, min_len=5, smooth=1.2, step=0.7):
        self.K, self.P = K, K.paint
        paths, deg, dt = wood_paths(mask, spur, min_len, smooth)
        self.dt = dt
        self.paths = []
        for p in paths:
            if len(p) < 2:
                continue
            pts = np.array([(x, y) for y, x in p], np.float32)
            r = np.array([dt[y, x] for y, x in p], np.float32)
            # inside a fork the distance map is the parent's radius: hold the child's radius from where it leaves it
            for end in (0, -1):
                node = p[end]
                if deg[node] >= 3:
                    rj = dt[node]
                    d = np.hypot(*(pts - pts[end]).T)
                    out = np.nonzero(d > rj * 0.9)[0]
                    if len(out):
                        k = out[0] if end == 0 else out[-1]
                        inside = d <= rj * 0.9
                        r[inside] = r[k]
            # a free end reaches out to the painted tip
            for end, nxt in ((0, 1), (-1, -2)):
                if deg[p[end]] <= 1 and len(pts) > 2:
                    k = min(len(pts) - 1, 3) if end == 0 else max(0, len(pts) - 4)
                    d = pts[end] - pts[k]
                    if np.hypot(*d) > 0:
                        tip = pts[end] + d / np.hypot(*d) * r[end] * 0.8
                        if end == 0:
                            pts = np.vstack([tip, pts]); r = np.concatenate([[max(0.6, r[0] * 0.5)], r])
                        else:
                            pts = np.vstack([pts, tip]); r = np.concatenate([r, [max(0.6, r[-1] * 0.5)]])
            self.paths.append(dict(pts=pts, r=r, a=p[0], b=p[-1], ends=(deg[p[0]], deg[p[-1]])))
        self.root_px = root_px
        self.step = step

    # -------------------------------------------------------------- depth
    def grow(self, spread=0.35, r_ref=None, root_z_px=None, root_spread=0.8, ymax=None, seed_dy=None):
        """Gives every point a depth: from the root node out, each path's far end moves forward or back by up to
        spread x its length, less for thick wood (radius near r_ref px stays in the painting's plane); paths below
        root_z_px (the roots) splay along the ground. ymax clamps the depth (metres)."""
        K, P = self.K, self.P
        rng = K.rng
        adj = collections.defaultdict(list)
        for i, p in enumerate(self.paths):
            adj[p["a"]].append((i, 0))
            adj[p["b"]].append((i, 1))
        nodes = list(adj)
        rx, ry = self.root_px
        r_ref = r_ref or max(float(np.max(p["r"])) for p in self.paths)
        ynode = {}
        self.parent = {}
        self.children = collections.defaultdict(list)
        done = set()
        order = sorted(nodes, key=lambda n: (n[1] - ry) ** 2 + (n[0] - rx) ** 2)
        for start in order:
            if start in ynode:
                continue
            if start != order[0]:
                # a piece of wood not joined to the tree (bark seen through the leaves): at the depth of the wood
                # nearest to it
                best = None
                for n, yv in ynode.items():
                    d = (n[0] - start[0]) ** 2 + (n[1] - start[1]) ** 2
                    if best is None or d < best[0]:
                        best = (d, yv)
                ynode[start] = (best[1] if best else 0.0) + rng.uniform(-0.3, 0.3) * spread
            else:
                ynode[start] = 0.0
            dq = collections.deque([start])
            while dq:
                n = dq.popleft()
                for i, end in adj[n]:
                    if i in done:
                        continue
                    done.add(i)
                    p = self.paths[i]
                    if end == 1:                              # walk every path away from the root
                        p["pts"], p["r"] = p["pts"][::-1].copy(), p["r"][::-1].copy()
                        p["a"], p["b"] = p["b"], p["a"]
                        p["ends"] = p["ends"][::-1]
                    o = p["b"]
                    seg = np.hypot(*np.diff(p["pts"], axis=0).T)
                    L = P.m(float(seg.sum()))
                    if o not in ynode:
                        rbar = float(np.mean(p["r"]))
                        w = float(np.clip(1 - rbar / r_ref, 0.08, 1.0))
                        if root_z_px is not None and p["pts"][-1][1] > root_z_px:
                            dy = rng.choice([-1, 1]) * rng.uniform(0.35, 1.0) * L * root_spread
                        else:
                            dy = rng.uniform(-1, 1) * spread * L * w
                        if seed_dy is not None:
                            dy = seed_dy(p, dy)
                        yo = ynode[n] + dy
                        if ymax is not None:
                            yo = float(np.clip(yo, -ymax, ymax))
                        ynode[o] = yo
                        dq.append(o)
                        self.children[i] = []
                    t = np.concatenate([[0], np.cumsum(seg)]) / max(1e-6, seg.sum())
                    p["y"] = ynode[n] + (ynode[o] - ynode[n]) * t ** 1.2
                    p["parent_node"] = n
        for i, p in enumerate(self.paths):
            if "y" not in p:
                p["y"] = np.zeros(len(p["pts"]))
        # children: paths that start where path i ends
        starts = collections.defaultdict(list)
        for i, p in enumerate(self.paths):
            starts[p["a"]].append(i)
        for i, p in enumerate(self.paths):
            self.children[i] = [j for j in starts[p["b"]] if j != i]
        return self

    def subtree(self, i, seen=None):
        seen = seen if seen is not None else set()
        if i in seen:
            return []
        seen.add(i)
        out = [i]
        for j in self.children.get(i, []):
            out += self.subtree(j, seen)
        return out

    # -------------------------------------------------------------- geometry
    def polyline(self, p, ys=None):
        """A path resampled every ~step x radius px and smoothed: [(x, y, z) metres], [radius metres]."""
        P = self.P
        pts, r = p["pts"], p["r"]
        y = p["y"] if ys is None else ys
        seg = np.hypot(*np.diff(pts, axis=0).T)
        s = np.concatenate([[0], np.cumsum(seg)])
        if len(pts) > 4:
            k = 2
            pts = np.vstack([pts[:1], np.array([pts[max(0, i - k):i + k + 1].mean(0) for i in range(1, len(pts) - 1)]),
                             pts[-1:]])
        out = [0.0]
        while out[-1] < s[-1]:
            ri = float(np.interp(out[-1], s, r))
            out.append(out[-1] + float(np.clip(ri * self.step, 2.0, 14.0)))
        out[-1] = s[-1]
        ss = np.array(out)
        if len(ss) < 2 or s[-1] <= 0:
            return None, None
        xs, zs = np.interp(ss, s, pts[:, 0]), np.interp(ss, s, pts[:, 1])
        rs, yv = np.interp(ss, s, r), np.interp(ss, s, y)
        return [(P.x(a), b, P.z(c)) for a, b, c in zip(xs, yv, zs)], [P.m(max(0.7, v)) for v in rs]

    def tubes(self, mat, fuse_r_px=3.0, thick=None, thin=None, rscale=1.0, seg_thick=14, seg_thin=6, only=None,
              transform=None, name="limb"):
        """Tubes for the paths (or `only` those): returns (thick parts to fuse, thin parts left as they are)."""
        thick, thin = (thick if thick is not None else []), (thin if thin is not None else [])
        for i in (only if only is not None else range(len(self.paths))):
            p = self.paths[i]
            pts, rs = self.polyline(p)
            if pts is None or len(pts) < 2:
                continue
            if transform is not None:
                pts = [transform(v) for v in pts]
            rs = [v * rscale for v in rs]
            big = float(np.max(p["r"])) * rscale >= fuse_r_px
            segs = seg_thick if float(np.max(p["r"])) > 3 * fuse_r_px else (10 if big else seg_thin)
            ob = self.K.tube(pts, rs, mat, segments=segs, name=name)
            (thick if big else thin).append(ob)
        return thick, thin

    def turned_copies(self, mat, picks, rscale=0.85, thick=None, thin=None, fuse_r_px=3.0):
        """Copies of whole limbs (path i with everything growing from it), turned `deg` about the vertical through
        the limb's start: picks [(path index, deg, dy)] carry the crown's wood round to the sides and back."""
        for i, deg, dy in picks:
            p = self.paths[i]
            x0, z0 = self.P.x(p["pts"][0][0]), self.P.z(p["pts"][0][1])
            y0 = float(p["y"][0])
            a = math.radians(deg)
            ca, sa = math.cos(a), math.sin(a)

            def tf(v, x0=x0, y0=y0, ca=ca, sa=sa, dy=dy):
                dx, dyy = v[0] - x0, v[1] - y0
                return (x0 + dx * ca - dyy * sa, y0 + dx * sa + dyy * ca + dy * (abs(dx) > 0), v[2])
            thick, thin = self.tubes(mat, fuse_r_px, thick, thin, rscale=rscale, only=self.subtree(i), transform=tf,
                                     name="limb_turned")
        return thick, thin

    def debug(self, path):
        """Draws the traced paths over the painting (for checking the trace)."""
        from PIL import ImageDraw
        P = self.P
        im = Image.new("RGBA", P.img.size, (90, 90, 90, 255))
        im.alpha_composite(P.img)
        im = Image.blend(im, Image.new("RGBA", im.size, (255, 255, 255, 255)), 0.45)
        d = ImageDraw.Draw(im)
        for p in self.paths:
            pts = [tuple(v) for v in p["pts"]]
            col = (255, 0, 0) if float(np.max(p["r"])) > 6 else (0, 0, 255)
            d.line(pts, fill=col, width=2)
            for (x, y), r in list(zip(p["pts"], p["r"]))[::6]:
                d.ellipse((x - r, y - r, x + r, y + r), outline=(0, 160, 0))
        im.convert("RGB").save(path)


def bark_material(K, mask, axis_x=0.0, squeeze=0.9, inset=2, name=None):
    """The painting projected straight through along y (like K.projected) but sampling only the wood in `mask`
    (eroded by inset px), every other pixel filled from the nearest wood: so a limb that goes back into the crown, or
    round behind the trunk, is bark, never leaf or sky."""
    P = K.paint
    a = np.asarray(P.img).astype(np.float32).copy()
    ok = ndimage.binary_erosion(mask, iterations=inset) if inset else mask.copy()
    if not ok.any():
        ok = mask
    _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
    a = a[iy, ix]
    a[..., 3] = 255
    pil = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    m = Mat(name or f"{K.name}_bark{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])

    def op(kind, x, y):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        for i, v in enumerate((x, y)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    xx = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["X"], axis_x), squeeze), axis_x)
    u = op("ADD", op("DIVIDE", xx, P.W), 0.5)
    v = op("DIVIDE", sep.outputs["Z"], P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(pil, f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[("bark", len(K._mats))] = m
    return m


def masked_material(K, mask, inset=1, name=None):
    """Like bark_material, with no squeeze: the painting's own pixels in `mask` projected straight through (fruit,
    pods, cactus pads, blades), every other pixel filled from the nearest one in the mask."""
    return bark_material(K, mask, 0.0, 1.0, inset, name)


TRACE = {}            # name -> fn(K) -> (wood mask, Wood): each tree's traced wood (also run by the tracing test)


def orange_bark(rgb):
    r, g, b, mx, mn = chan(rgb)
    return (r > g * 1.18) & (g >= b * 0.85) & (r > 35)


def grey_bark(rgb, sat=34, lo=40, hi=235):
    r, g, b, mx, mn = chan(rgb)
    return (mx - mn < sat) & (mx > lo) & (mx < hi) & ~((g > r + 6) & (g > b + 6))


def _trace_mango_1(K):
    mask = wood_mask(K, orange_bark, exclude=[(195, 188, 236, 246), (213, 243, 262, 300), (200, 262, 242, 318),
                                              (628, 280, 692, 342), (136, 632, 274, 712), (392, 648, 490, 712),
                                              (0, 698, 789, 720)])
    return mask, Wood(K, mask, root_px=(215, 690))


TRACE["tree_mango_1"] = _trace_mango_1


def pick_limbs(wood, py_max=None, py_min=None, r_min=4.0, r_max=40.0, min_len=50.0, n=6, roots=False, root_py=None):
    """Indices of limbs worth turning into the crown's depth (or, with roots=True, roots ending below root_py)."""
    out = []
    for i, p in enumerate(wood.paths):
        x0, y0 = p["pts"][0]
        x1, y1 = p["pts"][-1]
        L = float(np.hypot(*np.diff(p["pts"], axis=0).T).sum())
        rr = float(np.max(p["r"]))
        if L < min_len or not (r_min <= rr <= r_max):
            continue
        if roots:
            if root_py is not None and y1 < root_py:
                continue
        else:
            if py_max is not None and y0 > py_max:
                continue
            if py_min is not None and y0 < py_min:
                continue
        out.append((L * rr, i))
    out.sort(reverse=True)
    return [i for _, i in out[:n]]


def hang_fruit(K, fruits, y, mat_for, stalk, crown_d, back=1, spread=(40, 30), stalk_len=1.4):
    """Fruit [(px, py, rx, ry)] where they hang (at depth y), and `back` more of each somewhere behind in the crown,
    each textured with a real painted fruit (mat_for(i, dx_m, dz_m) -> material shifted onto fruit i)."""
    P = K.paint
    for i, (px, py, rx, ry) in enumerate(fruits):
        yy = y(i) if callable(y) else y
        fruit(K, px, py, rx, ry, yy, mat_for(i, 0.0, 0.0), stalk)
        for k in range(back):
            qx = px + K.rng.uniform(-spread[0], spread[0])
            qy = py + K.rng.uniform(-spread[1], spread[1])
            m = mat_for(i, P.x(px) - P.x(qx), P.z(py) - P.z(qy))
            fruit(K, qx, qy, rx, ry, crown_d * K.rng.uniform(-0.05, 0.42), m, stalk)


def earth(K, cx_px, rx_px, ry, colour_box, y=0.0, z=0.0, segments=36, h=0.04, name="earth"):
    """The patch of earth a tree stands on: a low uneven disc of the painting's own dirt."""
    P = K.paint
    soil = K.colour(colour_box, vary=0.2, scale=6) if len(colour_box) == 4 and max(colour_box) > 2 else \
        K.colour(colour_box, vary=0.2, scale=6)
    rx = P.m(rx_px)
    return K.lathe([(0.0, 0.0), (rx, 0.0), (rx * 0.95, h * 0.6), (rx * 0.6, h), (0.0, h * 1.05)], soil,
                   segments=segments, centre=(P.x(cx_px), y, z), scale_y=ry / rx, wobble=0.1, name=name)


def undergrowth(K, region, n, size, ys, yaw=80, name="undergrowth", centre_fn=None):
    """n cards of the painting's low plants, picked inside region (px) where it is opaque, spread in depth ys."""
    P = K.paint
    x0, y0, x1, y1 = region
    alpha = P.rgba[..., 3]
    placed = tries = 0
    while placed < n and tries < n * 40:
        tries += 1
        cx, cy = K.rng.uniform(x0, x1), K.rng.uniform(y0, y1)
        if alpha[int(min(P.h - 1, cy)), int(min(P.w - 1, cx))] < 0.5:
            continue
        w, h = size[0] * K.rng.uniform(0.8, 1.2), size[1] * K.rng.uniform(0.8, 1.2)
        y = K.rng.uniform(*ys) if centre_fn is None else centre_fn(cx, cy)
        K.card_from_painting((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), (P.x(cx), y, P.z(cy)),
                             yaw=K.rng.uniform(-yaw, yaw), name=name)
        placed += 1


@model("tree_mango_1", "lane", kind="prop", atlas=2048, leaves=1024)
def tree_mango_1(K):
    """A leaning mango tree: a twisted trunk on splayed roots, one long limb reaching right, a broad lopsided dome of
    leaves, five mangoes, two rocks and low plants at its foot."""
    P = K.paint
    mask, wood = TRACE["tree_mango_1"](K)
    crown_d = P.m(770) * 0.72
    wood.grow(spread=0.5, root_z_px=655, root_spread=0.9, ymax=crown_d * 0.42)
    bark = bark_material(K, mask, axis_x=P.x(250), squeeze=0.9)
    thick, thin = wood.tubes(bark, fuse_r_px=3.0)
    # the big limbs again, turned into the crown's depth, and roots round the back of the foot
    limbs = pick_limbs(wood, py_max=430, r_min=6, min_len=60, n=6)
    picks = [(i, (1 if k % 2 else -1) * K.rng.uniform(70, 130), 0.0) for k, i in enumerate(limbs)]
    roots = pick_limbs(wood, r_min=5, min_len=40, n=4, roots=True, root_py=640)
    picks += [(i, K.rng.choice([-1, 1]) * K.rng.uniform(100, 160), 0.0) for i in roots]
    wood.turned_copies(bark, picks, thick=thick, thin=thin)
    K.fuse(thick, voxel=0.03, faces=10000)
    # the crown: the painting's leaves on cards through its depth, and a denser front layer
    K.leaves_only((0, 0, 789, 470), foliage_pixels)
    K.canopy((8, 8, 782, 440), crown_d, n=190, size_px=(120, 100), yaw=40, pitch=25, bulge=0.35, centre_px=(400, 230))
    K.canopy((8, 8, 782, 440), crown_d * 0.25, n=70, size_px=(130, 110), yaw=20, pitch=10, centre_y=-crown_d * 0.3,
             bulge=1.0, centre_px=(400, 230))
    # mangoes, where they hang and more round the back
    fruits = [(211.5, 220, 16.5, 24), (236.5, 269.5, 16.5, 24.5), (222, 291.5, 12.5, 18.5), (648, 305, 11.5, 19),
              (667, 312.5, 17, 24.5)]
    keep = [(int(x - rx + 3), int(y - ry + 3), int(x + rx - 3), int(y + ry - 3)) for x, y, rx, ry in fruits]
    stalk = K.colour((0.25, 0.12, 0.02))

    def mango(i, dx, dz):
        return K.projected(squeeze=1.0, keep=keep, inset=2, dx=dx, dz=dz)
    hang_fruit(K, fruits, lambda i: -crown_d * (0.36 if i in (0, 1, 4) else 0.3), mango, stalk, crown_d, back=1)
    for i, (px, py, rx, ry) in enumerate(fruits):
        if i in (0, 1, 4):
            hang_fruit(K, [(px + K.rng.uniform(-200, 200) * (1 if px < 400 else -1), py + K.rng.uniform(-60, 20), rx, ry)],
                       crown_d * K.rng.uniform(0.15, 0.4), lambda j, dx, dz, i=i, px=px, py=py: mango(i, 0, 0), stalk,
                       crown_d, back=0)
    # rocks, and the low plants at the foot
    stone = K.projected(squeeze=1.0, keep=[(142, 640, 270, 703), (397, 654, 485, 703)], inset=3)
    rock(K, 206, 704, 130, 66, -0.55, stone)
    rock(K, 441, 704, 92, 50, -0.45, stone)
    rock(K, 300, 704, 80, 44, 1.2, K.projected(squeeze=1.0, keep=[(142, 640, 270, 703)], inset=3, dx=P.m(-90)))
    K.leaves_only((0, 440, 560, 712), foliage_pixels)
    undergrowth(K, (20, 470, 520, 700), 34, (80, 70), (-1.5, 1.5))
    K.card_from_painting((10, 520, 150, 705), (P.x(80), -0.35, P.z(612)), name="bush_front")
    K.card_from_painting((140, 570, 300, 705), (P.x(220), -0.75, P.z(637)), name="plants_front")
    earth(K, 260, 300, 2.2, (60, 700, 500, 712))
