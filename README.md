# Sarasa Term SC + Twemoji (Aligned)

CJK monospace + 彩色 emoji 严格等宽对齐字体。

> **问题**：VS Code 等 advance-width 渲染器里，emoji 回退到系统字体（Segoe UI Emoji 等），advance width 不严格 = 2× ASCII → 含 emoji 的行视觉偏列；表格、对齐注释等场景错位。
> **解法**：把 Twemoji 改造为 advance=1000、UPM=1000，与 Sarasa Term SC 的 CJK 严格等宽。

## 产物

| 文件 | 大小 | 用途 |
|------|------|------|
| `TwemojiAligned-Regular.ttf` | 18 KB | 仅 49 个常用 emoji，advance=1000，配 Sarasa Term SC 用 |
| `SarasaTermSCEmoji.ttc` | 24 MB | TTC 合集：Sarasa Term SC + Twemoji Aligned，单文件分发 |

49 个常用 emoji 范围：状态/标记（✅❌⭐⚠❓❗）+ 表情（👍👎😊🤔）+ 进度（⬆⬇⬅➡↩）+ 工具（🚀🔧📌🔒🔍）+ 心情（❤🔥✨）。完整列表见 [build/COMMON_EMOJI_CODEPOINTS](https://github.com/JoeZhangYN/claude-workbench/blob/main/tools/font-patcher/patch.py)。

## 安装

### 方案 A — 标准做法（推荐）

1. 双击 `TwemojiAligned-Regular.ttf` → Install for All Users
2. 装 [Sarasa Term SC](https://github.com/be5invis/Sarasa-Gothic/releases)（如未装）
3. VS Code `settings.json`：
   ```json
   "editor.fontFamily": "'Twemoji Aligned', 'Sarasa Term SC', 'Cascadia Code', monospace",
   "editor.unicodeHighlight.ambiguousCharacters": false,
   "editor.fontLigatures": false
   ```
4. **完全 Exit + 重开** VS Code（Reload Window 不刷新字体缓存）

### 方案 B — 单文件 TTC

1. 卸载已装的 `Sarasa Term SC` 系列字体（如有）
2. 双击 `SarasaTermSCEmoji.ttc` → Install for All Users
3. settings.json 同 A
4. 完全 Exit + 重开 VS Code

## 重建 / 自定义

字体由开源工具链生成：[claude-workbench/tools/font-patcher](https://github.com/JoeZhangYN/claude-workbench/tree/main/tools/font-patcher)

工具链支持：
- 换 emoji 源（Twemoji / Noto Color Emoji / 本机 Segoe UI Emoji）
- 调整 emoji 白名单（默认 49 个，可加更多但需控制 ≤300 避开 64K glyph 上限）
- 多权重（Regular / Bold / Italic）— 第一版只 Regular

## 许可证

| 来源 | 协议 | 文件 |
|------|------|------|
| Sarasa Gothic / Term SC | SIL OFL-1.1 | [LICENSE-OFL-1.1.txt](LICENSE-OFL-1.1.txt) |
| Twemoji emoji glyphs | CC-BY 4.0 | [LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt) |

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
- 修改 + 再分发（需保留同样的 License + 归属）

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| emoji 仍是 Windows 默认彩色 | VS Code 没有完全重启 | File → Exit（不是 Reload Window） |
| emoji 显示空白方框 | Sarasa Term SC 没装 | 装 Sarasa Term SC |
| 中文字体变了 | settings.json fontFamily 顺序 | 检查 'Sarasa Term SC' 在 fallback 链中 |
| 表格仍未对齐 | 老 emoji 字体优先级高 | DevTools (Ctrl+Shift+I) 看 computed font 是否真用了 Twemoji Aligned |

## Changelog

- v0.1.0（2026-04-25）：初版。49 emoji + Sarasa Term SC Regular。基于 Twemoji v0.7.0 / Sarasa 1.0.x。
