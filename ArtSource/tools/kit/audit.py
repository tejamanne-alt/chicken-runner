"""Audits the exported models: each FBX as the game loads it, checked against its painting and seen from every side.

    python ArtSource/tools/kit/audit.py --out DIR [--only a,b] [--folder lane] [--jobs 4]
    python ArtSource/tools/kit/audit.py --summary DIR            # DIR/summary.md and DIR/summary.json

For each model (ArtSource/models_kit/<name>.json) it imports Assets/ChickenRunner/Art/Models/<folder>/<name>.fbx, gives
it the game's toon look from its own atlas (and its leaf cards from <name>_leaves.png, cut out), and writes:

  DIR/<name>.jpg    the audit sheet: the painting, the model's front in the painting's frame, a difference map (red:
                    painted but missing in the model, blue: model where the painting is empty, yellow-white: colour
                    differs), the measurements; then the model from eight directions round it (every 45 degrees, a
                    little above eye level) and from above
  DIR/<name>.json   the measurements and the flags they raise

Measurements:
  front     iou (painted vs modelled silhouette), holes (share of the painting the model leaves empty), spill (model
            outside the painting), colour error (median and 90th percentile, 0-255, where both are opaque) and the share
            of the overlap that is badly off (> 60): smears, misplaced parts and wrong materials show up here
  views     for each of the nine views: streaks (blocks of the image smeared in one direction: a projection dragged
            across a side), flat (blocks of one flat colour: an untextured face), dark (pixels near black inside the
            silhouette, not counting the ink line); each against the same measure on the painting
  geometry  size against the painting's frame, how far the base floats above or sinks below the ground, parts lying
            loose in the air, parts turned inside out (closed parts with negative volume), texture stretch (share of
            the surface whose atlas mapping is stretched more than 3:1) and blur (share with less than a quarter of the
            usual texels), faces
A flag is a reason to look, not a verdict: the verdict is the eye's, on the sheet (see LEARNINGS.md, "Audit").
"""
import json
import math
import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ARGS = sys.argv[1:]


def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default


ROOT = HERE.parents[2]
RECORDS = ROOT / "ArtSource" / "models_kit"
MODELS = ROOT / "Assets" / "ChickenRunner" / "Art" / "Models"
BUDGET = {"building": 20000, "volume": 25000, "slab": 8000}
VIEWS = [(f"{name}", yaw, 12) for name, yaw in (("front", 0), ("front-right", 45), ("right", 90), ("back-right", 135),
                                               ("back", 180), ("back-left", 225), ("left", 270), ("front-left", 315))]
VIEWS.append(("above", 330, 58))


# ====================================================================== summary (no Blender needed)
FLAG_TEXT = {
    "front_holes": "front: parts of the painting missing in the model",
    "front_spill": "front: model reaches outside the painting",
    "front_colour": "front: colour differs from the painting over a large area",
    "streaks": "a side view is smeared (streaks)",
    "flat": "a side view has large flat untextured faces",
    "dark": "a side view has large near-black areas",
    "repeat": "a side view shows a texture repeating visibly",
    "floating": "the base floats above the ground",
    "sunk": "the base sinks well below the ground",
    "loose_parts": "parts hang loose in the air",
    "inside_out": "parts are turned inside out",
    "uv_stretch": "texture stretched over part of the surface",
    "uv_blur": "texture too coarse over part of the surface",
    "uv_squash": "the whole texture squashed one way (half its resolution in one direction)",
    "size": "size differs from the painting's frame",
    "faces": "over the face budget",
}


def flags_of(r):
    f = []
    fr = r["front"]
    if fr["holes"] > 0.06:
        f.append("front_holes")
    if fr["spill"] > 0.10:
        f.append("front_spill")
    if fr["bad"] > 0.18:
        f.append("front_colour")
    worst = lambda key: max(v[key] - v.get(key + "_base", 0) for v in r["views"].values())
    if worst("streaks") > 0.18:
        f.append("streaks")
    if worst("flat") > 0.30:
        f.append("flat")
    if max(v["dark"] for v in r["views"].values()) > max(0.12, 2.5 * r["paint_dark"]):
        f.append("dark")
    if max(v.get("repeat", 0) - max(0.45, v.get("repeat_base", 0) + 0.15) for v in r["views"].values()) > 0:
        f.append("repeat")
    g = r["geometry"]
    if g["base_z"] > 0.1:                      # the game sets a model down by up to 10 cm (its record's "lift")
        f.append("floating")
    if g["base_z"] < -0.25:
        f.append("sunk")
    if g["loose_parts"] > 0:
        f.append("loose_parts")
    if g["inside_out"] > 0:
        f.append("inside_out")
    if g["uv_stretch"] > 0.08:
        f.append("uv_stretch")
    if g["uv_blur"] > 0.15:
        f.append("uv_blur")
    if g.get("uv_squash", 1.0) > 1.3:
        f.append("uv_squash")
    if abs(g["width_ratio"] - 1) > 0.25 or abs(g["height_ratio"] - 1) > 0.25:
        f.append("size")
    if g["faces"] > BUDGET.get(r["kind"], 25000) * 1.15:
        f.append("faces")
    return f


def summary(out):
    out = pathlib.Path(out)
    rows = []
    for p in sorted(out.glob("*.json")):
        if p.name.startswith("summary"):
            continue
        r = json.loads(p.read_text())
        r["flags"] = flags_of(r)
        rows.append(r)
    rows.sort(key=lambda r: (-len(r["flags"]), r["front"]["iou"]))
    lines = [f"# Model audit: {len(rows)} models", "",
             "Flags are reasons to look, from the measurements; the verdicts are by eye, on each sheet.", "",
             "| Model | Folder | Front IoU | Holes | Colour off | Worst streaks | Worst flat | Flags |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        v = r["views"]
        ws = max(x["streaks"] - x.get("streaks_base", 0) for x in v.values())
        wf = max(x["flat"] - x.get("flat_base", 0) for x in v.values())
        lines.append(f"| {r['name']} | {r['folder']} | {r['front']['iou']:.2f} | {r['front']['holes']:.2f} | "
                     f"{r['front']['bad']:.2f} | {ws:.2f} | {wf:.2f} | {', '.join(r['flags']) or '-'} |")
    counts = {}
    for r in rows:
        for f in r["flags"]:
            counts[f] = counts.get(f, 0) + 1
    lines += ["", "## Flags", ""] + [f"- {k} ({FLAG_TEXT[k]}): {n}" for k, n in sorted(counts.items(), key=lambda x: -x[1])]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    (out / "summary.json").write_text(json.dumps([{k: r[k] for k in ("name", "folder", "flags")} | {
        "iou": r["front"]["iou"], "holes": r["front"]["holes"], "bad": r["front"]["bad"]} for r in rows], indent=1))
    print(f"{len(rows)} models, {sum(1 for r in rows if r['flags'])} flagged -> {out / 'summary.md'}")


# ====================================================================== the audit itself (inside Blender)
def audit_one(name, out):
    import bpy
    import bmesh
    import numpy as np
    from mathutils import Matrix, Vector
    from PIL import Image, ImageDraw, ImageFilter
    import kitlib as KL
    import review as RV

    rec = json.loads((RECORDS / f"{name}.json").read_text())
    folder = rec["folder"]
    fbx = MODELS / folder / f"{name}.fbx"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    main = next((o for o in meshes if not o.name.endswith("_leaves")), meshes[0])
    leaves = next((o for o in meshes if o.name.endswith("_leaves")), None)
    scene = bpy.context.scene

    # ---------------------------------------------------------------- geometry, on the imported mesh
    deps = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in meshes:
        pts += [o.matrix_world @ v.co for v in o.data.vertices]
    P = np.array([tuple(p) for p in pts])
    bmin, bmax = P.min(0), P.max(0)
    me = main.data
    mw = main.matrix_world
    co = np.array([tuple(mw @ v.co) for v in me.vertices])
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(mw)
    bm.verts.ensure_lookup_table()
    # connected parts
    seen = set()
    parts = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            x = stack.pop()
            comp.append(x)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen:
                    seen.add(y.index)
                    stack.append(y)
        parts.append(comp)
    boxes = []
    inside_out = 0
    for comp in parts:
        idx = {v.index for v in comp}
        c = np.array([tuple(v.co) for v in comp])
        boxes.append((c.min(0), c.max(0)))
        faces = {f for v in comp for f in v.link_faces}
        closed = all(e.is_manifold for f in faces for e in f.edges)
        if closed and len(faces) > 6:
            vol = 0.0
            for f in faces:
                vs = [l.vert.co for l in f.loops]
                for i in range(1, len(vs) - 1):
                    vol += vs[0].dot(vs[i].cross(vs[i + 1])) / 6
            if vol < -1e-6:
                inside_out += 1
    loose = 0
    for i, (lo, hi) in enumerate(boxes):
        if lo[2] < 0.05:
            continue
        touching = False
        for j, (lo2, hi2) in enumerate(boxes):
            if i == j:
                continue
            if np.all(lo <= hi2 + 0.03) and np.all(lo2 <= hi + 0.03):
                touching = True
                break
        if not touching and (hi - lo).max() > 0.03:
            loose += 1
    # texture stretch and density over the atlas
    uv = bm.loops.layers.uv.active
    stretch_area = blur_area = total = 0.0
    dens, aniso = [], []
    tris = bm.calc_loop_triangles()
    for t in tris:
        a, b, c = (l.vert.co for l in t)
        A = ((b - a).cross(c - a)).length / 2
        if A < 1e-9 or uv is None:
            continue
        ua, ub, uc = (Vector(t[i][uv].uv) for i in range(3))
        Au = abs((ub - ua).x * (uc - ua).y - (ub - ua).y * (uc - ua).x) / 2
        e1, e2 = b - a, c - a
        x = e1.normalized()
        n = e1.cross(e2).normalized()
        y = n.cross(x)
        M3 = np.array([[e1.dot(x), e2.dot(x)], [e1.dot(y), e2.dot(y)]])
        Mu = np.array([[(ub - ua).x, (uc - ua).x], [(ub - ua).y, (uc - ua).y]])
        try:
            J = Mu @ np.linalg.inv(M3)
            s = np.linalg.svd(J, compute_uv=False)
            st = s[0] / max(s[1], 1e-12)
        except np.linalg.LinAlgError:
            st = 99.0
        dens.append((Au / A, A))
        aniso.append((st, A))
        total += A
        if st > 3:
            stretch_area += A
    if dens:
        d = np.array(dens)
        order = np.argsort(d[:, 0])
        cum = np.cumsum(d[order, 1]) / d[:, 1].sum()
        med = d[order, 0][np.searchsorted(cum, 0.5)]
        blur_area = d[d[:, 0] < 0.25 * med, 1].sum()
    squash = 1.0
    if aniso:    # the area-weighted median stretch: above 1 when the whole atlas is squashed one way
        q = np.array(aniso)
        order = np.argsort(q[:, 0])
        cum = np.cumsum(q[order, 1]) / q[:, 1].sum()
        squash = float(q[order, 0][np.searchsorted(cum, 0.5)])
    bm.free()
    nfaces = sum(len(o.data.polygons) for o in meshes)
    geometry = {
        "width_ratio": float((bmax[0] - bmin[0]) / rec["width"]), "height_ratio": float(bmax[2] / rec["height"]),
        "depth": float(bmax[1] - bmin[1]), "base_z": float(bmin[2]), "parts": len(parts), "loose_parts": loose,
        "inside_out": inside_out, "uv_stretch": float(stretch_area / max(total, 1e-9)),
        "uv_blur": float(blur_area / max(total, 1e-9)), "uv_squash": squash, "faces": nfaces,
        "cards": len(leaves.data.polygons) if leaves else 0,
    }

    # ---------------------------------------------------------------- the toon look, from the model's own textures
    def image(path):
        return bpy.data.images.load(str(path)) if path.exists() else None

    def toon(img, name, cutout=False):
        tmp = bpy.data.materials.new(name + "_src")
        tmp.use_nodes = True
        t = tmp.node_tree.nodes.new("ShaderNodeTexImage")
        t.image = img
        return RV._toon(tmp, name, cutout=cutout)
    main.data.materials.clear()
    main.data.materials.append(toon(image(MODELS / folder / f"{name}.jpg"), "toon_main"))
    W, H = rec["width"], rec["height"]
    # The game's ink outline: none on flat pieces (they lie on the ground) or on a part under 2 cm (a cards-only
    # model's anchor), as ArtModels.Place draws it.
    if rec.get("kind") != "slab" and max(main.dimensions) >= 0.02:
        ink = main.modifiers.new("ink", "SOLIDIFY")
        ink.thickness = min(0.012, max(0.003, 0.0025 * max(W, H)))
        ink.offset = 1.0
        ink.use_flip_normals = True
        ink.material_offset = 1
        main.data.materials.append(RV._ink(ink.thickness))
    if leaves is not None:
        leaves.data.materials.clear()
        leaves.data.materials.append(toon(image(MODELS / folder / f"{name}_leaves.png"), "toon_leaves", cutout=True))
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 6
    scene.cycles.device = "CPU"
    scene.cycles.transparent_max_bounces = 128
    scene.cycles.max_bounces = 128
    KL.threads(scene)
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.world = bpy.data.worlds.new("w")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.clip_end = 500
    tmpdir = pathlib.Path(out) / "_tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)

    def render(path, rx, ry):
        scene.render.resolution_x, scene.render.resolution_y = rx, ry
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        im = Image.open(path).convert("RGBA")
        path.unlink()
        return im

    # front, in the painting's frame
    long = 640
    rx, ry = (long, max(8, round(long * H / W))) if W >= H else (max(8, round(long * W / H)), long)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(W, H)
    cam.location = (0, -100, H / 2)
    cam.rotation_euler = (math.radians(90), 0, 0)
    front = render(tmpdir / f"{name}_front.png", rx, ry)
    paint = KL.Painting(name, folder).img.convert("RGBA").resize((rx, ry), Image.LANCZOS)
    pa = np.asarray(paint).astype(np.float32)
    fa = np.asarray(front).astype(np.float32)
    pm, fm = pa[..., 3] > 127, fa[..., 3] > 127
    both = pm & fm
    blur = lambda a: np.asarray(Image.fromarray(a.clip(0, 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(2))).astype(np.float32)
    err = np.abs(blur(pa[..., :3]) - blur(fa[..., :3])).mean(2)
    e = err[both] if both.any() else np.array([255.0])
    frontm = {
        "iou": float((pm & fm).sum() / max(1, (pm | fm).sum())), "holes": float((pm & ~fm).sum() / max(1, pm.sum())),
        "spill": float((fm & ~pm).sum() / max(1, pm.sum())), "colour_median": float(np.median(e)),
        "colour_p90": float(np.percentile(e, 90)), "bad": float((e > 60).mean()),
    }
    # the difference map: grey painting, yellow-white where colour is off, red holes, blue spill
    g = pa[..., :3].mean(2, keepdims=True) * 0.45 + 120
    diff = np.repeat(g, 3, 2)
    hot = np.clip((err - 25) / 60, 0, 1)[..., None] * both[..., None]
    diff = diff * (1 - hot) + np.array([255, 235, 120]) * hot
    diff[pm & ~fm] = (220, 40, 40)
    diff[fm & ~pm] = (40, 90, 230)
    diff[~pm & ~fm] = (226, 221, 210)
    diff_im = Image.fromarray(diff.clip(0, 255).astype(np.uint8))

    # image measures, for a render or the painting
    def measures(arr):
        a = arr.astype(np.float32)
        m = a[..., 3] > 127
        lum = a[..., :3] @ np.array([0.3, 0.59, 0.11])
        # inside, away from the ink line
        from scipy import ndimage
        inner = ndimage.binary_erosion(m, iterations=4)
        gy, gx = np.gradient(lum)
        B = 12
        hh, ww = lum.shape
        streak = flat = cnt = 0
        for y0 in range(0, hh - B + 1, B):
            for x0 in range(0, ww - B + 1, B):
                if not inner[y0:y0 + B, x0:x0 + B].all():
                    continue
                cnt += 1
                blk = a[y0:y0 + B, x0:x0 + B, :3]
                if blk.std(axis=(0, 1)).max() < 2.5:
                    flat += 1
                    continue
                ex = (gx[y0:y0 + B, x0:x0 + B] ** 2).sum()
                ey = (gy[y0:y0 + B, x0:x0 + B] ** 2).sum()
                if max(ex, ey) > 400 * B * B / 144 and max(ex, ey) > 10 * min(ex, ey):
                    streak += 1
        dark = float(((lum < 35) & inner).sum() / max(1, inner.sum()))
        # a tile repeating visibly: the image's detail correlates with itself shifted by one tile
        rep = 0.0
        if inner.sum() > 4000:
            hp = (lum - ndimage.gaussian_filter(lum, 6)) * inner
            mk = inner.astype(np.float32)
            F = np.fft.rfft2(hp, s=(2 * hh, 2 * ww))
            M = np.fft.rfft2(mk, s=(2 * hh, 2 * ww))
            ac = np.fft.irfft2(F * np.conj(F), s=(2 * hh, 2 * ww))
            ov = np.fft.irfft2(M * np.conj(M), s=(2 * hh, 2 * ww))
            var = (hp ** 2).sum() / max(1.0, mk.sum())
            corr = ac / np.maximum(ov, 1.0) / max(var, 1e-6)
            yy = np.fft.fftfreq(2 * hh, 1 / (2 * hh))[:, None]
            xx = np.fft.fftfreq(2 * ww, 1 / (2 * ww))[None, :]
            ok = (ov > 0.3 * mk.sum()) & ((np.abs(yy) > 24) | (np.abs(xx) > 24))
            rep = float(corr[ok].max()) if ok.any() else 0.0
        return {"streaks": streak / max(1, cnt), "flat": flat / max(1, cnt), "dark": dark, "blocks": cnt, "repeat": rep}
    base = measures(np.asarray(paint))

    # eight round and one from above
    lo = np.array([min(p[i] for p in [bmin]) for i in range(3)])
    centre = Vector(((bmin[0] + bmax[0]) / 2, (bmin[1] + bmax[1]) / 2, (bmin[2] + bmax[2]) / 2))
    radius = float(np.linalg.norm(bmax - bmin)) / 2
    cam.data.type = "PERSP"
    cam.data.lens = 50
    fov = 2 * math.atan(18 / 50)
    dist = radius / math.sin(fov / 2) * 1.02
    res = 460
    views, vm = [], {}
    for label, yaw, pitch in VIEWS:
        a, b = math.radians(yaw), math.radians(pitch)
        loc = centre + Vector((dist * math.sin(a) * math.cos(b), -dist * math.cos(a) * math.cos(b), dist * math.sin(b)))
        cam.location = loc
        cam.rotation_euler = (centre - loc).to_track_quat("-Z", "Y").to_euler()
        im = render(tmpdir / f"{name}_{label}.png", res, res)
        views.append((label, im))
        m = measures(np.asarray(im))
        m["streaks_base"], m["flat_base"], m["repeat_base"] = base["streaks"], base["flat"], base["repeat"]
        vm[label] = m

    result = {"name": name, "folder": folder, "kind": rec["kind"], "front": frontm, "views": vm, "geometry": geometry,
              "paint_dark": base["dark"]}
    result["flags"] = flags_of(result)
    (pathlib.Path(out) / f"{name}.json").write_text(json.dumps(result, indent=1))

    # ---------------------------------------------------------------- the sheet
    cell = 460
    pad = 8
    cols = 4
    sheet = Image.new("RGB", (pad + cols * (cell + pad), pad + 4 * (cell + 26)), (205, 198, 186))
    d = ImageDraw.Draw(sheet)

    def put(i, im, label):
        x, y = pad + (i % cols) * (cell + pad), pad + (i // cols) * (cell + 26)
        bg = Image.new("RGBA", (cell, cell), (226, 221, 210, 255))
        t = im.copy()
        t.thumbnail((cell, cell))
        bg.alpha_composite(t.convert("RGBA"), ((cell - t.width) // 2, (cell - t.height) // 2))
        sheet.paste(bg.convert("RGB"), (x, y))
        d.text((x + 4, y + cell + 6), label, fill=(40, 30, 20))
    put(0, KL.Painting(name, folder).img, f"{name}: painting")
    put(1, front, "model, front (painting's frame)")
    put(2, diff_im, "difference: red missing, blue extra, yellow off")
    txt = Image.new("RGBA", (cell, cell), (245, 241, 232, 255))
    td = ImageDraw.Draw(txt)
    lines = [f"{name} ({folder}, {rec['kind']})", "",
             f"front  IoU {frontm['iou']:.2f}  holes {frontm['holes']:.2f}  spill {frontm['spill']:.2f}",
             f"       colour median {frontm['colour_median']:.0f}  p90 {frontm['colour_p90']:.0f}  off {frontm['bad']:.2f}",
             f"size   w {geometry['width_ratio']:.2f}  h {geometry['height_ratio']:.2f}  depth {geometry['depth']:.2f} m",
             f"base   {geometry['base_z']:+.3f} m   parts {geometry['parts']}  loose {geometry['loose_parts']}",
             f"inside-out {geometry['inside_out']}   faces {geometry['faces']}  cards {geometry['cards']}",
             f"uv     stretch {geometry['uv_stretch']:.2f}  blur {geometry['uv_blur']:.2f}  squash {geometry.get('uv_squash', 1.0):.2f}",
             f"paint  streaks {base['streaks']:.2f}  flat {base['flat']:.2f}  dark {base['dark']:.2f}", "",
             f"paint  repeat {base['repeat']:.2f}", "views  streaks  flat  dark  repeat"]
    for label, _ in views:
        m = vm[label]
        lines.append(f"{label:12s} {m['streaks']:.2f}   {m['flat']:.2f}  {m['dark']:.2f}  {m['repeat']:.2f}")
    lines += ["", "FLAGS: " + (", ".join(result["flags"]) or "none")]
    for i, ln in enumerate(lines):
        td.text((10, 10 + i * 17), ln, fill=(30, 25, 20))
    sheet.paste(txt.convert("RGB"), (pad + 3 * (cell + pad), pad))
    for i, (label, im) in enumerate(views):
        put(4 + i, im, f"{name}: {label}")
    sheet.save(pathlib.Path(out) / f"{name}.jpg", quality=88)
    return result


def names_for(only=None, folder=None, module=None):
    recs = {p.stem: json.loads(p.read_text()) for p in RECORDS.glob("*.json")}
    names = sorted(recs)
    if only:
        names = [n for n in names if n in set(only.split(","))]
    if folder:
        names = [n for n in names if recs[n]["folder"] in set(folder.split(","))]
    if module:
        import importlib
        import kitlib as KL
        for m in module.split(","):
            importlib.import_module(m)
        names = [n for n in names if n in KL.MODELS]
    return names


def main():
    if "--summary" in ARGS:
        return summary(arg("--summary"))
    out = pathlib.Path(arg("--out", "/tmp/model_audit"))
    out.mkdir(parents=True, exist_ok=True)
    jobs = int(arg("--jobs", "1"))
    names = names_for(arg("--only"), arg("--folder"), arg("--module"))
    if jobs > 1:
        chunks = [names[i::jobs] for i in range(jobs)]
        env = dict(os.environ, KIT_THREADS=os.environ.get("KIT_THREADS", "1"))
        procs = [subprocess.Popen([sys.executable, __file__, "--out", str(out), "--only", ",".join(c)], env=env,
                                  stdout=open(out / f"_log{i}.txt", "w"), stderr=subprocess.STDOUT)
                 for i, c in enumerate(chunks) if c]
        for p in procs:
            p.wait()
        return summary(out)
    for n in names:
        t = time.time()
        try:
            r = audit_one(n, out)
            print(f"AUDIT {n}: iou {r['front']['iou']:.2f} flags {r['flags']} ({time.time() - t:.0f} s)", flush=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"AUDIT {n}: FAILED {e!r}", flush=True)
    if len(names) > 1:
        summary(out)


if __name__ == "__main__":
    main()
