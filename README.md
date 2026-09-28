# Quizify VSCode Workspace Template

在 VSCode 中编写 Anki Quizify Markdown 题库的工作区模板。

## 功能特性

- 保存自动格式化：保存 `.md` 文件时自动运行 `scripts/format.py`，整理 `;;; ... ;;;` 选择题块。
- Quizify 语法高亮：通过 Highlight 扩展高亮 `{{填空}}`、`;;;选择;;;`、`[[揭示||答案]]`、`[批注]^(解释)^`、`:::`、`===`、`$$公式$$` 等语法。
- 全角/半角兼容：脚本支持全角 `；`、`Ａ`、`．` 与半角 `;`、`A`、`.` 混用。
- 选项自动分行：把挤在一行的 `A. xxx B. xxx` 拆成每项独占一行。
- 自动补分隔符：`+++` 卡片内缺少 `***` 时自动补上，避免 Quizify 导入报错。
- 空行稳定：重复保存不会累积空行，输出保持一致。
- 固定水平线样式：通过 markdownlint 的 `MD035` 规则，避免 `***` 被自动替换为 `---`。

## 目录结构

```
.
├── .vscode/
│   ├── settings.json      # 工作区配置
│   └── extensions.json    # 推荐扩展
├── scripts/
│   └── format.py          # 题库格式化脚本
├── quizify-template.md    # 题库示例 / 模板
└── README.md
```

## 环境要求

- VSCode
- Python 3（脚本仅使用标准库，无需额外安装依赖）
- Anki + Quizify 插件（用于导入题库）

## 推荐扩展

| 扩展 | ID | 用途 |
| --- | --- | --- |
| Run On Save | `emeraldwalk.RunOnSave` | 保存时自动运行格式化脚本 |
| markdownlint | `DavidAnson.vscode-markdownlint` | 固定 `MD035` 为 `***` |
| Highlight | `fabiospampinato.vscode-highlight` | Quizify 语法高亮 |

命令行安装：

```bash
code --install-extension emeraldwalk.RunOnSave
code --install-extension DavidAnson.vscode-markdownlint
code --install-extension fabiospampinato.vscode-highlight
```

> [!WARNING]
>
> ### 与 Prettier 的冲突
>
> Prettier 会把 Markdown 中的 `***` 自动改写为 `---`，这会破坏 Quizify 的卡片正反面分隔符，导致导入报错。

## 使用方式

1. 克隆仓库：

   ```bash
   git clone https://github.com/PfolgCodeDump/anki-quizify-workspace-template.git
   cd anki-quizify-workspace-template
   ```

2. 用 VSCode 打开工作区：

   ```bash
   code .
   ```

3. 安装上面的推荐扩展。

4. 打开任意 `.md` 题库文件，按 Quizify 语法编写题目。

5. 保存文件时，Run On Save 会自动执行：

   ```bash
   py scripts/format.py <当前文件>
   ```

6. 在 Anki 中使用 Quizify 插件导入 Markdown 题库。

## 脚本行为

`scripts/format.py` 在每次保存时执行，只处理 `;;;` 到 `;;;答案` 之间的内容，块外内容原样保留。

具体逻辑：

- 全角 `Ａ` `Ｂ` `Ｃ` `Ｄ` 转半角 `A` `B` `C` `D`。
- 全角 `．` `、`（紧跟选项字母时）转半角 `.`。
- 行内被空白隔开的多个选项拆成每项独占一行。
- 答案行字母全角转半角，输出统一为半角 `;;;X`。
- 空块（`;;;` 后直接空行或另一个 `;;;`）会被跳过。
- 每张 `+++` 卡片内若无 `***`，在内容末尾自动补一个。
- 空行只在块结束时补一个，重复运行不会累加。

运行示例：

```markdown
;;;
A.凝结核，不利于相变过程发生
B.催化剂，不利于水汽凝结
C.凝结核，有利于相变过程发生
D.催化剂，有利于水汽凝结
;;;C

```

转换为：

```markdown
;;;
A. 凝结核，不利于相变过程发生
B. 催化剂，不利于水汽凝结
C. 凝结核，有利于相变过程发生
D. 催化剂，有利于水汽凝结
;;;C

```

## 配置说明

`.vscode/settings.json` 中的关键配置：

```json
{
  "emeraldwalk.runonsave": {
    "commands": [
      {
        "match": "\\.md$",
        "cmd": "py scripts/format.py ${file}",
        "isAsync": true
      }
    ]
  }
}
```

- `match`：只对 `.md` 文件生效。
- `cmd`：保存时执行的命令。Windows 使用 `py`，macOS/Linux 可能需要改成 `python3`。
- `isAsync`：异步执行，避免阻塞编辑器。

其他配置：

- `markdownlint.config.MD035.style = "***"`：固定水平线为 `***`。
- `[markdown].editor.formatOnSave = false`：关闭 Markdown 保存时格式化，避免与脚本冲突。
- `highlight.regexes`：定义 Quizify 语法的高亮规则。

## 题库语法速查

| 语法 | 示例 |
| --- | --- |
| 填空 | `HTTP 默认端口是 {{80}}。` |
| 单选 | `;;; ... ;;;C` |
| 多选 | `;;; ... ;;;ABD` |
| 点击揭示 | `[[题干\|\|答案]]` |
| 批注 | `[术语]^(解释)^` |
| 折叠块 | `::: 标题 ... :::` |
| 标签页 | `=== 标题 === ... ===` |
| 音频 | `!audio[标题](文件.mp3)` |
| 随机遮罩 | `:::: recite ... ::::` |
| 高亮 | `==重点==` |
| 上标/下标 | `E = mc^2^`、`H~2~O` |
| 提示框 | `> [!WARNING]` |
| 代码块 | ` ```python ... ``` ` |
| 数学公式 | `$E = mc^2$`、`$$...$$` |

## 许可证

本项目采用 GNU General Public License v3.0（GPL-3.0）。完整许可证文本请参见：

<https://www.gnu.org/licenses/gpl-3.0.txt>

## 致谢

- Anki Quizify：<https://github.com/e-chehil/anki-quizify>
- VSCode Highlight：<https://github.com/fabiospampinato/vscode-highlight>
- Run On Save：<https://github.com/emeraldwalk/vscode-runonsave>
