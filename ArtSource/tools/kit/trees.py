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
                            lim = ymax(*p["pts"][-1]) if callable(ymax) else ymax
                            yo = float(np.clip(yo, -lim, lim))
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
              transform=None, name="limb", inside=None):
        """Tubes for the paths (or `only` those): returns (thick parts to fuse, thin parts left as they are)."""
        thick, thin = (thick if thick is not None else []), (thin if thin is not None else [])
        for i in (only if only is not None else range(len(self.paths))):
            p = self.paths[i]
            pts, rs = self.polyline(p)
            if pts is None or len(pts) < 2:
                continue
            if transform is not None:
                pts = [transform(v) for v in pts]
                if inside is not None and not all(inside(v) for v in pts):
                    continue
            rs = [v * rscale for v in rs]
            big = float(np.max(p["r"])) * rscale >= fuse_r_px
            segs = seg_thick if float(np.max(p["r"])) > 3 * fuse_r_px else (10 if big else seg_thin)
            ob = self.K.tube(pts, rs, mat, segments=segs, name=name)
            (thick if big else thin).append(ob)
        return thick, thin

    def turned_copies(self, mat, picks, rscale=0.85, thick=None, thin=None, fuse_r_px=3.0, ymax=None, rise=30,
                      whole=True):
        """Copies of whole limbs (path i with everything growing from it above its start), turned `deg` about the
        vertical through the limb's start: picks [(path index, deg, dy)] carry the crown's wood round to the sides
        and back. ymax: each copy is drawn in towards its pivot so it stays within +-ymax in depth."""
        for i, deg, dy in picks:
            p = self.paths[i]
            px0, py0 = p["pts"][0]
            x0, z0 = self.P.x(px0), self.P.z(py0)
            y0 = float(p["y"][0])
            only = [j for j in self.subtree(i) if float(np.max(self.paths[j]["pts"][:, 1])) <= py0 + rise] \
                if whole else [i]
            if i not in only:
                only = [i]
            a = math.radians(deg)
            ca, sa = math.cos(a), math.sin(a)
            shrink = 1.0
            if ymax is not None:
                reach = max(abs(y0 + (self.P.x(x) - x0) * sa + (yy - y0) * ca)
                            for j in only for (x, _), yy in zip(self.paths[j]["pts"], self.paths[j]["y"]))
                if reach > ymax:
                    shrink = max(0.3, (ymax - abs(y0)) / max(1e-6, reach - abs(y0)))

            def tf(v, x0=x0, y0=y0, ca=ca, sa=sa, dy=dy, k=shrink):
                dx, dyy = (v[0] - x0) * k, (v[1] - y0) * k
                return (x0 + dx * ca - dyy * sa, y0 + dx * sa + dyy * ca + dy, v[2])
            thick, thin = self.tubes(mat, fuse_r_px, thick, thin, rscale=rscale, only=only, transform=tf,
                                     name="limb_turned", inside=self.hidden)
        return thick, thin

    def hidden(self, v):
        """True where a point (metres) lies inside the painting's opaque outline (so from the front it is hidden
        behind what is painted there)."""
        P = self.P
        px, py = P.px(v[0]), P.py(v[2])
        if not (0 <= px < P.w and 0 <= py < P.h):
            return False
        return P.rgba[int(py), int(px), 3] > 0.5

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


class Crown:
    """A crown of leaf cards cut from the painting, shaped in depth like the painted outline blown up into a cushion:
    a card at painted spot (px, py) may lie as far forward or back as the crown is deep there (half_depth at its
    heart, falling off round to its painted outline), so from the front it is exactly the painting and from the side
    and above a rounded mass of leaves, not a slab. region_px bounds the crown; `mask` (bool HxW) is its outline
    (default: the painting's opaque pixels in region_px); R (px) how far in from the outline it reaches full depth."""

    def __init__(self, K, region_px, half_depth, centre_px, mask=None, R=None, core=0.15, y0=0.0, dome=None):
        self.K, self.P = K, K.paint
        P = self.P
        self.region, self.hd, self.c, self.core, self.y0 = region_px, half_depth, centre_px, core, y0
        if mask is None:
            mask = (P.rgba[..., 3] > 0.5) & box_mask(P.rgba.shape[:2], [region_px])
            mask = ndimage.binary_closing(mask, iterations=6)
            mask = ndimage.binary_fill_holes(mask)
        self.mask = mask
        self.dist = ndimage.distance_transform_edt(ndimage.gaussian_filter(mask.astype(np.float32), 6) > 0.5)
        self.R = R or float(self.dist.max()) * 0.85
        self.rzu = self.R
        # dome = (py of the crown's widest level, its top py, its bottom py): seen from the side the crown is an
        # ellipse through those, not as deep at its top and bottom as at its middle
        self.dome = dome

    def reach(self, px, py):
        d = self.dist[int(np.clip(py, 0, self.P.h - 1)), int(np.clip(px, 0, self.P.w - 1))]
        t = min(1.0, d / self.R)
        r = math.sqrt(max(0.0, 1 - (1 - t) ** 2))
        if self.dome:
            mid, top, bot = self.dome
            e = (mid - py) / max(1.0, mid - top) if py < mid else (py - mid) / max(1.0, bot - mid)
            r = min(r, math.sqrt(max(0.0, 1 - min(1.0, e) ** 2)))
        return r

    def extent(self, px, py):
        """How far forward / back of y0 the crown reaches at painted spot (px, py), metres."""
        return self.hd * (self.core + (1 - self.core) * self.reach(px, py))

    def front_y(self, px, py, k=1.0):
        return self.y0 - self.extent(px, py) * k

    def cards(self, n, size_px, layer="volume", yaw=40.0, pitch=25.0, region=None, mask=None, name="leaf",
              squash=1.0):
        """n cards: layer "volume" (all through the depth), "front" (the shell facing the camera: the painting) or
        "back" (the shell behind)."""
        K, P = self.K, self.P
        x0, y0, x1, y1 = region or self.region
        alpha = P.rgba[..., 3]
        cx, cy = self.c
        placed = tries = 0
        while placed < n and tries < n * 40:
            tries += 1
            px, py = K.rng.uniform(x0, x1), K.rng.uniform(y0, y1)
            if alpha[int(min(P.h - 1, py)), int(min(P.w - 1, px))] < 0.5:
                continue
            if mask is not None and not mask(px, py):
                continue
            ext = self.extent(px, py)
            if layer == "front":
                yy = self.y0 - ext * K.rng.uniform(0.8, 1.0)
            elif layer == "back":
                yy = self.y0 + ext * K.rng.uniform(0.8, 1.0)
            else:
                yy = self.y0 + K.rng.uniform(-1, 1) * ext * squash
            w, h = size_px[0] * K.rng.uniform(0.75, 1.25), size_px[1] * K.rng.uniform(0.75, 1.25)
            out = Vector((P.x(px) - P.x(cx), (yy - self.y0) * 1.3, P.z(py) - P.z(cy) + P.m(self.rzu) * 0.25))
            K.card_from_painting((px - w / 2, py - h / 2, px + w / 2, py + h / 2), (P.x(px), yy, P.z(py)),
                                 yaw=K.rng.uniform(-yaw, yaw), pitch=K.rng.uniform(-pitch, pitch), name=name,
                                 normal=tuple(out.normalized()) if out.length > 1e-6 else (0, -0.3, 1))
            placed += 1
        return placed

    def inside(self, px, py):
        P = self.P
        return P.rgba[int(np.clip(py, 0, P.h - 1)), int(np.clip(px, 0, P.w - 1)), 3] > 0.5


def fruit_in_crown(K, crown, fruits, mat_for, stalk, back=1, spread=(160, 60), tries=40):
    """Fruit [(px, py, rx, ry)] hanging where they are painted, just in front of the crown's leaves, and `back` more
    of each somewhere else in the crown (inside its painted outline, at any depth), textured with a painted fruit."""
    P = K.paint
    for i, (px, py, rx, ry) in enumerate(fruits):
        fruit(K, px, py, rx, ry, crown.front_y(px, py, 0.9) - P.m(rx), mat_for(i, 0.0, 0.0), stalk)
        for k in range(back):
            for _ in range(tries):
                qx = px + K.rng.uniform(-spread[0], spread[0])
                qy = py + K.rng.uniform(-spread[1], spread[1])
                if crown.inside(qx, qy) and crown.inside(qx, qy - ry * 2) and crown.reach(qx, qy) > 0.25:
                    break
            else:
                continue
            ext = crown.extent(qx, qy)
            fruit(K, qx, qy, rx, ry, crown.y0 + K.rng.uniform(-0.3, 0.95) * ext,
                  mat_for(i, P.x(px) - P.x(qx), P.z(py) - P.z(qy)), stalk)


@model("tree_mango_1", "lane", kind="prop", atlas=2048, leaves=1024)
def tree_mango_1(K):
    """A leaning mango tree: a twisted trunk on splayed roots, one long limb reaching right, a broad lopsided dome of
    leaves, five mangoes, two rocks and low plants at its foot."""
    P = K.paint
    mask, wood = TRACE["tree_mango_1"](K)
    crown = Crown(K, (8, 8, 782, 445), P.m(770) * 0.36, (400, 300), core=0.2, dome=(260, 0, 470))
    wood.grow(spread=0.5, root_z_px=655, root_spread=0.9, ymax=lambda px, py: max(0.4, crown.extent(px, py) * 0.8))
    bark = bark_material(K, mask, axis_x=P.x(250), squeeze=0.9)
    thick, thin = wood.tubes(bark, fuse_r_px=3.0)
    # the big limbs again, turned into the crown's depth, and roots round the back of the foot
    limbs = pick_limbs(wood, py_max=430, r_min=6, min_len=60, n=6)
    picks = [(i, (1 if k % 2 else -1) * K.rng.uniform(60, 120), 0.0) for k, i in enumerate(limbs)]
    wood.turned_copies(bark, picks, thick=thick, thin=thin, ymax=crown.hd * 0.8)
    roots = pick_limbs(wood, r_min=5, min_len=40, n=4, roots=True, root_py=640)
    wood.turned_copies(bark, [(i, K.rng.choice([-1, 1]) * K.rng.uniform(100, 160), 0.0) for i in roots],
                       thick=thick, thin=thin, whole=False, rscale=0.8)
    K.fuse(thick, voxel=0.03, faces=10000)
    # the crown: the painting's leaves on cards through its depth, and the shell facing the camera
    K.leaves_only((0, 0, 789, 470), foliage_pixels)
    crown.cards(230, (110, 95), "volume", yaw=85, pitch=35)
    crown.cards(70, (130, 110), "front", yaw=30, pitch=20)
    crown.cards(40, (120, 100), "back", yaw=30, pitch=20)
    # mangoes, where they hang and more round the back
    fruits = [(211.5, 220, 16.5, 24), (236.5, 269.5, 16.5, 24.5), (222, 291.5, 12.5, 18.5), (648, 305, 11.5, 19),
              (667, 312.5, 17, 24.5)]
    keep = [(int(x - rx + 3), int(y - ry + 3), int(x + rx - 3), int(y + ry - 3)) for x, y, rx, ry in fruits]
    stalk = K.colour((0.25, 0.12, 0.02))
    fruit_in_crown(K, crown, fruits, lambda i, dx, dz: K.projected(squeeze=1.0, keep=keep, inset=2, dx=dx, dz=dz),
                   stalk, back=2)
    # rocks, and the low plants at the foot
    stone = K.tile((160, 655, 250, 695), vary=0.08, soften=0.2)
    rock(K, 206, 704, 130, 66, -0.55, stone)
    rock(K, 441, 704, 92, 50, -0.45, stone)
    rock(K, 300, 704, 80, 44, 1.2, stone)
    rock(K, 120, 704, 50, 30, 0.9, stone)
    K.leaves_only((0, 440, 560, 712), foliage_pixels)
    undergrowth(K, (20, 470, 520, 700), 34, (80, 70), (-1.5, 1.5))
    K.card_from_painting((10, 520, 150, 705), (P.x(80), -0.35, P.z(612)), name="bush_front")
    K.card_from_painting((140, 570, 300, 705), (P.x(220), -0.75, P.z(637)), name="plants_front")
    earth(K, 280, 270, 2.2, (60, 700, 500, 712))
    undergrowth(K, (20, 560, 520, 700), 16, (70, 60), (0.6, 1.8), name="undergrowth_back")


# ====================================================================== solids traced off the painting
def _add(K, bm, mat, name, smooth=True):
    from kitlib import _obj
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=smooth)
    K.parts.append(ob)
    return ob


def prism_x(K, outline_yz, x0, x1, mat, name="prism_x"):
    """An outline [(y, z), ...] in a side plane, extruded across from x0 to x1 (a stair's string wall, a ramp)."""
    bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for y, z in outline_yz]
    b = [bm.verts.new((x1, y, z)) for y, z in outline_yz]
    n = len(outline_yz)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([a[i], a[j], b[j], b[i]])
    return _add(K, bm, mat, name, smooth=False)


def _poly_rows(poly, py):
    """Where a horizontal line at py crosses a polygon: (leftmost, rightmost) x, or None."""
    xs = []
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 <= py < y1) or (y1 <= py < y0):
            xs.append(x0 + (py - y0) * (x1 - x0) / (y1 - y0))
    return (min(xs), max(xs)) if len(xs) >= 2 else None


def poly_solid(K, poly_px, y, mat, depth=0.7, step=None, segments=16, name="solid", bulge=1.0, flat_back=0.0,
               rows=None):
    """A rounded solid whose outline from the front is the polygon poly_px (painted outline, px): each row across
    it a ring as wide as the outline there and depth x as deep (an idol, a lamp, a pad, a heap), centred at depth y
    (a number, or fn(px, py) -> y). flat_back (0..1) flattens its back (a relief, a pad lying on something)."""
    P = K.paint
    ys = [p[1] for p in poly_px]
    top, bot = min(ys), max(ys)
    step = step or max(2.0, (bot - top) / 18)
    levels = rows or list(np.arange(top + 0.5, bot, step)) + [bot - 0.5]
    bm = bmesh.new()
    rings = []
    for py in levels:
        span = _poly_rows(poly_px, py)
        if span is None:
            continue
        x0, x1 = span
        cx, hw = (x0 + x1) / 2, max(0.5, (x1 - x0) / 2)
        yc = y(cx, py) if callable(y) else y
        rw, rd = P.m(hw), P.m(hw) * depth
        ring = []
        for k in range(segments):
            a = 2 * math.pi * k / segments
            sy = math.sin(a)
            dy = rd * sy * (1 - flat_back * 0.7 if sy > 0 else 1.0)
            ring.append(bm.verts.new((P.x(cx) + rw * math.cos(a) * (1 if abs(math.cos(a)) > 0 else 1),
                                      yc + dy * bulge, P.z(py))))
        rings.append(ring)
    if len(rings) < 2:
        bm.free()
        return None
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(segments):
            j = (k + 1) % segments
            bm.faces.new([r0[k], r0[j], r1[j], r1[k]])
    for ring, top_end in ((rings[0], True), (rings[-1], False)):
        c = bm.verts.new(sum((v.co for v in ring), Vector()) / len(ring))
        for k in range(segments):
            j = (k + 1) % segments
            bm.faces.new([ring[k], ring[j], c])
    return _add(K, bm, mat, name)


def raster(shape, strokes, grow=0.0):
    """A bool mask of painted strokes [(px, py, r), ...] polylines drawn as chains of discs (r + grow px)."""
    from PIL import ImageDraw
    im = Image.new("L", (shape[1], shape[0]), 0)
    d = ImageDraw.Draw(im)
    for pts in strokes:
        for (x0, y0, r0), (x1, y1, r1) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 3))
            for k in range(n + 1):
                t = k / n
                x, y, r = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r0 + (r1 - r0) * t + grow
                d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    return np.asarray(im) > 127


def mask_rule(mask, box):
    """A leaves_only keep-rule that is a precomputed mask (HxW) seen through box (integer px inside the painting)."""
    x0, y0, x1, y1 = [int(v) for v in box]

    def keep(rgb, m=mask[y0:y1, x0:x1]):
        return m if m.shape == rgb.shape[:2] else np.ones(rgb.shape[:2], bool)
    return keep


def ring_tube(K, cx, cy, cz, rx, ry, mat, radius, tilt=(0.0, 0.0), segments=48, wobble=0.0, name="ring"):
    """A closed loop (a thread tied round a trunk): centre (metres), radii rx, ry, its height varying by
    tilt = (dz at +x, dz at -y: the front dips)."""
    pts = []
    ph = K.rng.uniform(0, 6.28)
    for k in range(segments + 1):
        a = 2 * math.pi * k / segments
        w = 1 + wobble * math.sin(3 * a + ph)
        x, y = cx + rx * w * math.cos(a), cy + ry * w * math.sin(a)
        z = cz + tilt[0] * math.cos(a) + tilt[1] * (-math.sin(a))
        pts.append((x, y, z))
    pts[-1] = pts[0]
    return K.tube(pts, radius, mat, segments=6, name=name, cap=False)
