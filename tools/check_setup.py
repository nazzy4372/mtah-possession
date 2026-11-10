"""Check the local setup before any modelling.

Prints only SAFE information: versions, file names, file sizes and pass/fail lines.
It never prints a value from the match data, so its output can be shared with anyone.

    python tools\\check_setup.py
"""
import importlib
import os
import sys
from pathlib import Path

EXPECTED = {
    "tactical": [
        "BAR-ATH_tactical.mp4",
        "BAR-ATH_tactical_atd.xml",
        "BAR-ATH_tactical_atd.txt",
        "BAR-ATH_tactical_homography.csv",
        "BAR-ATH_tactical_smart_tagging.xml",
    ],
    "broadcast": [
        "BAR-ATH_broadcast.mp4",
        "BAR-ATH_broadcast_atd.xml",
        "BAR-ATH_broadcast_atd.txt",
        "BAR-ATH_broadcast_homography.csv",
    ],
}
PACKAGES = ["numpy", "pandas", "kloppy", "matplotlib", "lightgbm", "optuna", "sklearn", "yaml", "pytest"]

ok = True


def report(passed, text):
    global ok
    ok = ok and passed
    print("[{}] {}".format("OK  " if passed else "FAIL", text))


print("== Python")
report(sys.version_info[:2] == (3, 11), "Python {}.{}.{} (want 3.11)".format(*sys.version_info[:3]))
report(".venv" in sys.prefix, "running inside the project venv ({})".format(sys.prefix))

print("\n== Packages")
for name in PACKAGES:
    try:
        module = importlib.import_module(name)
        report(True, "{} {}".format(name, getattr(module, "__version__", "")))
    except ImportError:
        report(False, "{} is not installed".format(name))

print("\n== Repo")
root = Path(__file__).resolve().parent.parent
for rel in ["CLAUDE.md", ".gitignore", ".claude/settings.json", "upstream/evaluation/run_evaluation.py"]:
    report((root / rel).exists(), rel)
gitignore = (root / ".gitignore").read_text() if (root / ".gitignore").exists() else ""
report("*.mp4" in gitignore and "*_atd.txt" in gitignore, ".gitignore excludes match data")

print("\n== Data")
data_dir = os.environ.get("MTAH_DATA_DIR")
report(bool(data_dir), "MTAH_DATA_DIR = {}".format(data_dir))
if data_dir:
    base = Path(data_dir)
    report(not str(base.resolve()).startswith(str(root)), "data lives outside the repo")
    for folder, names in EXPECTED.items():
        for name in names:
            path = base / folder / name
            if path.exists():
                report(path.stat().st_size > 0, "{}/{}  {:,.1f} MB".format(folder, name, path.stat().st_size / 1e6))
            else:
                report(False, "{}/{}  MISSING".format(folder, name))

print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED -- fix the FAIL lines above")
