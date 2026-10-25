# tx-fde · 腾讯云 FDE 培训电子书

把「腾讯云人工智能前沿部署工程师（FDE）」培训课程的 12 章正文、75 节内容、31 张配图整理成的一个**可离线阅读的单页站点**。

- 📖 打开方式：直接双击 `index.html`，或本地起个静态服务器（`python -m http.server`）。
- 🧭 左侧目录跟随滚动高亮，右上角搜索框按章节/小节过滤，`/` 聚焦搜索。
- 🌗 深色模式、阅读进度条、打印样式（每章另起一页）、窄屏抽屉目录。
- 🔤 排版：正文宋体、标题黑体、西文与数字 Times New Roman。

## 内容规模

| 项 | 数量 |
|---|---|
| 章 | 12 |
| 节（正文） | 75 |
| 本章小结 | 12 |
| 表格 | 123 |
| 代码块（含 Prompt 模板 / CLI / YAML / 目录树） | 16 |
| 配图 | 31（29 张内联 SVG，2 张位图） |
| 风险提示 / 提示卡片 | 40 |

## 目录结构

```
index.html          生成的单页（约 540 KB，内含全部正文与矢量图）
01.txt … 12.txt      各章原始文本（从课程页复制整理）
配图/                原始配图（PNG / JPG / SVG）
配图/svg/            由 PNG 重绘的矢量图（19 张）+ 重绘规范 _STYLE.md
_tools/              构建流水线
  parse.py           文本 → 结构化块（标题/表格/列表/代码/图注）
  build.py           块 → HTML（含内联 SVG、目录、章节互链）
  style.css          版式与配色
  app.js             目录高亮、搜索、主题切换、进度条
  lint.py            渲染结果体检（检查残留 Markdown 标记）
  verify.py          文本完整性校验（转换前后逐字比对）
```

## 重新生成

改完 `01.txt … 12.txt` 或样式后：

```bash
python _tools/parse.py   # 生成 _raw/blocks.json
python _tools/build.py   # 生成 index.html
python _tools/lint.py    # 体检：应为 suspect: 0
```

## 说明

课程文字与配图的著作权归**腾讯云**所有，本仓库仅作个人学习与离线阅读整理，请勿用于商业用途。
页面与构建脚本（HTML/CSS/JS/Python）为本仓库作者编写。
