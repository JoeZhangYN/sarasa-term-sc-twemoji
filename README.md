# Sarasa Term SC + Twemoji (Aligned)

CJK monospace + 彩色 emoji 严格等宽对齐字体——VS Code / 终端表格不再因 emoji 错位。

> **问题**：advance-width 渲染器（VS Code 等）里，emoji 回退到 Segoe UI Emoji 等系统字体，advance ≠ 2× ASCII → 含 emoji 的行视觉偏列；表格、对齐注释场景错位。
> **解法**：把 Twemoji 改造为 advance=1000、UPM=1000，与 Sarasa Term SC 的 CJK 严格等宽。

## 产物（直接安装）

| 文件 | 大小 | 用途 |
|------|------|------|
| `TwemojiAligned-Regular.ttf` | 18 KB | 49 个常用 emoji，advance=1000，配 Sarasa Term SC 用 |
| `SarasaTermSC-Circled-Regular.ttf` | 24 MB | Sarasa Term SC + 圈数字全角化（①②… 看清数字，详见 [圈数字加宽](#圈数字加宽看清里面的数字)）；family 名仍是 `Sarasa Term SC`，drop-in 替换原版 |
| `SarasaTermSCEmoji.ttc` | 24 MB | TTC 合集：圈数字加宽版 Sarasa Term SC + Twemoji Aligned 单文件 |

49 个 emoji 范围（完整列表见 [`patch.py`](patch.py) 的 `COMMON_EMOJI_CODEPOINTS`）：
- 状态/标记：✅ ❌ ❎ ⭐ ✓ ✗ ✔ ✘
- 警示：⚠ ⛔ 🚫 ❗ ❓ ❕ ❔
- 表情：👍 👎 👏 🔥 ✨ 🎉 💡 🤔 😊 😂 😢
- 方向/进度：⬅ ⬆ ⬇ ➡ ↩ ↪ 🔄
- 工具：🚀 🔧 🔨 📌 📎 📝 📖 📚 📅 🕑 ⏰ ⌛ 🔒 🔓 🔑 🔍
- 心情：❤ 💔 💯

## 圈数字加宽（看清里面的数字）

**问题**：Sarasa **Term** 变体把"东亚歧义宽度"字符（①②③… 等）压成半角（advance=500），圆圈被横向压扁（墨迹宽/高≈0.59），里头的数字挤成一小团看不清。

**解法**：同家族的 Sarasa **Mono** SC 里这些字符是正经全角（advance=1000、圆圈宽/高≈1.0），设计现成。[`patch_circled_width.py`](patch_circled_width.py) 把这 122 个字形 + advance 从 Mono 移植进 Term，**零下载、零失真**——只换轮廓和宽度，name/cmap/纵向 metrics 全不动，family 名仍是 `Sarasa Term SC`（drop-in 替换）。

覆盖"圈数字全家"122 个：①–⑳、⓪、⑴–⒇（括号）、⓫–⓴/⓿（实心反白）、⓵–⓾（双圈）、❶–❿/➀–➉/➊–➓（dingbat）、㉑–㊿。**只动这些，框线 `│─┌`、ASCII、CJK 一律不变。**

### ⚠️ 重要：只在按 advance 排版的渲染器里生效

"占几列"是**渲染器**按 Unicode 宽度表决定的，圈数字属"歧义宽度(Ambiguous)"——字体改不动这个。各场景实测：

| 渲染器 | 加宽效果 | 说明 |
|------|------|------|
| **VS Code 编辑器** | ✅ **生效** | 按字形 advance 排版（和本项目 emoji 对齐同一机制）→ 圈数字占 2 列、数字看清 |
| WezTerm / iTerm2 / macOS Terminal / mintty | ✅ 需配置 | 这些终端有"歧义宽度=宽/双宽"开关，打开后生效（如 WezTerm `treat_east_asian_ambiguous_width_as_wide = true`） |
| **Windows Terminal** | ⚠️ **不生效** | [无歧义宽度设置](https://github.com/microsoft/terminal/issues/10844)，按 [wcwidth 惯例](https://github.com/microsoft/terminal/issues/2066)当 1 格 → 字形被压回原样（无害但无改善），个别配置下会溢出重叠 |
| **VS Code 集成终端**（xterm.js） | ⚠️ **不生效** | [同样无该选项](https://github.com/xtermjs/xterm.js/issues/1453)，`rescaleOverlappingGlyphs` 会把超宽字形压回 1 格 |

**一句话**：在 **VS Code 编辑器**里读 markdown 表格 / 代码注释中的 ①②③ → 加宽有效、数字清晰；在 **Windows Terminal / VS Code 集成终端**里 → 被压回原样，无改善（也不会变更糟）。如果你重度依赖终端里看清圈数字，目前唯一办法是换支持歧义宽度开关的终端（如 WezTerm）。

## 安装

### 方案 A — 标准做法（推荐）

1. **圈数字加宽版**：先卸载原版 Sarasa Term SC（同 family 名，需替换）→ 双击 `SarasaTermSC-Circled-Regular.ttf` → Install for All Users
   （不需要加宽圈数字就跳过本步，直接装原版 [Sarasa Term SC](https://github.com/be5invis/Sarasa-Gothic/releases)）
2. 双击 `TwemojiAligned-Regular.ttf` → Install for All Users
3. VS Code `settings.json`（fontSize=16 实测甜点）：
   ```json
   "editor.fontFamily": "'Twemoji Aligned', 'Sarasa Term SC', 'Cascadia Code', monospace",
   "editor.fontSize": 16,
   "editor.unicodeHighlight.ambiguousCharacters": false,
   "editor.fontLigatures": false,
   "editor.lineHeight": 22,
   "terminal.integrated.lineHeight": 1.1
   ```
   > **为什么编辑器用 px、终端用倍率**：VS Code 编辑器 `lineHeight` 默认（=0）走平台常数（Win/Linux 1.35 × fontSize，Mac 1.5），**完全不读**字体的 1.25 em；终端 `lineHeight` 默认（=1.0）才是按字体 1.25 em 的倍率。两边规则不同，写同一个数字会得到不同绝对行高。这里都校准到 **22px**：编辑器写 px 绝对值最精准（≥8 走 px 模式），终端只支持倍率所以用 1.1（= 22 / (16 × 1.25)）。
   >
   > 改 fontSize 时换算公式：`terminal.integrated.lineHeight = 目标px / (fontSize × 1.25)`。
4. **完全 Exit + 重开** VS Code（Reload Window 不刷新字体缓存）。装新版字体后若行距仍异常，多半是 OS/编辑器仍吃旧字体缓存——见"故障排查"末行。

### 方案 B — 单文件 TTC

1. 卸载已装的 Sarasa Term SC（如有）
2. 双击 `SarasaTermSCEmoji.ttc` → Install for All Users
3. settings.json 同 A
4. 完全 Exit + 重开 VS Code

## 自己重建（修改白名单 / 换 emoji 源）

### 前置

- Python 3.10+
- 装 Sarasa Term SC Regular（路径：`%LOCALAPPDATA%\Microsoft\Windows\Fonts\SarasaTermSC-Regular.ttf`）
- 网络（下载 Twemoji ~1.5 MB）

### 一键构建（Windows）

```cmd
build.cmd
```

依次跑：
1. 创建 `.venv` 装 fontTools
2. [`patch_circled_width.py`](patch_circled_width.py) 从 Sarasa Mono SC 把圈数字全角字形移植进 Term → `SarasaTermSC-Circled-Regular.ttf`（需本机已装 Sarasa Mono SC Regular，与 Term 同发布包）
3. [`download.py`](download.py) 拉 Twemoji-Mozilla v0.7.0
4. [`patch_emoji_only.py`](patch_emoji_only.py) 子集化 + UPM 缩放 + advance 强制 1000
5. [`build_ttc.py`](build_ttc.py) 把加宽版 Sarasa + 改造后 Twemoji 装 .ttc

### 自定义白名单

改 [`patch.py`](patch.py) 的 `COMMON_EMOJI_CODEPOINTS`：

```python
COMMON_EMOJI_CODEPOINTS = {
    0x2705,  # ✅ check mark button
    0x274C,  # ❌ cross mark
    # ... 加你需要的 codepoint
    0x1F308, # 🌈 rainbow（举例）
}
```

⚠️ 上限约 ~200 codepoint：每 emoji 含 ~3-30 个 color layer glyph，加 Sarasa 56794 base glyph 容易撞 TTF 64K 上限。超过会报 `numGlyphs > 65535`，再裁。

### 换 emoji 源

```bash
# 用 Noto Color Emoji（OFL，扁平风）
python download.py --noto
python patch_emoji_only.py downloads/Noto-COLRv1.ttf TwemojiAligned-Regular.ttf "Noto Emoji Aligned"
```

或本机使用 Microsoft Segoe UI Emoji（**不可发布**）：

```bash
python patch_emoji_only.py "C:/Windows/Fonts/seguiemj.ttf" SegoeAligned.ttf "Segoe UI Emoji Aligned"
```

## 许可证

| 内容 | 协议 | 文件 |
|------|------|------|
| 构建脚本（`*.py`、`build.cmd`、`requirements.txt`） | MIT | [`LICENSE`](LICENSE) |
| Sarasa Gothic / Term SC | SIL OFL-1.1 | [`LICENSE-OFL-1.1.txt`](LICENSE-OFL-1.1.txt) |
| Twemoji emoji glyphs | CC-BY 4.0 | [`LICENSE-CC-BY-4.0.txt`](LICENSE-CC-BY-4.0.txt) |

**归属声明（CC-BY 4.0 必需）**：

> Emoji glyphs in this font are derived from [Twemoji](https://github.com/twitter/twemoji) © Twitter, Inc and contributors, licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).
>
> The CJK monospace base is [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic) by be5invis et al, licensed under [SIL OFL-1.1](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL).

**禁止**：
- 单独售卖字体（OFL 限制）
- 声称是 Twemoji 原版（CC-BY 限制）
- 移除归属声明

**允许**：
- 个人 / 商业 / 教育使用
- 嵌入软件、网站、文档
- 修改 + 再分发（保留同样的 License + 归属）

## 测试 / 验证

装好字体 + 重启 VS Code 后，新建一个 `.md` 文件粘下面这段 → 看三栏对齐 + emoji 彩色 → 即生效：

```
┌──────────────────────────┬──────────┬──────────┐
│ 思想                     │ 状态     │ 评分     │
├──────────────────────────┼──────────┼──────────┤
│ 摸着石头过河             │ ✅       │ ⭐⭐⭐⭐ │
│ 实事求是（仓库为准）     │ ✅       │ ⭐⭐⭐   │
│ 试点先行（dry-run 优先） │ ❌       │ ⭐⭐     │
│ 底线思维 ⚠ 不可逆动作    │ 🔥       │ ⭐⭐⭐   │
│ 钉钉子精神 🚀            │ ✅       │ ⭐⭐⭐⭐ │
└──────────────────────────┴──────────┴──────────┘
```

通过条件：
- ✓ 三栏 `│` 完全对齐（含 emoji 行）
- ✓ ⭐ ✅ ❌ ⚠ 🔥 🚀 显示 **Twemoji 风格彩色**（不是 Windows 默认 Segoe 3D 渐变）
- ✓ CJK + ASCII + emoji 严格 1:2:2 等宽

如不齐：见下方"故障排查"。

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| emoji 仍是 Win 默认彩色 | VS Code 没真正重启 | File → Exit（不是 Reload Window） |
| emoji 显示空白方框 | Sarasa Term SC 没装 | 装 [Sarasa Term SC](https://github.com/be5invis/Sarasa-Gothic/releases) |
| 中文字体变了 | settings.json fontFamily 顺序错 | 检查 `'Sarasa Term SC'` 在 fallback 链中 |
| 表格仍未对齐 | 老 emoji 字体优先级高 | DevTools (Ctrl+Shift+I) 看 computed font 是否真用了 Twemoji Aligned |
| 重建报 `numGlyphs > 65535` | 白名单太大 | 减 `COMMON_EMOJI_CODEPOINTS`，目标 ≤200 codepoint |
| 行距异常（太挤或太松）| 1) 编辑器/系统仍吃旧字体缓存（v0.1.0 metrics 比 Sarasa 小 11–13%）；2) `lineHeight` 用了不匹配你 fontSize 的倍率/像素值 | 1) 卸载旧字体 → 重启 Windows → 装新字体 → 完全退出（非 Reload）VS Code；2) 按"安装步骤 3"的换算公式调（编辑器走 px / 终端走倍率，两边规则不同） |

## Changelog

- v0.2.0（2026-06-18）：**圈数字加宽**。①②③… 等"东亚歧义宽度"字符在 Sarasa Term 里被压成半角、数字看不清；新增 [`patch_circled_width.py`](patch_circled_width.py) 从同家族 Sarasa Mono SC 移植 122 个全角字形（圈数字全家：①–⑳/⓪/括号/实心反白/双圈/dingbat/㉑–㊿），零下载零失真，family 名不变。新增产物 `SarasaTermSC-Circled-Regular.ttf`，TTC 改用加宽版 Sarasa。⚠️ 只在按 advance 排版的渲染器（VS Code 编辑器、或开了"歧义宽度=宽"的终端如 WezTerm/iTerm2）生效；Windows Terminal / VS Code 集成终端无该设置，会把字形压回原样（详见[圈数字加宽](#圈数字加宽看清里面的数字)）。
- v0.1.4（2026-04-25）：重新加回 `lineHeight` 推荐，但理由换了。v0.1.3 以为"字体 metrics 对齐 1.25 em → 默认行高就够"，实测发现 **VS Code 编辑器 `lineHeight=0` 默认走平台常数**（Win 1.35 × fontSize，Mac 1.5），**完全不读字体 metrics**；终端默认（1.0）才走字体 1.25 em。两边默认值不一致 + 都偏松。fontSize=16 实测甜点：`editor.lineHeight: 22`（px 绝对值）+ `terminal.integrated.lineHeight: 1.1`（= 22px）。README 增加换算公式给非 16 fontSize 用户。
- v0.1.3（2026-04-25）：~~撤回 v0.1.2 的 `lineHeight` 推荐。~~ **被 v0.1.4 部分推翻**——撤回的方向对（v0.1.2 的 1.5/1.3 确实太松），但"用字体自带就行"是错觉，因为 VS Code 编辑器压根不读字体 metrics。
- v0.1.2（2026-04-25）：~~README 推荐 `editor.lineHeight: 1.5` / `terminal.integrated.lineHeight: 1.3`。~~ **已被 v0.1.3 撤回**——当时的"挤"是字体缓存假象，非字体真实 metrics 问题。
- v0.1.1（2026-04-25）：修复终端行距偏窄。`TwemojiAligned` 的 `hhea` / `OS/2 sTypo*` / `OS/2 usWin*` 三套纵向 metrics 改为从 Sarasa Term SC 拷贝（原值约小 11–13%），解决"Aligned 在 fontFamily 链首位时终端拿到偏小行高"。`patch_emoji_only.py` 新增 `--metrics-from <font.ttf>` flag。
- v0.1.0（2026-04-25）：初版。49 emoji + Sarasa Term SC Regular。基于 Twemoji v0.7.0 / Sarasa 1.0.x。
