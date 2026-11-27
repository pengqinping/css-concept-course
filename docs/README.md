# CSS 教程（按知识点）

一份按知识点组织的完整 CSS 教程：**基础篇 → 进阶篇 → 高级篇**，28 章覆盖从书写样式到底层机制的完整知识地图。每个知识点配一张图示（讲复杂逻辑）与可交互 demo（动手验证），每章带**"常见问题"专节**（现象 → 原因 → 修法）。

## 阅读入口

- **在线站点（GitHub Pages）**：<https://pengqinping.github.io/css-concept-course/>
- **[教程总览与完整目录](tutorial/README.md)** —— 28 章知识点地图，含每章"解决什么问题"。
- **[可交互 demo 索引](https://github.com/pengqinping/css-concept-course/tree/main/examples)** —— 所有 demo 单文件、无框架无构建，可单独打开。

## 三篇结构

| 篇 | 章数 | 读完能做到 |
| --- | --- | --- |
| 基础篇 · 能写对 | 01–08 | 独立完成一个静态页面的样式 |
| 进阶篇 · 能搭稳 | 09–16 | 把设计稿变成可靠的自适应界面 |
| 高级篇 · 能讲清 | 17–28 | 预测任何样式行为，排查任何布局问题 |

## 写作与维护

- 教程正文 `docs/tutorial/`，图示 `docs/tutorial/figures/`；demo 在仓库根目录 `examples/`（`minimal/` 单概念演示 + 分类实验台），新旧章节共用。
- Markdown 是唯一源文件；图与 demo 都用标准 Markdown 语法引用，GitHub 仓库页与站点都能正确显示。
- 本地预览：`npm install && npm run docs:dev`；构建：`npm run docs:build`。
- 推送到 `main` 后，GitHub Actions 自动构建并发布 Pages。
