# -*- coding: utf-8 -*-
"""把"圈数字全角版"拆成 编辑器版 + 终端混合版。

为什么要拆：全角圈数字(advance=1000)在 VS Code 编辑器(按字形 advance 排版)里
两列清晰；但在 xterm.js 终端(VS Code 集成终端 / 多数终端)里字符占几列是按
Unicode East Asian Width 表决定的，与字体无关：

  - Ambiguous 圈数字(①–⑳ 等, U+2460+) → 终端强制 1 列 → 全角字形被压糊；
  - Wide 圈数字(㉑–㉟ U+3251-325F、㊱–㊿ U+32B1-32BF) → 终端给 2 列 → 需全角填满。

一套字体无法同时讨好编辑器和终端，于是拆成两个 family：

  编辑器版  family = 'Sarasa Term SC Circled'
            全部圈数字全角(2 列)，编辑器里最清晰。独立 family 名，不和原版撞名。
  终端版    family = 'Sarasa Term SC' (drop-in 替换原版)
            基底 = 原版半角(Ambiguous 1 列清晰)，仅 Wide 段换全角(终端 2 列填满)。

settings.json 配法：
  "editor.fontFamily":            "'Sarasa Term SC Circled', 'Sarasa Term SC', ..."
  "terminal.integrated.fontFamily": "'Sarasa Term SC', ..."

用法:
  python patch_split.py <full_width.ttf> <orig_term.ttf> [out_dir]
    full_width.ttf  圈数字全角版(本仓 SarasaTermSC-Circled-Regular.ttf，
                    由 patch_circled_width.py 产出)
    orig_term.ttf   原版 Sarasa Term SC Regular(本机安装，
                    %LOCALAPPDATA%/Microsoft/Windows/Fonts/SarasaTermSC-Regular.ttf)
    out_dir         输出目录(默认当前目录)
输出:
  SarasaTermSC-CircledNamed-Regular.ttf   (编辑器版)
  SarasaTermSC-TermFix-Regular.ttf        (终端版)
"""
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen

# 仅这两段圈数字是 Unicode East Asian Wide（终端给 2 列）；其余圈数字均 Ambiguous(1 列)
WIDE_RANGES = [(0x3251, 0x325F), (0x32B1, 0x32BF)]

EDITOR_FAMILY = "Sarasa Term SC Circled"
EDITOR_PS = "SarasaTermSC-Circled-Regular"
EDITOR_OUT = "SarasaTermSC-CircledNamed-Regular.ttf"
TERM_OUT = "SarasaTermSC-TermFix-Regular.ttf"


def make_editor(full_path: Path, out_dir: Path) -> Path:
    """全角版改 family 名 → 编辑器版(独立 family，与原版共存不撞名)。"""
    f = TTFont(str(full_path))
    overrides = {1: EDITOR_FAMILY, 2: "Regular", 4: EDITOR_FAMILY,
                 6: EDITOR_PS, 16: EDITOR_FAMILY, 17: "Regular"}
    for rec in f["name"].names:
        if rec.nameID in overrides:
            try:
                rec.string = overrides[rec.nameID]
            except Exception:
                rec.string = overrides[rec.nameID].encode("utf-16-be")
    out = out_dir / EDITOR_OUT
    f.save(str(out))
    return out


def make_terminal(orig_path: Path, full_path: Path, out_dir: Path) -> Path:
    """原版半角基底 + Wide 段移植全角字形 → 终端混合版(family 仍 'Sarasa Term SC')。"""
    base = TTFont(str(orig_path))
    full = TTFont(str(full_path))
    bc = base.getBestCmap(); fc = full.getBestCmap()
    bglyf = base["glyf"]; bhm = base["hmtx"].metrics
    fgs = full.getGlyphSet()
    n = 0
    for lo, hi in WIDE_RANGES:
        for cp in range(lo, hi + 1):
            fgn = fc.get(cp); bgn = bc.get(cp)
            if not fgn or not bgn:
                continue
            # 分解移植(避免跨字体 component id 错位)，advance 强制全角 1000
            rec = DecomposingRecordingPen(fgs); fgs[fgn].draw(rec)
            pen = TTGlyphPen(glyphSet=None); rec.replay(pen)
            g = pen.glyph(); bglyf[bgn] = g; g.recalcBounds(bglyf)
            bhm[bgn] = (1000, g.xMin if g.numberOfContours > 0 else 0)
            n += 1
    out = out_dir / TERM_OUT
    base.save(str(out))
    print(f"[term]   grafted {n} Wide glyphs -> full-width")
    return out


def main(argv) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    full = Path(argv[1]); orig = Path(argv[2])
    out_dir = Path(argv[3]) if len(argv) > 3 else Path(".")
    for p in (full, orig):
        if not p.exists():
            print(f"输入不存在: {p}", file=sys.stderr)
            return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    e = make_editor(full, out_dir)
    print(f"[editor] {e}  family='{EDITOR_FAMILY}'")
    t = make_terminal(orig, full, out_dir)
    print(f"[term]   {t}  family='Sarasa Term SC' (drop-in)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
