"""Fits each generated model to its painting and exports it for Unity: the Meshy models made from the four-view
sheets (ArtSource/models_meshy/<folder>/<name>.glb) first, else the TRELLIS ones (ArtSource/models_ai).

    python finish_models.py [--only name1,name2] [--sheet OUT.png]

For every piece:

1. Turn it to face the camera. TRELLIS stands the object up but chooses its own heading, so the model is turned
   about the vertical in steps (then finely) until its outline seen from the front best matches the cut-out's.
2. Size and place it as the card it replaces: its outline from the front fills the cut-out's painted area, at the
   cut-out's real size (the manifest), standing on the ground; a building's front on the card's plane, anything
   else centred on it.
3. Put the painting back on the front. Wherever the front camera sees the surface squarely, the painting itself is
   projected onto it (it is sharper and truer than the generated texture); elsewhere (sides, back, top) the
   generated texture stays, blending between them by angle. Baked into one texture.
4. Export Assets/ChickenRunner/Art/Models/<folder>/<name>.fbx with its .jpg, and its entry in models.json, replacing
   the extruded model build_models.py made for it. Pieces without a TRELLIS model keep theirs.
"""
import json
import math
import pathlib
import sys
import tempfile

sys.argv = [sys.argv[0], "--no-fbx"] + sys.argv[1:]   # build_models reads the arguments too; keep it from exporting
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from scipy import ndimage  # noqa: E402

import build_models as B  # noqa: E402

ARGS = sys.argv[2:]
ONLY = set(ARGS[ARGS.index("--only") + 1].split(",")) if "--only" in ARGS else None
SHEET = pathlib.Path(ARGS[ARGS.index("--sheet") + 1]) if "--sheet" in ARGS else None
AI = B.ROOT / "ArtSource" / "models_ai"
MESHY = B.ROOT / "ArtSource" / "models_meshy"    # models made in Meshy from the four-view sheets (view_prompts.py)
LISTING = B.OUT / "models.json"
MASK_RES = 160


# ------------------------------------------------------------------ outline matching
def outline(xz, tris, res, box=None):
    """The filled outline of triangles projected onto (x, z), rasterised into a res-sized mask over its bounding box."""
    lo = xz.min(0) if box is None else box[0]
    hi = xz.max(0) if box is None else box[1]
    span = np.maximum(hi - lo, 1e-6)
    scale = (res - 1) / span.max()
    w, h = max(2, int(span[0] * scale) + 1), max(2, int(span[1] * scale) + 1)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    p = (xz - lo) * scale
    p[:, 1] = (h - 1) - p[:, 1]
    for t in tris:
        d.polygon([tuple(p[t[0]]), tuple(p[t[1]]), tuple(p[t[2]])], fill=255)
    return np.asarray(im) > 0


def cutout_mask(png):
    """The painted area of the cut-out, cropped to its bounding box, and that box in the image's pixels."""
    a = np.asarray(Image.open(png).convert("RGBA"))[..., 3] > 110
    rows, cols = np.where(a.any(1))[0], np.where(a.any(0))[0]
    return a[rows.min():rows.max() + 1, cols.min():cols.max() + 1], (cols.min(), rows.min(), cols.max() + 1, rows.max() + 1)


def fit_to(mask, shape):
    im = Image.fromarray(mask.astype(np.uint8) * 255).resize((shape[1], shape[0]), Image.BILINEAR)
    return np.asarray(im) > 127


def iou(a, b):
    return (a & b).sum() / max(1, (a | b).sum())


def same_height(mask, h):
    """The mask scaled to h rows, its proportions kept."""
    w = max(2, int(round(mask.shape[1] * h / mask.shape[0])))
    return np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((w, h), Image.BILINEAR)) > 127


def overlap(a, b):
    """IoU of two masks of the same height, centred side by side: shape and proportions both count."""
    w = max(a.shape[1], b.shape[1])
    pa = np.zeros((a.shape[0], w), bool)
    pb = np.zeros((b.shape[0], w), bool)
    pa[:, (w - a.shape[1]) // 2:(w - a.shape[1]) // 2 + a.shape[1]] = a
    pb[:, (w - b.shape[1]) // 2:(w - b.shape[1]) // 2 + b.shape[1]] = b
    return iou(pa, pb)


def vertex_colours(me, image):
    """Each vertex's colour in the generated texture (0..1 RGB)."""
    if image is None:
        return np.full((len(me.vertices), 3), 0.6)
    w, h = image.size
    px = np.array(image.pixels[:], dtype=np.float32).reshape(h, w, -1)[..., :3]
    uv = np.zeros(len(me.loops) * 2)
    me.uv_layers[0].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    lv = np.zeros(len(me.loops), int)
    me.loops.foreach_get("vertex_index", lv)
    col = np.zeros((len(me.vertices), 3))
    xs = np.clip((uv[:, 0] % 1) * (w - 1), 0, w - 1).astype(int)
    ys = np.clip((uv[:, 1] % 1) * (h - 1), 0, h - 1).astype(int)
    col[lv] = px[ys, xs]
    return np.clip(col, 0, 1)       # an 8-bit sRGB texture reads back as stored: already as painted


def view(co, tris, colours, deg, res):
    """The model seen from the front after turning it `deg` degrees: an RGB picture and its mask, cropped to the
    outline (triangles drawn far to near)."""
    r = math.radians(deg)
    x = co[:, 0] * math.cos(r) - co[:, 1] * math.sin(r)
    y = co[:, 0] * math.sin(r) + co[:, 1] * math.cos(r)
    xz = np.stack([x, co[:, 2]], 1)
    lo, hi = xz.min(0), xz.max(0)
    scale = (res - 1) / max(1e-6, (hi - lo).max())
    w, h = max(2, int((hi[0] - lo[0]) * scale) + 1), max(2, int((hi[1] - lo[1]) * scale) + 1)
    p = (xz - lo) * scale
    p[:, 1] = (h - 1) - p[:, 1]
    rgb = Image.new("RGB", (w, h), (0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    dr, dm = ImageDraw.Draw(rgb), ImageDraw.Draw(mask)
    order = np.argsort(-y[tris].mean(1))                    # the camera looks along +y: largest y is farthest
    tri_col = (colours[tris].mean(1) * 255).astype(int)
    for t in order:
        pts = [tuple(p[i]) for i in tris[t]]
        dr.polygon(pts, fill=tuple(tri_col[t]))
        dm.polygon(pts, fill=255)
    return np.asarray(rgb).astype(float) / 255, np.asarray(mask) > 0


def heading(co, tris, colours, png):
    """The turn about the vertical (degrees) at which the model, seen from the front, looks most like the painting:
    TRELLIS repeats the painting on the side it was shown, so colour picks that side out (and tells it from its
    back, whose outline is the same mirrored); the outline helps where colours are plain."""
    src = Image.open(png).convert("RGBA")
    a = np.asarray(src)
    rows, cols = np.where((a[..., 3] > 110).any(1))[0], np.where((a[..., 3] > 110).any(0))[0]
    crop = src.crop((cols.min(), rows.min(), cols.max() + 1, rows.max() + 1))
    side = 96

    def score(deg):
        rgb, mask = view(co, tris, colours, deg, 200)
        # both squeezed to the same square: compare where things are, not the proportions TRELLIS chose
        m = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((side, side), Image.BILINEAR)) > 127
        c = np.asarray(Image.fromarray((rgb * 255).astype(np.uint8)).resize((side, side), Image.BILINEAR)) / 255
        t = np.asarray(crop.resize((side, side), Image.BILINEAR)).astype(float) / 255
        tm = t[..., 3] > 0.45
        both = m & tm
        colour = 1 - np.abs(c[both] - t[both, :3]).mean() * 2 if both.any() else 0
        return 0.6 * colour + 0.4 * iou(m, tm)
    # TRELLIS stands things square to its axes and the paintings are elevations, so the painted side is one of the
    # four square-on views; colour says which. Then a small correction, only if it clearly helps.
    square = max((0, 90, 180, 270), key=score)
    base = score(square)
    fine = max(np.arange(square - 10, square + 10.1, 2.5), key=lambda d: score(d) - 0.003 * abs(d - square))
    best = fine if score(fine) > base + 0.01 else square
    return float(best), score(best)


# ------------------------------------------------------------------ one piece
def finish(folder, name, glb, source="trellis"):
    png = B.CUT / folder / f"{name}.png"
    kind, _ = B.recipe(folder, name)
    img = Image.open(png)
    w_m, h_m = B.world_size(name, img.width, img.height)
    target, (c0, r0, c1, r1) = cutout_mask(png)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    for o in list(bpy.context.scene.objects):
        if o is not ob:
            bpy.data.objects.remove(o, do_unlink=True)
    ob.parent = None
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    target_faces = 20000 if kind == "building" or max(w_m, h_m) > 3 else 9000
    B.decimate(ob, target_faces)

    me = ob.data
    co = np.zeros(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    me.calc_loop_triangles()
    tris = np.zeros(len(me.loop_triangles) * 3, int)
    me.loop_triangles.foreach_get("vertices", tris)
    tris = tris.reshape(-1, 3)

    # 1. heading
    old_mat = me.materials[0] if me.materials else None
    gen_tex = None
    if old_mat and old_mat.use_nodes:
        gen_tex = next((n.image for n in old_mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image), None)
    deg, match = heading(co, tris, vertex_colours(me, gen_tex), png)
    r = math.radians(deg)
    rot = np.array([[math.cos(r), -math.sin(r), 0], [math.sin(r), math.cos(r), 0], [0, 0, 1]])
    co = co @ rot.T

    # 2. size and place: the outline's box onto the cut-out's painted box, in the card's metres (origin: the
    # image's bottom centre)
    iw, ih = img.size
    box_x0, box_x1 = (c0 / iw - 0.5) * w_m, (c1 / iw - 0.5) * w_m
    box_z0, box_z1 = (1 - r1 / ih) * h_m, (1 - r0 / ih) * h_m
    lo, hi = co.min(0), co.max(0)
    sx = (box_x1 - box_x0) / max(1e-6, hi[0] - lo[0])
    sz = (box_z1 - box_z0) / max(1e-6, hi[2] - lo[2])
    sy = (sx + sz) / 2
    co[:, 0] = box_x0 + (co[:, 0] - lo[0]) * sx
    co[:, 2] = box_z0 + (co[:, 2] - lo[2]) * sz
    co[:, 1] = (co[:, 1] - lo[1]) * sy if kind == "building" else (co[:, 1] - (lo[1] + hi[1]) / 2) * sy
    me.vertices.foreach_set("co", co.ravel())
    me.update()
    depth = float(co[:, 1].max() - co[:, 1].min())

    # 3. the painting on the front
    nrm = np.zeros(len(me.vertices) * 3)
    me.vertices.foreach_get("normal", nrm)
    nrm = nrm.reshape(-1, 3)
    ev = np.zeros(len(me.edges) * 2, int)
    me.edges.foreach_get("vertices", ev)
    ev = ev.reshape(-1, 2)
    spacing = float(np.median(np.linalg.norm(co[ev[:, 0]] - co[ev[:, 1]], axis=1)))
    cell = max(spacing * 0.5, 1e-4)
    bary = np.array([(i, j, 6 - i - j) for i in range(7) for j in range(7 - i)], float) / 6
    sx_ = np.einsum("tk,sk->ts", co[tris, 0], bary).ravel()
    sz_ = np.einsum("tk,sk->ts", co[tris, 2], bary).ravel()
    sd_ = np.einsum("tk,sk->ts", co[tris, 1], bary).ravel()       # depth from the front: smaller y is nearer
    x0, z0 = co[:, 0].min(), co[:, 2].min()
    gw = int((co[:, 0].max() - x0) / cell) + 2
    gh = int((co[:, 2].max() - z0) / cell) + 2
    zbuf = np.full((gw, gh), np.inf)
    np.minimum.at(zbuf, (((sx_ - x0) / cell).astype(int), ((sz_ - z0) / cell).astype(int)), sd_)
    vi = ((co[:, 0] - x0) / cell).astype(int), ((co[:, 2] - z0) / cell).astype(int)
    visible = co[:, 1] <= zbuf[vi] + 2.5 * spacing
    facing = -nrm[:, 1]
    weight = np.where(visible, np.clip((facing - 0.3) / 0.45, 0, 1), 0.0)
    # Only where the painting agrees with what TRELLIS made there: where a leg or an edge sits a little differently,
    # the painting would land on the wrong thing (background or another part), so the generated colour stays.
    src = np.asarray(Image.open(png).convert("RGBA").resize((512, max(2, int(512 * ih / iw))), Image.BILINEAR))
    src = ndimage.uniform_filter(src.astype(float), size=(5, 5, 1)) / 255
    pu = np.clip(((co[:, 0] / w_m + 0.5) * (src.shape[1] - 1)).astype(int), 0, src.shape[1] - 1)
    pv = np.clip(((1 - co[:, 2] / h_m) * (src.shape[0] - 1)).astype(int), 0, src.shape[0] - 1)
    painted_rgb, painted_a = src[pv, pu, :3], src[pv, pu, 3]
    generated = vertex_colours(me, gen_tex)
    diff = np.abs(painted_rgb - generated).mean(1)
    agree = np.clip(1 - (diff - 0.1) / 0.14, 0, 1) * np.clip((painted_a - 0.5) / 0.4, 0, 1)
    # spread a little over the surface, so the blend has no speckle
    adj_rows = np.r_[ev[:, 0], ev[:, 1]]
    adj_cols = np.r_[ev[:, 1], ev[:, 0]]
    for _ in range(2):
        acc = np.bincount(adj_rows, weights=agree[adj_cols], minlength=len(agree))
        cnt = np.bincount(adj_rows, minlength=len(agree))
        agree = 0.5 * agree + 0.5 * acc / np.maximum(cnt, 1)
    weight = (weight * agree).astype(np.float32)
    attr = me.color_attributes.new("front", "FLOAT_COLOR", "POINT")
    attr.data.foreach_set("color", np.repeat(weight, 4))

    painted = B.OUT / folder / f"{name}.jpg"
    painted.parent.mkdir(parents=True, exist_ok=True)
    bleed = pathlib.Path(tempfile.mkdtemp()) / f"{name}_front.png"
    B.bled_texture(png, bleed, max_side=2048)

    mat = bpy.data.materials.new(f"{name}_bake")
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    gen = nt.nodes.new("ShaderNodeTexImage")
    gen.image = gen_tex
    uvmap = nt.nodes.new("ShaderNodeUVMap")
    uvmap.uv_map = me.uv_layers[0].name
    nt.links.new(uvmap.outputs["UV"], gen.inputs["Vector"])
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])

    def m(op, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    # image u, v of a point (x, z) in card metres: the card spans x -w/2..w/2, z 0..h
    u = m("ADD", m("DIVIDE", sep.outputs["X"], w_m), 0.5)
    v = m("DIVIDE", sep.outputs["Z"], h_m)
    uvw = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, uvw.inputs[0])
    nt.links.new(v, uvw.inputs[1])
    paint = nt.nodes.new("ShaderNodeTexImage")
    paint.image = bpy.data.images.load(str(bleed))
    paint.extension = "EXTEND"
    nt.links.new(uvw.outputs[0], paint.inputs["Vector"])
    wnode = nt.nodes.new("ShaderNodeAttribute")
    wnode.attribute_name = "front"
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(wnode.outputs["Fac"], mix.inputs["Factor"])
    if gen_tex is not None:
        nt.links.new(gen.outputs["Color"], mix.inputs["A"])
    else:
        mix.inputs["A"].default_value = (0.6, 0.6, 0.6, 1)
    nt.links.new(paint.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], emit.inputs["Color"])
    nt.links.new(emit.outputs[0], out.inputs["Surface"])
    size = 2048 if kind == "building" or max(w_m, h_m) > 3 else 1024
    baked = bpy.data.images.new(f"{name}_baked", size, size, alpha=False)
    target_node = nt.nodes.new("ShaderNodeTexImage")
    target_node.image = baked
    nt.nodes.active = target_node
    me.materials.clear()
    me.materials.append(mat)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 1
    scene.render.bake.margin = 8
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.bake(type="EMIT")
    tmp = painted.with_suffix(".png")
    baked.filepath_raw = str(tmp)
    baked.file_format = "PNG"
    baked.save()
    Image.open(tmp).convert("RGB").save(painted, quality=90)
    tmp.unlink()

    # 4. export with a plain textured material
    me.color_attributes.remove(me.color_attributes["front"])
    me.materials.clear()
    me.materials.append(B.material(f"M_{name}", painted))
    for p in me.polygons:
        p.use_smooth = True
    ob.name = name
    B.export(ob, B.OUT / folder / f"{name}.fbx")
    return {"name": name, "folder": folder, "kind": kind, "width": round(w_m, 3), "height": round(h_m, 3),
            "depth": round(depth, 3), "faces": len(me.polygons), "source": source, "heading": round(deg, 1),
            "outline_match": round(match, 3)}


def main():
    listing = {m["name"]: m for m in json.loads(LISTING.read_text())["models"]} if LISTING.exists() else {}
    done = []
    # A model made in Meshy from its four views wins over the TRELLIS one. The characters and pickups are rigged
    # and placed by their own builders, so only the scenery is finished here.
    chosen = {}
    for source, base in (("trellis", AI), ("meshy", MESHY)):
        for glb in sorted(base.glob("*/*.glb")):
            if glb.parent.name in ("characters", "pickups"):
                continue
            chosen[glb.stem] = (glb.parent.name, glb, source)
    for name, (folder, glb, source) in sorted(chosen.items()):
        if ONLY and name not in ONLY:
            continue
        if not (B.CUT / folder / f"{name}.png").exists():
            print(f"SKIPPED {folder}/{name}: no cut-out of that name in ArtSource/cutouts/{folder}", flush=True)
            continue
        try:
            entry = finish(folder, name, glb, source)
        except Exception as e:     # one odd model must not stop the rest; it keeps its extruded model
            print(f"FAILED {folder}/{name}: {e}", flush=True)
            continue
        listing[name] = entry
        done.append((folder, name))
        print(f"finished {folder}/{name}: heading {entry['heading']} deg, outline match {entry['outline_match']}, "
              f"{entry['width']:.2f} x {entry['height']:.2f} x {entry['depth']:.2f} m, {entry['faces']} faces", flush=True)
        LISTING.write_text(json.dumps({"models": sorted(listing.values(), key=lambda m: (m["folder"], m["name"]))},
                                      indent=1))
    print(f"{len(done)} finished")


if __name__ == "__main__":
    main()
