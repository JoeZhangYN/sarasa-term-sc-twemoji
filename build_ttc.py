"""把 Sarasa Term SC + NotoEmojiAligned 装入单个 .ttc 文件。

TTC (TrueType Collection) 是 OpenType 标准的字体合集格式，单文件含多个字体，
共享相同的字形/表数据可去重。Windows / macOS / Linux 原生支持。

用户得到：
- 单文件 SarasaTermSCEmoji.ttc 替代两个独立 .ttf
- 单次安装注册两个 family（"Sarasa Term SC" + "Noto Emoji Aligned"）
- VS Code fontFamily 仍引两条名字（TTC 内 font 在 OS 是独立 family）
"""

import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.ttCollection import TTCollection


def build_ttc(font_paths: list[Path], output: Path) -> int:
    if not font_paths:
        print("[ttc] 至少需要一个字体", file=sys.stderr)
        return 1

    ttc = TTCollection()
    for p in font_paths:
        if not p.exists():
            print(f"[ttc] 字体不存在: {p}", file=sys.stderr)
            return 1
        font = TTFont(str(p))
        ttc.fonts.append(font)
        family = ""
        for r in font["name"].names:
            if r.nameID == 1 and r.platformID == 3:
                try:
                    family = r.toUnicode()
                except Exception:
                    family = repr(r.string)
                break
        size_mb = p.stat().st_size / 1024 / 1024
        print(f"[ttc] + {p.name} ({size_mb:.2f} MB) family='{family}'")

    output.parent.mkdir(parents=True, exist_ok=True)
    ttc.save(str(output))
    out_mb = output.stat().st_size / 1024 / 1024
    print(f"[ttc] 完成 {output} ({out_mb:.2f} MB, {len(ttc.fonts)} fonts)")
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "用法: python build_ttc.py <output.ttc> <font1.ttf> [<font2.ttf> ...]",
            file=sys.stderr,
        )
        return 2
    output = Path(sys.argv[1])
    fonts = [Path(p) for p in sys.argv[2:]]
    return build_ttc(fonts, output)


if __name__ == "__main__":
    sys.exit(main())
