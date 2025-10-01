"""organize_data.py

Small utility to move existing files from `./data` root into the
new subdirectories based on file extension. Safe to run multiple times.
"""
import os
import shutil
from pathlib import Path

# We want the data folder under app/ai-service/data; parents[2] resolves to ai-service
ROOT = Path(__file__).resolve().parents[2] / "data"

EXT_MAP = {
    ".pdf": "pdf",
    ".csv": "csv",
    ".json": "json",
    ".html": "web",
    ".htm": "web",
    ".txt": "raw",
}


def ensure_placeholders(dirs):
    for d in dirs:
        p = ROOT / d
        p.mkdir(parents=True, exist_ok=True)
        (p / ".gitkeep").touch(exist_ok=True)


def organize():
    # create expected dirs
    dirs = set(EXT_MAP.values()) | {"raw", "faiss", "processed"}
    ensure_placeholders(dirs)

    # move files from root data into subdirs
    for item in ROOT.iterdir():
        if item.is_file() and item.name != "scrape_index.csv":
            ext = item.suffix.lower()
            target = EXT_MAP.get(ext, "raw")
            dest = ROOT / target / item.name
            if dest.exists():
                # avoid overwriting; create a numeric suffix
                base = item.stem
                i = 1
                while (ROOT / target / f"{base}_{i}{ext}").exists():
                    i += 1
                dest = ROOT / target / f"{base}_{i}{ext}"
            shutil.move(str(item), str(dest))
            print(f"moved {item.name} -> {target}/")


if __name__ == "__main__":
    print("Organizing data directory:", ROOT)
    organize()
