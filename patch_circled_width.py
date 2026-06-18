"""把圈数字"全家"从 Sarasa Mono SC 移植成全角，写回 Sarasa Term SC。

为什么：Sarasa **Term** 变体把"东亚歧义宽度"字符（①②… 等）压成半角(advance=500)，
圆圈被横向压扁(墨迹 w/h≈0.59)，里头的数字挤成一小团看不清。
同家族的 Sarasa **Mono** 变体里这些字符是正经全角(advance=1000、圆圈 w/h≈1.0)，
设计现成、零失真。所以直接从本机已装的 Mono 把这 122 个字形 + advance 移植进 Term，
不下载、不缩放变形。

只换字形轮廓 + advance，不动 name table / cmap / 纵向 metrics —— family 名仍是
"Sarasa Term SC"，是原版的 drop-in 替换，settings.json 不用改。

⚠️ 渲染前提：字体只能把字形画大，决定"占几列"的是渲染器的 Unicode 宽度表。
- VS Code 编辑器按 advance 排版 → 改完直接生效。
- 终端按宽度表分配格子，圈数字属 Ambiguous → 需把终端设成"歧义宽度=宽/双宽"
  才会给 2 列；否则全角字形会和后一个字符重叠。详见 README。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


# 圈数字"全家" codepoint 区间（仅数字，不含 Ⓐ-ⓩ 圈字母）。
# (lo, hi, 说明)，闭区间。脚本只移植 target 里是半角、source 里是全角的成员。
CIRCLED_NUMBER_RANGES: tuple[tuple[int, int, str], ...] = (
    (0x2460, 0x2473, "circled 1-20 ①-⑳"),
    (0x2474, 0x2487, "parenthesized 1-20 ⑴-⒇"),
    (0x24EA, 0x24EA, "circled 0 ⓪"),
    (0x24EB, 0x24F4, "negative-circled 11-20 ⓫-⓴"),
    (0x24F5, 0x24FE, "double-circled 1-10 ⓵-⓾"),
    (0x24FF, 0x24FF, "negative-circled 0 ⓿"),
    (0x2776, 0x277F, "dingbat negative-circled 1-10 ❶-❿"),
    (0x2780, 0x2789, "dingbat circled sans 1-10 ➀-➉"),
    (0x278A, 0x2793, "dingbat negative-circled sans 1-10 ➊-➓"),
    (0x3251, 0x325F, "circled 21-35 ㉑-㉟"),
    (0x32B1, 0x32BF, "circled 36-50 ㊱-㊿"),
)


def circled_number_codepoints() -> list[int]:
    cps: list[int] = []
    for lo, hi, _ in CIRCLED_NUMBER_RANGES:
        cps.extend(range(lo, hi + 1))
    return cps


def graft_glyph(src: TTFont, src_gname: str, tgt: TTFont, tgt_gname: str) -> tuple[int, int]:
    """把 src 的字形轮廓（复合字形先 decompose 成实线）写到 tgt 的同 codepoint 字形上。

    返回 (advance, lsb)，advance 取自 src，lsb 按移植后字形实际 xMin 重算。
    src/tgt 同为 Sarasa（UPM=1000、TrueType glyf），坐标空间一致，可直接搬。
    """
    src_glyphset = src.getGlyphSet()
    # DecomposingRecordingPen 把 component 引用展开成轮廓 → 输出永远是 simple glyph，
    # 不依赖 src 的字形顺序/component 子字形是否同时存在于 tgt。
    rec = DecomposingRecordingPen(src_glyphset)
    src_glyphset[src_gname].draw(rec)
    pen = TTGlyphPen(glyphSet=None)
    rec.replay(pen)
    new_glyph = pen.glyph()

    tgt_glyf = tgt["glyf"]
    tgt_glyf[tgt_gname] = new_glyph
    new_glyph.recalcBounds(tgt_glyf)

    src_advance = src["hmtx"].metrics[src_gname][0]
    lsb = new_glyph.xMin if new_glyph.numberOfContours > 0 else 0
    return src_advance, lsb


def patch_circled_width(
    target_path: Path,
    output_path: Path,
    source_path: Path,
) -> int:
    print(f"[circled] source(全角源) = {source_path}")
    print(f"[circled] target(待加宽) = {target_path}")
    print(f"[circled] output         = {output_path}")

    src = TTFont(str(source_path))
    tgt = TTFont(str(target_path))

    if "glyf" not in tgt or "glyf" not in src:
        print("[circled] ERROR: 需要 TrueType (glyf) 字体", file=sys.stderr)
        return 1
    if src["head"].unitsPerEm != tgt["head"].unitsPerEm:
        print(
            f"[circled] ERROR: UPM 不一致 source={src['head'].unitsPerEm} "
            f"target={tgt['head'].unitsPerEm}，无法直接搬轮廓",
            file=sys.stderr,
        )
        return 1

    src_cmap = src.getBestCmap()
    tgt_cmap = tgt.getBestCmap()
    tgt_hmtx = tgt["hmtx"].metrics

    grafted = 0
    skipped_already_full = 0
    skipped_missing = 0
    for cp in circled_number_codepoints():
        tgt_gname = tgt_cmap.get(cp)
        src_gname = src_cmap.get(cp)
        if tgt_gname is None or src_gname is None:
            skipped_missing += 1
            continue
        tgt_adv = tgt_hmtx[tgt_gname][0]
        src_adv = src["hmtx"].metrics[src_gname][0]
        # 只动"target 半角、source 全角"的——已是全角的不碰，避免误改。
        if tgt_adv >= src_adv:
            skipped_already_full += 1
            continue
        advance, lsb = graft_glyph(src, src_gname, tgt, tgt_gname)
        tgt_hmtx[tgt_gname] = (advance, lsb)
        grafted += 1

    print(
        f"[circled] 移植 {grafted} 个字形全角化"
        f"（跳过 已全角={skipped_already_full} 缺失={skipped_missing}）"
    )
    if grafted == 0:
        print("[circled] WARNING: 没有任何字形被移植，输出与原字体等价", file=sys.stderr)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tgt.save(str(output_path))
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"[circled] 完成 {output_path} ({size_mb:.1f} MB)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="把圈数字全家从全角源字体(Sarasa Mono SC)移植成全角写回 Sarasa Term SC。"
    )
    ap.add_argument("target", type=Path, help="待加宽字体 (SarasaTermSC-Regular.ttf)")
    ap.add_argument("output", type=Path, help="输出 ttf 路径")
    ap.add_argument(
        "--source",
        type=Path,
        default=None,
        help="全角字形来源字体，默认取 target 同目录的 SarasaMonoSC-Regular.ttf",
    )
    args = ap.parse_args()

    source = args.source or (args.target.parent / "SarasaMonoSC-Regular.ttf")

    if not args.target.exists():
        print(f"target 不存在: {args.target}", file=sys.stderr)
        return 1
    if not source.exists():
        print(
            f"全角源字体不存在: {source}\n"
            "  圈数字全角字形取自 Sarasa Mono SC（与 Term 同属 Sarasa 发布包）。\n"
            "  装好 Sarasa Mono SC 或用 --source 指向任一全角圈数字字体。",
            file=sys.stderr,
        )
        return 1

    return patch_circled_width(args.target, args.output, source)


if __name__ == "__main__":
    sys.exit(main())
