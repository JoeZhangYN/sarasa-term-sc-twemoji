"""下载彩色 emoji 字体源到 downloads/。默认 Twemoji（CC-BY 4.0，可发布），
失败或显式 --noto 时改 Noto-COLRv1（OFL，也可发布）。"""

import os
import sys
import urllib.request
from pathlib import Path

DOWNLOAD_DIR = Path(__file__).parent / "downloads"

SOURCES = {
    "twemoji": (
        "https://github.com/mozilla/twemoji-colr/releases/download/v0.7.0/Twemoji.Mozilla.ttf",
        DOWNLOAD_DIR / "TwemojiMozilla.ttf",
    ),
    "noto": (
        "https://github.com/googlefonts/noto-emoji/raw/main/fonts/Noto-COLRv1.ttf",
        DOWNLOAD_DIR / "Noto-COLRv1.ttf",
    ),
}


def fetch(url: str, target: Path) -> int:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 5 * 1024:
        size_mb = target.stat().st_size / 1024 / 1024
        print(f"[download] 已存在 {target.name} ({size_mb:.2f} MB)")
        return 0
    print(f"[download] 拉取 {url}")
    print(f"[download] 目标 {target}")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            written = 0
            with open(target, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    written += len(chunk)
                    if total:
                        pct = written * 100 // total
                        print(
                            f"\r[download] {pct}% ({written // 1024 // 1024} / {total // 1024 // 1024} MB)",
                            end="",
                            flush=True,
                        )
            print()
    except Exception as e:
        print(f"[download] 失败: {e}", file=sys.stderr)
        if target.exists():
            target.unlink()
        return 1
    print(f"[download] 完成 {target.stat().st_size / 1024 / 1024:.2f} MB")
    return 0


def main() -> int:
    which = "twemoji"
    if len(sys.argv) > 1 and sys.argv[1] == "--noto":
        which = "noto"
    elif len(sys.argv) > 1 and sys.argv[1] == "--all":
        rc = 0
        for name in ("twemoji", "noto"):
            url, tgt = SOURCES[name]
            rc |= fetch(url, tgt)
        return rc
    url, target = SOURCES[which]
    return fetch(url, target)


if __name__ == "__main__":
    sys.exit(main())
