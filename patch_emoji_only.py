"""单独 patch emoji 字体（不合并 Sarasa——Merger 会丢 COLR/CPAL）。

子集化 → UPM=1000 → emoji glyph advance=1000 → 纵向 metrics 拷自 base。
这样 fontFamily 链里 Aligned 在前 + Sarasa 在后时，advance 与 line height 都对齐。
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from fontTools.subset import Options as SubsetOptions, Subsetter
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem

sys.path.insert(0, str(Path(__file__).parent))
from patch import COMMON_EMOJI_CODEPOINTS, in_common_emoji, update_name_table


@dataclass(frozen=True, slots=True)
class VerticalMetrics:
    """终端行距源：USE_TYPO_METRICS=1 → sTypo*；老 Win GDI → usWin*；hhea 兜底。三套一并对齐 base。"""
    upm: int
    hhea_ascent: int
    hhea_descent: int
    hhea_line_gap: int
    typo_ascent: int
    typo_descent: int
    typo_line_gap: int
    win_ascent: int
    win_descent: int
    fs_selection: int

    @classmethod
    def from_font(cls, font: TTFont) -> VerticalMetrics:
        head = font["head"]
        hhea = font["hhea"]
        os2 = font["OS/2"]
        return cls(
            upm=head.unitsPerEm,
            hhea_ascent=hhea.ascent,
            hhea_descent=hhea.descent,
            hhea_line_gap=hhea.lineGap,
            typo_ascent=os2.sTypoAscender,
            typo_descent=os2.sTypoDescender,
            typo_line_gap=os2.sTypoLineGap,
            win_ascent=os2.usWinAscent,
            win_descent=os2.usWinDescent,
            fs_selection=os2.fsSelection,
        )

    def apply_to(self, font: TTFont) -> None:
        if font["head"].unitsPerEm != self.upm:
            raise ValueError(
                f"UPM mismatch: target font UPM={font['head'].unitsPerEm} "
                f"!= source metrics UPM={self.upm}; rescale before apply",
            )
        hhea = font["hhea"]
        os2 = font["OS/2"]
        hhea.ascent = self.hhea_ascent
        hhea.descent = self.hhea_descent
        hhea.lineGap = self.hhea_line_gap
        os2.sTypoAscender = self.typo_ascent
        os2.sTypoDescender = self.typo_descent
        os2.sTypoLineGap = self.typo_line_gap
        os2.usWinAscent = self.win_ascent
        os2.usWinDescent = self.win_descent
        os2.fsSelection = (os2.fsSelection & ~(1 << 7)) | (self.fs_selection & (1 << 7))


def patch_emoji_only(
    emoji_path: Path,
    output_path: Path,
    target_upm: int = 1000,
    family_name: str = "Twemoji Aligned",
    metrics_from: Path | None = None,
) -> int:
    print(f"[patch-emoji] emoji   = {emoji_path}")
    print(f"[patch-emoji] output  = {output_path}")
    print(f"[patch-emoji] family  = {family_name}, UPM = {target_upm}")
    print(f"[patch-emoji] metrics = {metrics_from or '(keep emoji font defaults)'}")

    base_metrics: VerticalMetrics | None = None
    if metrics_from is not None:
        base_metrics = VerticalMetrics.from_font(TTFont(str(metrics_from)))
        if base_metrics.upm != target_upm:
            raise ValueError(
                f"metrics-from UPM={base_metrics.upm} != target_upm={target_upm}; "
                "must match so vertical metrics line up after rescale",
            )

    emoji = TTFont(str(emoji_path))
    emoji_cmap = emoji.getBestCmap()
    candidate_cps = sorted(c for c in emoji_cmap if in_common_emoji(c))
    print(f"[patch-emoji] 白名单 ∩ emoji cmap = {len(candidate_cps)} 字符")
    if not candidate_cps:
        return 1

    sub_opts = SubsetOptions()
    sub_opts.layout_features = ["*"]
    sub_opts.glyph_names = True
    sub_opts.legacy_cmap = True
    sub_opts.symbol_cmap = True
    sub_opts.notdef_glyph = True
    sub_opts.recommended_glyphs = False
    sub_opts.name_IDs = ["*"]
    sub_opts.name_legacy = True
    sub_opts.name_languages = ["*"]
    sub = Subsetter(options=sub_opts)
    sub.populate(unicodes=candidate_cps)
    sub.subset(emoji)
    print(f"[patch-emoji] 子集后 glyph 数 = {emoji['maxp'].numGlyphs}")

    if emoji["head"].unitsPerEm != target_upm:
        print(f"[patch-emoji] UPM {emoji['head'].unitsPerEm} -> {target_upm}")
        scale_upem(emoji, target_upm)

    cmap = emoji.getBestCmap()
    forced = 0
    for cp, gname in cmap.items():
        if in_common_emoji(cp) and gname in emoji["hmtx"].metrics:
            emoji["hmtx"].metrics[gname] = (target_upm, 0)
            forced += 1
    print(f"[patch-emoji] 强制 {forced} 个 emoji glyph advance = {target_upm}")

    if base_metrics is not None:
        base_metrics.apply_to(emoji)
        line_total = base_metrics.win_ascent + base_metrics.win_descent
        print(f"[patch-emoji] 纵向 metrics ← base，行距单位 = {line_total} (UPM {target_upm})")

    print(f"[patch-emoji] COLR={'COLR' in emoji} CPAL={'CPAL' in emoji} (彩色表保留)")
    update_name_table(emoji, family_name, "Regular")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    emoji.save(str(output_path))
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"[patch-emoji] 完成 {output_path} ({size_mb:.2f} MB)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Patch emoji font: subset + rescale + align metrics.")
    ap.add_argument("emoji", type=Path, help="emoji font path (e.g. TwemojiMozilla.ttf)")
    ap.add_argument("output", type=Path, help="output ttf path")
    ap.add_argument("family", nargs="?", default="Twemoji Aligned", help="family name")
    ap.add_argument(
        "--metrics-from",
        type=Path,
        default=None,
        help="copy vertical metrics from this font (e.g. Sarasa Term SC); "
        "must share the same UPM as --target-upm. Required to fix tight terminal line spacing.",
    )
    ap.add_argument("--target-upm", type=int, default=1000)
    args = ap.parse_args()

    if not args.emoji.exists():
        print(f"emoji 不存在: {args.emoji}", file=sys.stderr)
        return 1
    if args.metrics_from is not None and not args.metrics_from.exists():
        print(f"metrics-from 不存在: {args.metrics_from}", file=sys.stderr)
        return 1

    return patch_emoji_only(
        args.emoji,
        args.output,
        target_upm=args.target_upm,
        family_name=args.family,
        metrics_from=args.metrics_from,
    )


if __name__ == "__main__":
    sys.exit(main())
