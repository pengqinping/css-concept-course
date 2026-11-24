# CSS 学习手记

一套从零基础到工程实践的 CSS Markdown 知识库。目标不是罗列属性，而是建立可解释、可预测、可维护的样式心智模型。

> **现在有新的学习主线：[CSS 概念课](course/README.md)。** 12 篇短教程，每篇一张概念图 + 一个最小 demo，按"现象 → 直觉 → 机制 → 验证"推进；交互式版本在 [course-site/index.html](../course-site/index.html)。下面这套 27 篇手记保留为**参考区**：按需查属性、查配方、查兼容性，不再作为顺序学习路径。
>
> 两套材料的关系：概念课负责"理解"，学习手记负责"查阅"。概念课里遇到"这个属性还有哪些取值"，再跳到参考区。

## 参考区学习路线（按需查阅，不必顺序阅读）

| 阶段 | 文档 | 你将掌握 |
| --- | --- | --- |
| 基础 | [CSS 是如何工作的](01-foundations/01-how-css-works.md) | 样式来源、加载过程、规则结构与调试入口 |
| 基础 | [选择器与伪类](01-foundations/02-selectors.md) | 精准选中元素，表达交互与结构关系 |
| 基础 | [层叠、继承与 CSS 变量](01-foundations/03-cascade-inheritance.md) | 预测最终样式，管理覆盖关系与主题 |
| 基础 | [盒模型与尺寸](01-foundations/04-box-model.md) | content/padding/border/margin、box-sizing、百分比 |
| 视觉 | [排版与字体](02-visual/05-typography.md) | 字体栈、字号行高、文本溢出、文字排版 |
| 视觉 | [颜色、背景与边框](02-visual/06-color-background-border.md) | 颜色空间、渐变、阴影、边框与裁剪 |
| 视觉 | [视觉格式与溢出](02-visual/07-formatting-overflow.md) | display、visibility、opacity、overflow、层叠上下文 |
| 布局 | [文档流与格式化上下文](03-layout/08-normal-flow.md) | BFC、块级/行内布局、margin 折叠 |
| 布局 | [定位与层叠](03-layout/09-positioning-stacking.md) | relative/absolute/fixed/sticky、z-index |
| 布局 | [Flexbox 弹性布局](03-layout/10-flexbox.md) | 主轴、交叉轴、伸缩、对齐、实战模式 |
| 布局 | [Grid 网格布局](03-layout/11-grid.md) | 轨道、网格线、区域、自动布局、子网格 |
| 布局 | [容器查询与自适应布局](03-layout/12-container-queries.md) | 组件级响应式、内在尺寸、断点策略 |
| 响应式 | [响应式设计](04-responsive/13-responsive-design.md) | 移动优先、媒体查询、流式排版、媒体资源 |
| 响应式 | [现代 CSS 单位与函数](04-responsive/14-units-functions.md) | rem/em、vw/vh、clamp/min/max、calc |
| 进阶 | [变换与视觉状态](05-advanced/15-transforms.md) | translate/rotate/scale、3D 变换、变换原点 |
| 进阶 | [过渡与动画](05-advanced/16-animation.md) | transition、@keyframes、滚动驱动动画 |
| 进阶 | [渲染性能与调试](05-advanced/17-performance-debugging.md) | 重排重绘、合成、DevTools、样式排查 |
| 工程 | [CSS 架构与工程化](06-engineering/18-architecture.md) | 命名、变量、@layer、预处理器与 CSS Modules |
| 工程 | [兼容性、无障碍与测试](06-engineering/19-compatibility-accessibility.md) | 渐进增强、浏览器支持、键盘与减弱动画 |
| 参考 | [属性速查表](07-reference/20-cheatsheet.md) | 高频属性、布局决策与最小初始化 |
| 参考 | [常见布局方案](07-reference/21-recipes.md) | 居中、导航、侧边栏、卡片、弹层等可复制方案 |
| 参考 | [练习与参考答案](07-reference/22-exercises.md) | 分层练习、验收标准与参考实现 |
| 参考 | [表单、表格与原生 UI](07-reference/23-forms-tables-native-ui.md) | 表单控件、表格、列表计数、dialog 与 popover |
| 参考 | [现代 CSS 平台特性](07-reference/24-modern-features.md) | 原生嵌套、锚点定位、滚动驱动、视图过渡与 Houdini |
| 参考 | [打印与分页媒体](07-reference/25-print-paged-media.md) | A4、分页、跨页表格、链接与黑白打印 |
| 参考 | [常见问题速查](07-reference/26-common-pitfalls.md) | 按症状定位样式、尺寸、层叠、响应式与动画问题 |
| 参考 | [补充属性与专题](07-reference/27-additional-properties.md) | 多列、形状环绕、混合模式、交互属性、表单状态与 Shadow DOM |

## 建议学习方式

1. **先预测，再运行。** 阅读示例前先判断尺寸、位置或覆盖结果。
2. **每篇只解决一类问题。** 理解文档流、包含块、格式化上下文等概念，比背属性更重要。
3. **边读边改。** 示例都可保存为 `.html` 文件直接打开；完整示例见 [examples](../examples)。
4. **建立自己的速查表。** 在 [属性速查表](07-reference/20-cheatsheet.md) 中补充实际项目中遇到的细节。

## 可运行示例

遇到不熟悉的术语，可先查 [CSS 术语表](GLOSSARY.md)。

示例库现有 **30 个独立 HTML Demo**，不依赖构建工具、框架或外部资源，直接用浏览器打开即可：

- [打开示例画廊](../examples/index.html)：按基础、视觉、布局、响应式、动效、表单、现代特性和工程分组浏览。
- [查看示例覆盖矩阵](../examples/README.md)：每个 Demo 对应的章节、属性组合与学习目标。
- 重点入口：[层叠与主题](../examples/foundations/cascade-layers-theme.html)、[多列与形状环绕](../examples/visual/shape-multicol.html)、[定位与层叠](../examples/layout/positioning-stacking.html)、[表单状态](../examples/forms/form-states.html)、[滚动驱动动画](../examples/modern/scroll-driven-animation.html)、[Web Components 样式边界](../examples/engineering/webcomponents.html)。

## 文档约定

- 尺寸默认按 CSS 像素理解。
- 示例优先使用现代浏览器已普遍支持的 CSS；兼容性差异会单独说明。
- 图中文字方块代表元素或内容，箭头代表尺寸、空间分配或状态变化。
- `!important`、全局标签选择器、过深选择器只在需要解释原理时使用。

## 覆盖清单

- [x] 工作原理、选择器、优先级、层叠、继承、变量与 `@property`
- [x] 盒模型、包含块、百分比、margin 折叠、逻辑尺寸
- [x] 字体、排版、颜色、渐变、背景、边框、阴影、遮罩、混合模式
- [x] 普通流、BFC、多列、形状环绕、定位、层叠上下文、Flex、Grid、subgrid
- [x] 媒体查询、容器查询、视口单位、流式排版、响应式媒体
- [x] transform、2D/3D、过渡、关键帧、滚动驱动、减弱动画
- [x] 重排重绘、合成、布局抖动、CLS、DevTools 调试
- [x] 命名、设计令牌、`@layer`、预处理器、CSS Modules、兼容与无障碍
- [x] 表单状态、表格、列表计数、dialog、popover、打印分页
- [x] 原生嵌套、`@scope`、锚点定位、视图过渡、Houdini、Shadow DOM 与常见问题速查

## 覆盖边界

这套手记覆盖 CSS 的主要知识路径和高频工程问题，但不是浏览器全部属性的逐项字典。`image-set()`、`border-image`、彩色字体、`touch-action` 等零散属性集中在[补充属性与专题](07-reference/27-additional-properties.md)，并与对应 Demo 一起学习；实际项目仍应以 [MDN](https://developer.mozilla.org/zh-CN/docs/Web/CSS)、浏览器兼容性数据和目标用户环境为准。

## 最重要的四条原则

> 1. CSS 的难点通常是布局上下文，而不是属性名。  
> 2. 先让内容自然流动，再只干预真正需要控制的部分。  
> 3. 用变量表达设计决策，用组件边界控制影响范围。  
> 4. 可访问性和性能不是收尾工作，而是样式设计的一部分。
