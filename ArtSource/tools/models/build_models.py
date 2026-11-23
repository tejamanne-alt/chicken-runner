"""Turns every painted cut-out into a 3D model, keeping the painting exactly as painted on its front.

    python ArtSource/tools/models/build_models.py [--only name1,name2] [--sheet OUT.png] [--no-fbx]

Three recipes, picked per piece by RECIPES below:

  * volume: animals, people, trees, plants, pots and baskets. The outline is inflated into a rounded solid whose
    thickness at each point grows with its distance from the edge (thin legs and branches stay thin, bodies and crowns
    swell), built as one closed surface by marching cubes and simplified.
  * slab: flat or thin things (a cot, a cart, a cycle, a clothesline, mats, kolams and ground details): the outline
    extruded to the thing's real thickness.
  * building: houses, shops, sheds, stalls and temple pieces: the painted front as the facade and the outline extruded
    back to the building's depth; walls, roof and underside show the painting just inside each edge (its plaster, brick,
    thatch or tiles), mirrored to and fro, so they read as the same building rather than streaks of edge colour.

The painting is projected straight onto the front (and mirrored onto the back), with its colours bled past the edge so
no dark fringe shows. Sizes come from the cut-out manifest, as in the Blender scenes. Each model goes to
Assets/ChickenRunner/Art/Models/<folder>/<name>.fbx with its texture beside it, facing -Y in Blender (Unity +Z),
standing on the origin.

The scenery bands and far layers stay painted cards: they are whole landscapes, not objects.
"""
import json
import math
import pathlib
import sys

import bpy
import bmesh
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure

ROOT = pathlib.Path(__file__).resolve().parents[3]
CUT = ROOT / "ArtSource" / "cutouts"
OUT = ROOT / "Assets" / "ChickenRunner" / "Art" / "Models"
MANIFEST = json.loads((CUT / "lane" / "manifest.json").read_text())
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ONLY = set(ARGS[ARGS.index("--only") + 1].split(",")) if "--only" in ARGS else None
SHEET = pathlib.Path(ARGS[ARGS.index("--sheet") + 1]) if "--sheet" in ARGS else None

# Pieces that are not objects: whole painted landscapes, ground textures, and the characters (built from their
# turnarounds by ArtSource/tools/characters).
SKIP_PREFIX = ("mid_", "far_", "ground_earth", "paddy_water", "canal_water")
SKIP_FOLDERS = {"kid", "rooster", "textures"}

# Real-world sizes for lane pieces the manifest leaves without one (as the lane scene sizes them).
SIZES = {"pot_stack": ("h", 0.65), "dung": ("w", 0.6), "hand_pump": ("h", 1.2), "rope_cot": ("w", 1.9),
         "bicycle": ("w", 1.7), "tulsi_planter": ("h", 1.1), "brass_pots": ("h", 0.45), "bullock_cart": ("w", 3.8),
         "clothesline": ("w", 2.4), "chicken_basket": ("h", 0.6), "jute_sacks": ("h", 0.8), "doorway_garland": ("h", 2.3),
         "shrine_stone": ("h", 1.0), "water_pot_stand": ("h", 1.1), "dog_sleeping": ("w", 0.9), "bullocks": ("h", 1.55),
         "house_limewash": ("h", 4.27), "house_pink": ("h", 4.27), "house_indigo_veranda": ("h", 4.2),
         "house_turmeric_ladder": ("h", 3.97), "tree_mango_1": ("h", 6.0), "tree_mango_2": ("h", 6.0),
         "kolam": ("w", 0.9), "hen": ("h", 0.42), "cat_on_wall": ("h", 0.9), "goat_on_wall": ("h", 1.4),
         "crows_on_ledge": ("w", 1.2), "parrots": ("w", 0.6), "peacock": ("h", 1.0), "squirrel": ("w", 0.3),
         "duck": ("h", 0.4), "hen_with_chicks": ("h", 0.45), "calf": ("h", 0.9), "cow": ("h", 1.4), "goat_eating": ("h", 0.75),
         "goat_kid": ("h", 0.55), "dog_barking": ("h", 0.6), "buffalo_mud": ("h", 1.5), "people": ("h", 1.6),
         "plants": ("h", 1.2), "ground": ("w", 0.4)}


def recipe(folder, name):
    """(kind, thickness in metres or a fraction of the piece's width with 'w'), from the piece's name and folder."""
    n = name
    if folder == "ground" or n.startswith("kolam"):
        return ("slab", 0.012)
    building_depth = [("house_tiled_gate", 6), ("house_village_head", 7), ("house_", 4.5), ("shop_", 4), ("panchayat", 6),
                      ("cattle_shed", 4), ("granary", 3), ("pump_house", 3), ("hut_with_pen", 4), ("field_bldg", 3.5),
                      ("field_shrine", 1.5), ("roof_house", 6), ("mandapam", 4), ("chariot_shed", 5), ("tank_wall", 0.5),
                      ("peepal_platform", 4), ("stall_", 1.6), ("flower_stall", 1.4), ("coconut_cart", 1.1),
                      ("lamp_step", 0.6), ("parapet_gap", 0.3), ("canal_bank", 0.8), ("canal_bridge", 1.0),
                      ("sluice_gate", 0.8), ("well", 1.6), ("bund_", 0.9), ("shrine_tree", 4), ("lamp_pillar", 0.7)]
    for prefix, depth in building_depth:
        if n.startswith(prefix):
            return ("building", depth)
    slabs = {"rope_cot": 0.85, "bullock_cart": 1.1, "bicycle": 0.12, "clothesline": 0.05, "hand_pump": 0.2,
             "doorway_garland": 0.06, "chilli_mat": 0.05, "papad_mat": 0.05, "bunting": 0.015, "kite": 0.02,
             "water_pot_stand": 0.45, "scarecrow": 0.25, "lantern": 0.2, "dung": 0.08}
    if n in slabs:
        return ("slab", slabs[n])
    if n.startswith(("crop_strip", "paddy_", "sugarcane")):
        return ("volume", 0.45)     # a row of crop, not a loaf: the same depth however long the strip
    # Body widths, side to side, in metres.
    animals = {"cow": 0.6, "calf": 0.42, "buffalo_mud": 0.72, "bullocks": 1.3, "goat_eating": 0.3, "goat_kid": 0.24,
               "goat_on_wall": 0.32, "dog_sleeping": 0.3, "dog_barking": 0.24, "cat_on_wall": 0.16, "hen_1": 0.18,
               "hen_2": 0.18, "hen_3": 0.18, "hen_with_chicks": 0.3, "duck_1": 0.16, "duck_2": 0.16, "peacock": 0.26,
               "parrots": 0.1, "crows_on_ledge": 0.14, "squirrel": 0.08}
    if n in animals:
        return ("volume", animals[n])
    if folder == "people" or n.startswith(("field_life",)):
        return ("volume", 0.34)
    if folder == "plants" or n.startswith(("tree_", "palmyra", "field_tree", "h1_", "h2_", "h3_", "h4_", "h5_", "h6_", "h7_")):
        return ("volume", ("w", 0.32))
    return ("volume", ("w", 0.8))    # pots, baskets, vessels, sacks, tanks and other round props


def find_png(name):
    for folder in sorted(p.name for p in CUT.iterdir() if p.is_dir()):
        p = CUT / folder / f"{name}.png"
        if p.exists():
            return folder, p
    return None, None


def world_size(name, img_w, img_h):
    """(width, height) in metres from the manifest (px_per_m, height_m or width_m), or the SIZES table."""
    meta = MANIFEST.get(name) if isinstance(MANIFEST.get(name), dict) else {}
    aspect = img_w / img_h
    if meta.get("px_per_m") and meta.get("px"):
        return meta["px"][0] / meta["px_per_m"], meta["px"][1] / meta["px_per_m"]
    if meta.get("height_m"):
        return meta["height_m"] * aspect, meta["height_m"]
    if meta.get("width_m"):
        return meta["width_m"], meta["width_m"] / aspect
    for key in (name, name.rstrip("0123456789_"), name.split("_")[0]):
        if key in SIZES:
            kind, v = SIZES[key]
            return (v, v / aspect) if kind == "w" else (v * aspect, v)
    return aspect, 1.0


def bled_texture(src, dst, inset=0, max_side=2048):
    """The cut-out with its colours pushed out past its edge, so mesh edges never sample the dark transparent pixels,
    no bigger than max_side. With `inset`, the outermost `inset` pixels (the painted ink outline) are replaced by
    the colours just inside them."""
    src_im = Image.open(src).convert("RGBA")
    if max(src_im.size) > max_side:
        scale = max_side / max(src_im.size)
        src_im = src_im.resize((round(src_im.width * scale), round(src_im.height * scale)), Image.LANCZOS)
    im = np.asarray(src_im)
    solid = dehalo(im, im[..., 3] > 8)
    if inset and solid.any():
        core = ndimage.binary_erosion(solid, iterations=inset)
        if core.sum() > 50:
            solid = core
    if solid.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~solid, return_indices=True)
        rgb = im[..., :3][iy, ix]
    else:
        rgb = im[..., :3]
    Image.fromarray(rgb.astype(np.uint8), "RGB").save(dst, quality=90)


def dehalo(im, solid, width=4):
    """The solid pixels less a near-white fringe along the outline: some cut-outs keep a thin white halo of the
    background they were cut from, which would otherwise outline the model and bleed into its walls."""
    if not solid.any():
        return solid
    rim = solid & ~ndimage.binary_erosion(solid, iterations=width)
    white = rim & (im[..., :3].min(axis=2) > 215)
    kept = solid & ~white
    return kept if kept.sum() > 0.9 * solid.sum() else solid


def mask_of(src, max_side):
    im = Image.open(src).convert("RGBA")
    scale = max_side / max(im.size)
    small = np.asarray(im.resize((max(2, round(im.width * scale)), max(2, round(im.height * scale))), Image.LANCZOS))
    a = small[..., 3] > 110
    a = ndimage.binary_opening(a, iterations=1) | (small[..., 3] > 200)
    return dehalo(small, a, width=1)


# ------------------------------------------------------------------ recipes
def volume_mesh(mask, w_m, h_m, half):
    """Inflated solid: marching cubes on h(x,y) - |z|, where h rounds up from 0 at the outline to `half` inside."""
    rows, cols = mask.shape
    pix = w_m / cols
    pad = 2
    m = np.pad(mask, pad)
    inside = ndimage.distance_transform_edt(m) * pix
    outside = ndimage.distance_transform_edt(~m) * pix
    r = max(half, pix * 2)
    k = np.clip(inside / r, 0, 1)
    h = np.where(m, half * np.sqrt(1 - (1 - k) ** 2), -outside)
    h = ndimage.gaussian_filter(h, 0.8)
    nz = max(6, int(math.ceil(half / pix)) + 2)
    zs = (np.arange(-nz, nz + 1)) * pix
    field = h[:, :, None] - np.abs(zs)[None, None, :]
    verts, faces, _, _ = measure.marching_cubes(field, level=0.0)
    rr, cc, zz = verts[:, 0] - pad, verts[:, 1] - pad, verts[:, 2] - nz
    x = (cc - (cols - 1) / 2) * pix
    up = (rows - 1 - rr) * pix
    depth = zz * pix
    uv = np.stack([cc / (cols - 1), 1 - rr / (rows - 1)], 1)
    return np.stack([x, -depth, up], 1), faces[:, ::-1], uv


def prism_loops(mask, w_m):
    """Outline loops (outer edges and holes) in metres, with the image UV of each point and the direction into the
    painting there (for the walls that run back from it)."""
    rows, cols = mask.shape
    pix = w_m / cols
    loops = []
    for c in measure.find_contours(np.pad(mask.astype(float), 1), 0.5):
        if len(c) < 8:
            continue
        # evenly spaced points every 3 pixels (not simplified to corners: each stretch of wall needs its own
        # direction into the painting and its own depth of paint)
        c = c - 1
        seg = np.linalg.norm(np.diff(c, axis=0), axis=1)
        dist = np.r_[0, np.cumsum(seg)]
        if dist[-1] < 12:
            continue
        at = np.arange(0, dist[-1], 3.0)
        c = np.stack([np.interp(at, dist, c[:, 0]), np.interp(at, dist, c[:, 1])], 1)
        c = np.r_[c, c[:1]]
        if len(c) < 5:
            continue
        r, cc = np.clip(c[:-1, 0], 0, rows - 1), np.clip(c[:-1, 1], 0, cols - 1)
        pts = np.stack([(cc - (cols - 1) / 2) * pix, (rows - 1 - r) * pix], 1)
        uv = np.stack([cc / (cols - 1), 1 - r / (rows - 1)], 1)
        area = 0.5 * abs(np.dot(pts[:, 0], np.roll(pts[:, 1], 1)) - np.dot(pts[:, 1], np.roll(pts[:, 0], 1)))
        if area <= (pix * 3) ** 2:
            continue
        # inward: perpendicular to the outline, toward whichever side the painting is on
        t = np.roll(pts, -1, 0) - np.roll(pts, 1, 0)
        n = np.stack([-t[:, 1], t[:, 0]], 1)
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        probe = pts + n * pix * 2.5
        pc = np.round(probe[:, 0] / pix + (cols - 1) / 2).astype(int)
        pr = np.round(rows - 1 - probe[:, 1] / pix).astype(int)
        ok = (pc >= 0) & (pc < cols) & (pr >= 0) & (pr < rows)     # past the image's edge is outside
        inside = np.zeros(len(pts), bool)
        inside[ok] = mask[pr[ok], pc[ok]]
        n[~inside] *= -1
        n = ndimage.uniform_filter1d(n, size=5, axis=0, mode="wrap")     # steady along jagged edges
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        # how far in from each point the painting runs before a gap (metres), so walls never sample across one
        solid = np.zeros(len(pts))
        for k in range(1, 60):
            probe = pts + n * pix * k
            pc = np.round(probe[:, 0] / pix + (cols - 1) / 2).astype(int)
            pr = np.round(rows - 1 - probe[:, 1] / pix).astype(int)
            ok = (pc >= 0) & (pc < cols) & (pr >= 0) & (pr < rows)
            inside = np.zeros(len(pts), bool)
            inside[ok] = mask[pr[ok], pc[ok]]
            still = solid == (k - 1) * pix
            solid[still & inside] = k * pix
        solid = ndimage.median_filter(solid, size=5, mode="wrap")     # steady along the wall
        loops.append((pts, uv, n, solid))
    return loops


def fold(d, band):
    """0 at the front edge, out to `band` and back again, over and over: the painting's edge band, mirrored."""
    k = np.mod(d, 2 * band)
    return band - np.abs(k - band)


def prism_object(name, loops, depth, w_m, h_m):
    """The outline filled (holes kept) and extruded back by `depth`: front at y=0 facing -Y, back at y=depth.
    The front is the painting. Walls, roof and underside run back from each edge showing the painting just inside
    that edge (the plaster, brick, thatch or tiles there), mirrored to and fro every `band`, rather than one edge
    pixel stretched into streaks; the back is the painting again."""
    band = float(np.clip(0.18 * min(w_m, h_m), 0.12, 0.9))
    inset = 0.006 * max(w_m, h_m)                          # past the painted ink outline
    steps = max(1, int(math.ceil(depth / band)))
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    layer = bm.loops.layers.uv.new("UVMap")
    rings = []        # per loop: [ring 0 verts, ring 1 verts, ...]
    edges = []
    for pts, uv, n, _ in loops:
        loop_rings = []
        for k in range(steps + 1):
            y = depth * k / steps
            loop_rings.append([bm.verts.new((p[0], y, p[1])) for p in pts])
        rings.append(loop_rings)
        front = loop_rings[0]
        for i in range(len(front)):
            edges.append(bm.edges.new((front[i], front[(i + 1) % len(front)])))
    # the front cap, and the back cap as its mirror image at the far side
    filled = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)["geom"]
    front_faces = [f for f in filled if isinstance(f, bmesh.types.BMFace)]
    where = {}
    for li, loop_rings in enumerate(rings):
        for i, v in enumerate(loop_rings[0]):
            where[v] = (li, i)
    for f in front_faces:
        if f.normal.y > 0:
            f.normal_flip()
        f.material_index = 0
        for lp in f.loops:
            li, i = where[lp.vert]
            lp[layer].uv = tuple(loops[li][1][i])
    for f in front_faces:
        back = bm.faces.new([rings[where[v][0]][-1][where[v][1]] for v in reversed(list(f.verts))])
        back.material_index = 0
        for lp, src in zip(back.loops, reversed(list(f.verts))):
            li, i = where[src]
            lp[layer].uv = tuple(loops[li][1][i])
    # the walls
    for li, (pts, uv, n, solid) in enumerate(loops):
        n_uv = n / np.array([w_m, h_m])
        # the band at each point: as wide as the painting runs inward there (less the outline), up to `band`
        reach = np.clip(solid - inset, 0.25 * inset, band)
        loop_rings = rings[li]
        count = len(pts)
        for k in range(steps):
            d0, d1 = depth * k / steps, depth * (k + 1) / steps
            for i in range(count):
                j = (i + 1) % count
                quad = [loop_rings[k][i], loop_rings[k][j], loop_rings[k + 1][j], loop_rings[k + 1][i]]
                try:
                    f = bm.faces.new(quad)
                except ValueError:
                    continue
                f.material_index = 0
                for lp, (pi, d) in zip(f.loops, ((i, d0), (j, d0), (j, d1), (i, d1))):
                    lp[layer].uv = tuple(uv[pi] + (min(inset, solid[pi] * 0.5) + fold(d, reach[pi])) * n_uv[pi])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def mesh_object(name, verts, faces, uv):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(int(i) for i in f) for f in faces])
    layer = me.uv_layers.new(name="UVMap")
    loop_vert = np.zeros(len(me.loops), dtype=np.int64)
    me.loops.foreach_get("vertex_index", loop_vert)
    layer.data.foreach_set("uv", uv[loop_vert].astype(np.float32).ravel())
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def material(name, texture_path):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(texture_path))
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    return mat


def decimate(ob, target_faces):
    faces = len(ob.data.polygons)
    if faces > target_faces:
        mod = ob.modifiers.new("Decimate", "DECIMATE")
        mod.ratio = target_faces / faces
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)


def build(folder, name, png):
    kind, thick = recipe(folder, name)
    img = Image.open(png)
    w_m, h_m = world_size(name, img.width, img.height)
    if isinstance(thick, tuple):
        thick = thick[1] * w_m
    out_dir = OUT / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    tex_path = out_dir / f"{name}.jpg"
    bled_texture(png, tex_path, max_side=2048 if kind == "building" or max(w_m, h_m) > 3 else 1024)
    if kind == "volume":
        mask = mask_of(png, 180 if max(w_m, h_m) < 3 else 240)
        verts, faces, uv = volume_mesh(mask, w_m, h_m, thick / 2)
        ob = mesh_object(name, verts, faces, uv)
        decimate(ob, 6000 if max(w_m, h_m) < 3 else 12000)
    else:
        mask = mask_of(png, 400 if kind == "building" else 260)
        loops = prism_loops(mask, w_m)
        if not loops:
            return None
        ob = prism_object(name, loops, thick, w_m, h_m)
        if kind == "slab":
            ob.location.y = -thick / 2   # centred on its depth
    ob.data.materials.append(material(f"M_{name}", tex_path))
    return ob, kind, (w_m, h_m, thick)


def export(ob, path):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", bake_anim=False,
                             mesh_smooth_type="FACE", path_mode="RELATIVE", embed_textures=False)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    pieces = []
    for folder in sorted(p.name for p in CUT.iterdir() if p.is_dir()):
        if folder in SKIP_FOLDERS:
            continue
        for png in sorted((CUT / folder).glob("*.png")):
            name = png.stem
            if name.startswith(SKIP_PREFIX) or (ONLY and name not in ONLY):
                continue
            pieces.append((folder, name, png))
    index = {}
    built = []
    for folder, name, png in pieces:
        try:
            res = build(folder, name, png)
        except Exception as e:   # one odd cut-out must not stop the rest
            print(f"FAILED {folder}/{name}: {e}")
            continue
        if res is None:
            print(f"SKIPPED {folder}/{name}: no outline")
            continue
        ob, kind, (w, h, d) = res
        if "--no-fbx" not in ARGS:
            export(ob, OUT / folder / f"{name}.fbx")
        index[name] = {"name": name, "folder": folder, "kind": kind, "width": round(w, 3), "height": round(h, 3),
                       "depth": round(d, 3), "faces": len(ob.data.polygons)}
        built.append(ob)
        ob.hide_render = True
        print(f"built {folder}/{name}: {kind} {w:.2f} x {h:.2f} x {d:.2f} m, {len(ob.data.polygons)} faces")
    if "--no-fbx" not in ARGS:     # a list under "models", as Unity's JsonUtility reads it (ArtModels.cs)
        listing = OUT / "models.json"
        if ONLY and listing.exists():   # a partial run updates its pieces' entries and keeps the rest
            kept = {m["name"]: m for m in json.loads(listing.read_text()).get("models", [])}
            kept.update(index)
            index = kept
        listing.write_text(json.dumps({"models": sorted(index.values(), key=lambda m: (m["folder"], m["name"]))}, indent=1))
    if SHEET:
        contact_sheet(built, index)


def contact_sheet(objects, index):
    """Every model at a three-quarter view, lit, in a grid."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.render.resolution_x = scene.render.resolution_y = 220
    world = bpy.data.worlds.new("W")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
    scene.collection.objects.link(sun)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    scene.collection.objects.link(cam)
    scene.camera = cam
    tiles = []
    tmp = SHEET.parent / "_model_tile.png"
    for ob in objects:
        ob.hide_render = False
        info = index[ob.name]
        size = max(info["width"], info["height"], info["depth"]) * 1.25
        cam.data.ortho_scale = size
        d = size * 3
        ang = math.radians(35)
        cx, cz = 0.0, info["height"] / 2
        cam.location = (math.sin(ang) * d, -math.cos(ang) * d, cz + d * 0.35)
        direction = __import__("mathutils").Vector((cx, info["depth"] / 2 if info["kind"] == "building" else 0, cz)) - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(tmp)
        bpy.ops.render.render(write_still=True)
        tiles.append((ob.name, Image.open(tmp).convert("RGBA").copy()))
        ob.hide_render = True
    from PIL import ImageDraw
    cols = 10
    sheet = Image.new("RGB", (cols * 220, ((len(tiles) + cols - 1) // cols) * 240), (214, 206, 196))
    d = ImageDraw.Draw(sheet)
    for i, (name, t) in enumerate(tiles):
        x, y = (i % cols) * 220, (i // cols) * 240
        sheet.paste(t, (x, y), t)
        d.text((x + 4, y + 222), name[:30], fill=(40, 30, 30))
    sheet.save(SHEET)


if __name__ == "__main__":
    main()
