"""Trees, modelled from their paintings. See kitlib.py for the kit.

A tree is its trunk, limbs and roots as real tapering tubes traced along the painted ones (taking the painted bark
from the front, the same bark round the back), a crown of leaf cards cut from the painting's own foliage and spread
through the crown's depth (so it is the painting from the front and a leafy volume from every other side), its fruit
as real fruit, and the rocks and undergrowth at its foot.
"""
import collections
import math
import zlib

import bmesh
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

from kitlib import Mat, _image, _vary, foliage_pixels, model, plant_pixels, seamless


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


MANGO2_FRUIT = [(327, 162, 16, 22), (350, 195, 16, 22), (350, 230, 14, 20), (535, 250, 15, 22), (555, 265, 16, 24),
                (162, 305, 15, 22), (120, 410, 15, 22), (640, 405, 15, 22)]


def _trace_mango_2(K):
    fruit_boxes = [(x - rx - 4, y - ry - 8, x + rx + 4, y + ry + 4) for x, y, rx, ry in MANGO2_FRUIT]
    mask = wood_mask(K, orange_bark, exclude=fruit_boxes + [(130, 640, 230, 712), (455, 635, 595, 712),
                                                            (0, 700, 743, 728)])
    return mask, Wood(K, mask, root_px=(365, 690))


@model("tree_mango_2", "lane", kind="prop", atlas=2048, leaves=1024)
def tree_mango_2(K):
    """A mango tree: a thick, twisting trunk on buttress roots, five big limbs, a broad dome of leaves with mangoes
    hanging in it, two rocks and low plants at its foot."""
    P = K.paint
    mask, _ = _trace_mango_2(K)
    wood, crown, bark, thin = traced_tree(
        K, mask, (365, 690), (0, 0, 743, 450), (372, 300), (290, 0, 450), foliage_pixels, spread=0.5, root_z_px=650,
        card_px=(110, 95), n_cards=(230, 80, 45, 25), limb_py_max=420, n_limbs=6, n_roots=4, root_py=660,
        depth_ratio=0.378, core=0.2, dome_pow=0.85, min_r_px=1.5, trunk=(680, 410, 360, 620, 0.6),
        leaf_all=True)                               # its deep-shaded leaves under the crown are not "foliage" green
    # mangoes where they hang, and more round the back
    keep = [(int(x - rx + 3), int(y - ry + 3), int(x + rx - 3), int(y + ry - 3)) for x, y, rx, ry in MANGO2_FRUIT]
    stalk = K.colour((0.1, 0.18, 0.03))
    fruit_in_crown(K, crown, MANGO2_FRUIT, lambda i, dx, dz: K.projected(squeeze=1.0, keep=keep, inset=2, dx=dx, dz=dz),
                   stalk, back=1)
    # rocks and the low plants at the foot
    # (the rocks a tile of their own painted stone: projected, the leaves painted in front of them streaked them)
    stone = K.tile((470, 655, 540, 688), vary=0.08, soften=0.25)
    rock(K, 180, 690, 80, 55, -0.5, stone)
    rock(K, 525, 690, 120, 65, -0.35, stone)
    rock(K, 300, 700, 70, 40, 1.1, stone)
    # the low plants at the foot: cards covering every painted leaf there (exactly the painting from the front), a
    # layer in front of the trunk's foot and one behind it
    K.leaves_only((90, 550, 640, 712))
    low = leaf_mask_of(K, (90, 550, 640, 712), plant_pixels)
    rng = K.rng
    cover_cards(K, low, (70, 60), lambda px, py: -rng.uniform(0.5, 1.3), slope=(0.8, 0.2), name="undergrowth",
                normal=(0, -0.3, 1))
    cover_cards(K, low, (70, 60), lambda px, py: rng.uniform(0.5, 1.3), slope=(0.8, 0.2), name="undergrowth_back",
                normal=(0, 0.3, 1))
    # the patch of earth
    earth(K, 365, 270, P.m(270) * 0.7, (150, 706, 280, 713), h=0.04)


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

    def __init__(self, K, mask, root_px, spur=1.5, min_len=5, smooth=1.2, step=1.2):
        self.K, self.P = K, K.paint
        paths, deg, dt = wood_paths(mask, spur, min_len, smooth)
        self.dt = dt
        self.paths = []
        for p in paths:
            if len(p) < 2:
                continue
            pts = np.array([(x, y) for y, x in p], np.float32)
            r = np.array([dt[y, x] for y, x in p], np.float32)
            # inside a fork the distance map is the junction's radius: from where the limb leaves the junction, ease
            # its radius up into the junction's (a crotch that flares, not a shoulder)
            for end in (0, -1):
                node = p[end]
                if deg[node] >= 3:
                    rj = dt[node]
                    d = np.hypot(*(pts - pts[end]).T)
                    out = np.nonzero(d > rj * 0.9)[0]
                    if len(out):
                        k = out[0] if end == 0 else out[-1]
                        inside = d <= rj * 0.9
                        f = np.clip(1 - d[inside] / (rj * 0.9), 0, 1) ** 1.5
                        r[inside] = r[k] + (max(r[k], rj * 0.8) - r[k]) * f
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
        order = sorted(nodes, key=lambda n: (n[0] - ry) ** 2 + (n[1] - rx) ** 2)       # nodes are (row, col)
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
                if ymax is not None:
                    lim = ymax(start[1], start[0]) if callable(ymax) else ymax
                    ynode[start] = float(np.clip(ynode[start], -lim, lim))
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
        if getattr(self, "r_cap", None):
            r = np.minimum(r, self.r_cap)
        if len(r) > 6:                                    # the distance map is noisy: a limb tapers smoothly
            r = ndimage.median_filter(r, size=7, mode="nearest")
            r = ndimage.uniform_filter1d(r, size=7, mode="nearest")
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
            out.append(out[-1] + float(np.clip(ri * self.step, 4.0, 18.0)))
        out[-1] = s[-1]
        ss = np.array(out)
        if len(ss) < 2 or s[-1] <= 0:
            return None, None
        xs, zs = np.interp(ss, s, pts[:, 0]), np.interp(ss, s, pts[:, 1])
        rs, yv = np.interp(ss, s, r), np.interp(ss, s, y)
        return [(P.x(a), b, P.z(c)) for a, b, c in zip(xs, yv, zs)], [P.m(max(0.7, v)) for v in rs]

    def tubes(self, mat, fuse_r_px=3.0, thick=None, thin=None, rscale=1.0, seg_thick=14, seg_thin=6, only=None,
              transform=None, name="limb", inside=None, min_r_px=0.0, ylim=None):
        """Tubes for the paths (or `only` those): returns (thick parts to fuse, thin parts left as they are)."""
        thick, thin = (thick if thick is not None else []), (thin if thin is not None else [])
        for i in (only if only is not None else range(len(self.paths))):
            p = self.paths[i]
            if float(np.max(p["r"])) < min_r_px:
                continue
            pts, rs = self.polyline(p)
            if pts is None or len(pts) < 2:
                continue
            if transform is not None:
                pts = [transform(v) for v in pts]
                if inside is not None and not all(inside(v) for v in pts):
                    continue
            if ylim is not None:
                pts = [(v[0], float(np.clip(v[1], -ylim(self.P.px(v[0]), self.P.py(v[2])),
                                            ylim(self.P.px(v[0]), self.P.py(v[2])))), v[2]) for v in pts]
            rs = [v * rscale for v in rs]
            big = float(np.max(p["r"])) * rscale >= fuse_r_px
            segs = seg_thick if float(np.max(p["r"])) > 3 * fuse_r_px else (10 if big else seg_thin)
            ob = self.K.tube(pts, rs, mat, segments=segs, name=name)
            (thick if big else thin).append(ob)
        return thick, thin

    def turned_copies(self, mat, picks, rscale=0.85, thick=None, thin=None, fuse_r_px=3.0, ymax=None, rise=30,
                      whole=True, min_r_px=0.0, ylim=None):
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
                                     name="limb_turned", inside=self.hidden, min_r_px=min_r_px, ylim=ylim)
        return thick, thin

    def at(self, px, py):
        """The depth (metres) of the traced wood nearest to painted (px, py)."""
        best = None
        for p in self.paths:
            d = np.hypot(p["pts"][:, 0] - px, p["pts"][:, 1] - py)
            i = int(np.argmin(d))
            if best is None or d[i] < best[0]:
                best = (float(d[i]), float(p["y"][i]), float(p["r"][i]))
        return best[1], best[2]

    def hidden(self, v):
        """True where a point (metres) lies inside the painting's opaque outline (so from the front it is hidden
        behind what is painted there)."""
        P = self.P
        px, py = P.px(v[0]), P.py(v[2])
        if not (0 <= px < P.w and 0 <= py < P.h):
            return False
        c = P.rgba[int(py), int(px)]
        white = min(c[:3]) > 0.7 and max(c[:3]) - min(c[:3]) < 0.16      # the painted white halo / sky gaps
        return c[3] > 0.5 and not white

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
TRACE["tree_mango_2"] = _trace_mango_2


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


def earth(K, cx_px, rx_px, ry, colour_box, y=0.0, z=0.0, segments=36, h=0.04, name="earth"):
    """The patch of earth a tree stands on: a low uneven disc of the painting's own dirt."""
    P = K.paint
    # a box of the painting: a tile of its earth (a plain colour reads as untextured from the side and above)
    if len(colour_box) == 4 and max(colour_box) > 2:
        soil = strip_tile(K, colour_box, soften=0.45, blur=1.0, quilt=True)
    else:
        soil = K.colour(colour_box, vary=0.2, scale=6)
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


def blob_card(K, box_px, centre, yaw=0.0, pitch=0.0, normal=None, name="leaf", n=9, rag=0.22):
    """A leaf card like K.card_from_painting, but cut as a ragged rounded blob inscribed in its box instead of a
    rectangle: its outline is irregular from every side (a rectangle of dense foliage seen from the side or above
    shows straight cut edges and square corners)."""
    from kitlib import _obj
    P = K.paint
    x0, y0, x1, y1 = box_px
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(P.w, x1), min(P.h, y1)
    if cx1 - cx0 < 3 or cy1 - cy0 < 3:
        return None
    c = Vector(centre) + Vector((P.m((cx0 + cx1) / 2 - (x0 + x1) / 2), 0, -P.m((cy0 + cy1) / 2 - (y0 + y1) / 2)))
    x0, y0, x1, y1 = cx0, cy0, cx1, cy1
    hw, hh = P.m(x1 - x0) / 2, P.m(y1 - y0) / 2
    R = Matrix.Rotation(math.radians(yaw), 3, "Z") @ Matrix.Rotation(math.radians(pitch), 3, "X")
    ph = K.rng.uniform(0, 2 * math.pi)
    bm = bmesh.new()
    vs, uvs = [], []
    for k in range(n):
        a = ph + 2 * math.pi * k / n
        rr = 1.0 - rag * K.rng.uniform(0, 1)
        u, v = math.cos(a) * rr, math.sin(a) * rr
        vs.append(bm.verts.new(c + R @ Vector((u * hw, 0, v * hh))))
        px = x0 + (u + 1) / 2 * (x1 - x0)
        py = y1 - (v + 1) / 2 * (y1 - y0)
        uvs.append((px / P.w, 1 - py / P.h))
    f = bm.faces.new(vs)
    layer = bm.loops.layers.uv.new("UVMap")
    for lp, uv in zip(f.loops, uvs):
        lp[layer].uv = uv
    ob = _obj(name, bm, None)
    ob["kit_normal"] = list(normal) if normal is not None else [0.0, -0.35, 1.0]
    K.cards_parts.append(ob)
    return ob


def clear_sky(K, box, exclude=()):
    """Makes the pale sky and the white cut-out halo painted between a crown's leaves and limbs (inside box, not in
    the exclude boxes) transparent in the painting the model is projected from and its cards are cut from: wood seen
    through those gaps then keeps its bark, never a white patch."""
    P = K.paint
    a = np.asarray(P.img).copy()
    r, g, b, mx, mn = chan(a[..., :3].astype(np.int32))
    sky = (mn > 175) & (mx - mn < 45) & (a[..., 3] > 0) & box_mask(mx.shape, [box])
    if exclude:
        sky &= ~box_mask(mx.shape, exclude)
    a[sky, 3] = 0
    P.img = Image.fromarray(a, "RGBA")


# ====================================================================== bark, earth, trunks, cards: the audit's fixes
def _math(nt, kind, a, b):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = kind
    for i, v in enumerate((a, b)):
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = float(v)
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def _tile_socket(m, pil, sw, sh, blend=0.25):
    """In material m: a seamless tile of the image pil, box-projected (one tile sw x sh metres), sampled twice at
    different scales and offsets blended by a soft noise (as K.tile), so it never repeats in a grid. Returns the
    colour socket."""
    nt = m.nt
    img = _image(seamless(pil, blend), f"{m.mat.name}_tile")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    samples = []
    for scale, offset in ((1.0, 0.0), (0.77, 0.381)):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.projection = "BOX"
        tex.projection_blend = 0.3
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (scale / sw, scale / sw, scale / sh)
        mapping.inputs["Location"].default_value = (offset, offset * 0.7, offset * 1.3)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs[0], tex.inputs["Vector"])
        samples.append(tex.outputs["Color"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.9 / max(sw, sh)
    noise.inputs["Detail"].default_value = 2.0
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.4
    ramp.inputs["From Max"].default_value = 0.6
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(ramp.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(samples[0], mix.inputs["A"])
    nt.links.new(samples[1], mix.inputs["B"])
    return mix.outputs["Result"]


def _softened(pil, soften):
    a = np.asarray(pil.convert("RGB")).astype(np.float32)
    if soften:
        med = np.median(a.reshape(-1, 3), axis=0)
        a = a * (1 - soften) + med * soften
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def strip_tile(K, box, soften=0.35, vary=0.08, name=None, blur=0.0, quilt=False):
    """A tile of a strip of the painting (the red earth under a tree, painted as a thin band): the strip mirrored and
    stacked into a square first, so on a wide patch of ground it does not stretch into streaks."""
    P = K.paint
    key = ("trees_strip", tuple(int(v) for v in box), soften, vary, blur, quilt)
    if key in K._mats:
        return K._mats[key]
    crop = P.crop(box).convert("RGBA")
    a = np.asarray(crop).astype(np.float32)
    mx_, mn_ = a[..., :3].max(2), a[..., :3].min(2)
    ok = (a[..., 3] > 200) & ~((mn_ > 175) & (mx_ - mn_ < 45))       # not the white cut-out halo either
    if (~ok).any() and ok.any():                         # fill the crop's transparent or halo pixels first
        _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
        a = a[iy, ix]
    a = a[..., :3]
    w, h = a.shape[1], a.shape[0]
    if quilt:
        # patches of the strip scattered at random over a square with soft edges (mirror-stacking a strip with
        # pebbles in it made rows of the same marks: a herringbone on the ground)
        rng = np.random.default_rng(zlib.crc32(repr(box).encode()))
        side = w
        acc = np.zeros((side, side, 3), np.float64)
        wsum = np.zeros((side, side, 1), np.float64)
        ps = max(4, h)
        yy, xx = np.mgrid[0:ps, 0:ps]
        feather = (np.minimum(np.minimum(yy, ps - 1 - yy), np.minimum(xx, ps - 1 - xx)) + 1.0)[..., None] / (ps / 2)
        for _ in range(int(6 * (side / ps) ** 2)):
            sx, sy = int(rng.integers(0, max(1, w - ps + 1))), int(rng.integers(0, max(1, h - ps + 1)))
            patch = a[sy:sy + ps, sx:sx + ps]
            if patch.shape[:2] != (ps, ps):
                continue
            if rng.uniform() < 0.5:
                patch = patch[:, ::-1]
            if rng.uniform() < 0.5:
                patch = patch[::-1]
            dx, dy = int(rng.integers(-ps // 2, side)), int(rng.integers(-ps // 2, side))
            for oy in (0, -side, side):                    # wrapped round, so the square tiles seamlessly
                for ox in (0, -side, side):
                    x0, y0 = dx + ox, dy + oy
                    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(side, x0 + ps), min(side, y0 + ps)
                    if X1 <= X0 or Y1 <= Y0:
                        continue
                    sl = (slice(Y0 - y0, Y1 - y0), slice(X0 - x0, X1 - x0))
                    acc[Y0:Y1, X0:X1] += patch[sl] * feather[sl]
                    wsum[Y0:Y1, X0:X1] += feather[sl]
        med = np.median(a.reshape(-1, 3), axis=0)
        sq = np.where(wsum > 1e-6, acc / np.maximum(wsum, 1e-6), med)
    else:
        n = max(1, int(round(w / max(1, h))))
        sq = np.concatenate([a if k % 2 == 0 else a[::-1] for k in range(n)], axis=0)
    if blur:
        sq = ndimage.gaussian_filter(sq, (blur, blur, 0))
    pil = _softened(Image.fromarray(sq.clip(0, 255).astype(np.uint8)), soften)
    m = Mat(name or f"{K.name}_strip{len(K._mats)}")
    sw = P.m(w)
    col = _tile_socket(m, pil, sw, sw * pil.height / pil.width)
    if vary:
        col = _vary(m, col, vary, 3.0 / sw)
    m.set_colour(col)
    K._mats[key] = m
    return m


def bark_box(mask, near=None, side=(28, 150)):
    """A box (px) of clean bark for a tile: the square inside the wood mask, round its thickest point (or the
    thickest point near `near` (px, py)), cut well inside its painted outline."""
    dt = ndimage.distance_transform_edt(mask)
    if near is not None:
        yy, xx = np.mgrid[0:mask.shape[0], 0:mask.shape[1]]
        dt = dt * (np.hypot(xx - near[0], yy - near[1]) < 120)
    py, px = np.unravel_index(int(np.argmax(dt)), dt.shape)
    s = float(np.clip(dt[py, px] * 1.1, *side))
    return (int(px - s / 2), int(py - s * 0.6), int(px + s / 2), int(py + s * 0.6))


def bark_mix(K, mask, tile_box=None, squeeze=0.86, inset=2, lo=0.25, hi=0.6, soften=0.3, name=None):
    """The bark of traced wood seen from every side. Where a limb or trunk faces the camera or away from it, the
    painting projected straight through, each pixel squeezed towards the nearest point of the wood's own centre line
    (so a leaning trunk or a limb running any way keeps its painted bark, never its ink outline or the leaves beside
    it); where it faces sideways, or wherever that projection would land off the painted wood, a seamless tile of the
    painted bark (so the sides are bark, not the painting's edge column dragged across into stripes)."""
    P = K.paint
    key = ("trees_bark", id(mask), tile_box, squeeze, inset)
    if key in K._mats:
        return K._mats[key]
    m = Mat(name or f"{K.name}_barkmix{len(K._mats)}")
    nt = m.nt
    # ---- the projection, squeezed towards the centre lines
    sm = ndimage.gaussian_filter(mask.astype(np.float32), 1.2) > 0.5
    sk = skeletonize(sm)
    if not sk.any():
        sk = sm
    dts, (iy, ix) = ndimage.distance_transform_edt(~sk, return_indices=True)
    H, W = mask.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    qx = np.clip(ix + (xx - ix) * squeeze, 0, W - 1).astype(np.int32)
    qy = np.clip(iy + (yy - iy) * squeeze, 0, H - 1).astype(np.int32)
    ok = ndimage.binary_erosion(mask, iterations=inset) if inset else mask
    a = np.asarray(P.img).astype(np.float32)
    rgb = a[qy, qx, :3]
    valid = ok[qy, qx].astype(np.float32)
    valid = ndimage.gaussian_filter(valid, 1.0)
    # off the wood (where the tile shows): the colour of the nearest valid sample, so the blend never reaches black
    good = valid > 0.5
    if good.any() and (~good).any():
        _, (jy, jx) = ndimage.distance_transform_edt(~good, return_indices=True)
        rgb = rgb[jy, jx]
    img = np.dstack([rgb, valid[..., None] * 255]).clip(0, 255).astype(np.uint8)
    proj = Image.fromarray(img, "RGBA")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])
    u = _math(nt, "ADD", _math(nt, "DIVIDE", sep.outputs["X"], P.W), 0.5)
    v = _math(nt, "DIVIDE", sep.outputs["Z"], P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(proj, f"{m.mat.name}_proj")
    tex.image.alpha_mode = "CHANNEL_PACKED"
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    # ---- the tile
    box = tile_box or bark_box(mask)
    crop = _softened(P.crop(box), soften)
    sw = P.m(box[2] - box[0])
    tile = _tile_socket(m, crop, sw, sw * (box[3] - box[1]) / max(1, box[2] - box[0]))
    tile = _vary(m, tile, 0.06, 3.0 / sw)
    # ---- the blend: how squarely the surface faces front or back, times whether the projection is on the wood
    nsep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Normal"], nsep.inputs[0])
    ny = _math(nt, "ABSOLUTE", nsep.outputs["Y"], 0.0)
    face = nt.nodes.new("ShaderNodeMapRange")
    face.interpolation_type = "SMOOTHSTEP"
    face.inputs["From Min"].default_value = lo
    face.inputs["From Max"].default_value = hi
    nt.links.new(ny, face.inputs["Value"])
    w = _math(nt, "MULTIPLY", face.outputs["Result"], tex.outputs["Alpha"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(w, mix.inputs["Factor"])
    nt.links.new(tile, mix.inputs["A"])
    nt.links.new(tex.outputs["Color"], mix.inputs["B"])
    m.set_colour(mix.outputs["Result"])
    K._mats[key] = m
    return m


def earth_patch(K, cx_px, rx_px, ry, box, y=0.0, z=0.0, h=0.04, segments=36, name="earth", soften=0.35):
    """The patch of earth a tree stands on, textured with a tile of the painted earth (box, px) all over (a plain
    colour reads as untextured from the side and above); its rim tucked down to z."""
    P = K.paint
    soil = strip_tile(K, box, soften=soften)
    rx = P.m(rx_px)
    return K.lathe([(0.0, 0.0), (rx, 0.0), (rx * 0.95, h * 0.6), (rx * 0.6, h), (0.0, h * 1.05)], soil,
                   segments=segments, centre=(P.x(cx_px), y, z), scale_y=ry / rx, wobble=0.1, name=name)


def mound(K, cx_px, rx_px, ry, py_rim, py_top, tile_box, y=0.0, segments=44, rings=8, name="earth", wobble=0.08,
          rise=0.6):
    """The patch of earth a tree stands on, as painted: a low mound textured all over with a tile of the painted
    earth (tile_box, px), its rim on the ground at the painted band's front edge (py_rim: the model's foot) and its
    middle `rise` x as high as the band's top (py_top), so from the front it fills the painted band and from the side
    and above it is a gentle rise of red earth, not a flat plain disc. Returns height(x, y) (metres) of its surface,
    for setting stones and roots on it."""
    P = K.paint
    soil = strip_tile(K, tile_box, soften=0.45, blur=1.0, quilt=True)
    rx, z0 = P.m(rx_px), P.z(py_rim)
    h = max(0.005, (P.z(py_top) - z0) * rise)
    prof = [(rx, 0.0)]
    for k in range(1, rings + 1):
        u = 1 - k / rings
        prof.append((rx * u, h * (1 - u * u) ** 0.7))
    K.lathe(prof, soil, segments=segments, centre=(P.x(cx_px), y, z0), scale_y=ry / rx, wobble=wobble, name=name)
    x0 = P.x(cx_px)

    def height(x, yy):
        u2 = ((x - x0) / rx) ** 2 + ((yy - y) / ry) ** 2
        return z0 + (h * (1 - u2) ** 0.7 if u2 < 1 else 0.0)
    return height


def trunk_runs(mask, py_bot, py_top, x_start, step=3, grow=1.2, flare_py=None, flare=0.6):
    """The painted trunk's width down its height: at each row from py_top (where it forks) down to py_bot (the
    ground), the run of wood pixels that continues the trunk (nearest the centre of the row above), as
    [(py, x_left, x_right)], bottom row first. A row where limbs or roots leave the trunk is held round its centre to
    `grow` x the trunk's own width (the median over its rows above flare_py), and below flare_py to up to
    (1 + flare) x that, flaring towards the ground."""
    raw = []
    cx = float(x_start)
    for py in range(int(py_top), int(py_bot) + 1, step):
        py = min(py, mask.shape[0] - 1)
        r = mask[py]
        idx = np.nonzero(np.diff(np.concatenate([[0], r.astype(np.int8), [0]])))[0]
        runs = [(a, b) for a, b in zip(idx[::2], idx[1::2]) if b - a >= 3]
        if not runs:
            continue
        a, b = min(runs, key=lambda ab: 0 if ab[0] <= cx <= ab[1] else min(abs(ab[0] - cx), abs(ab[1] - cx)))
        if not (a - 15 <= cx <= b + 15):
            continue
        raw.append((py, float(a), float(b)))
        cx = (a + b) / 2
    if not raw:
        return []
    while raw[-1][0] < py_bot - step:                # the mask stops short of the ground (grass, stones): carry on
        raw.append((raw[-1][0] + step, raw[-1][1], raw[-1][2]))
    upper = [b - a for py, a, b in raw if flare_py is None or py <= flare_py] or [b - a for _, a, b in raw]
    ref = float(np.median(upper))
    rows = []
    cx = (raw[0][1] + raw[0][2]) / 2
    for py, a, b in raw:
        if flare_py is not None and py > flare_py and rows:
            # below where the roots leave it, a smooth trumpet down to the ground (the painted runs there are roots)
            fpy, fa, fb = next(r for r in reversed(rows) if r[0] <= flare_py) if any(
                r[0] <= flare_py for r in rows) else rows[-1]
            g = 1 + flare * min(1.0, (py - fpy) / max(1.0, py_bot - fpy)) ** 1.5
            c, w = (fa + fb) / 2, (fb - fa) * g
            rows.append((py, c - w / 2, c + w / 2))
            continue
        if b - a > ref * grow:
            c = (a + b) / 2 if abs((a + b) / 2 - cx) < ref * 0.3 else cx
            a, b = c - ref * grow / 2, c + ref * grow / 2
        rows.append((py, a, b))
        cx = (a + b) / 2
    return rows[::-1]


def loft_trunk(K, rows, mat, y=0.0, depth=0.85, max_depth_px=None, segments=20, name="trunk_loft", smooth_rows=3):
    """A trunk lofted through the painted rows [(py, x_left, x_right)]: each row a ring as wide as the trunk is
    painted there and `depth` x as deep (at most max_depth_px, a number or fn(py)), centred at depth y (a number or
    fn(px, py)): from
    the front its outline is exactly the painted trunk's, from the side a round trunk."""
    P = K.paint
    if len(rows) < 2:
        return None
    arr = np.array(rows, np.float32)
    if smooth_rows and len(arr) > smooth_rows * 2:
        for c in (1, 2):
            arr[:, c] = ndimage.uniform_filter1d(arr[:, c], smooth_rows, mode="nearest")
    bm = bmesh.new()
    rings = []
    n = len(arr)
    for i, (py, a, b) in enumerate(arr):
        cx, hw = (a + b) / 2, max(1.0, (b - a) / 2)
        cap = max_depth_px(py) if callable(max_depth_px) else max_depth_px
        hd = hw * depth if cap is None else min(hw * depth, cap)
        # its top rounds off into the limbs, over the last ~half its width
        top_py = float(arr[-1][0])
        t = float(np.clip(1 - abs(py - top_py) / max(3.0, hw * 0.7), 0.0, 1.0))
        hw, hd = hw * (1 - 0.4 * t * t), hd * (1 - 0.4 * t * t)
        yc = y(cx, py) if callable(y) else y
        ring = [bm.verts.new((P.x(cx) + P.m(hw) * math.cos(2 * math.pi * k / segments),
                              yc + P.m(hd) * math.sin(2 * math.pi * k / segments), P.z(py))) for k in range(segments)]
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(segments):
            j = (k + 1) % segments
            bm.faces.new([r0[k], r0[j], r1[j], r1[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return _add(K, bm, mat, name)


def sheared_card(K, box_px, yc, slope=(0.0, 0.0), normal=None, name="leaf", n=9, rag=0.22):
    """A leaf card cut from the painting as a ragged blob inscribed in box_px, every vertex at its painted (x, z)
    and only its depth varying: y = yc + slope[0] (x - x_c) + slope[1] (z - z_c) (a turn about the vertical, or a
    tilt, sheared into depth instead of rotated). Whatever its depth and slope it shows exactly the painting there
    from the front, and from the side or above it is a leafy patch at that depth. Returns (object, outline px)."""
    from kitlib import _obj
    P = K.paint
    x0, y0, x1, y1 = max(0, box_px[0]), max(0, box_px[1]), min(P.w, box_px[2]), min(P.h, box_px[3])
    if x1 - x0 < 3 or y1 - y0 < 3:
        return None, None
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hh = (x1 - x0) / 2, (y1 - y0) / 2
    ph = K.rng.uniform(0, 2 * math.pi)
    bm = bmesh.new()
    vs, uvs, poly = [], [], []
    for k in range(n):
        a = ph + 2 * math.pi * k / n
        rr = 1.0 - rag * K.rng.uniform(0, 1)
        px, py = cx + math.cos(a) * rr * hw, cy - math.sin(a) * rr * hh
        yy = yc + slope[0] * (P.x(px) - P.x(cx)) + slope[1] * (P.z(py) - P.z(cy))
        vs.append(bm.verts.new((P.x(px), yy, P.z(py))))
        uvs.append((px / P.w, 1 - py / P.h))
        poly.append((px, py))
    f = bm.faces.new(vs)
    layer = bm.loops.layers.uv.new("UVMap")
    for lp, uv in zip(f.loops, uvs):
        lp[layer].uv = uv
    ob = _obj(name, bm, None)
    ob["kit_normal"] = list(normal) if normal is not None else [0.0, -0.35, 1.0]
    K.cards_parts.append(ob)
    return ob, poly


def leaf_mask_of(K, box, rule):
    """The pixels a leaves_only rule keeps inside box, as a full-painting bool mask."""
    P = K.paint
    x0, y0, x1, y1 = [int(round(v)) for v in (max(0, box[0]), max(0, box[1]), min(P.w, box[2]), min(P.h, box[3]))]
    a = np.asarray(P.img).copy()
    m = np.zeros((P.h, P.w), bool)
    sub = a[y0:y1, x0:x1]
    m[y0:y1, x0:x1] = rule(sub[..., :3]) & (sub[..., 3] > 127)
    return m


def cover_cards(K, target, size_px, depth, slope=(0.6, 0.3), cover=0.995, n_max=400, name="card", normal=None):
    """Sheared cards (sheared_card) placed until they cover the painted pixels in target (bool HxW): each centred on a
    pixel not yet covered, at depth(px, py) (metres), sheared by up to +-slope (x, z) into depth: from the front
    exactly the painting, from the side a spread of it in depth. The cards show what the leaf rules let them."""
    rng = K.rng
    H, W = target.shape
    covered = np.zeros_like(target)
    total = max(1, int(target.sum()))
    placed = 0
    from PIL import ImageDraw
    while placed < n_max:
        free = np.flatnonzero(target & ~covered)
        if free.size <= (1 - cover) * total:
            break
        py, px = divmod(int(free[rng.integers(free.size)]), W)
        w, h = size_px[0] * rng.uniform(0.8, 1.2), size_px[1] * rng.uniform(0.8, 1.2)
        a = rng.choice([-1, 1]) * rng.uniform(0.3, 1.0) * slope[0]
        b = rng.uniform(-1, 1) * slope[1]
        ob, poly = sheared_card(K, (px - w / 2, py - h / 2, px + w / 2, py + h / 2), depth(px, py), (a, b),
                                normal=normal, name=name)
        if ob is None:
            covered[py, px] = True
            continue
        bx0, by0 = int(max(0, px - w)), int(max(0, py - h))
        bx1, by1 = int(min(W, px + w + 1)), int(min(H, py + h + 1))
        im = Image.new("L", (bx1 - bx0, by1 - by0), 0)
        ImageDraw.Draw(im).polygon([(px + (qx - px) * 0.92 - bx0, py + (qy - py) * 0.92 - by0) for qx, qy in poly],
                                   fill=255)
        covered[by0:by1, bx0:bx1] |= np.asarray(im) > 127
        covered[py, px] = True
        placed += 1
    return placed


class Crown:
    """A crown of leaf cards cut from the painting, shaped in depth like the painted outline blown up into a cushion:
    a card at painted spot (px, py) may lie as far forward or back as the crown is deep there (half_depth at its
    heart, falling off round to its painted outline), so from the front it is exactly the painting and from the side
    and above a rounded mass of leaves, not a slab. region_px bounds the crown; `mask` (bool HxW) is its outline
    (default: the painting's opaque pixels in region_px); R (px) how far in from the outline it reaches full depth."""

    def __init__(self, K, region_px, half_depth, centre_px, mask=None, R=None, core=0.15, y0=0.0, dome=None,
                 dome_pow=0.5):
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
        self.dome, self.dome_pow = dome, dome_pow

    def reach(self, px, py):
        d = self.dist[int(np.clip(py, 0, self.P.h - 1)), int(np.clip(px, 0, self.P.w - 1))]
        t = min(1.0, d / self.R)
        r = math.sqrt(max(0.0, 1 - (1 - t) ** 2))
        if self.dome:
            mid, top, bot = self.dome
            e = (mid - py) / max(1.0, mid - top) if py < mid else (py - mid) / max(1.0, bot - mid)
            r = min(r, max(0.0, 1 - min(1.0, e) ** 2) ** self.dome_pow)
        return r

    def extent(self, px, py):
        """How far forward / back of y0 the crown reaches at painted spot (px, py), metres."""
        return self.hd * (self.core + (1 - self.core) * self.reach(px, py))

    def front_y(self, px, py, k=1.0):
        return self.y0 - self.extent(px, py) * k

    def grad(self, px, py, d=6.0):
        """How the crown's extent changes across the painting at (px, py): (d ext / dx, d ext / dz), metres per
        metre."""
        P = self.P
        gx = (self.extent(px + d, py) - self.extent(px - d, py)) / P.m(2 * d)
        gz = (self.extent(px, py - d) - self.extent(px, py + d)) / P.m(2 * d)
        return gx, gz

    def leaves(self):
        """The pixels the crown's cards can show (the leaves texture's alpha, as finish() makes it from the leaf rules
        registered so far), inside the crown's region: a bool mask."""
        K, P = self.K, self.P
        key = len(K.leaf_rules)
        if getattr(self, "_lm_key", None) == key and self._lm is not None:
            return self._lm
        a = np.asarray(P.img).copy()
        inside = np.zeros(a.shape[:2], bool)
        for (x0, y0, x1, y1), keep in K.leaf_rules:
            inside[int(max(0, y0)):int(y1), int(max(0, x0)):int(x1)] = True
        a[~inside, 3] = 0
        for (x0, y0, x1, y1), keep in K.leaf_rules:
            x0, y0, x1, y1 = [int(round(v)) for v in (max(0, x0), max(0, y0), min(P.w, x1), min(P.h, y1))]
            sub = a[y0:y1, x0:x1]
            sub[..., 3] = np.where(keep(sub[..., :3]), sub[..., 3], 0)
        lm = (a[..., 3] > 127) & box_mask(a.shape[:2], [self.region])
        self._raw = lm
        lm = ndimage.binary_opening(lm, iterations=1)
        self._lm, self._lm_key = lm, key
        return lm

    def cards(self, n, size_px, layer="volume", yaw=40.0, pitch=25.0, region=None, mask=None, name="leaf",
              squash=1.0, max_slope=1.3, cover=0.996, rag=0.22):
        """Cards cut from the painting, every vertex at its painted (x, z) and only its depth varying (sheared_card):
        however deep or turned, from the front each shows exactly the painting where it is, so the crown is the
        painting from the front however many layers it has. layer "front": the shell facing the camera, placed until
        it covers every painted leaf (cover: the share; n is only a guide); "back": the shell behind, the same way;
        "volume": n through the depth, turned (sheared) up to yaw degrees about the vertical and pitch about the
        horizontal; "top": n lying nearly flat in the crown's upper part, for the view from above."""
        K, P = self.K, self.P
        rng = K.rng
        x0, y0, x1, y1 = region or self.region
        lm = self.leaves()
        cx, cy = self.c
        H, W = lm.shape
        if layer == "top":
            return self.top_cards(int(round(n * 3.0)), size_px, region=(x0, y0, x1, y1), name=name)
        shell = layer in ("front", "back")
        if shell:
            # every painted leaf pixel, the thin wisps too (an opened mask left the fine needles at the crown's edge
            # uncovered)
            target = self._raw & box_mask(lm.shape, [(x0, y0, x1, y1)])
            total = max(1, int(target.sum()))
            covered = np.zeros_like(target)
            free = None
            n_max = max(n * 4, 60)
        else:
            n = int(round(n * (3.0 if layer == "top" else 1.3)))    # the top is where a crown is thinnest
            grow = max(2, int(min(size_px) * 0.2))
            near = ndimage.binary_dilation(lm, iterations=grow) & box_mask(lm.shape, [(x0, y0, x1, y1)])
            n_max = n
        placed = tries = 0
        while placed < n_max and tries < n_max * 40:
            tries += 1
            if shell:
                if free is None or placed % 6 == 0:
                    free = np.flatnonzero(target & ~covered)
                    if free.size <= (1 - cover) * total:
                        break
                j = int(free[rng.integers(free.size)])
                py, px = divmod(j, W)
                if covered[py, px]:
                    continue
                px, py = px + rng.uniform(-0.5, 0.5), py + rng.uniform(-0.5, 0.5)
            else:
                px, py = rng.uniform(x0, x1), rng.uniform(y0, y1)
                if not near[int(np.clip(py, 0, H - 1)), int(np.clip(px, 0, W - 1))]:
                    continue
            if mask is not None and not mask(px, py):
                continue
            ext = self.extent(px, py)
            gx, gz = self.grad(px, py)
            # the slopes: a card sheared a (x) into depth shows its painted patch from the side at a x its painted
            # width, so a slope near 1 (a 45 degree turn) shows the leaves at their own size from every side; much
            # less and it is a sliver from the side, much more and its leaves are dragged out into streaks
            if layer == "front":
                yy = self.y0 - ext * rng.uniform(0.8, 1.0)
                a, b = -gx * 0.7 + rng.uniform(-0.5, 0.5), -gz * 0.7 + rng.uniform(-0.4, 0.4)
            elif layer == "back":
                yy = self.y0 + ext * rng.uniform(0.8, 1.0)
                a, b = gx * 0.7 + rng.uniform(-0.5, 0.5), gz * 0.7 + rng.uniform(-0.4, 0.4)
            elif layer == "top":
                yy = self.y0 + rng.uniform(-1, 1) * ext * 0.9
                a = rng.uniform(-0.4, 0.4)
                b = rng.choice([-1, 1]) * rng.uniform(1.0, 1.8)
            else:
                u = rng.uniform(-1, 1)
                yy = self.y0 + math.copysign(abs(u) ** 0.8, u) * ext * squash     # more of them near its surface
                a = rng.choice([-1, 1]) * rng.uniform(0.6, 1.25) * min(1.0, yaw / 60)
                b = rng.uniform(-1, 1) * min(1.0, math.tan(math.radians(min(pitch, 60))))
            lim = max_slope
            a, b = float(np.clip(a, -lim, lim)), float(np.clip(b, -lim, lim))
            if layer == "top":
                k = 0.95
            elif shell:
                k = 1.0
            else:
                k = (0.6 + 0.4 * self.reach(px, py)) * (1 - 0.3 * min(1.0, abs(yy - self.y0) / max(1e-6, ext)))
            w, h = size_px[0] * rng.uniform(0.8, 1.2) * k, size_px[1] * rng.uniform(0.8, 1.2) * k
            out = Vector((P.x(px) - P.x(cx), (yy - self.y0) * 1.3, P.z(py) - P.z(cy) + P.m(self.rzu) * 0.25))
            ob, poly = sheared_card(K, (px - w / 2, py - h / 2, px + w / 2, py + h / 2), yy, (a, b),
                                    normal=tuple(out.normalized()) if out.length > 1e-6 else (0, -0.3, 1), name=name,
                                    rag=rag)
            if ob is None:
                continue
            if shell:
                from PIL import ImageDraw
                bx0, by0 = int(max(0, px - w)), int(max(0, py - h))
                bx1, by1 = int(min(W, px + w + 1)), int(min(H, py + h + 1))
                im = Image.new("L", (bx1 - bx0, by1 - by0), 0)
                # the blob's outline drawn a little inside itself (the leaves near its edge count as covered only
                # once a neighbour reaches over them)
                c0 = (px, py)
                ImageDraw.Draw(im).polygon([(c0[0] + (qx - c0[0]) * 0.92 - bx0, c0[1] + (qy - c0[1]) * 0.92 - by0)
                                            for qx, qy in poly], fill=255)
                covered[by0:by1, bx0:bx1] |= np.asarray(im) > 127
            placed += 1
        return placed

    def top_cards(self, n, size_px, region=None, name="leaf"):
        """n cards lying (nearly) flat over the crown's top, each showing the painted leaves near the top of the crown
        at its x: from the front they are edge-on, so they do not change the painting, and from above they show the
        leaves at their own size (a card sheared up into a flat one would drag them out into streaks). Each lies on
        the crown's dome: at the painted top at its x where the crown is deepest, lower towards its front and back."""
        K, P = self.K, self.P
        rng = K.rng
        lm = self.leaves()
        H, W = lm.shape
        x0, y0, x1, y1 = region or self.region
        cols = lm.any(0)
        top_row = np.where(cols, lm.argmax(0), H)
        placed = tries = 0
        while placed < n and tries < n * 40:
            tries += 1
            px = rng.uniform(x0, x1)
            c = int(np.clip(px, 0, W - 1))
            if not cols[c]:
                continue
            w, h = size_px[0] * rng.uniform(0.8, 1.2), size_px[1] * rng.uniform(0.8, 1.2)
            # from the front it is a thin line: kept inside the crown's painted outline (a margin below its top, and
            # its whole width inside), and behind the front shell
            pt = float(top_row[c]) + max(6.0, h * 0.22)
            row = self.mask[int(np.clip(pt, 0, H - 1))]
            if not row[int(np.clip(px - w * 0.55, 0, W - 1)):int(np.clip(px + w * 0.55, 0, W - 1)) + 1].all():
                continue
            # the leaves it shows: a patch just under the painted top there
            sy = pt + rng.uniform(0.0, 1.0) * size_px[1]
            if not lm[int(np.clip(sy, 0, H - 1)), c]:
                continue
            ext = self.extent(px, pt + size_px[1] * 1.5)
            u = rng.uniform(-0.72, 0.92)
            yy = self.y0 + u * ext
            # its height: on a dome over the crown, the painted top where it is deepest, falling to front and back
            z = P.z(pt) - (1 - math.sqrt(max(0.0, 1 - u * u))) * ext * 0.8
            ob = K.card_from_painting((px - w / 2, sy - h / 2, px + w / 2, sy + h / 2), (P.x(px), yy, z),
                                      yaw=rng.uniform(-90, 90), pitch=90 + rng.uniform(-4, 4), name=name,
                                      normal=(P.x(px) - P.x(self.c[0]), (yy - self.y0) * 1.3, ext * 2.0))
            if ob is not None:
                placed += 1
        return placed

    def cards_rotated(self, n, size_px, layer="volume", yaw=40.0, pitch=25.0, region=None, mask=None, name="leaf",
                      squash=1.0):
        """The earlier cards: n cards turned (rotated) about their centres: layer "volume" (all through the depth),
        "front" (the shell facing the camera: the painting) or "back" (the shell behind)."""
        K, P = self.K, self.P
        x0, y0, x1, y1 = region or self.region
        alpha = P.rgba[..., 3]
        cx, cy = self.c
        if layer != "front":
            n = int(round(n * 1.3))                       # blobs cover less than rectangles: a few more of them
        placed = tries = 0
        while placed < n and tries < n * 40:
            tries += 1
            px, py = K.rng.uniform(x0, x1), K.rng.uniform(y0, y1)
            if alpha[int(min(P.h - 1, py)), int(min(P.w - 1, px))] < 0.5:
                continue
            if mask is not None and not mask(px, py):
                continue
            ext = self.extent(px, py)
            pitch_k = None
            if layer == "front":
                yy = self.y0 - ext * K.rng.uniform(0.8, 1.0)
            elif layer == "top":
                yy = self.y0 + K.rng.uniform(-1, 1) * ext * 0.9
                pitch_k = K.rng.choice([-1, 1]) * K.rng.uniform(60, 90)
            elif layer == "back":
                yy = self.y0 + ext * K.rng.uniform(0.8, 1.0)
            else:
                u = K.rng.uniform(-1, 1)
                yy = self.y0 + math.copysign(abs(u) ** 0.8, u) * ext * squash     # more of them near its surface
            k = 0.6 + 0.4 * self.reach(px, py) if layer != "front" else 1.0      # smaller towards its rim
            if layer != "front":
                k *= 1 - 0.35 * min(1.0, abs(yy - self.y0) / max(1e-6, ext))     # and towards its depth's edge
            if layer == "front":
                k = 1.2                                    # a blob covers less than its box: the front stays whole
            w, h = size_px[0] * K.rng.uniform(0.75, 1.25) * k, size_px[1] * K.rng.uniform(0.75, 1.25) * k
            # the card stays inside the crown's leaf box (beyond it the leaves texture is cut away in a straight line)
            bx0, by0, bx1, by1 = self.region
            l, t, r_, b_ = max(px - w / 2, bx0), max(py - h / 2, by0), min(px + w / 2, bx1), min(py + h / 2, by1)
            if r_ - l < 8 or b_ - t < 8:
                continue
            qx, qy = (l + r_) / 2, (t + b_) / 2
            out = Vector((P.x(qx) - P.x(cx), (yy - self.y0) * 1.3, P.z(qy) - P.z(cy) + P.m(self.rzu) * 0.25))
            blob_card(K, (l, t, r_, b_), (P.x(qx), yy, P.z(qy)), yaw=K.rng.uniform(-yaw, yaw),
                      pitch=K.rng.uniform(-pitch, pitch) if pitch_k is None else pitch_k, name=name,
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
    mask, _ = TRACE["tree_mango_1"](K)
    wood, crown, bark, thin = traced_tree(
        K, mask, (215, 690), (0, 0, 789, 470), (400, 300), (260, 0, 470), foliage_pixels, spread=0.5, root_z_px=655,
        card_px=(110, 95), n_cards=(230, 70, 40, 25), limb_py_max=430, n_limbs=6, n_roots=4, root_py=640,
        depth_ratio=0.351, core=0.2, dome_pow=0.85, min_r_px=1.5, trunk=(650, 430, 260, 590, 0.5))
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
    K.leaves_only((0, 470, 560, 712), foliage_pixels)
    # the low plants: cards covering every painted leaf at the foot (the painting from the front), in front of the
    # trunk's foot and behind it
    low = leaf_mask_of(K, (0, 470, 560, 712), foliage_pixels)
    rng = K.rng
    cover_cards(K, low, (75, 65), lambda px, py: -rng.uniform(0.4, 1.5), slope=(0.8, 0.2), name="undergrowth",
                normal=(0, -0.3, 1))
    cover_cards(K, low, (75, 65), lambda px, py: rng.uniform(0.5, 1.6), slope=(0.8, 0.2), name="undergrowth_back",
                normal=(0, 0.3, 1))
    earth(K, 270, 250, 1.7, (300, 700, 420, 712), h=0.035)


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


# ====================================================================== the peepal katte (and the shrine's tree)
PEEPAL_TRUNK = [(915, 1125, 200), (916, 1040, 188), (918, 960, 168), (920, 880, 160), (918, 780, 150),
                (915, 650, 132), (915, 520, 114), (918, 430, 104), (915, 350, 92), (915, 300, 84)]
PEEPAL_LIMBS = [
    # up into the crown
    [(870, 400, 62), (800, 330, 52), (720, 260, 42), (650, 190, 32), (590, 130, 22)],
    [(900, 330, 56), (885, 250, 46), (872, 180, 36), (870, 110, 26), (880, 60, 16)],
    [(940, 330, 56), (960, 250, 46), (982, 180, 36), (1000, 110, 26), (1010, 70, 16)],
    [(990, 400, 60), (1060, 340, 50), (1140, 300, 42), (1250, 240, 32), (1350, 190, 22)],
    # out to the sides, under the crown's tiers
    [(840, 440, 56), (720, 385, 46), (620, 355, 40), (500, 375, 34), (400, 430, 28), (300, 482, 22), (190, 500, 15)],
    [(1000, 470, 56), (1150, 440, 46), (1250, 432, 40), (1400, 458, 32), (1520, 470, 24), (1640, 482, 15)],
    [(850, 560, 46), (700, 580, 38), (550, 600, 31), (420, 618, 24), (290, 615, 15)],
    [(990, 580, 46), (1150, 590, 38), (1300, 600, 32), (1420, 622, 26), (1560, 650, 17)],
]
PEEPAL_ROOTS = [
    [(735, 1005, 48), (680, 1035, 38), (620, 1062, 30), (520, 1110, 20), (430, 1148, 9)],
    [(760, 1050, 44), (700, 1085, 34), (650, 1112, 26), (550, 1155, 15), (488, 1166, 7)],
    [(790, 1090, 36), (740, 1125, 26), (690, 1150, 16), (640, 1160, 8)],
    [(860, 1030, 44), (856, 1080, 34), (850, 1120, 22), (846, 1150, 10)],
    [(985, 1030, 44), (990, 1080, 34), (996, 1120, 22), (1000, 1150, 10)],
    [(1080, 1005, 48), (1140, 1035, 38), (1190, 1062, 30), (1285, 1110, 20), (1390, 1145, 11), (1440, 1150, 5)],
    [(1070, 1055, 44), (1130, 1085, 34), (1190, 1112, 26), (1280, 1145, 15), (1340, 1156, 7)],
    [(1050, 1100, 36), (1100, 1132, 26), (1150, 1155, 14), (1185, 1162, 6)],
]


class Katte:
    """The stone platform round a sacred tree: a plinth, a body, a coping slab, a gently raised top (in the painting
    seen from a little above; here it rises from its edges to the trunk, so from the front it fills the same band)
    and a flight of steps between string walls in front."""

    def __init__(self, K, x0, x1, half_depth, z_edge_py, z_top_py, xc_px):
        P = K.paint
        self.K, self.P = K, P
        self.X0, self.X1, self.hy = P.x(x0), P.x(x1), half_depth
        self.xc, self.hx = P.x(xc_px), (P.x(x1) - P.x(x0)) / 2
        self.zf, self.h = P.z(z_edge_py), P.z(z_top_py) - P.z(z_edge_py)

    def top(self, x, y):
        """The height of the platform's top at (x, y) metres."""
        a, b = abs(x - self.xc) / self.hx, abs(y) / self.hy
        d = min(1.0, (a ** 4 + b ** 4) ** 0.25)
        return self.zf + self.h * (1 - d)

    def y_on_top(self, px, py, r_px=0.0, side=-1):
        """The depth at which a thing painted at (px, py) (its centre r px above the surface) lies on the top's
        slope facing the camera (side -1) or its back (+1)."""
        P = self.P
        z = P.z(py) - P.m(r_px) * 0.6
        t = (z - self.zf) / max(1e-6, self.h)
        return side * self.hy * float(np.clip(1 - t, 0.0, 1.0))

    def surface(self, mat, n=40):
        K = self.K

        def f(u, v):
            x = self.xc + (2 * u - 1) * self.hx
            y = (2 * v - 1) * self.hy
            return (x, y, self.top(x, y))
        return K.sheet(f, n, n, mat, name="katte_top", thickness=0.0)


def _peepal_tree(K, crown_box, trunk, limbs, roots, katte, bark_box, crown_half_depth, dome, exclude_wood,
                 crown_extra_exclude=None, n_cards=(300, 120, 70), card_px=(190, 160), y0=0.0, ground_roots=0,
                 crown_extra_keep=None, bark_mat=None, root_dirs=(0, 360), sky_exclude=(), bark_tile=None,
                 bark_exclude=()):
    """The peepal over its platform: trunk, limbs and roots fused, roots lying on the platform's top, a domed crown of
    the painting's heart-shaped leaves."""
    P = K.paint
    rng = K.rng
    mask = raster((P.h, P.w), [trunk] + limbs + roots)
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    r, g, b, mx, mn = chan(rgb)
    barkish = (r - b > 35) & (mx < 215) & (mx > 60) & (r >= g)
    bmask = mask & barkish & (P.rgba[..., 3] > 0.5) & box_mask(mask.shape, [bark_box])
    if bark_exclude:
        bmask &= ~box_mask(mask.shape, bark_exclude)
    bark = bark_mix(K, bmask, tile_box=bark_tile)
    # where the painting is solid (not sky, not the white cut-out halo): a limb turned round the trunk must stay
    # behind it, or from the front it pokes out below the crown where the painting shows sky
    solid = (P.rgba[..., 3] > 0.5) & ~((mn > 175) & (mx - mn < 45))
    solid = ndimage.binary_erosion(solid, iterations=2)

    def hidden(x, py, r_px):
        px = P.px(x)
        return all(solid[int(np.clip(py + dy, 0, P.h - 1)), int(np.clip(px + dx, 0, P.w - 1))]
                   for dx, dy in ((0, 0), (-r_px * 0.8, 0), (r_px * 0.8, 0), (0, -r_px * 0.8), (0, r_px * 0.8)))
    crown = Crown(K, crown_box, crown_half_depth, ((crown_box[0] + crown_box[2]) / 2, dome[0]), core=0.12, dome=dome,
                  dome_pow=0.9, y0=y0)
    clear_sky(K, crown_box, sky_exclude)
    # the hand-traced strokes made no thicker than the painting is solid round them: a limb's tube may not reach
    # over the sky painted between the limbs (from the front, bark where the painting shows sky)
    dsolid = ndimage.distance_transform_edt((P.rgba[..., 3] > 0.5) & ~((mn > 175) & (mx - mn < 45)))

    def fit(pts, lo=4.0):
        return [(px, py, float(min(r, max(lo, dsolid[int(np.clip(py, 0, P.h - 1)), int(np.clip(px, 0, P.w - 1))]
                                           + 1))))
                for px, py, r in pts]
    trunk = fit(trunk, lo=20.0)
    limbs = [fit(pts) for pts in limbs]
    wood = [limb(K, trunk, bark, y=y0, segments=24, name="trunk")]
    for k, pts in enumerate(limbs):
        n = len(pts)
        reach = rng.uniform(0.08, 0.25) if rng.uniform() < 0.75 else -rng.uniform(0.0, 0.08)
        # in the painting's plane where it leaves the trunk (threads tied round it stay on it), then into the crown
        ys = [y0, y0] + [y0 + reach * crown.hd * (i - 1) / max(1, n - 2) for i in range(2, n)]
        wood.append(limb(K, pts, bark, y=ys, segments=14, name="limb"))
    # the limbs again, leading off round the trunk (to the sides and back, never across its painted front), holding
    # up the crown all round
    for k, pts in enumerate(limbs):
        x0 = P.x(pts[0][0])
        dirs = (35, 75, 110, 150, -160, -25) if k >= 4 else (rng.uniform(40, 140),)
        for phi in dirs:
            a = math.radians(phi + rng.uniform(-12, 12))
            q = []
            for i, (px, py, r) in enumerate(pts):
                dist = abs(P.x(px) - x0)
                for _ in range(16):                       # stay behind the painted crown, seen from the front
                    x = x0 + dist * math.cos(a)
                    if hidden(x, py, r):
                        break
                    dist *= 0.85
                y = dist * math.sin(a)
                lim = crown.extent(P.px(x), py) * (0.55 if y < 0 else 0.8)
                y = y0 + float(np.clip(y, -lim, lim))
                q.append((x, y, P.z(py) + (rng.uniform(-0.1, 0.0) if i else 0.0)))
            wood.append(K.tube(q, [P.m(r) * 0.9 for _, _, r in pts], bark, segments=12, name="limb_turned"))
    # roots lying on the platform: the painted ones on the slope facing the camera, more round the sides and back
    for pts in roots:
        q, rr = [], []
        for i, (px, py, r) in enumerate(pts):
            y = katte.y_on_top(px, py, r) if i else 0.0
            q.append((P.x(px), y, P.z(py)))
            rr.append(P.m(r))
        q[0] = (q[0][0], q[1][1] * 0.3, q[0][2])
        # its tip lies on the platform's top (on a level top, below where it is painted on the receding top face)
        drop = q[-1][2] - (katte.top(q[-1][0], q[-1][1]) + rr[-1] * 0.4)
        if drop > 0:
            n = len(q)
            q = [(x, y, z - drop * (i / (n - 1)) ** 1.5) for i, (x, y, z) in enumerate(q)]
        wood.append(K.tube(q, rr, bark, segments=12, name="root"))
    xt = P.x(trunk[0][0])
    for k, pts in enumerate(roots):
        for phi in (rng.uniform(20, 160), rng.uniform(20, 160) if k % 2 else rng.choice([-1, 1]) * rng.uniform(0, 15)):
            a = math.radians(phi)
            q, rr = [], []
            for i, (px, py, r) in enumerate(pts):
                dx = P.x(px) - xt
                dy = katte.y_on_top(px, py, r) if i else 0.0
                dist = math.hypot(dx, dy) if i else 0.0
                x, y = xt + dist * math.cos(a), dist * math.sin(a)
                y = float(np.clip(y, -katte.hy * 0.95, katte.hy * 0.95))
                x = float(np.clip(x, katte.X0 + 0.1, katte.X1 - 0.1))
                if hasattr(katte, "clip"):
                    x, y = katte.clip(x, y)
                z = max(P.z(py), katte.top(x, y) + P.m(r) * 0.4) if i else P.z(py)
                if i == len(pts) - 1:
                    z = katte.top(x, y) + P.m(r) * 0.4
                q.append((x, y, z))
                rr.append(P.m(r) * 0.95)
            wood.append(K.tube(q, rr, bark, segments=10, name="root_turned"))
    # roots spreading over the ground all round the foot (where no platform holds them)
    for k in range(ground_roots):
        a = math.radians(root_dirs[0] + (root_dirs[1] - root_dirs[0]) * (k + 0.5 + rng.uniform(-0.3, 0.3)) / ground_roots)
        r0 = P.m(trunk[0][2])
        L = r0 * rng.uniform(1.4, 2.2)
        q = [(P.x(trunk[0][0]) + math.cos(a) * r0 * f, y0 + math.sin(a) * r0 * f, z)
             for f, z in ((0.3, r0 * 0.9), (0.8, r0 * 0.35), (1.0 + L / r0 * 0.5, 0.06), (1.0 + L / r0, 0.02))]
        wood.append(K.tube(q, [r0 * 0.4, r0 * 0.3, r0 * 0.15, r0 * 0.05], bark, segments=10, name="root"))
    trunk_ob = K.fuse(wood, voxel=P.H / 180, faces=8500)
    # the crown: everything painted in its box but the wood modelled there
    # (grown by a pixel only: a wider ring round the modelled wood showed as a see-through slit along every limb
    # once the cards show exactly their painted place)
    excl = raster((P.h, P.w), [fit(st) for st in exclude_wood], grow=1)
    if crown_extra_exclude is not None:
        excl |= crown_extra_exclude
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    r, g, b, mx, mn = chan(rgb)
    halo = (mn > 175) & (mx - mn < 45)
    leaves = (P.rgba[..., 3] > 0.5) & ~excl & ~halo
    leaves = ndimage.binary_opening(leaves, iterations=1)
    if crown_extra_keep is not None:
        leaves |= crown_extra_keep
    box = tuple(int(v) for v in crown_box)
    K.leaves_only(box, mask_rule(leaves, box))
    nv, nf, nb = n_cards
    crown.cards(nv, card_px, "volume", yaw=85, pitch=45)
    crown.cards(nb // 2, card_px, "top", yaw=90, region=(crown_box[0], crown_box[1], crown_box[2], dome[0]))
    crown.cards(nf, (card_px[0] * 1.1, card_px[1] * 1.1), "front", yaw=30, pitch=20)
    crown.cards(nb, card_px, "back", yaw=30, pitch=20)
    return crown, trunk_ob


@model("peepal_platform", "lane", kind="prop", atlas=2048, leaves=2048)
def peepal_platform(K):
    """A great peepal on its stone katte: a stepped platform with a coping, a flight of three steps between string
    walls, the trunk on roots spreading over the top, red and yellow threads tied round it with tassels and a bell,
    Ganesha idols, a small stone and a Nandi at its foot, clay lamps and heaps of flowers, under a vast umbrella of
    golden heart-shaped leaves."""
    P = K.paint
    hy = 2.1
    katte = Katte(K, 206, 1644, hy, 1197, 1122, 925)
    # ---- the platform
    face = K.tile((300, 1245, 640, 1330), vary=0.05, soften=0.35)
    plinth = K.tile((260, 1345, 640, 1385), vary=0.05, soften=0.3)
    coping = K.tile((300, 1201, 640, 1228), vary=0.05, soften=0.3)
    # the top: a tile of its painted stone, squared (a thin strip streaked) and softened (its cracks, mirrored,
    # made a chevron pattern)
    top = strip_tile(K, (200, 1158, 440, 1192), soften=0.6, blur=2.0)
    zb = P.z(1409)                                   # the painted foot of the steps (the game sets it down)
    K.box(P.x(177), P.x(1669), -hy - 0.11, hy + 0.11, zb, P.z(1337), plinth, bevel=0.01, name="plinth")
    K.box(P.x(206), P.x(1644), -hy, hy, P.z(1337), P.z(1231), face, name="body")
    K.box(P.x(181), P.x(1662), -hy - 0.09, hy + 0.09, P.z(1231), P.z(1197), coping, bevel=0.012, name="coping")
    katte.surface(top)
    # the steps, between their string walls
    yf = -hy - 0.09
    for k, top_py in enumerate((1231, 1287, 1341)):
        K.box(P.x(769), P.x(1075), yf - 0.3 * (k + 1), yf + 0.05, zb, P.z(top_py), face, bevel=0.01, name=f"step{k}")
    for x0, x1 in ((681, 769), (1075, 1162)):
        prism_x(K, [(yf + 0.05, zb), (yf - 0.95, zb), (yf - 0.95, P.z(1337)), (yf + 0.05, P.z(1197))],
                P.x(x0), P.x(x1), coping, name="string")
    # ---- the tree
    crown, trunk_ob = _peepal_tree(
        K, (0, 0, 1844, 900), PEEPAL_TRUNK, PEEPAL_LIMBS, PEEPAL_ROOTS, katte, (380, 250, 1480, 1200),
        P.m(1780) * 0.37, (470, 15, 900),
        exclude_wood=[PEEPAL_TRUNK[2:], PEEPAL_LIMBS[0][:3], PEEPAL_LIMBS[1][:2], PEEPAL_LIMBS[2][:2],
                      PEEPAL_LIMBS[3][:3], [(300, 482, 22), (400, 430, 28)], [(1250, 432, 40), (1520, 470, 24)]])
    # ---- the threads tied round the trunk, their tassels and the bell
    red = K.colour((780, 870, 800, 878), vary=0.1)
    yellow = K.colour((800, 893, 820, 899), vary=0.1)
    tx = P.x(918)
    for py_l, py_c, py_r, mat in ((867, 887, 862, red), (875, 895, 866, red), (885, 905, 868, yellow),
                                  (891, 911, 872, yellow), (897, 917, 877, red), (908, 925, 895, red),
                                  (915, 930, 905, yellow)):
        zc = P.z((py_l + py_r) / 2)
        rr = P.m(166)
        ring_tube(K, tx, 0.0, zc, rr, rr, mat, P.m(3.5), tilt=(P.m(py_l - py_r) / 2 * -1, P.m(py_c - (py_l + py_r) / 2)),
                  wobble=0.015, name="thread")
    for px, top_py, bot_py in ((892, 918, 950), (900, 920, 958), (930, 918, 955), (940, 917, 948), (756, 900, 942),
                               (1080, 882, 936)):
        dx = P.x(px) - tx
        yy = -math.sqrt(max(0.0, (P.m(170)) ** 2 - dx * dx)) - 0.02
        K.tube([(P.x(px), yy, P.z(top_py)), (P.x(px) + 0.01, yy - 0.03, P.z((top_py + bot_py) / 2)),
                (P.x(px), yy - 0.02, P.z(bot_py))], P.m(3.5), red, segments=6, name="tassel")
    brass = K.colour((0.42, 0.25, 0.05), vary=0.1)
    by = -P.m(172) - 0.04
    K.tube([(P.x(916), by + 0.02, P.z(925)), (P.x(916), by, P.z(952))], P.m(2), brass, segments=5, name="bell_cord")
    K.lathe([(P.m(r), P.z(py)) for r, py in ((11, 983), (10, 978), (7, 965), (6, 957), (3, 952), (0.5, 951))], brass,
            segments=16, centre=(P.x(916), by, 0.0), name="bell")
    # ---- the idols at its foot (stone, carved: their fronts are the painting, sides and backs plain stone)
    stone = K.colour((920, 1120, 940, 1130), vary=0.08)
    idols = [
        ([(912, 1017), (928, 1017), (940, 1035), (952, 1050), (967, 1062), (967, 1100), (962, 1140), (967, 1145),
          (967, 1162), (875, 1162), (875, 1145), (880, 1140), (874, 1100), (874, 1062), (890, 1050), (900, 1035)], 0.6),
        ([(812, 1050), (826, 1050), (835, 1065), (845, 1072), (855, 1080), (855, 1130), (850, 1150), (857, 1155),
          (857, 1167), (782, 1167), (782, 1155), (788, 1150), (782, 1130), (782, 1080), (795, 1072), (803, 1065)], 0.6),
        ([(749, 1097), (762, 1102), (770, 1115), (772, 1140), (774, 1177), (726, 1177), (728, 1140), (730, 1115),
          (737, 1102)], 0.45),
        ([(990, 1064), (1000, 1070), (1012, 1070), (1022, 1064), (1025, 1080), (1030, 1095), (1060, 1092),
          (1080, 1105), (1088, 1125), (1089, 1150), (1092, 1165), (972, 1165), (974, 1148), (985, 1140), (992, 1110),
          (986, 1090)], 0.5),
    ]
    for poly, depth in idols:
        bot = max(p[1] for p in poly)
        cx = (min(p[0] for p in poly) + max(p[0] for p in poly)) / 2
        y = katte.y_on_top(cx, bot, 0) + P.m(30) * depth
        poly_solid(K, poly, y, stone, depth=depth, name="idol", rows=None)
        # its pedestal: a squared block under it
        x0, x1 = min(p[0] for p in poly), max(p[0] for p in poly)
        K.box(P.x(x0), P.x(x1), y - P.m(x1 - x0) * depth * 0.5, y + P.m(x1 - x0) * depth * 0.5,
              katte.top(P.x(cx), y) - 0.05, P.z(bot - 12), stone, bevel=0.008, name="pedestal")
    # ---- clay lamps with their flames
    clay = K.colour((660, 1168, 685, 1178), vary=0.08)
    flame = K.colour((668, 1148, 674, 1156), vary=0.05)
    for x0, x1, top_py, bot_py, fx in ((654, 690, 1163, 1182, 672), (695, 741, 1168, 1191, 718),
                                       (1076, 1123, 1168, 1191, 1099), (1126, 1156, 1166, 1185, 1141)):
        cx, rw = (x0 + x1) / 2, (x1 - x0) / 2
        y = katte.y_on_top(cx, bot_py, 0)
        zb = katte.top(P.x(cx), y)
        hh = P.m(bot_py - top_py)
        K.lathe([(P.m(rw) * 0.45, 0.0), (P.m(rw) * 0.85, hh * 0.45), (P.m(rw), hh), (P.m(rw) * 0.88, hh * 0.95),
                 (P.m(rw) * 0.5, hh * 0.7), (0.0, hh * 0.65)], clay, segments=18, centre=(P.x(cx), y, zb),
                name="lamp")
        K.lathe([(0.0, 0.0), (P.m(4), P.m(4)), (P.m(3.5), P.m(10)), (0.0, P.m(19))], flame, segments=10,
                centre=(P.x(fx), y, zb + hh * 0.85), name="flame")
    # ---- the flowers heaped in front of the idols: marigolds, jasmine, roses: low heaps, loose flowers on them
    heaps = [(782, 1157, 838, 1192), (848, 1146, 935, 1196), (930, 1150, 1010, 1210), (1010, 1162, 1068, 1194)]
    petals = K.projected(squeeze=1.0, keep=heaps, inset=1)
    for x0, y0, x1, y1 in heaps:
        cx = (x0 + x1) / 2
        poly = [(cx + (x1 - x0) / 2 * math.cos(t), (y0 + y1) / 2 + (y1 - y0) / 2 * math.sin(t))
                for t in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
        poly_solid(K, poly, katte.y_on_top(cx, y1, 0) + P.m(y1 - y0) * 0.3, petals, depth=0.9, name="flowers",
                   segments=12)
    K.leaves_only((770, 1140, 1180, 1212), plant_pixels)
    for i in range(18):
        cx, cy = K.rng.uniform(780, 1170), K.rng.uniform(1150, 1205)
        y = katte.y_on_top(cx, cy, 0) - 0.04
        K.card_from_painting((cx - 22, cy - 16, cx + 22, cy + 16), (P.x(cx), y, P.z(cy)),
                             yaw=K.rng.uniform(-40, 40), pitch=K.rng.uniform(-60, 10), name="flowers")


def wrap_limb(K, a, b, r, mat, n, radius, wobble=0.25, name="thread"):
    """n threads tied round a limb between points a and b (metres), r its radius there: loops round its axis."""
    A, B = Vector(a), Vector(b)
    t = (B - A).normalized()
    ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
    u = t.cross(ref).normalized()
    v = t.cross(u).normalized()
    obs = []
    for k in range(n):
        f = (k + K.rng.uniform(-0.3, 0.3)) / max(1, n - 1) if n > 1 else 0.5
        c = A + (B - A) * float(np.clip(f, 0, 1))
        tilt = K.rng.uniform(-wobble, wobble)
        pts = []
        for i in range(25):
            ang = 2 * math.pi * i / 24
            off = u * math.cos(ang) + v * math.sin(ang)
            pts.append(tuple(c + off * (r * 1.04) + t * (tilt * r * math.sin(ang))))
        obs.append(K.tube(pts, radius, mat, segments=5, name=name, cap=False))
    return obs


def strand(K, top, length, mat, radius, sway=0.06, name="strand"):
    """A thread hanging from `top` (metres): a slightly swinging tube `length` long, with a knot at its end."""
    x, y, z = top
    dx, dy = K.rng.uniform(-sway, sway), K.rng.uniform(-sway, sway)
    pts = [(x, y, z), (x + dx * 0.4, y + dy * 0.4, z - length * 0.4), (x + dx, y + dy, z - length)]
    return K.tube(pts, radius, mat, segments=5, name=name)


SHRINE_TRUNK = [(905, 1395, 245), (905, 1150, 225), (905, 900, 212), (905, 700, 205), (905, 520, 200),
                (905, 400, 195), (905, 320, 175), (905, 280, 150)]
SHRINE_LIMBS = [
    [(860, 300, 70), (823, 273, 60), (783, 220, 50), (740, 160, 38), (700, 110, 26)],
    [(950, 300, 70), (943, 273, 60), (970, 220, 50), (1000, 150, 36), (1030, 90, 22)],
    [(760, 420, 70), (690, 393, 58), (557, 353, 46), (423, 327, 34), (330, 320, 22)],
    [(1050, 420, 70), (1103, 380, 58), (1237, 340, 46), (1397, 313, 34), (1500, 300, 22)],
    [(760, 620, 80), (690, 585, 64), (570, 527, 52), (450, 493, 44), (330, 480, 38), (200, 470, 28), (90, 470, 16)],
    [(1050, 620, 80), (1103, 593, 64), (1210, 540, 54), (1317, 507, 46), (1423, 487, 40), (1530, 467, 30),
     (1650, 462, 20), (1740, 465, 12)],
]


@model("shrine_tree", "lane", kind="prop", atlas=2048, leaves=2048)
def shrine_tree(K):
    """A small white wayside shrine under a great peepal: a lime-washed cell with a deep niche (its deity, a brass
    bell, a marigold garland round the opening), two lamp niches in its face, a heavy cornice, a three-tiered tower
    with finials; behind it the peepal's trunk, its limbs wound with red and orange threads, and its golden crown;
    a painted kalash by the door."""
    P = K.paint
    rng = K.rng
    yt = 0.55                                     # the trunk's depth: the shrine stands against its front
    yb0, yb1 = -1.55, 0.25                        # the shrine's front and back
    # ---- the shrine
    wall = K.tile((680, 1150, 770, 1340), vary=0.05, soften=0.45)
    tower_mat = K.tile((795, 715, 860, 790), vary=0.05, soften=0.4)
    cornice = K.tile((660, 815, 1180, 845), vary=0.05, soften=0.4)
    body = K.box(P.x(640), P.x(1205), yb0, yb1, 0.0, P.z(910), wall, name="shrine_body")
    K.box(P.x(620), P.x(1222), yb0 - 0.05, yb1 + 0.05, P.z(910), P.z(880), cornice, bevel=0.01, name="moulding")
    K.box(P.x(600), P.x(1245), yb0 - 0.12, yb1 + 0.12, P.z(880), P.z(808), cornice, bevel=0.015, name="cornice")
    # the niche: a deep opening, dark inside, its deity on a pedestal, the bell hanging in its mouth
    K.cut(body, P.x(815), P.x(1025), yb0 - 0.1, yb0 + 0.75, P.z(1356), P.z(945))
    dark = K.colour((830, 1000, 860, 1080), vary=0.08)
    K.box(P.x(815), P.x(1025), yb0 + 0.7, yb0 + 0.8, P.z(1356), P.z(945), dark, name="niche_back")
    K.box(P.x(815), P.x(1025), yb0 + 0.05, yb0 + 0.75, P.z(1356) - 0.02, P.z(1356), dark, name="niche_floor")
    for x0, x1 in ((815, 816), (1024, 1025)):
        K.box(P.x(x0) - 0.005, P.x(x1) + 0.005, yb0 + 0.05, yb0 + 0.75, P.z(1356), P.z(945), dark, name="niche_side")
    K.box(P.x(815), P.x(1025), yb0 + 0.05, yb0 + 0.75, P.z(945), P.z(945) + 0.01, dark, name="niche_roof")
    stone = K.colour((880, 1150, 960, 1240), vary=0.08)
    deity = [(918, 1095), (935, 1105), (940, 1125), (962, 1140), (975, 1175), (965, 1200), (980, 1230), (975, 1255),
             (862, 1255), (858, 1230), (872, 1200), (862, 1175), (875, 1140), (897, 1125), (902, 1105)]
    poly_solid(K, deity, yb0 + 0.5, stone, depth=0.55, name="deity")
    K.box(P.x(862), P.x(978), yb0 + 0.38, yb0 + 0.66, P.z(1356), P.z(1255), stone, bevel=0.01, name="deity_pedestal")
    brass = K.colour((880, 1010, 910, 1060), vary=0.08)
    by = yb0 + 0.12
    K.lathe([(P.m(r), P.z(py)) for r, py in ((58, 1095), (57, 1085), (50, 1070), (38, 1030), (33, 1000), (30, 975),
                                             (18, 962), (6, 957), (0.5, 956))], brass, segments=24,
            centre=(P.x(918), by, 0.0), name="bell", cap=False)
    K.lathe([(P.m(r), P.z(py)) for r, py in ((50, 1093), (36, 1040), (28, 990), (0.5, 980))], dark, segments=24,
            centre=(P.x(918), by, 0.0), name="bell_inside", cap=True)
    K.tube([(P.x(922), by, P.z(905)), (P.x(922), by, P.z(958))], P.m(6), brass, segments=6, name="bell_hanger")
    K.lathe([(P.m(r), P.z(py)) for r, py in ((8, 1112), (9, 1102), (5, 1095))], brass, segments=10,
            centre=(P.x(918), by, 0.0), name="clapper")
    # the wooden door frame round the opening and its threshold
    frame = K.colour((790, 1000, 808, 1200), vary=0.06)
    for x0, x1 in ((785, 815), (1025, 1055)):
        K.box(P.x(x0), P.x(x1), yb0 - 0.04, yb0 + 0.12, P.z(1370), P.z(915), frame, bevel=0.006, name="door_post")
    K.box(P.x(785), P.x(1055), yb0 - 0.04, yb0 + 0.12, P.z(945), P.z(915), frame, bevel=0.006, name="lintel")
    K.box(P.x(780), P.x(1060), yb0 - 0.18, yb0 + 0.1, 0.0, P.z(1356), wall, bevel=0.01, name="threshold")
    # the marigold garland round the opening (strings of flowers: a rope of them, with leaf tassels)
    marigold = K.colour((760, 930, 775, 1060), vary=0.25, scale=60)
    leaf = K.colour((0.06, 0.16, 0.03), vary=0.1)
    gy = yb0 - 0.07
    swag = [(765, 905), (790, 950), (845, 975), (900, 935), (925, 900), (950, 935), (1000, 975), (1055, 950),
            (1075, 905)]
    K.tube([P.pt(x, y, gy) for x, y in swag], P.m(11), marigold, segments=8, name="garland")
    for x in (767, 1075):
        K.tube([P.pt(x, 900, gy), P.pt(x, 1000, gy - 0.01), P.pt(x, 1085, gy)], P.m(11), marigold, segments=8,
               name="garland_string")
        K.lathe([(P.m(7), 0), (P.m(9), P.m(8)), (0.0, P.m(16))], leaf, segments=8,
                centre=(P.x(x), gy, P.z(1100)), name="garland_leaf")
    # the two lamp niches in its face, a clay lamp burning in each
    clay = K.colour((1230, 1320, 1280, 1370), vary=0.08)
    flame = K.colour((0.95, 0.6, 0.05), vary=0.05)
    for x0, x1 in ((682, 740), (1105, 1163)):
        K.cut(body, P.x(x0), P.x(x1), yb0 - 0.1, yb0 + 0.16, P.z(1138), P.z(1045))
        K.box(P.x(x0), P.x(x1), yb0 + 0.12, yb0 + 0.18, P.z(1138), P.z(1045), K.colour((690, 1060, 700, 1090),
                                                                                         vary=0.05), name="lamp_niche")
        cx = (x0 + x1) / 2
        K.lathe([(P.m(10), 0.0), (P.m(20), P.m(7)), (P.m(22), P.m(12)), (0.0, P.m(9))], clay, segments=16,
                centre=(P.x(cx), yb0 + 0.06, P.z(1138)), name="lamp")
        K.lathe([(0.0, 0.0), (P.m(5), P.m(6)), (P.m(4), P.m(14)), (0.0, P.m(26))], flame, segments=8,
                centre=(P.x(cx), yb0 + 0.06, P.z(1126)), name="flame")
    # the tower: three tiers stepping in, small domes on each, a front bay with its door, kalasha finials on top
    ty0, ty1 = yb0 + 0.25, yb1 - 0.35
    tc = (ty0 + ty1) / 2
    K.box(P.x(780), P.x(1065), ty0, ty1, P.z(808), P.z(700), tower_mat, bevel=0.01, name="tier1")
    K.box(P.x(870), P.x(970), ty0 - 0.08, ty1, P.z(808), P.z(640), tower_mat, bevel=0.008, name="bay")
    K.cut(K.parts[-1], P.x(902), P.x(942), ty0 - 0.2, ty0 + 0.05, P.z(808), P.z(725))
    K.box(P.x(902), P.x(942), ty0 + 0.0, ty0 + 0.04, P.z(808), P.z(725), dark, name="tower_door")
    K.box(P.x(802), P.x(1045), ty0 + 0.08, ty1 - 0.08, P.z(700), P.z(600), tower_mat, bevel=0.01, name="tier2")
    K.box(P.x(825), P.x(1020), ty0 + 0.16, ty1 - 0.16, P.z(600), P.z(470), tower_mat, bevel=0.01, name="tier3")
    K.box(P.x(815), P.x(1030), ty0 + 0.12, ty1 - 0.12, P.z(478), P.z(462), tower_mat, bevel=0.005, name="tier3_cap")

    def dome(px, top_py, bot_py, r_px, y):
        K.lathe([(P.m(r_px), 0.0), (P.m(r_px) * 1.05, P.m(bot_py - top_py) * 0.35),
                 (P.m(r_px) * 0.8, P.m(bot_py - top_py) * 0.7), (P.m(r_px) * 0.25, P.m(bot_py - top_py) * 0.92),
                 (0.0, P.m(bot_py - top_py))], tower_mat, segments=16, centre=(P.x(px), y, P.z(bot_py)), name="dome")
    for px in (802, 860, 980, 1042):
        for y in (ty0 + 0.06, ty1 - 0.06):
            dome(px, 655, 700, 22, y)
    dome(920, 645, 700, 28, ty0 - 0.02)
    for px in (822, 875, 965, 1025):
        for y in (ty0 + 0.14, ty1 - 0.14):
            dome(px, 585, 610, 17, y)
    dome(922, 490, 545, 27, ty0 + 0.12)
    for px in (862, 892, 922, 952, 984):
        K.lathe([(P.m(r), P.z(py)) for r, py in ((9, 472), (11, 462), (7, 452), (4, 445), (6, 440), (0.5, 430))],
                tower_mat, segments=12, centre=(P.x(px), tc, 0.0), name="finial")
    # ---- the peepal behind it (the painted skeins of thread hanging from its limbs go on cards with its leaves)
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    r, g, b, mx, mn = chan(rgb)
    skein = (r > 150) & (r - b > 110) & (g < 0.8 * r) & (P.rgba[..., 3] > 0.5)
    skein = ndimage.binary_dilation(skein, iterations=1) & (P.rgba[..., 3] > 0.5)
    skein &= box_mask(skein.shape, [(370, 470, 800, 800), (1020, 490, 1350, 790)])
    crown, trunk_ob = _peepal_tree(
        K, (0, 0, 1844, 790), SHRINE_TRUNK, SHRINE_LIMBS, [], None, (300, 200, 1600, 800), P.m(1780) * 0.36,
        (440, 10, 790),
        exclude_wood=[SHRINE_TRUNK[3:-2] + [(905, 340, 120)], SHRINE_LIMBS[0][:2], SHRINE_LIMBS[1][:2],
                      SHRINE_LIMBS[2][:3], SHRINE_LIMBS[3][:3], SHRINE_LIMBS[4][:6], SHRINE_LIMBS[5][:7]],
        crown_extra_exclude=box_mask((P.h, P.w), [(380, 470, 1350, 800)]), y0=yt, ground_roots=6,
        crown_extra_keep=skein, bark_tile=(835, 300, 900, 400), root_dirs=(55, 125),
        bark_exclude=[(590, 420, 1260, 1412), (760, 420, 1085, 820)],
        sky_exclude=[(760, 420, 1085, 820)])
    # ---- the threads tied round its limbs and trunk, hanging in skeins (the painted skeins as cards in front)
    red = K.colour((0.6, 0.06, 0.02), vary=0.12)
    orange = K.colour((0.85, 0.3, 0.03), vary=0.12)
    for limb_pts, segs in ((SHRINE_LIMBS[4], [(1, 2), (3, 4)]), (SHRINE_LIMBS[5], [(2, 3)])):
        for i0, i1 in segs:
            a, b = limb_pts[i0], limb_pts[i1]
            for mat in (red, orange):
                wrap_limb(K, (P.x(a[0]), yt, P.z(a[1])), (P.x(b[0]), yt, P.z(b[1])), P.m((a[2] + b[2]) / 2), mat,
                          5, P.m(2.5))
    for py in range(600, 770, 18):
        ring_tube(K, P.x(905), yt, P.z(py), P.m(212), P.m(212), rng.choice([red, orange]), P.m(2.5),
                  tilt=(rng.uniform(-0.05, 0.05), rng.uniform(0.0, 0.08)), wobble=0.03, name="thread")
    # the painted skeins in front of the trunk: cards covering every painted skein pixel, sheared into depth
    def skein_y(px, py):
        # hanging just in front of the trunk where it is behind them, else in front of the limb they are tied to
        R, dx = P.m(212), P.m(px - 905)
        front = math.sqrt(R * R - dx * dx) if abs(dx) < R * 0.97 else P.m(45)
        return yt - max(front, P.m(45)) - 0.05 - rng.uniform(0, 0.05)
    cover_cards(K, skein, (80, 110), skein_y, slope=(0.5, 0.15), name="skein", normal=(0.0, -0.6, 0.8))
    # ---- the kalash by the door: a painted pot of water, mango leaves and a coconut in its mouth
    pot = K.projected(axis_x=P.x(1253), squeeze=0.93, keep=[(1214, 1300, 1296, 1392)])
    prof = [(28, 1393), (36, 1385), (42, 1360), (40, 1330), (30, 1310), (18, 1302), (20, 1296), (16, 1292)]
    K.lathe([(P.m(r), P.z(py)) for r, py in prof], pot, segments=24, centre=(P.x(1253), yb0 + 0.1, 0.0), name="kalash")
    coconut = K.colour((0.35, 0.16, 0.05), vary=0.1)
    K.lathe([(P.m(r), P.z(py)) for r, py in ((14, 1296), (16, 1290), (12, 1280), (4, 1272), (0.5, 1268))], coconut,
            segments=12, centre=(P.x(1253), yb0 + 0.1, 0.0), name="coconut")
    K.leaves_only((1215, 1265, 1300, 1300), plant_pixels)
    for yaw in (0, 60, -60, 120):
        K.card_from_painting((1215, 1265, 1300, 1300), (P.x(1257), yb0 + 0.1, P.z(1282)), yaw=yaw, name="mango_leaves")
    # ---- the beaten earth it stands on
    earth(K, 905, 520, 2.4, (500, 1393, 1600, 1400), y=yt * 0.4, h=0.03)


def _trace_field_tree_1(K):
    def rule(rgb):
        r, g, b, mx, mn = chan(rgb)
        return grey_bark(rgb, sat=40, lo=45, hi=200) & ~((r - g > 14) & (mx < 110))
    mask = wood_mask(K, rule, boxes=[(0, 280, 938, 960)], close=2, hole=600, min_area=30)
    return mask, Wood(K, mask, root_px=(470, 930), spur=1.3, min_len=6)


TRACE["field_tree_1"] = _trace_field_tree_1


def hanging(p, r_max=6.0, min_drop=40):
    """True for a path that hangs: thin and running downwards (an aerial root, a pod's stalk)."""
    return float(np.max(p["r"])) <= r_max and p["pts"][-1][1] - p["pts"][0][1] > min_drop and \
        abs(p["pts"][-1][0] - p["pts"][0][0]) < (p["pts"][-1][1] - p["pts"][0][1]) * 0.5


@model("field_tree_1", "fields", kind="prop", atlas=2048, leaves=1024)
def field_tree_1(K):
    """A banyan: a thick, twisting grey trunk on a spread of great roots, limbs reaching out under a broad dark-green
    dome, aerial roots hanging from them in curtains, a mound of red earth with pebbles."""
    P = K.paint
    rng = K.rng
    mask, _ = TRACE["field_tree_1"](K)

    def seed(p, dy):
        return 0.0 if hanging(p) else dy
    wood, crown, bark, thin = traced_tree(
        K, mask, (470, 930), (0, 0, 938, 510), (470, 300), (300, 0, 510), foliage_pixels, spread=0.55,
        root_z_px=860, card_px=(110, 95), n_cards=(230, 90, 50, 30), limb_py_max=560, limb_py_min=300, n_limbs=7,
        n_roots=6, root_py=880, depth_ratio=0.365, core=0.18, dome_pow=0.9, seed_dy=seed, min_r_px=1.5,
        trunk=(940, 560, 465, 860, 0.7), leaf_all=True)          # its dark shaded leaves are not "foliage" green
    # the aerial roots again, hanging in curtains through the crown's depth behind and before the painted ones
    for i, p in enumerate(wood.paths):
        if hanging(p):
            for k in range(2):
                dy = rng.uniform(0.4, 1.0) * crown.extent(*p["pts"][0]) * rng.choice([-0.6, 1.0])
                pts, rs = wood.polyline(p, p["y"] + dy)
                if pts is not None and len(pts) > 1:
                    K.tube(pts, [r * 0.7 for r in rs], bark, segments=6, name="aerial_root")
    # the mound of red earth at its foot, pebbles on it
    ground = mound(K, 455, 335, 2.6, 980, 945, (300, 950, 600, 964))
    stone = K.colour((0.32, 0.3, 0.27), vary=0.15)
    for px, w in ((222, 16), (418, 20), (478, 18), (520, 14), (650, 12), (300, 12)):
        y = rng.uniform(-1.6, -0.6)
        K.boulder(P.x(px), y, ground(P.x(px), y) + P.m(w * 0.6) * 0.35, P.m(w), P.m(w) * 0.75, P.m(w * 0.6) * 1.1,
                  stone)
    for k in range(6):
        a = rng.uniform(0, 2 * math.pi)
        x, y = P.x(455) + math.cos(a) * rng.uniform(1.0, 3.0), math.sin(a) * rng.uniform(1.0, 2.4)
        K.boulder(x, y, ground(x, y) + 0.03, 0.18, 0.14, 0.12, stone)


def _trace_field_tree_2(K):
    def rule(rgb):
        r, g, b, mx, mn = chan(rgb)
        return (mx - mn < 45) & (mx < 170) & (mx > 25) & ~((g > r + 3) & (g > b + 12)) & (r >= b)
    mask = wood_mask(K, rule, boxes=[(0, 0, 525, 528)], exclude=[(160, 478, 208, 530), (312, 488, 352, 530),
                                                                 (150, 518, 400, 560)], close=1, hole=300, min_area=40)
    return mask, Wood(K, mask, root_px=(255, 525), spur=1.3, min_len=5)


TRACE["field_tree_2"] = _trace_field_tree_2


def sage_leaves(rgb):
    """The pale sage-green leaves of the fields' trees (and their dark outlines), not their white cut-out halo."""
    r, g, b, mx, mn = chan(rgb)
    green = (g >= r - 4) & (g > b + 8) & (mx < 235) & ~((mn > 165) & (mx - mn < 45))
    keep = ndimage.binary_opening(ndimage.binary_closing(green, iterations=1), iterations=1)
    keep |= (mx < 80) & ndimage.binary_dilation(keep, iterations=2)
    return keep


def sage_inked(rgb):
    """sage_leaves with their whole ink outline (sage_leaves keeps only the darkest ink: the paler grey outline round
    each leaf went missing, a red rim round every leaf from the front)."""
    r, g, b, mx, mn = chan(rgb)
    lv = sage_leaves(rgb)
    return lv | ((mx < 130) & ~((mn > 175) & (mx - mn < 45)) & ndimage.binary_dilation(lv, iterations=3))


@model("field_tree_2", "fields", kind="prop", atlas=2048, leaves=1024)
def field_tree_2(K):
    """A gnarled old tree: a twisting, knotted trunk leaning one way then the other, crooked limbs splitting into
    knobbly twigs, sprays of feathery sage leaves at their ends, grass tufts and stones on a mound of red earth."""
    P = K.paint
    rng = K.rng
    mask, _ = TRACE["field_tree_2"](K)
    ground = mound(K, 263, 131, 1.0, 553, 525, (180, 540, 340, 550))

    def foot(bark):
        # the foot flares into roots all round, down onto the earth
        out = []
        x0, r0 = P.x(258), P.m(48)
        for k in range(7):
            a = 2 * math.pi * (k + rng.uniform(-0.25, 0.25)) / 7
            x1, y1 = x0 + math.cos(a) * r0 * 2.0, math.sin(a) * r0 * 2.0
            out.append(K.tube([(x0 + math.cos(a) * r0 * 0.2, math.sin(a) * r0 * 0.2, P.z(470)),
                               (x0 + math.cos(a) * r0 * 0.9, math.sin(a) * r0 * 0.9, P.z(505)),
                               (x1, y1, ground(x1, y1) + r0 * 0.05)],
                              [r0 * 0.45, r0 * 0.3, r0 * 0.1], bark, segments=10, name="root"))
        return out
    wood, crown, bark, thin = traced_tree(
        K, mask, (255, 525), (0, 0, 525, 410), (262, 220), (220, 0, 410), sage_inked, spread=0.6, root_z_px=505,
        card_px=(70, 60), n_cards=(220, 100, 50, 20), limb_py_max=330, n_limbs=7, n_roots=0, depth_ratio=0.343,
        core=0.2, dome_pow=0.9, min_r_px=2.2, trunk=(536, 380, 300, 500, 0.25), foot=foot)
    # grass tufts and stones on the earth
    K.leaves_only((150, 470, 360, 530), plant_pixels)
    for box, cx in (((160, 470, 210, 528), 185), ((312, 485, 352, 528), 332)):
        for yaw in (0, 60, -60):
            y = rng.uniform(-0.5, -0.2)
            K.card_from_painting(box, (P.x(cx), y, P.z((box[1] + box[3]) / 2)), yaw=yaw, name="grass")
    for k in range(5):
        cx = rng.uniform(150, 360)
        y = rng.uniform(0.2, 0.8)
        zc = ground(P.x(cx), y) + P.m(20)
        K.card_from_painting((cx - 20, 488, cx + 20, 528), (P.x(cx), y, zc), yaw=rng.uniform(-80, 80), name="grass")
    stone = K.tile((250, 528, 272, 542), vary=0.08)
    for px, w, h, y in ((170, 22, 13, -0.55), (212, 26, 15, -0.7), (258, 26, 16, -0.6), (310, 20, 12, -0.65),
                        (360, 20, 12, -0.4), (230, 22, 14, 0.7), (300, 26, 16, 0.8), (190, 18, 12, 0.3)):
        x = P.x(px)
        K.boulder(x, y, ground(x, y) + P.m(h) * 0.4, P.m(w), P.m(w) * 0.75, P.m(h) * 1.1, stone)


def culm(K, pts, radius, mat, node_mat, node_every=0.55, node_r=1.18, segments=8, name="culm"):
    """A bamboo culm: a tube along pts (metres) with radii, and a raised ring at every node (node_every metres)."""
    ob = K.tube(pts, radius, mat, segments=segments, name=name)
    rr = list(radius) if isinstance(radius, (list, tuple)) else [radius] * len(pts)
    seg = [(Vector(b) - Vector(a)).length for a, b in zip(pts, pts[1:])]
    total = sum(seg)
    s = node_every * K.rng.uniform(0.3, 0.9)
    while s < total - 0.05:
        acc, i = 0.0, 0
        while i < len(seg) - 1 and acc + seg[i] < s:
            acc += seg[i]
            i += 1
        t = (s - acc) / max(1e-6, seg[i])
        c = Vector(pts[i]).lerp(Vector(pts[i + 1]), t)
        d = (Vector(pts[i + 1]) - Vector(pts[i])).normalized()
        r = (rr[i] + (rr[i + 1] - rr[i]) * t) * node_r
        K.tube([tuple(c - d * r * 0.25), tuple(c + d * r * 0.25)], r, node_mat, segments=segments, name="node")
        s += node_every * K.rng.uniform(0.85, 1.15)
    return ob


@model("field_tree_3", "fields", kind="prop", atlas=2048, leaves=1024)
def field_tree_3(K):
    """A clump of bamboo: a sheaf of tall jointed green culms rising from a knot of roots, fanning out and arching
    over at the top under sprays of narrow leaves."""
    P = K.paint
    rng = K.rng
    green = K.colour((250, 600, 258, 700), vary=0.12, scale=20)
    node = K.colour((0.03, 0.045, 0.02), vary=0.1)
    base_py, cx = 768, 245
    alpha = P.rgba[..., 3]
    crown = Crown(K, (0, 0, 511, 640), P.m(480) * 0.34, (250, 300), core=0.2, dome=(300, 0, 640), dome_pow=0.6)
    clear_sky(K, (0, 0, 511, 640))
    # the culms painted in front, fanning out from the clump, then more all through the clump behind them
    n = 13
    for layer, count, yr in (("front", n, (-0.32, -0.05)), ("mid", 10, (-0.1, 0.15)), ("back", 13, (0.05, 0.4))):
        for i in range(count):
            f = (i + rng.uniform(-0.3, 0.3)) / (count - 1)
            xb = 200 + 88 * f
            x5 = 190 + 112 * f                              # within the painted clump, seen from the front
            y_base = rng.uniform(*yr)
            spread = (f - 0.5) * 2
            top_py = rng.uniform(140, 330) - 80 * (1 - abs(spread))
            xt = x5 + spread * rng.uniform(40, 120)
            while top_py < 620 and alpha[int(top_py) - 25:int(top_py) + 1, int(np.clip(xt, 0, P.w - 1))].min() < 0.5:
                top_py += 8                                 # its tip stays among the painted leaves
                xt = x5 + (xt - x5) * 0.93
            yt = y_base * 2.5 + rng.uniform(-0.5, 0.5)
            yt = float(np.clip(yt, -crown.extent(xt, top_py + 60) * 0.9, crown.extent(xt, top_py + 60) * 0.9))
            pts_px = [(xb, base_py), (xb + (x5 - xb) * 0.5, 640), (x5, 520), (x5 + (xt - x5) * 0.45, 420),
                      (x5 + (xt - x5) * 0.8, (420 + top_py) / 2), (xt, top_py)]
            ys = [y_base, y_base + (yt - y_base) * 0.1, y_base + (yt - y_base) * 0.3, y_base + (yt - y_base) * 0.55,
                  y_base + (yt - y_base) * 0.8, yt]
            pts = [(P.x(px), y, P.z(py)) for (px, py), y in zip(pts_px, ys)]
            r0 = P.m(rng.uniform(4.5, 5.8))
            culm(K, pts, [r0, r0 * 0.95, r0 * 0.88, r0 * 0.75, r0 * 0.55, r0 * 0.3], green, node, node_every=0.6)
    # the knot of roots at the foot: a low mound of earth and root, and the fibrous roots on cards round it
    # (low, inside the painted knot of roots, and a tile of the painted root knot: a tall plain lump read as a sack)
    soil = strip_tile(K, (215, 785, 300, 815), soften=0.3, quilt=True)
    K.lathe([(P.m(r_), P.z(py)) for r_, py in ((62, 837), (58, 818), (50, 800), (36, 786), (18, 778), (0.0, 775))],
            soil, segments=20, centre=(P.x(cx), 0.0, 0.0), scale_y=0.85, wobble=0.12, name="root_mound")

    def roots_rule(rgb):
        r, g, b, mx, mn = chan(rgb)
        return (mx < 175) & (mx > 20) & (r >= g - 4)
    K.leaves_only((100, 745, 420, 837), roots_rule)
    for k in range(8):
        a = rng.uniform(0, 360)
        px = rng.uniform(190, 300)
        K.card_from_painting((px - 35, 770, px + 35, 837), (P.x(px), rng.uniform(-0.3, 0.3), P.z(803)),
                             yaw=rng.uniform(-60, 60) + rng.choice([0, 180]), name="roots")
    K.card_from_painting((95, 745, 425, 837), (P.x(260), -0.3, P.z(791)), name="roots_front")
    K.leaves_only((0, 0, 511, 640), sage_inked)
    crown.cards(200, (70, 60), "volume", yaw=85, pitch=45)
    crown.cards(110, (80, 70), "front", yaw=30, pitch=20)
    crown.cards(50, (70, 60), "back", yaw=30, pitch=20)
    crown.cards(20, (70, 60), "top", yaw=90, region=(0, 0, 511, 250))


# ====================================================================== solid blades (screwpine, agave, rosettes)
def blade(K, pts, widths, mat, thick=0.18, fold=0.22, roll=0.0, name="blade", side=None):
    """A solid blade along pts (metres) with widths (metres; 0 at the tip): its face turned to the camera (-y) and
    rolled `roll` degrees about its length, cupped along its midrib into a shallow V (fold x width), `thick` x width
    thick at the midrib and thin at its edges (a lens in section: two skins meeting at the edges, so it unwraps into
    two broad pieces of texture, not many slivers). Returns the part."""
    bm = bmesh.new()
    n = len(pts)
    P = [Vector(p) for p in pts]
    top, bot = [], []
    for i in range(n):
        t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        view = Vector((0, -1, 0))
        s = t.cross(view) if side is None else Vector(side)
        if s.length < 1e-4:
            s = t.cross(Vector((0, 0, 1)))
        s = (s - t * s.dot(t)).normalized()
        if roll:
            s = Matrix.Rotation(math.radians(roll), 3, t) @ s
        up = s.cross(t).normalized()                      # the blade's face normal (towards the camera)
        if up.y > 0:
            up = -up
        w = widths[i] / 2
        th = max(1e-4, widths[i] * thick)
        el, er = P[i] - s * w + up * fold * w, P[i] + s * w + up * fold * w
        if i == n - 1:
            v = bm.verts.new(P[i])
            top.append([v, v, v])
            bot.append([v, v, v])
            continue
        l, r = bm.verts.new(el), bm.verts.new(er)
        top.append([l, bm.verts.new(P[i] + up * th * 0.5), r])
        bot.append([l, bm.verts.new(P[i] - up * th * 0.5), r])
    for i in range(n - 1):
        for k in range(2):
            for row, flip in ((top, False), (bot, True)):
                q = [row[i][k], row[i][k + 1], row[i + 1][k + 1], row[i + 1][k]]
                q = [v for j, v in enumerate(q) if v not in q[:j]]
                if len(q) >= 3:
                    bm.faces.new(q[::-1] if flip else q)
    bm.faces.new([top[0][0], top[0][1], top[0][2], bot[0][1]])
    return _add(K, bm, mat, name, smooth=True)


def _bezier(a, c, b, n):
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
             (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]) for t in np.linspace(0, 1, n)]


def stroke_field(K, sigma=1.5, rho=5.0):
    """The direction of the painted strokes at every pixel (unit (dx, dy), sign-free): along the blades, veins and
    outlines, from the painting's structure tensor."""
    lum = ndimage.gaussian_filter((K.paint.rgba[..., :3] @ np.array([0.3, 0.59, 0.11])).astype(np.float64), sigma)
    gr, gc = ndimage.sobel(lum, 0), ndimage.sobel(lum, 1)
    Arr, Arc, Acc = [ndimage.gaussian_filter(v, rho) for v in (gr * gr, gr * gc, gc * gc)]
    th = 0.5 * np.arctan2(2 * Arc, Acc - Arr)              # the gradient's direction, from the x axis
    return np.stack([-np.sin(th), np.cos(th)], -1)          # along the strokes


def blade_tips(mask, smooth=1.0, min_branch=12):
    """The painted blades' tips: the ends of the blade mass's skeleton (px (x, y))."""
    m = ndimage.gaussian_filter(mask.astype(np.float32), smooth) > 0.5
    sk = skeletonize(m)
    paths, deg = _skel_graph(sk)
    tips = []
    for p in paths:
        for end in (p[0], p[-1]):
            if deg[end] == 1 and len(p) >= min_branch:
                tips.append((float(end[1]), float(end[0])))
    return tips


def blades_cover(K, mask, bases, n, w_px, len_px=(60, 400), profile="strap", tries=3000, inside=0.92, min_gain=30,
                 target=0.96, field=None, arch=0.45, tips=None, **_):
    """Blades that together cover a painted mass of blades (mask, bool HxW) as seen from the front: first one to
    every painted tip (an end of the mass's skeleton), then more through ground not yet covered; each springs from
    one of the `bases` boxes (px), and of the arcs it could take it takes the one that runs along the painting's
    strokes and stays inside the mask. Greedy: every blade lies (inside x) within the mask and covers new ground.
    Returns [(points px [(x, y)], widths px)], coverage."""
    from PIL import ImageDraw
    rng = K.rng
    H, W = mask.shape
    field = stroke_field(K) if field is None else field
    cover = np.zeros_like(mask)
    total = mask.sum()
    out = []
    tips = blade_tips(mask) if tips is None else tips
    order = list(rng.permutation(len(tips)))

    def width_at(t, w0):
        if profile == "strap":
            return w0 * (1 - t ** 1.6) * (0.75 + 0.25 * min(1.0, t * 6))
        if profile == "leaf":
            return w0 * math.sin(math.pi * min(1.0, 0.08 + t * 0.92)) ** 0.8 * (1 - t ** 3)
        return w0 * (1 - t)

    def best_arc(B, T):
        L = float(np.hypot(*(T - B)))
        d = (T - B) / max(1e-6, L)
        perp = np.array([d[1], -d[0]])
        m = max(6, int(L / 12))
        best = None
        for a in np.linspace(-arch, arch, 11):
            C = (B + T) / 2 + perp * a * L
            pts = np.array(_bezier(tuple(B), tuple(C), tuple(T), m))
            tang = np.gradient(pts, axis=0)
            tang /= np.maximum(1e-6, np.hypot(*tang.T))[:, None]
            ix = np.clip(pts[:, 0].astype(int), 0, W - 1)
            iy = np.clip(pts[:, 1].astype(int), 0, H - 1)
            align = np.abs((tang * field[iy, ix]).sum(1))[m // 4:].mean()
            ins = mask[iy, ix][m // 5:].mean()
            score = align + 2.0 * ins
            if best is None or score > best[0]:
                best = (score, pts)
        return best[1]
    k = 0
    for attempt in range(tries):
        if len(out) >= n or cover.sum() > target * total:
            break
        bx0, by0, bx1, by1 = bases[rng.integers(len(bases))]
        B = np.array((rng.uniform(bx0, bx1), rng.uniform(by0, by1)))
        if k < len(order):
            T = np.array(tips[order[k]])
            k += 1
            from_tip = True
        else:
            un = np.nonzero(mask & ~cover)
            if len(un[0]) == 0:
                break
            j = rng.integers(len(un[0]))
            Q = np.array((float(un[1][j]), float(un[0][j])))
            d = Q - B
            Ld = float(np.hypot(*d))
            if Ld < 8:
                continue
            d /= Ld
            T = Q.copy()
            while True:
                nxt = T + d * 3
                if not (0 <= nxt[0] < W and 0 <= nxt[1] < H) or not mask[int(nxt[1]), int(nxt[0])]:
                    break
                T = nxt
            from_tip = False
        L = float(np.hypot(*(T - B)))
        if not (len_px[0] <= L <= len_px[1]):
            continue
        pts = best_arc(B, T)
        m = len(pts)
        w0 = rng.uniform(*w_px)
        wd = [width_at(i / (m - 1), w0) for i in range(m)]
        left, right = [], []
        for i in range(m):
            a = pts[min(i + 1, m - 1)] - pts[max(i - 1, 0)]
            a /= max(1e-6, np.hypot(*a))
            nrm = np.array([-a[1], a[0]])
            left.append(tuple(pts[i] + nrm * wd[i] / 2))
            right.append(tuple(pts[i] - nrm * wd[i] / 2))
        im = Image.new("L", (W, H), 0)
        ImageDraw.Draw(im).polygon(left + right[::-1], fill=255)
        bmask = np.asarray(im) > 127
        area = bmask.sum()
        if area < 10 or (bmask & mask).sum() < (inside - (0.04 if from_tip else 0.0)) * area:
            continue
        gain = (bmask & mask & ~cover).sum()
        if gain < (min_gain * 0.3 if from_tip else min_gain):
            continue
        cover |= bmask
        out.append(([tuple(p) for p in pts], wd))
    return out, cover


def place_blades(K, blades, mat, y_of, rolls=35.0, thick=0.18, fold=0.22, name="blade"):
    """Builds the blades found by blades_cover in 3D: y_of(t, px, py, k) gives each point's depth (k: the blade)."""
    P = K.paint
    for k, (pts, wd) in enumerate(blades):
        n = len(pts)
        p3 = [(P.x(x), y_of(i / (n - 1), x, y, k), P.z(y)) for i, (x, y) in enumerate(pts)]
        blade(K, p3, [P.m(w) for w in wd], mat, thick=thick, fold=fold, roll=K.rng.uniform(-rolls, rolls), name=name)


@model("field_tree_4", "fields", kind="prop", atlas=2048, leaves=1024)
def field_tree_4(K):
    """A screwpine clump: a short brown stump bristling with long, thick, saw-edged blades that shoot up from its top
    and arch out and droop all round, on red earth with stones."""
    P = K.paint
    rng = K.rng
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    halo = (mn > 175) & (mx - mn < 40)
    stumpish = (r > g + 6) & (r > b + 18) & (mx < 140)
    plant = opaque & ~halo & box_mask(opaque.shape, [(0, 0, 512, 405)])
    blades_mask = ndimage.binary_opening(plant & ~stumpish, iterations=1)
    shape = Crown(K, (0, 0, 512, 410), P.m(480) * 0.36, (260, 260), core=0.25, dome=(260, 0, 420), dome_pow=0.6)
    # the stump
    bark = K.tile((255, 330, 300, 395), vary=0.08, soften=0.2)
    K.lathe([(P.m(r_), P.z(py)) for r_, py in ((64, 425), (62, 412), (58, 400), (50, 370), (46, 330), (44, 300),
                                               (36, 285), (0.0, 278))], bark, segments=20, centre=(P.x(272), 0.0, 0.0),
            wobble=0.08, name="stump")
    # the blades: solid, saw-edged straps covering the painted mass, springing from the stump's top and sides
    found, cover = blades_cover(K, blades_mask, [(225, 270, 315, 305), (215, 290, 330, 360), (235, 330, 310, 395)],
                                240, (12, 20), len_px=(40, 360), profile="strap", inside=0.93, min_gain=18, arch=0.6,
                                target=0.985, tries=9000)
    green = masked_material(K, blades_mask & (mx > 75), inset=1)       # the blades' greens, not their ink

    def y_of(t, x, y, k, tips={}):
        if k not in tips:
            tips[k] = (rng.uniform(-0.2, 0.2), rng.choice([-1, 1]) * rng.uniform(0.25, 0.8))
        yb, f = tips[k]
        return yb + f * shape.extent(x, y) * (t ** 1.3)
    place_blades(K, found, green, y_of, rolls=15, thick=0.14, fold=0.15)
    K.ao = 0.12
    # what the solid blades leave of the painting (the thin drooping tips, the ink round the blades): cards of exactly
    # those pixels, each where it is painted, at a depth in the clump's outer shell
    rest = plant & ~stumpish & ~ndimage.binary_erosion(cover, iterations=1)
    rest = ndimage.binary_opening(rest, iterations=1) | (rest & (mx < 90))
    K.leaves_only((0, 0, 512, 410), mask_rule(rest, (0, 0, 512, 410)))
    cover_cards(K, rest & ~box_mask(rest.shape, [(220, 300, 330, 410)]), (40, 40),
                lambda px, py: rng.choice([-1, 1]) * shape.extent(px, py) * rng.uniform(0.3, 0.9),
                slope=(0.9, 0.4), name="blade_tips", n_max=600)
    # the mound of red earth and its stones
    ground = mound(K, 266, 149, 1.3, 430, 402, (280, 416, 340, 428))
    stone = K.tile((172, 405, 192, 418), vary=0.08)
    for px, w, h, y in ((172, 30, 18, -0.6), (195, 26, 16, -0.75), (225, 18, 10, -0.8), (272, 16, 10, -0.9),
                        (300, 20, 12, -0.8), (330, 26, 15, -0.7), (360, 22, 14, -0.6), (240, 24, 14, 0.8),
                        (310, 22, 14, 0.9), (190, 20, 12, 0.6), (350, 18, 12, 0.5)):
        x = P.x(px)
        K.boulder(x, y, ground(x, y) + P.m(h) * 0.4, P.m(w), P.m(w) * 0.75, P.m(h) * 1.1, stone)


def needles(rgb):
    """Casuarina needles and the fine dark twigs among them: green to grey-green, not the white halo or the bark."""
    r, g, b, mx, mn = chan(rgb)
    keep = (g >= r - 2) & (g >= b) & (mn < 200)
    keep |= (mx < 70)
    return ndimage.binary_opening(keep, iterations=1) | (keep & (mx < 120))


CASUARINA_TRUNKS = [
    [(164, 868, 6.5), (163, 800, 6), (161, 700, 5), (159, 650, 4.8), (155, 560, 4), (148, 450, 3), (140, 340, 2),
     (136, 270, 1.2)],
    [(206, 872, 8), (206, 800, 7.5), (205, 700, 7), (205, 650, 6.8), (205, 560, 6), (206, 420, 4.5), (206, 280, 3),
     (205, 160, 1.5)],
    [(239, 868, 6.5), (239, 800, 6), (240, 700, 5.2), (242, 650, 4.6), (245, 560, 3.8), (250, 450, 2.5),
     (253, 380, 1.4)],
    [(268, 866, 6.5), (268, 800, 6), (266, 700, 4.6), (267, 650, 4.2), (272, 560, 3.5), (280, 420, 2.6),
     (287, 290, 1.6), (290, 240, 1.0)],
]


@model("field_tree_5", "fields", kind="prop", atlas=2048, leaves=1024)
def field_tree_5(K):
    """A stand of four casuarinas: tall, thin, straight grey trunks from one patch of red earth, each a narrow spire of
    wispy drooping needles."""
    P = K.paint
    rng = K.rng
    crown = Crown(K, (0, 0, 401, 640), P.m(330) * 0.42, (205, 380), core=0.3, dome=(420, 0, 640), dome_pow=0.6)
    clear_sky(K, (0, 0, 401, 640))
    bark = K.tile((198, 700, 212, 840), vary=0.08, soften=0.2)
    ys = [-0.35, 0.05, 0.45, -0.1]
    wood = []
    for (pts, y0) in zip(CASUARINA_TRUNKS, ys):
        pts = [(pts[0][0], 880, pts[0][2] * 1.05)] + list(pts)       # down into the earth
        lean = rng.uniform(-0.12, 0.12)                               # straight, leaning a little
        n = len(pts)
        wood.append(limb(K, pts, bark, y=[y0 + lean * ((pts[0][1] - p[1]) / 600.0) for p in pts], segments=10,
                         name="trunk"))
    # branches leaning out from each trunk through its spire, under the needles
    for pts, y0 in zip(CASUARINA_TRUNKS, ys):
        for k in range(7):
            i = rng.integers(2, len(pts) - 1)
            px, py, r = pts[i]
            if py > 600:
                continue
            a = rng.uniform(0, 2 * math.pi)
            L = P.m(rng.uniform(40, 110)) * (py / 600 + 0.3)
            x0, z0 = P.x(px), P.z(py)
            q = [(x0, y0, z0), (x0 + math.cos(a) * L * 0.6, y0 + math.sin(a) * L * 0.6, z0 + L * 0.35),
                 (x0 + math.cos(a) * L, y0 + math.sin(a) * L, z0 + L * 0.2)]
            if all(P.rgba[int(np.clip(P.py(v[2]), 0, P.h - 1)), int(np.clip(P.px(v[0]), 0, P.w - 1)), 3] > 0.5
                   for v in q):
                wood.append(K.tube(q, [P.m(r) * 0.45, P.m(r) * 0.3, P.m(r) * 0.15], bark, segments=6, name="branch"))
    # the needles
    K.leaves_only((0, 0, 401, 640), needles)
    crown.cards(230, (60, 70), "volume", yaw=85, pitch=40)
    crown.cards(120, (70, 80), "front", yaw=30, pitch=20)
    crown.cards(60, (60, 70), "back", yaw=30, pitch=20)
    crown.cards(20, (60, 70), "top", yaw=90, region=(0, 0, 401, 300))
    # the mound of red earth, stones
    ground = mound(K, 228, 110, 0.8, 881, 855, (180, 866, 300, 878))
    stone = K.colour((245, 858, 255, 866), vary=0.1)
    for px, w, h, y in ((245, 30, 16, -0.4), (285, 22, 12, -0.45), (175, 18, 10, -0.35), (300, 16, 10, 0.4),
                        (200, 20, 12, 0.5)):
        x = P.x(px)
        K.boulder(x, y, ground(x, y) + P.m(h) * 0.4, P.m(w), P.m(w) * 0.75, P.m(h) * 1.1, stone)


def rosette(K, cx_px, bot_py, r_px, h_px, mat, y=0.0, name="rosette"):
    """A succulent rosette (echeveria) standing on the ground at painted (cx, bottom), r px across its widest and
    h px tall: rings of thick, pointed, cupped leaves round its heart, the inner ones upright, the outer ones lying
    open, as round as a cabbage from every side."""
    P = K.paint
    c = Vector((P.x(cx_px), y, P.z(bot_py)))
    R, Hh = P.m(r_px), P.m(h_px)
    rings = ((5, Hh * 0.95, 78, 0.32), (8, (R * R * 0.33 + (Hh * 0.8) ** 2) ** 0.5, 55, 0.12),
             (11, R * 1.02, 24, 0.0))
    for k, (n, L0, tilt, rr) in enumerate(rings):
        ph = K.rng.uniform(0, 2 * math.pi)
        for i in range(n):
            a = ph + 2 * math.pi * i / n
            L = L0 * K.rng.uniform(0.9, 1.08)
            tl = math.radians(tilt + K.rng.uniform(-6, 6))
            d = Vector((math.cos(a) * math.cos(tl), math.sin(a) * math.cos(tl), math.sin(tl)))
            base = c + Vector((math.cos(a), math.sin(a), 0)) * R * rr * 0.4 + Vector((0, 0, Hh * 0.06 * (2 - k)))
            mid = base + d * L * 0.55 + Vector((0, 0, L * 0.08))
            tip = base + d * L
            w = L * (0.55 if k < 2 else 0.5)
            pts = [tuple(base), tuple(base + (mid - base) * 0.5), tuple(mid), tuple(mid + (tip - mid) * 0.6),
                   tuple(tip)]
            blade(K, pts, [w * 0.45, w * 0.85, w, w * 0.6, 0.0], mat, thick=0.35, fold=0.35,
                  side=(-math.sin(a), math.cos(a), 0.0), name=name)


@model("field_tree_6", "fields", kind="prop", atlas=2048, leaves=1024)
def field_tree_6(K):
    """A dry-ground group: an agave of thick, sharp, blue-grey blades, a prickly-pear cactus of jointed flat pads
    (one with a fruit on top), three fleshy succulent rosettes, stones on red earth."""
    P = K.paint
    rng = K.rng
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    halo = (mn > 185) & (mx - mn < 40)
    # ---- the prickly pear: flat pads, each the painted ellipse, turned a little, at its depth in the plant
    pads = [(290.1, 41.7, 12.6, 22.8, 103.9, -0.05), (243.7, 42.3, 9.2, 15.7, 99.6, 0.05), (205.3, 60.8, 11.9, 18.5, 61.4, 0.0),
            (235.7, 86.8, 18.1, 29.9, 86.8, -0.12), (275.0, 74.2, 11.9, 18.0, 59.5, 0.08), (325.8, 77.9, 9.9, 18.0, 92.7, 0.12),
            (287.5, 111.7, 15.1, 23.7, 80.0, 0.02), (334.9, 112.4, 15.5, 23.3, 129.7, -0.05),
            (193.0, 121.9, 18.5, 31.7, 55.7, -0.15), (244.6, 131.2, 16.7, 19.1, -137.6, 0.18),
            (274.1, 145.3, 12.1, 20.7, 88.2, 0.2), (306.0, 154.3, 16.9, 28.0, 114.1, -0.08),
            (232.2, 168.3, 19.2, 30.5, 66.5, -0.2), (272.6, 190.0, 19.0, 30.0, 95.0, -0.1)]
    boxes = [(int(cx - 30), int(cy - 30), int(cx + 30), int(cy + 30)) for cx, cy, *_ in pads]
    pad_mat = K.projected(squeeze=1.0, keep=[(165, 15, 370, 225)], exclude=[(140, 175, 215, 240), (205, 195, 260, 240),
                                                                             (300, 175, 370, 240)], inset=2)

    def ellipse(cx, cy, a_minor, a_major, ang, n=28):
        A = math.radians(ang)
        return [(cx + a_major * math.cos(t) * math.cos(A) - a_minor * math.sin(t) * math.sin(A),
                 cy + a_major * math.cos(t) * math.sin(A) + a_minor * math.sin(t) * math.cos(A))
                for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]

    def pad(cx, cy, a0, a1, ang, y, turn, grow=1.12):
        ob = poly_solid(K, ellipse(cx, cy, a0 * grow, a1 * grow, ang), y, pad_mat, depth=0.3, segments=14,
                        name="pad")
        if ob is not None and turn:
            M = (Matrix.Translation((P.x(cx), y, P.z(cy))) @ Matrix.Rotation(math.radians(turn), 4, "Z")
                 @ Matrix.Translation((-P.x(cx), -y, -P.z(cy))))
            ob.data.transform(M)
        return ob
    # each pad at its depth in the clump (the higher, the further it may have grown forward or back), turned on its
    # own way about the vertical
    # each pad at its depth in the clump, close to the pad it grows from (a pad standing apart in depth from the one
    # below it hangs in the air), turned a little on its own way about the vertical
    for cx, cy, a0, a1, ang, y in pads:
        lift = (225 - cy) / 200
        pad(cx, cy, a0, a1, ang, y * 0.6 + rng.uniform(-0.05, 0.05) * lift, rng.uniform(-30, 30))
    # more pads just behind the painted ones, joined to them: a bush of pads from every side
    for cx, cy, a0, a1, ang, y in pads[3:]:
        if rng.uniform() < 0.7:
            pad(cx + rng.uniform(-8, 8), cy + rng.uniform(-6, 6), a0 * 0.9, a1 * 0.9, ang + rng.uniform(-30, 30),
                y * 0.6 + rng.uniform(0.1, 0.18), rng.uniform(-50, 50), grow=1.0)
    fruit(K, 297, 15, 7, 8, -0.05, K.projected(squeeze=1.0, keep=[(290, 8, 305, 22)], inset=1))
    # ---- the agave: thick, sharp blades covering the painted rosette from its heart outwards
    ag = opaque & ~halo & box_mask(opaque.shape, [(0, 60, 192, 224)]) & ~box_mask(opaque.shape, [(140, 170, 220, 240)])
    ag &= ~((r > g + 5) & (py_mask := box_mask(opaque.shape, [(0, 205, 200, 240)])))
    ag = ndimage.binary_opening(ag, iterations=1)
    found, cover = blades_cover(K, ag, [(98, 196, 126, 218), (88, 200, 136, 222)], 130, (14, 30), len_px=(30, 190),
                                arch=0.15, droop=0.05, profile="leaf", inside=0.88, min_gain=20, target=0.985,
                                tries=6000)
    agave_mat = masked_material(K, ag & (mx > 85), inset=1)
    shape = Crown(K, (0, 60, 195, 225), P.m(180) * 0.4, (110, 160), core=0.3)

    def y_of(t, x, y, k, tips={}):
        if k not in tips:
            tips[k] = rng.choice([-1, 1]) * rng.uniform(0.2, 1.0)
        return tips[k] * shape.extent(x, y) * t ** 1.2
    place_blades(K, found, agave_mat, y_of, rolls=25, thick=0.25, fold=0.3, name="agave")
    # what the solid blades leave of the painted agave (thin tips, ink): cards of exactly those pixels, in its shell
    rest = ag & ~ndimage.binary_erosion(cover, iterations=1)
    rest = ndimage.binary_opening(rest, iterations=1) | (rest & (mx < 90))
    K.leaves_only((0, 60, 195, 225), mask_rule(rest, (0, 60, 195, 225)))
    cover_cards(K, rest & ~box_mask(rest.shape, [(80, 185, 145, 225)]), (30, 30),
                lambda px, py: rng.choice([-1, 1]) * shape.extent(px, py) * rng.uniform(0.3, 0.9),
                slope=(0.9, 0.4), name="agave_tips", n_max=400)
    # ---- the rosettes
    ros = opaque & ~halo & box_mask(opaque.shape, [(140, 172, 220, 238), (205, 192, 260, 238), (298, 172, 370, 236)])
    ros_mat = masked_material(K, ros, inset=1)
    for cx, bot, rr, hh, y in ((182, 238, 34, 60, -0.25), (233, 236, 22, 44, -0.3), (336, 236, 33, 60, -0.2),
                               (300, 236, 24, 40, 0.35), (150, 236, 22, 36, 0.3)):
        rosette(K, cx, bot, rr, hh, ros_mat, y=y)
    # ---- the mound of red earth, stones
    ground = mound(K, 206, 172, 0.8, 243, 212, (60, 226, 140, 238), rise=0.35)
    stone = K.colour((75, 215, 95, 225), vary=0.1)
    for px, w, h, y in ((38, 22, 10, -0.2), (90, 26, 12, -0.25), (128, 26, 14, -0.3), (262, 14, 8, -0.3),
                        (290, 18, 10, -0.25), (60, 20, 10, 0.3), (170, 22, 12, 0.35), (280, 20, 10, 0.4)):
        x = P.x(px)
        K.boulder(x, y, ground(x, y) + P.m(h) * 0.4, P.m(w), P.m(w) * 0.75, P.m(h) * 1.1, stone)


# ====================================================================== the generic traced tree (the plants' trees)
def traced_tree(K, mask, root_px, crown_box, crown_centre, dome, leaf_rule, spread=0.5, root_z_px=None,
                card_px=None, n_cards=(220, 90, 50, 25), limb_py_max=None, limb_py_min=None, n_limbs=6, n_roots=4,
                root_py=None, bark_axis_px=None, depth_ratio=0.36, core=0.18, dome_pow=1.0, fuse_faces=9000,
                rscale=0.95, seed_dy=None, crown_mask=None, spur=1.3, root_turn=(100, 160), voxel_div=260,
                min_r_px=0.0, trunk=None, tile_box=None, straight_py=None, foot=None, bark_mask=None,
                leaf_all=False, r_cap_px=None, bark_inset=2):
    """A tree whose wood is traced off its painting (mask: its bark pixels) and whose crown is the painting's leaves
    on cards: the trunk, limbs, twigs and roots as fused tubes, leaning into the crown's depth, the big limbs and
    roots turned round the trunk as well; returns (wood, crown, bark material, thin parts). trunk = (py at the ground,
    py where it forks, px of its foot[, py where its foot flares, flare, depth]): the trunk lofted through its painted
    outline (a traced tube is only as thick as the circle inside its outline: a braided or knobbly trunk came out too
    thin)."""
    P = K.paint
    rng = K.rng
    wood = Wood(K, mask, root_px, spur=spur, min_len=5)
    wood.r_cap = r_cap_px                             # no limb thicker than this (clumped twigs traced as blobs)
    cw = crown_box[2] - crown_box[0]
    crown = Crown(K, crown_box, P.m(cw) * depth_ratio, crown_centre, core=core, dome=dome, dome_pow=dome_pow,
                  mask=crown_mask)
    clear_sky(K, crown_box)
    if root_z_px is not None:
        # and the white cut-out halo round the roots: a root's tip reaching past its painted tip took it as a white
        # shard from the front
        clear_sky(K, (0, root_z_px - 60, P.w, P.h))
    floor = P.m(cw) * 0.06
    root_lim = crown.hd * 0.6                          # the roots spread round the foot, whatever the crown does

    def ylim(px, py):
        if root_z_px is not None and py > root_z_px:
            return root_lim
        return max(floor, crown.extent(px, py) * 0.8)
    def seed(p, dy):
        # a root leans into depth in proportion to how far it runs across the painting, one this way and the next
        # the other, so seen from above the roots fan out round the foot (and seen from the side they slope down
        # to the ground like a flare, not crossing sticks)
        if straight_py is not None and p["pts"][-1][1] >= straight_py - 4 and (
                root_z_px is None or p["pts"][-1][1] <= root_z_px):
            return 0.0                                   # the trunk below its fork stands straight up
        if root_z_px is not None and p["pts"][-1][1] > root_z_px:
            dx = P.m(float(p["pts"][-1][0] - p["pts"][0][0]))
            s = rng.uniform(0.3, 1.0) ** 1.6 * (1 if len(root_sign) % 2 else -1)
            root_sign.append(s)
            return dx * s + rng.uniform(-0.15, 0.15) * P.m(float(np.hypot(*(p["pts"][-1] - p["pts"][0]))))
        return seed_dy(p, dy) if seed_dy is not None else dy
    root_sign = []
    if straight_py is None and trunk is not None:
        straight_py = trunk[1]
    wood.grow(spread, root_z_px=root_z_px, root_spread=0.9, ymax=ylim, seed_dy=seed)
    bark = bark_mix(K, mask if bark_mask is None else bark_mask, tile_box=tile_box, inset=bark_inset)
    voxel = P.H / voxel_div
    fuse_r = voxel * 2.5 * P.ppm                     # thinner wood stays clean tubes (a voxel remesh would bloat it)
    thick, thin = wood.tubes(bark, fuse_r_px=fuse_r, rscale=rscale, min_r_px=min_r_px)
    if trunk is not None:
        py_bot, py_top, tx = trunk[:3]
        flare_py = trunk[3] if len(trunk) > 3 else None
        flare = trunk[4] if len(trunk) > 4 else 0.6
        depth = trunk[5] if len(trunk) > 5 else 0.85
        rows = trunk_runs(mask, py_bot, py_top, tx, flare_py=flare_py, flare=flare)
        if rows:
            hw = float(np.median([(b - a) / 2 for py, a, b in rows if flare_py is None or py <= flare_py]))
            def cap(py):
                if flare_py is None or py <= flare_py:
                    return hw * 1.1
                return hw * 1.1 * (1 + 0.35 * min(1.0, (py - flare_py) / max(1.0, py_bot - flare_py)))
            ob = loft_trunk(K, rows, bark, y=0.0, depth=depth, max_depth_px=cap)
            if ob is not None:
                thick.append(ob)
    limbs = pick_limbs(wood, py_max=limb_py_max, py_min=limb_py_min, r_min=max(fuse_r * 0.6, min_r_px),
                       min_len=cw * 0.08, n=n_limbs)
    picks = [(i, (1 if k % 2 else -1) * rng.uniform(60, 125), 0.0) for k, i in enumerate(limbs)]
    wood.turned_copies(bark, picks, thick=thick, thin=thin, ymax=crown.hd * 0.8, fuse_r_px=fuse_r,
                       min_r_px=min_r_px, ylim=lambda px, py: max(floor, crown.extent(px, py) * 0.85))
    if n_roots and root_z_px is not None:
        # every painted root again, mirrored through the trunk's plane: the roots behind the foot, each exactly
        # behind (so hidden by) the painted one in front
        for i, p in enumerate(wood.paths):
            if p["pts"][-1][1] > root_z_px and float(np.max(p["r"])) >= max(min_r_px, 1.5):
                pts, rs = wood.polyline(p, ys=-p["y"])
                if pts is not None and len(pts) > 1:
                    big = float(np.max(p["r"])) * rscale >= fuse_r
                    (thick if big else thin).append(K.tube(pts, [r * rscale for r in rs], bark,
                                                           segments=10 if big else 6, name="root_back"))
    elif n_roots:
        roots = pick_limbs(wood, r_min=fuse_r, min_len=cw * 0.05, n=n_roots, roots=True, root_py=root_py)
        wood.turned_copies(bark, [(i, rng.choice([-1, 1]) * rng.uniform(*root_turn), 0.0) for i in roots],
                           thick=thick, thin=thin, whole=False, rscale=0.85, fuse_r_px=fuse_r, min_r_px=min_r_px)
    if foot is not None:
        thick += foot(bark)
    if thick:
        K.fuse(thick, voxel=voxel, faces=fuse_faces)
    # the leaves only: never the painted wood (some of it is as green-grey as the leaves), which a card would carry
    # out of its place into the crown's sides as a pale streak
    box = tuple(int(v) for v in crown_box)
    if leaf_all:
        # everything painted in the crown but the traced wood (its twigs too thin to trace go on the cards) and the
        # white cut-out halo
        def leaf_rule(rgb):
            r, g, b, mx, mn = chan(rgb)
            return ~((mn > 175) & (mx - mn < 45))
    # (only the wood thicker than an ink line: the leaves' own outlines, traced as wood too, stay on the cards)
    # (and only the wood modelled as tubes, min_r_px and up)
    k_open = max(2, int(math.ceil(min_r_px)))
    leafpix = leaf_mask_of(K, box, leaf_rule) & ~ndimage.binary_dilation(
        ndimage.binary_opening(mask, iterations=k_open), iterations=2)
    K.leaves_only(box, mask_rule(leafpix, box))
    cp = card_px or (cw * 0.14, cw * 0.12)
    nv, nf, nb, nt = n_cards
    crown.cards(nv, cp, "volume", yaw=85, pitch=45)
    crown.cards(nf, (cp[0] * 1.1, cp[1] * 1.1), "front", yaw=30, pitch=20)
    crown.cards(nb, cp, "back", yaw=30, pitch=20)
    if nt:
        crown.cards(nt, cp, "top", yaw=90, region=(crown_box[0], crown_box[1], crown_box[2],
                                                      (crown_box[1] + crown_box[3]) / 2))
    return wood, crown, bark, thin


def _trace_grey(K, boxes, root_px, exclude=(), sat=40, lo=40, hi=225, close=2, hole=600, min_area=30, spur=1.3,
                extra_rule=None):
    def rule(rgb):
        r, g, b, mx, mn = chan(rgb)
        m = grey_bark(rgb, sat=sat, lo=lo, hi=hi)
        return m & extra_rule(rgb) if extra_rule is not None else m
    mask = wood_mask(K, rule, boxes=boxes, exclude=exclude, close=close, hole=hole, min_area=min_area)
    return mask, Wood(K, mask, root_px=root_px, spur=spur, min_len=5)


TRACE["h1_1"] = lambda K: _trace_grey(K, [(0, 380, 1239, 1187)], (600, 1150),
                                      extra_rule=lambda rgb: (chan(rgb)[1] - chan(rgb)[2]) <= 14)    # not the leaves


@model("h1_1", "plants", kind="prop", atlas=2048, leaves=1024)
def h1_1(K):
    """A spreading shade tree: a thick grey trunk of twisted, braided strands on a great splay of roots, crooked
    limbs reaching out under a broad dome of feathery compound leaves."""
    mask, _ = TRACE["h1_1"](K)
    traced_tree(K, mask, (600, 1150), (0, 0, 1239, 730), (620, 380), (380, 10, 740), sage_inked, spread=0.55,
                root_z_px=1000, limb_py_max=650, limb_py_min=380, n_limbs=7, n_roots=6, root_py=1080,
                n_cards=(240, 100, 55, 25), trunk=(1150, 700, 600, 960, 0.7), min_r_px=2.5)


TRACE["h1_2"] = lambda K: _trace_grey(K, [(0, 120, 528, 972)], (272, 955), sat=45, lo=35, hi=222, close=1, hole=200,
                                      extra_rule=lambda rgb: (chan(rgb)[1] - chan(rgb)[2]) <= 10)    # not the leaves


@model("h1_2", "plants", kind="prop", atlas=2048, leaves=1024)
def h1_2(K):
    """A young tree: a slim straight grey trunk on a few thin roots, forking high into slender limbs and twigs under
    loose sprays of compound leaves."""
    mask, _ = TRACE["h1_2"](K)
    traced_tree(K, mask, (272, 955), (0, 0, 528, 520), (265, 280), (280, 0, 520), sage_inked, spread=0.6,
                root_z_px=900, limb_py_max=520, limb_py_min=150, n_limbs=6, n_roots=4, root_py=920,
                n_cards=(170, 80, 45, 15), card_px=(75, 65), min_r_px=3.5, trunk=(950, 530, 275, 900, 0.8),
                leaf_all=True)


TRACE["h1_3"] = lambda K: _trace_grey(K, [(0, 190, 864, 1024)], (150, 1000),
                                      exclude=[(393, 525, 424, 960), (533, 518, 564, 955), (372, 832, 598, 958)],
                                      extra_rule=lambda rgb: (chan(rgb)[1] - chan(rgb)[2]) <= 12)    # not the leaves


@model("h1_3", "plants", kind="prop", atlas=2048, leaves=1024)
def h1_3(K):
    """A leaning tree with a swing: a grey trunk curving up from a splayed foot into a long limb, a plank seat hung
    from the limb on two ropes looped round it, and a crown of feathery compound leaves."""
    P = K.paint
    rng = K.rng
    mask, _ = TRACE["h1_3"](K)
    wood, crown, bark, thin = traced_tree(K, mask, (150, 1000), (90, 0, 864, 535), (480, 270), (280, 0, 540),
                                          sage_inked, spread=0.5, root_z_px=960, limb_py_max=470, limb_py_min=200,
                                          n_limbs=6, n_roots=3, root_py=975, n_cards=(190, 90, 45, 20),
                                          card_px=(90, 80), min_r_px=2.5, trunk=(990, 530, 160, 940, 0.6))
    # the swing: two ropes looped round the limb, each splitting into a V to the ends of a plank seat
    rope = K.colour((400, 650, 416, 760), vary=0.08)
    plank = K.tile((400, 874, 570, 896), vary=0.06)
    for (lx, ly), (kx, ky), (sx0, sx1) in (((407, 512), (408, 822), (392, 422)), ((549, 485), (548, 822), (536, 562))):
        yb, rb = wood.at(lx, ly)
        rr = P.m(rb)
        wrap_limb(K, (P.x(lx - 10), yb, P.z(ly + 6)), (P.x(lx + 10), yb, P.z(ly - 6)), rr, rope, 4, P.m(3.5),
                  wobble=0.15, name="rope_loop")
        top = (P.x(lx), yb, P.z(ly) - rr)
        knot = (P.x(kx), yb, P.z(ky))
        K.tube([top, (P.x(kx), yb, (top[2] + knot[2]) / 2), knot], P.m(3.2), rope, segments=6, name="rope")
        K.lathe([(P.m(4), P.z(ky + 14)), (P.m(6), P.z(ky + 6)), (P.m(6), P.z(ky - 6)), (P.m(4), P.z(ky - 14))], rope,
                segments=10, centre=(P.x(kx), yb, 0.0), name="knot")
        for sx, dy in ((sx0, -P.m(28)), (sx1, P.m(28))):
            K.tube([knot, (P.x(sx), yb + dy, P.z(888))], P.m(2.6), rope, segments=6, name="rope_v")
    # the plank seat (its painted top face is the perspective of a level plank: from the front, its front face)
    ys, _ = wood.at(470, 495)
    K.block((P.x(383) + P.x(582)) / 2, ys, P.z(897), P.m(200), P.m(62), P.m(22), plank, rot=(0, 3.4, 0),
            bevel=P.m(2), name="seat")
    # the frayed rope ends under it: the painted tassels, crossed cards (thin tubes read as black legs)
    def fibres(rgb):
        r, g, b, mx, mn = chan(rgb)
        return ~((mn > 175) & (mx - mn < 45)) & (mx < 200)
    for box in ((386, 900, 418, 942), (533, 898, 566, 940)):
        K.leaves_only(box, fibres)
        cx = (box[0] + box[2]) / 2
        for yaw in (0, 90):
            K.card_from_painting(box, (P.x(cx), ys, P.z((box[1] + box[3]) / 2)), yaw=yaw, name="rope_fray",
                                 normal=(0, -0.6, 0.8))


def pod_mask(K, box, rule=None):
    """The painted pods (tamarind: orange-brown) inside box: a bool mask."""
    P = K.paint
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    r, g, b, mx, mn = chan(rgb)
    m = (r - b > 55) & (r > g + 18) & (r > 100) if rule is None else rule(rgb)
    m &= (P.rgba[..., 3] > 0.5) & box_mask(m.shape, [box])
    m = ndimage.binary_closing(m, iterations=2)
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, iterations=1)
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.nonzero(sizes >= 40)[0])
    return m


def hang_pods(K, mask, crown, mat, copies=2, flatten=0.6, lump=0.12, rscale=1.0, min_len=10, segments=10,
              stalk=None, traced=()):
    """Pods (tamarind, drumstick) where they hang in the painting: each painted pod's centre line (the skeleton of
    the pod mask) as a curved, slightly flattened tube, waisted between its seeds, just in front of the crown's
    leaves; and `copies` more of each hanging at the same place deeper in the crown, so from the side and back the
    tree is as full of pods as from the front."""
    P = K.paint
    rng = K.rng
    pw = Wood(K, mask, root_px=(0, 0), spur=1.0, min_len=4, smooth=0.8, step=1.6)
    for pts_px, r_px in traced:                       # pods traced by hand where a bunch is painted touching
        a = np.array(pts_px, np.float32)
        t = np.linspace(0, 1, 12)
        s_ = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(a, axis=0).T))])
        s_ /= s_[-1]
        pp = np.stack([np.interp(t, s_, a[:, 0]), np.interp(t, s_, a[:, 1])], 1)
        rr = r_px * np.sqrt(np.clip(np.sin(np.pi * (0.06 + 0.88 * t)), 0.25, 1))
        pw.paths.append(dict(pts=pp, r=rr.astype(np.float32), a=None, b=None, ends=(1, 1)))
    out = []
    for p in pw.paths:
        L = float(np.hypot(*np.diff(p["pts"], axis=0).T).sum())
        if L < min_len:
            continue
        cx, cy = p["pts"].mean(0)
        r_max = float(np.max(p["r"]))
        for k in range(1 + copies):
            if k == 0:
                y = crown.front_y(cx, cy, 1.0) - P.m(r_max) * 1.5
            else:
                y = crown.y0 + rng.uniform(-0.5, 0.95) * crown.extent(cx, cy)
            p["y"] = np.full(len(p["pts"]), y)
            pts, rs = pw.polyline(p)
            if pts is None or len(pts) < 2:
                continue
            ph = rng.uniform(0, 6.28)
            seg = [0.0] + list(np.cumsum([math.dist(a, b) for a, b in zip(pts, pts[1:])]))
            rs = [r * rscale * (1 + lump * math.sin(s / max(1e-6, r * 2.2) + ph)) for r, s in zip(rs, seg)]
            ob = K.tube(pts, rs, mat, segments=segments, name="pod")
            for v in ob.data.vertices:
                v.co.y = y + (v.co.y - y) * flatten
            out.append(ob)
            if stalk is not None:
                top = max(pts, key=lambda v: v[2])
                K.tube([top, (top[0], top[1], top[2] + P.m(r_max) * 1.3)], P.m(r_max) * 0.22, stalk, segments=5,
                       name="pod_stalk")
    return out


TRACE["h2_1"] = lambda K: _trace_grey(K, [(0, 240, 1120, 1100)], (540, 1060), sat=42, hole=8000,
                                      exclude=[(255, 995, 420, 1090), (535, 1035, 625, 1085)],
                                      extra_rule=lambda rgb: ~((chan(rgb)[0] - chan(rgb)[2] > 55))
                                      & (chan(rgb)[0] >= chan(rgb)[1] - 2))      # not the pods, not the leaves


@model("h2_1", "plants", kind="prop", atlas=2048, leaves=1024)
def h2_1(K):
    """An old tamarind: a massive grey trunk twisting up from buttress roots, crooked limbs spreading under a dome of
    feathery leaves, clusters of brown curved pods hanging all through it, mossy rocks and grass at its foot."""
    P = K.paint
    rng = K.rng
    mask, _ = TRACE["h2_1"](K)
    wood, crown, bark, thin = traced_tree(K, mask, (540, 1060), (0, 0, 1120, 670), (560, 330), (330, 0, 680),
                                          sage_inked, spread=0.5, root_z_px=980, limb_py_max=560, limb_py_min=250,
                                          n_limbs=7, n_roots=5, root_py=1030, n_cards=(210, 95, 50, 20),
                                          fuse_faces=7000, trunk=(1060, 580, 600, 980, 0.6))
    pm = pod_mask(K, (150, 220, 1000, 690))
    hang_pods(K, pm, crown, masked_material(K, pm, inset=1), copies=1, flatten=0.6, lump=0.12, segments=7,
              stalk=K.colour((0.12, 0.08, 0.03)))
    # mossy rocks, grass at the foot
    stone = K.projected(squeeze=1.0, keep=[(262, 1000, 415, 1085), (540, 1040, 620, 1080)], inset=3)
    zg = P.z(1085)
    for px, w, h, y in ((338, 150, 82, -0.12), (580, 80, 40, -0.1), (420, 60, 30, 0.14), (700, 70, 35, 0.12)):
        K.boulder(P.x(px), y, zg + P.m(h) * 0.5, P.m(w), P.m(w) * 0.7, P.m(h) * 1.1, stone, name="rock")
    K.leaves_only((240, 920, 860, 1090), plant_pixels)
    undergrowth(K, (260, 930, 820, 1080), 22, (70, 60), (-0.2, 0.2))
    earth(K, 555, 330, P.m(600) * 0.35, (420, 1070, 700, 1085), h=P.m(10), z=zg - P.m(8))


def pale_wood(rgb):
    """The drumstick tree's pale cream-grey bark (and its shaded side), not its green leaflets and pods."""
    r, g, b, mx, mn = chan(rgb)
    sat = mx - mn
    cream = (sat < 62) & (mx > 120) & (r >= g - 12) & (g - b < 50) & ~((g - r > 6) & (g - b > 28) & (mx < 175))
    return cream & ~((mn > 200) & (sat < 22))


DRUM_TRUNK = {"h2_2": [(300, 1052, 24), (298, 900, 21), (297, 750, 18), (298, 650, 16), (296, 590, 14)],
              "h2_4": [(232, 828, 16), (231, 760, 13), (230, 700, 12), (232, 600, 10.5), (232, 470, 9)]}
DRUM_FOOT = {"h2_2": 1045, "h2_4": 795}
DRUM_BARK = {"h2_2": (288, 700, 306, 800), "h2_4": (226, 610, 238, 700)}     # clean cream bark, mid trunk


def _trace_drum(K, box, root, exclude=()):
    extra = raster((K.paint.h, K.paint.w), [DRUM_TRUNK[K.name]]) & (K.paint.rgba[..., 3] > 0.5)
    m = wood_mask(K, pale_wood, boxes=[box], exclude=exclude, close=1, hole=150, open_=1, min_area=80, extra=extra)
    return m, Wood(K, m, root_px=root, spur=1.4, min_len=6)


TRACE["h2_2"] = lambda K: _trace_drum(K, (0, 60, 641, 1060), (300, 1045), exclude=[(150, 1000, 400, 1089)])
TRACE["h2_4"] = lambda K: _trace_drum(K, (0, 0, 473, 800), (232, 795))


def drum_pods(K, box):
    """The drumstick tree's long green pods: saturated green, long and upright (an upright opening drops the
    leaflets), with their dark outline."""
    P = K.paint
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    r, g, b, mx, mn = chan(rgb)
    m = (g - b > 45) & (g - r > 12) & (P.rgba[..., 3] > 0.5) & box_mask(r.shape, [box])
    m = ndimage.binary_closing(m, structure=np.ones((5, 1)), iterations=2)
    m = ndimage.binary_opening(m, structure=np.ones((45, 1)))
    m = ndimage.binary_dilation(m, structure=np.ones((3, 3)), iterations=1)
    m = ndimage.binary_fill_holes(m)
    return m


def drumstick_tree(K, crown_box, centre, dome, root, n_cards, card_px, ground):
    P = K.paint
    rng = K.rng
    mask, _ = TRACE[K.name](K)
    # the trunk itself is lofted whole through its painted outline, up from its foot (the traced paths go on from
    # its top)
    tpts = DRUM_TRUNK[K.name]
    full = mask
    mask = mask & ~box_mask(mask.shape, [(0, tpts[-1][1] + 10, P.w, P.h)])
    pods = drum_pods(K, crown_box)
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    r, g, b, mx, mn = chan(rgb)
    halo = (mn > 185) & (mx - mn < 40)
    thick = ndimage.binary_opening(full, iterations=4)
    leaves = (P.rgba[..., 3] > 0.5) & ~halo & ~ndimage.binary_dilation(pods, iterations=2) & ~thick
    box = tuple(int(v) for v in crown_box)
    tx, ty, tr = tpts[0]

    def foot(bark):
        rows = trunk_runs(full, ty, tpts[-1][1] - 25, tpts[-1][0], grow=1.35)      # up into the fork
        out = [loft_trunk(K, rows, bark, y=0.0, depth=0.92, segments=16)]
        for k in range(5):                           # a few roots into the ground
            a = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / 5
            r0 = P.m(tr)
            out.append(K.tube([(P.x(tx) + math.cos(a) * r0 * 0.5, math.sin(a) * r0 * 0.5, P.z(ty) + r0 * 0.8),
                               (P.x(tx) + math.cos(a) * r0 * 1.3, math.sin(a) * r0 * 1.3, P.z(ty) + r0 * 0.1),
                               (P.x(tx) + math.cos(a) * r0 * 2.0, math.sin(a) * r0 * 2.0, P.z(ty))],
                              [r0 * 0.35, r0 * 0.2, r0 * 0.05], bark, segments=8, name="root"))
        return [o for o in out if o is not None]
    wood, crown, bark, thin = traced_tree(K, mask, tpts[-1][:2], crown_box, centre, dome, mask_rule(leaves, box),
                                          spread=0.6, root_z_px=None, limb_py_max=dome[2], limb_py_min=dome[1],
                                          n_limbs=6, n_roots=0, n_cards=n_cards, card_px=card_px, core=0.2,
                                          dome_pow=0.6, min_r_px=2.0, foot=foot, bark_mask=full, r_cap_px=tr * 0.45,
                                          bark_inset=1, tile_box=DRUM_BARK[K.name])
    # the pods: long, thin, ribbed green tubes hanging from the branches, and one more of each round the back
    hang_pods(K, pods, crown, masked_material(K, pods, inset=1), copies=1, flatten=0.85, lump=0.05, min_len=40,
              segments=7)
    return wood, crown, bark


@model("h2_2", "plants", kind="prop", atlas=2048, leaves=1024)
def h2_2(K):
    """A drumstick (moringa) tree: a smooth pale trunk forking into slender limbs, airy sprays of tiny round
    leaflets, a dozen long green drumstick pods hanging straight down, rocks and a grass tuft at its foot."""
    P = K.paint
    drumstick_tree(K, (0, 0, 641, 620), (300, 330), (300, 0, 620), (300, 1045), (200, 90, 50, 20), (70, 60),
                   (240, 1060, 300, 1075))
    stone = K.projected(squeeze=1.0, keep=[(160, 1000, 390, 1085)], inset=3)
    zg = P.z(1080)
    for px, w, h, y in ((240, 95, 62, -0.06), (175, 50, 25, -0.08), (320, 45, 25, -0.07), (275, 60, 28, 0.08),
                        (200, 50, 25, 0.07)):
        K.boulder(P.x(px), y, zg + P.m(h) * 0.5, P.m(w), P.m(w) * 0.7, P.m(h) * 1.1, stone, name="rock")
    K.leaves_only((320, 985, 395, 1062), plant_pixels)
    for yaw in (0, 60, -60):
        K.card_from_painting((320, 985, 395, 1062), (P.x(357), -0.03, P.z(1023)), yaw=yaw, name="grass")


@model("h2_4", "plants", kind="prop", atlas=2048, leaves=1024)
def h2_4(K):
    """A young drumstick tree: a slim cream trunk, a few slender forking limbs, airy sprays of round leaflets and
    long green pods hanging in two bunches, grass at its foot."""
    P = K.paint
    drumstick_tree(K, (0, 0, 473, 520), (232, 260), (250, 0, 520), (232, 818), (170, 80, 45, 15), (60, 52),
                   (225, 820, 240, 830))
    K.leaves_only((180, 790, 290, 835), plant_pixels)
    for box, cx in (((180, 795, 220, 832), 200), ((250, 795, 290, 832), 270)):
        for yaw in (0, 60, -60):
            K.card_from_painting(box, (P.x(cx), K.rng.uniform(-0.03, 0.03), P.z(813)), yaw=yaw, name="grass")


TRACE["h2_3"] = lambda K: _trace_grey(K, [(0, 150, 593, 735)], (300, 715), sat=40, hole=2000,
                                      extra_rule=lambda rgb: ~((chan(rgb)[0] - chan(rgb)[2] > 55))
                                      & ((chan(rgb)[1] - chan(rgb)[2]) <= 26))     # not the pods, not the leaves


@model("h2_3", "plants", kind="prop", atlas=2048, leaves=1024)
def h2_3(K):
    """A young tamarind: a grey trunk with a knot-hole or two, forking into two limbs, a dome of feathery leaves, and
    bunches of brown curved pods hanging below it."""
    P = K.paint
    mask, _ = TRACE["h2_3"](K)
    wood, crown, bark, thin = traced_tree(K, mask, (300, 715), (0, 0, 593, 470), (300, 210), (210, 0, 470),
                                          sage_inked, spread=0.5, root_z_px=680, limb_py_max=420, limb_py_min=150,
                                          n_limbs=6, n_roots=4, root_py=700, n_cards=(170, 80, 45, 15),
                                          card_px=(80, 70), trunk=(700, 440, 305, 660, 0.7))
    pm = pod_mask(K, (100, 60, 500, 460))
    mat = masked_material(K, pm, inset=1)
    pm = pm & ~box_mask(pm.shape, [(398, 345, 478, 440)])          # the bunch of three, traced by hand
    bunch = [([(418, 362), (416, 385), (410, 405), (405, 420)], 9), ([(430, 356), (432, 380), (428, 405), (433, 430)], 9),
             ([(446, 366), (450, 390), (456, 410), (462, 430)], 9)]
    hang_pods(K, pm, crown, mat, copies=2, flatten=0.6, lump=0.12, segments=8, stalk=K.colour((0.12, 0.08, 0.03)),
              traced=bunch)


class DiamondKatte:
    """A square stone platform turned so a corner faces the camera (as painted, seen from a little above): corners
    F (front), L, R painted at x_F, x_L, x_R px; level and square, its top at the front corner's painted height (the
    painted top face recedes in perspective: from the front that face is not matched, and the things standing on it
    stand on the level top)."""

    def __init__(self, K, xL, xF, xR, zL_py, zF_py, cx_px=None):
        P = K.paint
        self.K, self.P = K, P
        a_c, a_s = P.m(xF - xL), P.m(xR - xF)
        self.F = Vector((P.x(xF), -(a_c * a_s) / math.hypot(a_c, a_s) * 0 - 0.0, 0))
        # plan: F + u (L - F) + v (R - F); centre (L + R) / 2 at y = 0
        L2 = Vector((P.x(xL), 0, 0))
        R2 = Vector((P.x(xR), 0, 0))
        dyL, dyR = a_s, a_c                                      # L - F has y = a sin, R - F has y = a cos
        yF = -(dyL + dyR) / 2
        self.F = Vector((P.x(xF), yF, 0))
        self.L = Vector((P.x(xL), yF + dyL, 0))
        self.R = Vector((P.x(xR), yF + dyR, 0))
        self.B = self.L + self.R - self.F
        self.yF = yF
        self.zF, self.zL = P.z(zF_py), P.z(zL_py)
        self.hy = -yF
        self.X0, self.X1 = P.x(xL), P.x(xR)

    def top(self, x, y):
        """Its top is level (at the painted front corner's height); the painting's receding top face is perspective,
        not a slope."""
        return self.zF

    def y_on_top(self, px, py, r_px=0.0, side=-1):
        z = self.P.z(py) - self.P.m(r_px) * 0.6
        t = float(np.clip((z - self.zF) / max(1e-6, self.zL - self.zF), 0.0, 1.0))
        return self.yF * (1 - t) if side < 0 else -self.yF * (1 - t) * 0.9

    def uv(self, x, y):
        M = np.array([[self.L.x - self.F.x, self.R.x - self.F.x], [self.L.y - self.F.y, self.R.y - self.F.y]])
        return np.linalg.solve(M, np.array([x - self.F.x, y - self.F.y]))

    def clip(self, x, y, m=0.04):
        u, v = np.clip(self.uv(x, y), m, 1 - m)
        p = self.F + (self.L - self.F) * float(u) + (self.R - self.F) * float(v)
        return p.x, p.y

    def solid(self, mat, scale, zbot, ztop, n=20, name="platform"):
        """A closed solid over the diamond (scaled about its centre): its top at ztop(x, y), its bottom at
        zbot(x, y) (functions, metres)."""
        c = (self.L + self.R) / 2
        F, L, R = [c + (v - c) * scale for v in (self.F, self.L, self.R)]
        bm = bmesh.new()

        def at(u, v):
            p = F + (L - F) * u + (R - F) * v
            return p.x, p.y
        top = [[bm.verts.new((*at(i / n, j / n), ztop(*at(i / n, j / n)))) for i in range(n + 1)] for j in range(n + 1)]
        bot = [[bm.verts.new((*at(i / n, j / n), zbot(*at(i / n, j / n)))) for i in range(n + 1)] for j in range(n + 1)]
        for j in range(n):
            for i in range(n):
                bm.faces.new([top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]])
                bm.faces.new([bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]])
        ring = [(0, i) for i in range(n)] + [(i, n) for i in range(n)] + [(n, n - i) for i in range(n)] + \
            [(n - i, 0) for i in range(n)]
        for (a, b), (c2, d) in zip(ring, ring[1:] + ring[:1]):
            bm.faces.new([top[a][b], bot[a][b], bot[c2][d], top[c2][d]])
        return _add(K=self.K, bm=bm, mat=mat, name=name, smooth=False)

    def build(self, side_mat, top_mat, coping_mat=None, coping=0.03, lip=0.015, n=20):
        """The platform: its body, from the ground up to under the coping, and the coping slab on it, a little
        proud of the walls, its top sloping as painted."""
        half = (self.R - self.L).length / 2
        self.solid(side_mat, 1.0, lambda x, y: 0.0, lambda x, y: self.top(x, y) - coping, n=n, name="platform_body")
        self.solid(coping_mat or top_mat, 1.0 + lip / half, lambda x, y: self.top(x, y) - coping,
                   lambda x, y: self.top(x, y), n=n, name="platform_coping")


NAGA_STONES = [
    [(840, 1108), (858, 1112), (866, 1135), (862, 1160), (880, 1170), (885, 1195), (860, 1205), (815, 1205),
     (800, 1190), (808, 1170), (828, 1160), (826, 1135)],
    [(905, 1098), (925, 1100), (938, 1120), (935, 1150), (945, 1170), (945, 1190), (890, 1190), (888, 1170),
     (895, 1150), (890, 1120)],
    [(995, 1045), (1020, 1050), (1035, 1080), (1030, 1110), (1025, 1140), (1075, 1150), (1100, 1165), (1095, 1185),
     (1000, 1190), (960, 1180), (960, 1160), (990, 1145), (985, 1110), (980, 1080)],
    [(1135, 1080), (1155, 1085), (1160, 1110), (1158, 1130), (1175, 1150), (1180, 1172), (1110, 1175), (1100, 1160),
     (1120, 1140), (1125, 1110), (1125, 1090)],
]
H31_TRUNK = [(880, 1160, 190), (880, 1050, 175), (880, 950, 152), (880, 850, 145), (885, 750, 135), (890, 650, 115),
             (895, 560, 100), (900, 500, 80), (905, 440, 50), (905, 400, 28)]
H31_LIMBS = [
    [(830, 620, 55), (740, 600, 42), (660, 580, 34), (580, 560, 26), (500, 520, 18)],
    [(880, 560, 70), (860, 470, 55), (850, 380, 40), (860, 300, 30), (880, 220, 20)],
    [(960, 600, 60), (1030, 560, 48), (1090, 520, 38), (1150, 470, 28), (1220, 420, 20)],
    [(760, 760, 40), (690, 712, 32), (615, 685, 26), (520, 678, 20), (430, 672, 15)],
    [(990, 790, 55), (1090, 770, 38), (1180, 748, 33), (1280, 690, 24), (1380, 678, 18)],
    [(1200, 725, 30), (1260, 650, 24), (1330, 610, 18), (1400, 600, 12)],
]
H31_ROOTS = [
    [(720, 1050, 60), (620, 1100, 40), (540, 1140, 22), (490, 1152, 8)],
    [(760, 1080, 55), (700, 1140, 35), (650, 1175, 18), (620, 1190, 8)],
    [(820, 1100, 50), (800, 1160, 30), (790, 1195, 12)],
    [(1000, 1080, 55), (1080, 1120, 40), (1160, 1140, 25), (1220, 1150, 10)],
    [(1050, 1050, 50), (1150, 1100, 35), (1210, 1130, 18)],
]


@model("h3_1", "plants", kind="prop", atlas=2048, leaves=2048)
def h3_1(K):
    """A peepal on its square stone katte, a corner to the front: the massive fluted trunk on roots gripping the
    platform, red and yellow threads wound round it and round its right limb, four carved naga stones at its foot,
    clay lamps burning and marigolds before them, and a broad crown of big heart-shaped leaves."""
    P = K.paint
    rng = K.rng
    katte = DiamondKatte(K, 208, 800, 1582, 1150, 1290)
    side = K.tile((1050, 1310, 1190, 1385), vary=0.06, soften=0.35)      # inside the wall: no edge lines
    top = K.tile((420, 1200, 640, 1260), vary=0.08, soften=0.4)
    coping = K.tile((560, 1262, 760, 1300), vary=0.06, soften=0.3)
    katte.build(side, top, coping, coping=P.m(45), lip=P.m(8))
    # ---- the tree
    zt = katte.top(0.0, 0.0)
    trunk = [(880, P.py(zt) + 4, 200)] + H31_TRUNK          # its foot down onto the level top
    # below the painted roots' tips the painting shows the receding top face: not projected onto the trunk's foot
    # and the roots that now come down onto the level top
    K.front_exclude.append((0, 1170, P.w, P.py(zt) - 2))
    crown, trunk_ob = _peepal_tree(
        K, (0, 0, 1743, 830), trunk, H31_LIMBS, H31_ROOTS, katte, (420, 480, 1420, 1200),
        P.m(1700) * 0.34, (430, 0, 830),
        exclude_wood=[H31_TRUNK[1:], H31_LIMBS[3][:4], H31_LIMBS[4][:4], H31_LIMBS[0][:2], H31_LIMBS[2][:2]],
        bark_exclude=[(0, 1170, 1743, 1468)],
        n_cards=(300, 120, 70), card_px=(180, 160))
    # ---- the threads round the trunk (they droop at the front) and round the right limb
    red = K.colour((0.6, 0.08, 0.02), vary=0.12)
    yellow = K.colour((0.85, 0.55, 0.06), vary=0.12)
    tx = P.x(880)
    for k, py in enumerate(np.linspace(905, 985, 9)):
        rr = P.m(160 + (py - 900) * 0.25)
        ring_tube(K, tx, 0.0, P.z(py), rr, rr, red if k % 3 else yellow, P.m(3),
                  tilt=(rng.uniform(-0.01, 0.01), P.m(rng.uniform(5, 25))), wobble=0.02, name="thread")
    a, b = H31_LIMBS[4][0], H31_LIMBS[4][2]
    for mat, n in ((red, 6), (yellow, 5)):
        wrap_limb(K, (P.x(1060), 0.0, P.z(780)), (P.x(1170), 0.0, P.z(752)), P.m(40), mat, n, P.m(3))
    for px in (1105, 1120, 1135, 1150, 1165):
        strand(K, (P.x(px), -P.m(30), P.z(800)), P.m(rng.uniform(40, 110)), rng.choice([red, yellow]), P.m(3))
    # the knot and tassels at the front of the trunk band
    for px in (930, 950, 965, 980):
        K.tube([(P.x(px), -P.m(165), P.z(960)), (P.x(px), -P.m(170), P.z(1000 + rng.uniform(0, 30)))], P.m(4),
               rng.choice([red, yellow]), segments=5, name="tassel")
    # ---- the naga stones, the lamps and the flowers on the platform
    # each stands on the level top, below where it is painted on the receding top face: it carries its own painted
    # carving down with it (a projection of its painted place), and the painting is not projected onto it from the
    # front where it now stands (nor onto the trunk's foot where it was painted)
    def sunk(box, bot):
        dz = P.z(bot) - zt
        K.front_exclude.append(tuple(box))
        K.front_exclude.append((box[0], box[1] + P.m(0) + dz * P.ppm, box[2], box[3] + dz * P.ppm))
        return dz
    for poly in NAGA_STONES:
        bot = max(p[1] for p in poly)
        x0, x1, y0 = min(p[0] for p in poly), max(p[0] for p in poly), min(p[1] for p in poly)
        cx = (x0 + x1) / 2
        y = katte.y_on_top(cx, bot, 0) + P.m(18)
        dz = sunk((x0 - 4, y0 - 4, x1 + 4, bot + 4), bot)
        carved = K.projected(axis_x=P.x(cx), squeeze=0.9, keep=[(x0, y0, x1, bot)], inset=2, dz=dz)
        ob = poly_solid(K, poly, y, carved, depth=0.5, name="naga")
        if ob is not None:
            ob.data.transform(Matrix.Translation((0, 0, -dz - 0.004)))
    clay = K.colour((1010, 1205, 1040, 1215), vary=0.08)
    flame = K.colour((0.95, 0.6, 0.05), vary=0.05)
    for x0, x1, top_py, bot_py, fx in ((908, 970, 1185, 1212, 960), (1000, 1065, 1195, 1225, 1058),
                                       (1185, 1245, 1160, 1186, 1242)):
        cx, rw = (x0 + x1) / 2, (x1 - x0) / 2
        y = katte.y_on_top(cx, bot_py, 0)
        zb = katte.top(P.x(cx), y)
        hh = P.m(bot_py - top_py)
        sunk((x0 - 4, top_py - 30, x1 + 4, bot_py + 4), bot_py)
        K.lathe([(P.m(rw) * 0.45, 0.0), (P.m(rw) * 0.85, hh * 0.45), (P.m(rw), hh), (P.m(rw) * 0.88, hh * 0.95),
                 (P.m(rw) * 0.5, hh * 0.7), (0.0, hh * 0.65)], clay, segments=18, centre=(P.x(cx), y, zb),
                name="lamp")
        K.lathe([(0.0, 0.0), (P.m(4), P.m(5)), (P.m(3.5), P.m(12)), (0.0, P.m(24))], flame, segments=10,
                centre=(P.x(fx), y, zb + hh * 0.8), name="flame")
    for x0, y0, x1, y1 in ((1095, 1178, 1185, 1215), (1030, 1140, 1062, 1160)):
        cx = (x0 + x1) / 2
        dz = sunk((x0 - 3, y0 - 3, x1 + 3, y1 + 3), y1)
        petals = K.projected(squeeze=1.0, keep=[(x0, y0, x1, y1)], inset=1, dz=dz)
        poly = [(cx + (x1 - x0) / 2 * math.cos(t), (y0 + y1) / 2 + (y1 - y0) / 2 * math.sin(t))
                for t in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        ob = poly_solid(K, poly, katte.y_on_top(cx, y1, 0) + P.m(y1 - y0) * 0.3, petals, depth=0.9, name="flowers",
                        segments=10)
        if ob is not None:
            ob.data.transform(Matrix.Translation((0, 0, -dz - 0.003)))
