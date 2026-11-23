"""Where to find a reference image: the real one in ArtSource/references/, else its placeholder.

A real image listed in ArtSource/placeholders/rejected.json with its SHA-256 (one that came out wrong and is being made
again) is skipped in favour of the placeholder, until a new version with a different hash is pushed.
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
REF = ROOT / "ArtSource" / "references"
PLACEHOLDERS = ROOT / "ArtSource" / "placeholders"
_REJECTED = PLACEHOLDERS / "rejected.json"


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def rejected():
    return json.loads(_REJECTED.read_text()) if _REJECTED.exists() else {}


def is_real(name):
    """True if a usable real image is in references/ (present and not the rejected version)."""
    real = REF / name
    return real.exists() and rejected().get(name) != sha256(real)


def path(name):
    """The real image if usable, else the placeholder, else the (missing) real path."""
    if is_real(name):
        return REF / name
    ph = PLACEHOLDERS / name
    return ph if ph.exists() else REF / name


def is_placeholder(name):
    return path(name).parent == PLACEHOLDERS
