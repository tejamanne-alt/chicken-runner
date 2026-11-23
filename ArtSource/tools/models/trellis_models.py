"""Full 3D models of the painted cut-outs from TRELLIS (image to 3D), run on its Hugging Face Space.

    python trellis_models.py [--only name1,name2] [--seed N] [--redo]

For each cut-out (the same pieces as build_models.py) the painting is sent to the Space by its public GitHub URL,
TRELLIS generates the whole object (front, sides, back and top) as a textured mesh, and the GLB is saved to
ArtSource/models_ai/<folder>/<name>.glb with a record of how it was made. finish_models.py then fits each one to its
cut-out's real size and puts the painting itself back on its front, and exports it for Unity.

The Space is used with the Hugging Face token the network proxy adds for its host (so the GPU time counts against
that account's daily quota). When the quota runs out the run stops; run it again later and it carries on with the
pieces still missing.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import time

from gradio_client import Client, handle_file

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(pathlib.Path(__file__).parent))
CUT = ROOT / "ArtSource" / "cutouts"
OUT = ROOT / "ArtSource" / "models_ai"
SPACE = "https://trellis-community-trellis.hf.space/"
REPO = "tejamanne-alt/chicken-runner"
ARGS = sys.argv[1:]
ONLY = set(ARGS[ARGS.index("--only") + 1].split(",")) if "--only" in ARGS else None
SEED = int(ARGS[ARGS.index("--seed") + 1]) if "--seed" in ARGS else 1
# Pieces TRELLIS read wrongly with the usual seed (the pair of bullocks came out as three), and the seed to use.
SEEDS = {"bullocks": 2}
SKIP_PREFIX = ("mid_", "far_", "ground_earth", "paddy_water", "canal_water")
SKIP_FOLDERS = {"kid", "rooster", "textures", "ground"}   # ground details stay flat slabs (they are seen from above)


# The pieces the levels stand on the lane itself (obstacles, roofs, stalls: GameBuilder.Kit/Chunks), made first so
# each day's GPU quota goes where the player looks most; then houses, shops and stalls; then everything else.
FIRST = ["pot_stack", "rope_cot", "bullock_cart", "haystack", "haystack_small", "buffalo_mud", "hens_basket",
         "black_tank", "hand_pump", "clothesline", "dog_sleeping", "water_pot_stand", "brass_pots", "well",
         "house_indigo_veranda", "house_limewash", "house_pink", "house_turmeric_ladder", "tree_mango_1", "mandapam",
         "stall_c_1", "stall_d_2", "stall_e_3", "stall_f_1", "stall_flowers", "stall_g_2", "stall_h_1",
         "stall_vessels", "lamp_step", "lantern", "chilli_mat", "papad_mat", "hen_1", "hen_2", "hen_3", "dung"]
THEN = ("house_", "shop_", "stall_", "roof_house", "cattle_shed", "granary", "panchayat", "hut_", "field_bldg",
        "pump_house", "chariot_shed", "peepal", "shrine", "tree_")


def order(item):
    folder, name, _ = item
    if name in FIRST:
        return (0, FIRST.index(name), "")
    if name.startswith(THEN):
        return (1, 0, name)
    return (2, 0, folder + "/" + name)


def pieces():
    found = []
    for folder in sorted(p.name for p in CUT.iterdir() if p.is_dir()):
        if folder in SKIP_FOLDERS:
            continue
        for png in sorted((CUT / folder).glob("*.png")):
            if png.stem.startswith(SKIP_PREFIX + ("kolam",)) or (ONLY and png.stem not in ONLY):
                continue
            found.append((folder, png.stem, png))
    return sorted(found, key=order)


def public_url(png):
    """The cut-out as GitHub serves it (the repository is public; the file is in LFS)."""
    sha = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%H", "--", str(png)],
                         capture_output=True, text=True, check=True).stdout.strip()
    rel = png.relative_to(ROOT).as_posix()
    return f"https://media.githubusercontent.com/media/{REPO}/{sha}/{rel}"


def main():
    client = Client(SPACE, verbose=False)
    client.predict(api_name="/start_session")
    done = failed = 0
    for folder, name, png in pieces():
        dst = OUT / folder / f"{name}.glb"
        if dst.exists() and "--redo" not in ARGS:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        url = public_url(png)
        t0 = time.time()
        try:
            prompt = client.predict(handle_file(url), api_name="/preprocess_image")
            seed = SEEDS.get(name, SEED) if "--seed" not in ARGS else SEED
            result = client.predict(handle_file(prompt), [], seed, 7.5, 12, 3.0, 12, "stochastic", 0.95, 1024,
                                    api_name="/generate_and_extract_glb")
        except Exception as e:      # quota, queue or a bad picture: note it and carry on (or stop on quota)
            msg = str(e)
            print(f"FAILED {folder}/{name}: {msg[:300]}", flush=True)
            failed += 1
            if "quota" in msg.lower() or "exceeded" in msg.lower():
                print("GPU quota reached: run again later to continue.", flush=True)
                break
            continue
        glb = result[2] if isinstance(result, (list, tuple)) and len(result) > 2 else result
        if isinstance(glb, dict):
            glb = glb.get("value") or glb.get("path")
        shutil.copy(glb, dst)
        (dst.with_suffix(".json")).write_text(json.dumps({"source": url, "seed": seed, "model": "TRELLIS (image-large)",
                                                          "space": SPACE, "seconds": round(time.time() - t0, 1)}))
        done += 1
        print(f"made {folder}/{name} in {time.time() - t0:.0f} s", flush=True)
    print(f"{done} made, {failed} failed", flush=True)


if __name__ == "__main__":
    main()
