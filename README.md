# Sarasa Term SC + Twemoji (Aligned)

CJK monospace + 彩色 emoji 严格等宽对齐字体——VS Code / 终端表格不再因 emoji 错位。

> **问题**：advance-width 渲染器（VS Code 等）里，emoji 回退到 Segoe UI Emoji 等系统字体，advance ≠ 2× ASCII → 含 emoji 的行视觉偏列；表格、对齐注释场景错位。
> **解法**：把 Twemoji 改造为 advance=1000、UPM=1000，与 Sarasa Term SC 的 CJK 严格等宽。

## 产物（直接安装）

| 文件 | 大小 | 用途 |
|------|------|------|
| `TwemojiAligned-Regular.ttf` | 18 KB | 49 个常用 emoji，advance=1000，配 Sarasa Term SC 用 |
| `SarasaTermSCEmoji.ttc` | 24 MB | TTC 合集：Sarasa Term SC + Twemoji Aligned 单文件 |

49 个 emoji 范围（完整列表见 [`patch.py`](patch.py) 的 `COMMON_EMOJI_CODEPOINTS`）：
- 状态/标记：✅ ❌ ❎ ⭐ ✓ ✗ ✔ ✘
- 警示：⚠ ⛔ 🚫 ❗ ❓ ❕ ❔
- 表情：👍 👎 👏 🔥 ✨ 🎉 💡 🤔 😊 😂 😢
- 方向/进度：⬅ ⬆ ⬇ ➡ ↩ ↪ 🔄
- 工具：🚀 🔧 🔨 📌 📎 📝 📖 📚 📅 🕑 ⏰ ⌛ 🔒 🔓 🔑 🔍
- 心情：❤ 💔 💯

## 安装

### 方案 A — 标准做法（推荐）

1. 装 [Sarasa Term SC](https://github.com/be5invis/Sarasa-Gothic/releases)（如未装）
2. 双击 `TwemojiAligned-Regular.ttf` → Install for All Users
3. VS Code `settings.json`：
   ```json
   "editor.fontFamily": "'Twemoji Aligned', 'Sarasa Term SC', 'Cascadia Code', monospace",
   "editor.unicodeHighlight.ambiguousCharacters": false,
   "editor.fontLigatures": false
   ```
4. **完全 Exit + 重开** VS Code（Reload Window 不刷新字体缓存）

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
2. [`download.py`](download.py) 拉 Twemoji-Mozilla v0.7.0
3. [`patch_emoji_only.py`](patch_emoji_only.py) 子集化 + UPM 缩放 + advance 强制 1000
4. [`build_ttc.py`](build_ttc.py) 把 Sarasa + 改造后 Twemoji 装 .ttc

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

## Changelog

- v0.1.1（2026-04-25）：修复终端行距偏窄。`TwemojiAligned` 的 `hhea` / `OS/2 sTypo*` / `OS/2 usWin*` 三套纵向 metrics 改为从 Sarasa Term SC 拷贝（原值约小 11–13%），解决"Aligned 在 fontFamily 链首位时终端拿到偏小行高"。`patch_emoji_only.py` 新增 `--metrics-from <font.ttf>` flag。
- v0.1.0（2026-04-25）：初版。49 emoji + Sarasa Term SC Regular。基于 Twemoji v0.7.0 / Sarasa 1.0.x。
