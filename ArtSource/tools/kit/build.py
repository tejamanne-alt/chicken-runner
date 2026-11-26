"""Builds the hand-made models (every category module in this folder registers its builders with @model).

    python ArtSource/tools/kit/build.py --only house_pink,pot_stack [--review DIR] [--grid DIR]
    python ArtSource/tools/kit/build.py --all [--review DIR]
    python ArtSource/tools/kit/build.py --list
    python ArtSource/tools/kit/build.py --merge          # ArtSource/models_kit/*.json into models.json
    --module lane_houses,trees  imports only those category modules (faster, and safe while others are being written)
    KIT_THREADS=2 python ...    caps Blender's CPU threads (when several builds run at once)

Each model goes to Assets/ChickenRunner/Art/Models/<folder>/<name>.fbx with <name>.jpg (and <name>_leaves.png when it
has cards), and its record to ArtSource/models_kit/<name>.json; --merge writes those records into models.json, where
ArtModels finds them. --review DIR renders DIR/<name>.jpg, the review sheet; --grid DIR writes the painting with a pixel
grid (DIR/<name>_grid.png) for measuring its parts.
"""
import importlib
import json
import pathlib
import sys
import time
import traceback

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kitlib as KL  # noqa: E402

ARGS = sys.argv[1:]


def arg(name):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else None


def load_modules(only=None):
    """Imports the category modules (only those named, with --module a,b), each on its own: one that fails to import
    (someone is still writing it) is reported and skipped, the rest still build."""
    for p in sorted(HERE.glob("*.py")):
        if p.stem in ("kitlib", "build", "review") or p.stem.startswith("_"):
            continue
        if only and p.stem not in only:
            continue
        try:
            importlib.import_module(p.stem)
        except Exception as e:
            print(f"warning: module {p.stem} did not import: {e!r}")


def merge():
    path = KL.OUT / "models.json"
    data = json.loads(path.read_text()) if path.exists() else {"models": []}
    by_name = {m["name"]: m for m in data["models"]}
    n = 0
    for rec_path in sorted(KL.RECORDS.glob("*.json")):
        rec = json.loads(rec_path.read_text())
        by_name[rec["name"]] = rec
        n += 1
    data["models"] = sorted(by_name.values(), key=lambda m: (m["folder"], m["name"]))
    path.write_text(json.dumps(data, indent=1))
    print(f"merged {n} kit records into {path}")


def main():
    if "--merge" in ARGS:
        return merge()
    load_modules(set(arg("--module").split(",")) if arg("--module") else None)
    if "--list" in ARGS:
        for name, spec in sorted(KL.MODELS.items()):
            print(spec["folder"], name, spec["kind"])
        return
    names = sorted(KL.MODELS) if "--all" in ARGS else (arg("--only") or "").split(",")
    names = [n for n in names if n]
    review = pathlib.Path(arg("--review")) if arg("--review") else None
    grid = pathlib.Path(arg("--grid")) if arg("--grid") else None
    failed = []
    for name in names:
        if grid:
            grid.mkdir(parents=True, exist_ok=True)
            folder = KL.MODELS[name]["folder"] if name in KL.MODELS else None
            KL.Painting(name, folder).grid(grid / f"{name}_grid.png")
            if name not in KL.MODELS:
                continue
        t = time.time()
        try:
            rec, ob, leaves = KL.build(name)
        except Exception:
            traceback.print_exc()
            failed.append(name)
            continue
        print(f"{name}: {rec['faces']} faces, {rec['width']} x {rec['height']} x {rec['depth']} m, {time.time() - t:.0f} s")
        if review:
            import review as RV
            review.mkdir(parents=True, exist_ok=True)
            RV.render_sheet(rec, ob, leaves, KL.Painting(name, rec["folder"]).img, review / f"{name}.jpg")
            print("  review", review / f"{name}.jpg")
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
