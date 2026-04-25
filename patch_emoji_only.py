"""v2 路线：单独 patch Noto-COLRv1，不合并 Sarasa。

不合并的理由：fontTools Merger 不支持 COLR/CPAL 彩色表（merge 后会丢失），
导致 emoji 字形被合并但失去彩色信息渲染为空白。

替代方案：
- 把 Noto-COLRv1 子集化（仅常用 emoji 50 个），UPM 重缩放至 1000，
  所有 emoji glyph 的 advance 强制 = 1000（与 Sarasa CJK 等宽）
- COLR/CPAL 表完整保留（彩色信息未动）
- 用户 fontFamily 配置：Noto-Aligned 在前 + Sarasa 在后
  - Chromium 渲染：emoji codepoint 在 Noto-Aligned 找到 → 用它（彩色 + 等宽）
  - 其他 codepoint 在 Sarasa 找到 → 用 Sarasa
- 两个字体的 advance 对齐到同一 UPM (1000)，VS Code 视觉对齐
"""

import sys
from pathlib import Path

from fontTools.subset import Options as SubsetOptions, Subsetter
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem

# 复用主 patch.py 的白名单
sys.path.insert(0, str(Path(__file__).parent))
from patch import COMMON_EMOJI_CODEPOINTS, in_common_emoji, update_name_table


def patch_emoji_only(
    emoji_path: Path,
    output_path: Path,
    target_upm: int = 1000,
    family_name: str = "Noto Emoji Aligned",
) -> int:
    print(f"[patch-emoji] emoji  = {emoji_path}")
    print(f"[patch-emoji] output = {output_path}")
    print(f"[patch-emoji] family = {family_name}, UPM = {target_upm}")

    emoji = TTFont(str(emoji_path))
    emoji_cmap = emoji.getBestCmap()
    candidate_cps = sorted(c for c in emoji_cmap if in_common_emoji(c))
    print(f"[patch-emoji] 白名单 ∩ Noto cmap = {len(candidate_cps)} 字符")
    if not candidate_cps:
        return 1

    # 子集化（COLR/CPAL 跟随 layer glyph 自动保留）
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

    # UPM 重缩放
    if emoji["head"].unitsPerEm != target_upm:
        print(f"[patch-emoji] UPM {emoji['head'].unitsPerEm} -> {target_upm}")
        scale_upem(emoji, target_upm)

    # 强制 advance：仅 cmap-mapped glyph（color layer glyph 由 COLR 引用，宽度不参与排版）
    cmap = emoji.getBestCmap()
    forced = 0
    for cp, gname in cmap.items():
        if in_common_emoji(cp) and gname in emoji["hmtx"].metrics:
            emoji["hmtx"].metrics[gname] = (target_upm, 0)
            forced += 1
    print(f"[patch-emoji] 强制 {forced} 个 emoji glyph advance = {target_upm}")

    # 检查 COLR/CPAL 仍存（彩色信息）
    has_colr = "COLR" in emoji
    has_cpal = "CPAL" in emoji
    print(f"[patch-emoji] COLR={has_colr} CPAL={has_cpal} (彩色表保留)")

    # name 表
    update_name_table(emoji, family_name, "Regular")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    emoji.save(str(output_path))
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"[patch-emoji] 完成 {output_path} ({size_mb:.2f} MB)")
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "用法: python patch_emoji_only.py <noto-colrv1.ttf> <output.ttf> [family]",
            file=sys.stderr,
        )
        return 2
    emoji = Path(sys.argv[1])
    output = Path(sys.argv[2])
    family = sys.argv[3] if len(sys.argv) > 3 else "Noto Emoji Aligned"
    if not emoji.exists():
        print(f"emoji 不存在: {emoji}", file=sys.stderr)
        return 1
    return patch_emoji_only(emoji, output, target_upm=1000, family_name=family)


if __name__ == "__main__":
    sys.exit(main())
