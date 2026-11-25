# CSS 技术教程

一份按依赖顺序组织的 CSS 教程：**30 篇正文 + 5 份附录**，每篇配一张概念图、一个可交互 demo 和带验收标准的练习。

## 阅读入口

- **在线站点（GitHub Pages）**：<https://pengqinping.github.io/css-concept-course/>
- **[课程总览与完整目录](course/README.md)** —— 30 篇正文按三阶段组织：能预测、能构建、能维护。
- **[写作规范](course/STYLE.md)** —— 六段结构、图示与 demo 的要求。
- **[最小 demo 索引](https://github.com/pengqinping/css-concept-course/tree/main/examples/minimal)** —— 30 个单概念演示，可单独打开。

## 六大主题

| 部分 | 篇数 | 解决什么 |
| --- | --- | --- |
| 核心机制 | 01–08 | 规则如何变成像素、选择器、层叠、继承、盒模型、包含块、BFC、层叠上下文 |
| 视觉表现 | 09–14 | 排版、颜色、背景边框、display/overflow、transform、动画 |
| 布局 | 15–19 | Flex、Grid、容器查询、单位、响应式 |
| 内容与组件 | 20–22 | 表单、表格与计数、原生弹层 |
| 工程与平台 | 23–28 | 架构令牌、无障碍兼容、渲染性能、嵌套/@scope/:has、锚点滚动视图过渡、打印 |
| 专题补充 | 29–30 | 多列形状混合、交互状态与组件边界 |

附录 A–E 分别是属性速查表、布局配方、练习、常见问题速查和术语表。

## 写作与维护

- Markdown 是唯一源文件；图示在 `docs/course/figures/`，demo 在仓库根目录 `examples/minimal/`。
- 图与 demo 都用标准 Markdown 语法引用，GitHub 仓库页与站点都能正确显示。
- 本地预览：`npm install && npm run docs:dev`；构建：`npm run docs:build`。
- 推送到 `main` 后，GitHub Actions 会自动构建并发布 Pages。
