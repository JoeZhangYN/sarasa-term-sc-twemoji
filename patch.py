"""把 Noto Color Emoji 的 emoji 字形合并入 Sarasa Term SC，
advance width 强制 = base 的 units_per_em（= CJK 宽度）。

输出：单一 .ttf，emoji 与 CJK 等宽对齐，兼容 advance-width-based 渲染器（VS Code 等）。
"""

import sys
import tempfile
from pathlib import Path

from fontTools.merge import Merger
from fontTools.subset import Options as SubsetOptions, Subsetter
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem


# 常用 emoji 白名单 — Sarasa 56794 base glyph + Noto-COLRv1 每 emoji ~28 layer glyph，
# TTF 64K glyph 上限只允许 ~300 emoji 余量。此精选 ~50 字符覆盖代码/笔记 90% 场景。
COMMON_EMOJI_CODEPOINTS = {
    # 状态/标记 (最常用)
    0x2705,  # ✅ check mark button
    0x274C,  # ❌ cross mark
    0x274E,  # ❎ negative squared X
    0x2B50,  # ⭐ star
    0x2713,  # ✓ check
    0x2717,  # ✗ ballot X
    0x2714,  # ✔ heavy check
    0x2718,  # ✘ heavy ballot X
    # 警示/提醒
    0x26A0,  # ⚠ warning
    0x26D4,  # ⛔ no entry
    0x1F6AB, # 🚫 prohibited
    0x2757,  # ❗ exclamation
    0x2753,  # ❓ question
    0x2755,  # ❕ white exclamation
    0x2754,  # ❔ white question
    # 表情/态度
    0x1F44D, # 👍 thumbs up
    0x1F44E, # 👎 thumbs down
    0x1F44F, # 👏 clapping
    0x1F525, # 🔥 fire
    0x2728,  # ✨ sparkles
    0x1F389, # 🎉 party popper
    0x1F4A1, # 💡 light bulb
    0x1F914, # 🤔 thinking
    0x1F60A, # 😊 smiling
    0x1F602, # 😂 laughing
    0x1F622, # 😢 crying
    # 进度/方向
    0x2B05,  # ⬅ left arrow
    0x2B06,  # ⬆ up arrow
    0x2B07,  # ⬇ down arrow
    0x27A1,  # ➡ right arrow
    0x21A9,  # ↩ leftwards arrow with hook
    0x21AA,  # ↪ rightwards arrow with hook
    0x1F504, # 🔄 counterclockwise
    # 工具/技术
    0x1F680, # 🚀 rocket
    0x1F527, # 🔧 wrench
    0x1F528, # 🔨 hammer
    0x1F4CC, # 📌 push pin
    0x1F4CE, # 📎 paperclip
    0x1F4DD, # 📝 memo
    0x1F4D6, # 📖 book
    0x1F4DA, # 📚 books
    0x1F4C5, # 📅 calendar
    0x1F551, # 🕑 clock
    0x23F0,  # ⏰ alarm clock
    0x231B,  # ⌛ hourglass
    0x1F512, # 🔒 lock
    0x1F513, # 🔓 unlock
    0x1F511, # 🔑 key
    0x1F50D, # 🔍 magnifying glass
    # 心情/对错
    0x2764,  # ❤ heart
    0x1F494, # 💔 broken heart
    0x1F4AF, # 💯 hundred points
}


def in_common_emoji(cp: int) -> bool:
    return cp in COMMON_EMOJI_CODEPOINTS


def force_emoji_advance(merged: TTFont, base_glyphs: set, target_advance: int,
                        emoji_cps: set) -> int:
    """两类 glyph advance 强制 = target：
    1. 来自 emoji 字体的新增 glyph（不在 base_glyphs）
    2. base 字体已有的 emoji codepoint 对应 glyph（如 Sarasa 有 ⭐ 但宽度=500 半角）
    后者关键——否则 mdtable 按 W 算 2 col 的字符在 base 字体里仍是 1 col → 不齐
    """
    n = 0
    hmtx = merged["hmtx"].metrics
    cmap = merged.getBestCmap()
    # 1. 先收集所有 emoji codepoint 对应的 glyph name
    emoji_glyphs_via_cmap = {cmap[cp] for cp in emoji_cps if cp in cmap}
    # 2. 加上所有 base 没有的 glyph（来自 emoji 字体）
    new_glyphs = {g for g in merged.getGlyphOrder() if g not in base_glyphs and g != ".notdef"}
    # 3. 合并两类
    targets = emoji_glyphs_via_cmap | new_glyphs
    for gname in targets:
        if gname not in hmtx:
            continue
        old_adv, _lsb = hmtx[gname]
        if old_adv != target_advance:
            # base emoji glyph 居中（lsb 调整使视觉居中）
            new_lsb = (target_advance - old_adv) // 2 if gname in emoji_glyphs_via_cmap and gname in base_glyphs else 0
            hmtx[gname] = (target_advance, new_lsb)
            n += 1
    return n


def update_name_table(font: TTFont, family: str, subfamily: str = "Regular") -> None:
    """改 name table 让新字体在系统字体列表里显示为新 family。"""
    full = f"{family} {subfamily}"
    ps = (family + "-" + subfamily).replace(" ", "")
    # nameID: 1=Family 2=Subfamily 4=Full 6=PostScript 16=Preferred Family 17=Preferred Subfamily
    overrides = {1: family, 2: subfamily, 4: full, 6: ps, 16: family, 17: subfamily}
    for record in font["name"].names:
        if record.nameID in overrides:
            try:
                record.string = overrides[record.nameID]
            except Exception:
                # 某些 platform/encoding 需 bytes
                record.string = overrides[record.nameID].encode("utf-16-be")


def patch(base_path: Path, emoji_path: Path, output_path: Path, family_name: str) -> int:
    print(f"[patch] base    = {base_path}")
    print(f"[patch] emoji   = {emoji_path}")
    print(f"[patch] output  = {output_path}")

    # 1. 读 base 取目标 advance
    base = TTFont(str(base_path))
    target_advance = base["head"].unitsPerEm
    base_cmap_before = base.getBestCmap()
    print(f"[patch] base UPM={target_advance} 现有 glyph={base['maxp'].numGlyphs} cmap={len(base_cmap_before)}")

    # 2. 读 emoji 看哪些 codepoint 我们要用（白名单交 emoji.cmap）
    emoji = TTFont(str(emoji_path))
    emoji_cmap = emoji.getBestCmap()
    candidate_cps = sorted(c for c in emoji_cmap if in_common_emoji(c))
    print(f"[patch] 候选 codepoint={len(candidate_cps)} (常用 emoji 白名单 ∩ Noto cmap)")
    if not candidate_cps:
        print("[patch] 无新字符可合，退出")
        return 1

    # 3. 关键：从 base cmap 移除所有 emoji codepoint（Sarasa 这些字形是空壳），
    #    让 Noto 的彩色字形通过 Merger 接管
    removed = 0
    for table in base["cmap"].tables:
        if table.format in (4, 6, 12, 13):
            for cp in candidate_cps:
                if cp in table.cmap:
                    del table.cmap[cp]
                    removed += 1
    print(f"[patch] 从 base cmap 移除 {removed} 个 emoji codepoint 映射 (让 Noto 顶上)")

    # 写改造后的 base 到 temp 给 Merger 读
    tmpdir = Path(tempfile.mkdtemp())
    base_clean_path = tmpdir / f"{base_path.stem}_no_emoji.ttf"
    base.save(str(base_clean_path))

    # 4. 子集化 emoji（避开 64K 上限）
    print(f"[patch] 子集 Noto-COLRv1 → {len(candidate_cps)} codepoint")
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
    sub_opts.drop_tables = []
    sub_opts.no_subset_tables = ["COLR", "CPAL"]
    sub = Subsetter(options=sub_opts)
    sub.populate(unicodes=candidate_cps)
    sub.subset(emoji)

    # 5. UPM 重缩放
    emoji_upm = emoji["head"].unitsPerEm
    if emoji_upm != target_advance:
        print(f"[patch] emoji UPM={emoji_upm} != base UPM={target_advance}，重缩放")
        scale_upem(emoji, target_advance)

    emoji_path_for_merge = tmpdir / f"{emoji_path.stem}_subset_scaled.ttf"
    emoji.save(str(emoji_path_for_merge))

    # 6. Merger
    print("[patch] Merger.merge 启动...")
    merger = Merger()
    merged = merger.merge([str(base_clean_path), str(emoji_path_for_merge)])

    # 7. 强制 advance（现在 emoji codepoint 在 cmap 指向 Noto 的 glyph，不是 Sarasa 空壳）
    base_glyphs_orig = set(TTFont(str(base_path)).getGlyphOrder())
    forced = force_emoji_advance(merged, base_glyphs_orig, target_advance, set(candidate_cps))
    print(f"[patch] 强制 advance 修正 {forced} 个 emoji glyph 至 {target_advance}")

    # 5. 改 name table
    update_name_table(merged, family_name, "Regular")
    print(f"[patch] name table → {family_name} Regular")

    # 6. 保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.save(str(output_path))
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"[patch] 完成 {output_path} ({size_mb:.1f} MB)")
    return 0


def main() -> int:
    if len(sys.argv) < 4:
        print("用法: python patch.py <base.ttf> <emoji.ttf> <output.ttf> [family-name]", file=sys.stderr)
        return 2
    base = Path(sys.argv[1])
    emoji = Path(sys.argv[2])
    output = Path(sys.argv[3])
    family = sys.argv[4] if len(sys.argv) > 4 else "Sarasa Term SC Emoji"
    if not base.exists():
        print(f"base 不存在: {base}", file=sys.stderr)
        return 1
    if not emoji.exists():
        print(f"emoji 不存在: {emoji}", file=sys.stderr)
        return 1
    return patch(base, emoji, output, family)


if __name__ == "__main__":
    sys.exit(main())
