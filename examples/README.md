# CSS 可运行示例库

这里包含 **30 个独立 HTML 示例**，覆盖从层叠、盒模型到现代平台特性的主要知识路径。示例不依赖构建工具、框架、图片 CDN 或外部字体，直接用浏览器打开即可。

另有 [12 个技术教程最小 demo](minimal/README.md)：一个概念一个文件、1–2 个可调参数、带"先预测再揭晓"，与 [CSS 技术教程](https://pengqinping.github.io/css-concept-course/) 一一对应。本节的多控件实验台适合进阶拆解，最小 demo 适合初次理解。

## 使用方式

1. 从 [示例画廊](index.html) 选择主题。
2. 先预测示例结果，再用页面控件切换状态。
3. 打开浏览器 DevTools 检查 Computed、Layout 和 Animations。
4. 回到 [CSS 学习手记](../docs/README.md) 查找对应原理与练习。

部分现代特性需要较新的 Chrome、Edge、Safari 或 Firefox。页面会尽量提供 `@supports`、API 检测或静态回退；回退状态下仍应保证内容与基本交互可用。

## 覆盖矩阵

| 主题 | 示例 | 对应文档 | 主要演示 |
| --- | --- | --- | --- |
| 基础 | [层叠、层与主题](foundations/cascade-layers-theme.html) | [层叠与继承](../docs/01-foundations/03-cascade-inheritance.md) | `@layer`、`revert-layer`、全局关键字、`light-dark()` |
| 基础 | [盒模型与 margin 折叠](foundations/box-model-margin.html) | [盒模型](../docs/01-foundations/04-box-model.md)、[文档流](../docs/03-layout/08-normal-flow.md) | `box-sizing`、负 margin、`display: flow-root`、`contain: layout` |
| 基础 | [选择器实验台](foundations/selectors-playground.html) | [选择器](../docs/01-foundations/02-selectors.md) | 组合器、结构伪类、`:is()`、`:where()`、`:has()`、`:user-invalid` |
| 基础 | [自定义属性与类型注册](foundations/custom-properties.html) | [层叠与继承](../docs/01-foundations/03-cascade-inheritance.md) | 变量继承、`var()` 回退、`@property`、主题令牌 |
| 视觉 | [排版实验室](visual/typography-lab.html) | [排版与字体](../docs/02-visual/05-typography.md) | 字体度量、`text-wrap`、截断、竖排、逻辑属性 |
| 视觉 | [颜色、混合与主题](visual/color-blend-theme.html) | [颜色、背景与边框](../docs/02-visual/06-color-background-border.md) | OKLCH、`color-mix()`、`currentColor`、混合模式、隔离 |
| 视觉 | [背景、边框与滤镜](visual/background-border-filter.html) | [颜色、背景与边框](../docs/02-visual/06-color-background-border.md) | 多层背景、`background-blend-mode`、`border-image`、`filter` |
| 视觉 | [裁剪、遮罩与阴影](visual/filters-masks-clip.html) | [颜色、背景与边框](../docs/02-visual/06-color-background-border.md) | `clip-path`、`mask-*`、`mask-composite`、两种阴影 |
| 视觉 | [多列与形状环绕](visual/shape-multicol.html) | [补充属性与专题](../docs/07-reference/27-additional-properties.md) | `columns`、`column-span`、`shape-outside`、`shape-margin` |
| 布局 | [定位与层叠上下文](layout/positioning-stacking.html) | [定位与层叠](../docs/03-layout/09-positioning-stacking.md) | 四种定位、`inset`、`z-index`、`isolation`、sticky 阈值 |
| 布局 | [Flexbox 模式](layout/flex-patterns.html) | [Flexbox](../docs/03-layout/10-flexbox.md) | grow/shrink/basis、wrap、gap、对齐、`order`、最小宽度 |
| 布局 | [Grid 模式](layout/grid-patterns.html) | [Grid](../docs/03-layout/11-grid.md) | 命名区域、`minmax()`、span、dense、subgrid |
| 布局 | [滚动吸附轨道](layout/scroll-snap.html) | [现代平台特性](../docs/07-reference/24-modern-features.md) | `scroll-snap-*`、overscroll、滚动条、键盘滚动 |
| 布局 | [布局实验台](layout-playground.html) | [Flexbox](../docs/03-layout/10-flexbox.md)、[Grid](../docs/03-layout/11-grid.md) | Flex/Grid 切换、跨列项目、容器查询 |
| 布局 | [容器查询卡片](container-query-card.html) | [容器查询](../docs/03-layout/12-container-queries.md) | 同一卡片在窄侧栏与宽主栏中的重排 |
| 响应式 | [媒体特性与用户偏好](responsive/media-preference.html) | [响应式设计](../docs/04-responsive/13-responsive-design.md) | hover/pointer、深色、对比度、减弱动态、强制颜色 |
| 响应式 | [流式单位与函数](responsive/fluid-units.html) | [现代单位与函数](../docs/04-responsive/14-units-functions.md) | rem/em、视口单位、`clamp()`、`min()`、`max()`、容器单位 |
| 响应式 | [视口高度与安全区](responsive/safe-area-viewport.html) | [现代单位与函数](../docs/04-responsive/14-units-functions.md) | `svh`/`lvh`/`dvh`、`env()`、刘海屏安全区 |
| 动效 | [变换原点与 3D](motion/transform-origin.html) | [变换](../docs/05-advanced/15-transforms.md) | transform 函数、`transform-origin`、perspective、3D |
| 动效 | [过渡、时间轴与滚动动画](motion/transitions-scroll-timeline.html) | [动画](../docs/05-advanced/16-animation.md) | transition、keyframes、`scroll()`/`view()`、`@starting-style` |
| 动效 | [动效实验台](animation-playground.html) | [过渡与动画](../docs/05-advanced/16-animation.md) | transform 过渡、Grid `0fr → 1fr` 折叠、减弱动态 |
| 表单 | [表单状态实验台](forms/form-states.html) | [表单、表格与原生 UI](../docs/07-reference/23-forms-tables-native-ui.md) | `:checked`、`:indeterminate`、校验状态、`accent-color` |
| 表单 | [原生 UI 组件](forms/native-ui.html) | [表单、表格与原生 UI](../docs/07-reference/23-forms-tables-native-ui.md) | dialog、popover、details、表格、计数器 |
| 现代 | [嵌套、scope 与 :has](modern/scope-nesting-has.html) | [现代平台特性](../docs/07-reference/24-modern-features.md) | nesting、`@scope`、`:has()`、容器样式查询 |
| 现代 | [锚点定位](modern/anchor-positioning.html) | [现代平台特性](../docs/07-reference/24-modern-features.md) | `anchor-name`、`anchor()`、`@position-try`、边缘回退 |
| 现代 | [视图过渡](modern/view-transition.html) | [现代平台特性](../docs/07-reference/24-modern-features.md) | `startViewTransition()`、`view-transition-name`、API 回退 |
| 现代 | [滚动驱动动画](modern/scroll-driven-animation.html) | [现代平台特性](../docs/07-reference/24-modern-features.md) | 阅读进度、进入视口、`animation-range` |
| 工程 | [Web Components 样式边界](engineering/webcomponents.html) | [CSS 架构](../docs/06-engineering/18-architecture.md)、[补充专题](../docs/07-reference/27-additional-properties.md) | `:host`、`::slotted()`、`::part()`、变量穿透 |
| 工程 | [性能容器与长列表](engineering/performance-containment.html) | [性能与调试](../docs/05-advanced/17-performance-debugging.md) | `content-visibility`、`contain-*`、`contain` 副作用 |
| 工程 | [打印与分页布局](engineering/print-layout.html) | [打印与分页媒体](../docs/07-reference/25-print-paged-media.md) | `@page`、分页规则、表头、打印颜色 |

## 学习建议

- **基础类**：先手算尺寸与优先级，再打开示例验证。
- **视觉类**：同时检查普通背景、图片背景和高对比度模式。
- **布局类**：缩窄容器而不只是缩窄窗口，区分视口响应与组件响应。
- **动效类**：分别测试鼠标、键盘、触屏和“减弱动态效果”。
- **工程类**：观察样式边界、性能副作用和打印结果，不只看静态截图。
