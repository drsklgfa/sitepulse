from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
BASE = ROOT.parent / f"sitepulse-checkpoint-v{VERSION}"
EXCLUDES = {
    ".git", ".env", ".venv", "venv", "node_modules", "dist", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage", "htmlcov",
}


def ignore(_path: str, names: list[str]) -> set[str]:
    return {
        name for name in names
        if name in EXCLUDES or name.endswith((".db", ".zip", ".zip.sha256", ".pyc"))
    }


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary) / "sitepulse"
        shutil.copytree(ROOT, staging, ignore=ignore)
        shutil.make_archive(str(BASE), "zip", staging.parent, staging.name)
    zip_path = Path(f"{BASE}.zip")
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    checksum = Path(f"{zip_path}.sha256")
    checksum.write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8")
    print(zip_path)
    print(checksum)


if __name__ == "__main__":
    main()
