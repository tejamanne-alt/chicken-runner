"""Builds the prompt sheet page (art-prompts.html) and the repo copies (docs/art/prompt-sheet.md and
prompt-sheet-gemini.md) from prompts.py and pongal.py.

    python ArtSource/tools/prompts/build.py [page.html]
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import prompts as P  # noqa: E402

HERE = pathlib.Path(__file__).parent
REPO = pathlib.Path(__file__).resolve().parents[3]
# The page is a build product (published as the art prompts artifact), kept out of the repo.
PAGE_OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "art-prompts.html"


def full_text(p):
    parts = [f"{p['aspect']} image."]
    if "A1" in [r.strip() for r in p["attach"].split(",")]:
        parts.append(P.ANCHOR)
    parts.append(p["prompt"])
    parts.append({"texture": P.TEXTURE, "piece": P.PIECE_STYLE,
                  "character": getattr(P, "CHARACTER_STYLE", P.PIECE_STYLE)}.get(p.get("block"), P.STYLE))
    return "\n\n".join(parts)


def gemini_body(p):
    body = p["prompt"]
    for old, new in getattr(P, "GEMINI_GLOBAL_EDITS", []):
        body = body.replace(old, new)
    for old, new in P.GEMINI_EDITS.get(p["id"], []):
        assert body.count(old) == 1, (p["id"], old)
        body = body.replace(old, new)
    return body.replace("attached", "uploaded")


def gemini_text(p):
    parts = [f"Create a {p['gshape']} image."]
    refs = [r.strip() for r in p["attach"].split(",") if r.strip()]
    for r in refs:
        assert r in P.GEMINI_ROLES, (p["id"], r)
    if refs:
        parts.append("Use the images I've uploaded: " + "; ".join(P.GEMINI_ROLES[r] for r in refs) + ".")
    if p["id"] in P.GEMINI_SIDE_ON:
        parts.append(P.GEMINI_CAMERA)
    parts.append(p["gbody"])
    parts.append({"texture": P.GEMINI_TEXTURE, "piece": P.GEMINI_PIECE_STYLE,
                  "character": getattr(P, "GEMINI_CHARACTER_STYLE", P.GEMINI_PIECE_STYLE)}.get(p.get("block"),
                                                                                              P.GEMINI_STYLE))
    return "\n\n".join(parts)


order = {k: i for i, (k, _, _) in enumerate(P.SECTIONS)}
P.PROMPTS.sort(key=lambda p: (order[p["id"][0]], int(p["id"][1:])))
ids = [p["id"] for p in P.PROMPTS]
assert len(ids) == len(set(ids)), "duplicate ids"
for p in P.PROMPTS:
    assert p["file"].startswith(p["id"] + "_"), p["id"]
    p.setdefault("block", "style")
    p["text"] = full_text(p)
    p["gshape"] = P.GEMINI_SHAPES[p["id"]]
    p["gbody"] = gemini_body(p)
    p["gtext"] = gemini_text(p)

# Which images are already in the repo: any file in ArtSource/references starting with the image's ID.
REFS = sorted(f.name for f in (REPO / "ArtSource" / "references").iterdir() if not f.name.startswith("."))
sys.path.insert(0, str(REPO / "ArtSource" / "tools"))
import refs  # noqa: E402

for p in P.PROMPTS:
    p["redo"] = getattr(P, "REDO", {}).get(p["id"], "")
    if p["redo"] and refs.is_real(p["file"]):
        p["redo"] = ""  # a new version has been pushed since the rejected one
    p["note"] = getattr(P, "NOTES", {}).get(p["id"], "")
    p.setdefault("refined", False)
    # An image waiting to be made again doesn't count as made, even though a file is in the repo.
    p["inRepo"] = [] if p["redo"] else [r for r in REFS if r.startswith(p["id"] + "_")]
import datetime  # noqa: E402
CHECKED = datetime.date.today().strftime("%-d %b %Y")

VARIETY = {"B8", "B9", "B10", "C8", "C9", "C10", "T8", "T9", "T10", "T11", "T12",
           "D5", "D6", "D7", "E6", "E7", "E8", "E9", "E10", "B11", "B12", "B13", "B14", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18",
           "D8", "D9", "D10", "D11", "D12", "D13"}
for p in P.PROMPTS:
    p["new"] = p["id"][0] in "GHK" or p["id"] in VARIETY
first = [p for p in P.PROMPTS if p["batch"] == 1]
import pongal  # noqa: E402
PONGAL = pongal.entries(P.PROMPTS)
for p in PONGAL:
    p.update(redo="", note="", refined=False, inRepo=[], new=True)
data = {
    "sections": [{"key": k, "name": n, "blurb": b} for k, n, b in P.SECTIONS]
                + [{"key": pongal.KEY, "name": pongal.NAME, "blurb": pongal.BLURB + " " + pongal.UNCHANGED}],
    "prompts": P.PROMPTS + PONGAL,
    "style": P.STYLE,
    "texture": P.TEXTURE,
    "pipeline": P.PIPELINE,
    "needs": P.NEEDS,
    "firstCount": len(first),
    "repoChecked": CHECKED,
    "geminiStyle": P.GEMINI_STYLE,
    "geminiTexture": P.GEMINI_TEXTURE,
    "geminiHowto": P.GEMINI_HOWTO,
    "geminiFix": P.GEMINI_FIX,
}

# ---------------------------------------------------------------- page
template = (HERE / "page.html").read_text()
page = template.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
PAGE_OUT.write_text(page)

# ---------------------------------------------------------------- markdown
import re  # noqa: E402


def plain(html):
    html = re.sub(r"</?code>", "`", html)
    return re.sub(r"</?(b|i)>", lambda m: "**" if m.group(1) == "b" else "*", html)


md = []
md.append("# Chicken Runner — art prompt sheet\n")
md.append("Image prompts for ChatGPT, written for the Blender pipeline: every image has an ID, a file name and a shape, "
          "so the images come back named for the scenes they feed. The web version has copy buttons and a checklist. "
          "Gemini versions of the same prompts, with the same IDs and file names, are in "
          "[prompt-sheet-gemini.md](prompt-sheet-gemini.md).\n")
made = [p for p in P.PROMPTS if p["inRepo"]]
first_left = [p["id"] for p in first if not p["inRepo"]]
md.append(f"**Progress:** {len(made)} of {len(P.PROMPTS)} images are in `ArtSource/references/` (checked {CHECKED}); "
          f"{len(first) - len(first_left)} of the {len(first)} first-batch images. "
          f"First batch still to make: {', '.join(first_left) or 'none'}.\n")
md.append("**The village is celebrating Pongal.** Every image already made gets a festive edit in "
          f"[section {pongal.KEY}](#{pongal.KEY.lower()}-pongal-the-festive-repaint) (keep the picture, add the festival); "
          "every new image is made for the festival.\n")
md.append("## How to use it\n")
md.append("1. Make **A0** first, in a new ChatGPT chat, attaching your four kid turnaround images. Then make **A1**, attaching A0 and your rooster photo.")
md.append("2. Stay in that chat for the rest. Each prompt below is copy-ready: it asks ChatGPT to match A1 and carries the style rules. Attach the files listed under *Attach* (A0 is the kid reference from now on).")
md.append("3. Save each image with the file name shown.")
md.append(f"4. Put the images in the repo at `ArtSource/references/` (or upload them in the chat), in batches, starting with the {len(first)} marked *first batch*.\n")
md.append("Regenerate an image when words or labels appear in it, when a model sheet is not side-on and orthographic, or when "
          "the background is not plain.\n")
for key, name, blurb in P.SECTIONS:
    md.append(f"## {key}. {name}\n")
    md.append(blurb + "\n")
    for p in P.PROMPTS:
        if p["id"][0] != key:
            continue
        batch = ("first batch" if p["batch"] == 1 else "second batch") + (" · **new**" if p["new"] else "")
        md.append(f"### {p['id']} · {p['title']}\n")
        status = f"🔁 make again: {p['redo']}" if p["redo"] else ("✅ in the repo" if p["inRepo"] else "⬜ to make")
        if p["note"]:
            status += f" ({p['note']})"
        if p["refined"] and not p["inRepo"]:
            status += " · prompt updated"
        md.append(f"{status} · Save as `{p['file']}` · {p['aspect']} · {batch} · Attach: {p['attach']}  ")
        md.append(f"Used for: {p['use']}\n")
        md.append("```text\n" + p["text"] + "\n```\n")
md.append(f"## {pongal.KEY}. {pongal.NAME}\n")
md.append(pongal.BLURB + "\n")
for i, step in enumerate(pongal.HOWTO, 1):
    md.append(f"{i}. {plain(step)}")
md.append("\n" + pongal.UNCHANGED + "\n")
for p in PONGAL:
    md.append(f"### {p['id']} · {p['title']}\n")
    md.append(f"⬜ to make · Save as `{p['file']}` (replacing {p['orig']}) · {p['aspect']} · Attach: `{p['attach']}`\n")
    md.append("```text\n" + p["text"] + "\n```\n")
md.append("## What happens in Blender\n")
for i, (head, body) in enumerate(P.PIPELINE, 1):
    md.append(f"{i}. **{head}.** {body}")
md.append("\n## What I need from you\n")
for n in P.NEEDS:
    md.append(f"- {n}")
out = REPO / "docs" / "art" / "prompt-sheet.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md) + "\n")
# ---------------------------------------------------------------- Gemini markdown
import re  # noqa: E402

def plain(html):
    html = re.sub(r"</?code>", "`", html)
    return re.sub(r"</?(b|i)>", lambda m: "**" if m.group(1) == "b" else "*", html)

g = []
g.append("# Chicken Runner — art prompt sheet for Gemini\n")
g.append("The same images as [the ChatGPT sheet](prompt-sheet.md), with the same IDs and file names, rewritten for "
         "Gemini's image model: full sentences, positive wording, a stated job for every uploaded image, and wider "
         "16:9 and 21:9 shapes for the side-on scenes.\n")
g.append("## How to use it\n")
for i, step in enumerate(P.GEMINI_HOWTO, 1):
    g.append(f"{i}. {plain(step)}")
g.append(f"\nStart with the {len(first)} marked *first batch*. {plain(P.GEMINI_FIX)}\n")
g.append(f"**Progress:** {len(made)} of {len(P.PROMPTS)} images are in `ArtSource/references/` (checked {CHECKED}); "
         f"first batch still to make: {', '.join(first_left) or 'none'}.\n")
for key, name, blurb in P.SECTIONS:
    g.append(f"## {key}. {name}\n")
    g.append(blurb + "\n")
    for p in P.PROMPTS:
        if p["id"][0] != key:
            continue
        batch = ("first batch" if p["batch"] == 1 else "second batch") + (" · **new**" if p["new"] else "")
        g.append(f"### {p['id']} · {p['title']}\n")
        status = f"🔁 make again: {p['redo']}" if p["redo"] else ("✅ in the repo" if p["inRepo"] else "⬜ to make")
        if p["note"]:
            status += f" ({p['note']})"
        if p["refined"] and not p["inRepo"]:
            status += " · prompt updated"
        g.append(f"{status} · Save as `{p['file']}` · {p['gshape']} · {batch} · Upload: {p['attach']}  ")
        g.append(f"Used for: {p['use']}\n")
        g.append("```text\n" + p["gtext"] + "\n```\n")
g.append(f"## {pongal.KEY}. {pongal.NAME}\n")
g.append(pongal.BLURB + "\n")
for i, step in enumerate(pongal.HOWTO, 1):
    g.append(f"{i}. {plain(step)}")
g.append("\n" + pongal.UNCHANGED + "\n")
for p in PONGAL:
    g.append(f"### {p['id']} · {p['title']}\n")
    g.append(f"⬜ to make · Save as `{p['file']}` (replacing {p['orig']}) · keeps its shape · Upload: `{p['attach']}`\n")
    g.append("```text\n" + p["gtext"] + "\n```\n")
(REPO / "docs" / "art" / "prompt-sheet-gemini.md").write_text("\n".join(g) + "\n")

print(f"{len(P.PROMPTS)} prompts, {len(first)} in the first batch, {len(made)} in the repo; wrote {out} and art-prompts.html")
