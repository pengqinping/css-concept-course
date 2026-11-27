# CSS 教程（按知识点）

一份按知识点组织的完整 CSS 教程：**基础篇 → 进阶篇 → 高级篇**，从零基础写到能驾驭底层机制。每个知识点配一张图示（讲复杂逻辑）和一个可交互 demo（动手验证），demo 都可以单独打开。

写作思路只有一条：**每个知识点都从"现象"讲起，落到"为什么会这样"，再用 demo 让你亲手验证**。不背属性表——查属性请用附录 A 的速查表。

## 基础篇 · 写出样式（全部完成）

| 章 | 知识点 | 解决什么问题 |
| --- | --- | --- |
| [01 你写的 CSS 是怎么变成画面的](01-how-css-works.md) | 引入方式 · 规则与 at-rule · 容错解析 · UA 默认样式 · 流水线 | 样式从哪来，到哪去，为什么错字静默失效 |
| [02 选择器：精准选中元素](02-selectors.md) | 属性匹配 · nth 公式 · :is/:where/:has · 伪元素 content · 优先级 · 原生嵌套 | 怎么选中该选的元素 |
| [03 谁说了算：层叠与继承](03-cascade-inheritance.md) | 来源→优先级→顺序 · 动画插队 · @layer · 继承边界 · revert 家族 | 冲突时哪条规则生效 |
| [04 盒子到底占多大](04-box-model.md) | 四层盒 · box-sizing · width:auto · 内容三兄弟 · aspect-ratio · margin 折叠 | width 为什么不是 300px |
| [05 单位：长度以谁为基准](05-units.md) | px/%/em/rem/ch · 视口三兄弟 · calc/min/max/clamp | 每个单位参照谁，怎么跨单位运算 |
| [06 颜色与背景](06-colors-backgrounds.md) | hsl/oklch · color-mix · 背景分层 · 渐变三形状 · 阴影 · outline | 怎么画出想要的效果 |
| [07 文字排版](07-typography.md) | 字体栈 · @font-face 与 font-display · 行高 · white-space 与断行 · 对齐分工 | 文字为什么这样占空间 |
| [08 display 与文档流](08-display-flow.md) | 正常流 · 两轴模型 · 逻辑属性 · inline 空隙坑 · 隐藏三式 | 元素凭什么这样排 |

## 进阶篇 · 搭出布局与动效（全部完成）

| 章 | 知识点 | 解决什么问题 |
| --- | --- | --- |
| [09 position：定位的参照系](09-position.md) | 五个定位值 · 参照系 · inset · sticky 阈值 | 元素怎么"浮"到指定位置 |
| [10 Flexbox](10-flex.md) | 四步分配算法 · flex 简写 · 对齐换行 | 一行空间怎么分，为什么 flex:1 不等宽 |
| [11 Grid](11-grid.md) | 网格线 · 轨道与 fr · areas · auto-fill 配方 | 二维布局怎么画 |
| [12 响应式](12-responsive.md) | viewport meta · 移动优先 · 流式尺寸 · 媒体偏好 | 断点定在哪里 |
| [13 transform 与过渡](13-transform-transition.md) | 坐标系变换 · origin · 可插值属性 · timing | 变形为什么不动布局 |
| [14 动画 animation](14-animation.md) | 关键帧 · 八个子属性 · fill-mode · 层叠席位 | 动画怎么动起来、为什么不跳回 |
| [15 自定义属性与主题](15-custom-properties.md) | 作用域继承 · 失效行为 · @property · 主题切换 | 样式怎么复用与换肤 |
| [16 伪类与伪元素进阶](16-pseudo-elements.md) | 伪元素真盒子 · content 五来源 · counter · 纯 CSS 开关 | 不加元素怎么画装饰 |

## 高级篇 · 理解与驾驭（全部完成）

| 章 | 知识点 | 解决什么问题 |
| --- | --- | --- |
| [17 overflow 与滚动](17-overflow-scroll.md) | 四值语义 · scroll-snap · 滚动穿透治理 | 装不下怎么办、滚动怎么听话 |
| [18 层叠上下文](18-stacking-context.md) | 绘制七层 · 上下文创建清单 · isolation | 谁盖住谁 |
| [19 BFC 与包含块](19-bfc-containing-block.md) | 参照盒四型 · BFC 三大能力 · flow-root | 布局为什么塌、百分比以谁为准 |
| [20 容器查询与现代选择器](20-container-query.md) | @container · cqw · @scope · 选择器矩阵 | 组件自己的断点 |
| [21 渲染与性能](21-rendering-performance.md) | 流水线成本 · 合成层 · will-change · content-visibility | 为什么动画会卡 |
| [22 架构与影响范围](22-architecture.md) | 设计令牌 · @layer · @scope · Shadow DOM | 样式怎么不打架 |
| [23 可访问性与渐进增强](23-accessibility.md) | 焦点可见 · 对比度 · sr-only · @supports | 样式怎么照顾所有人 |
| [24 表单控件与状态](24-forms.md) | appearance · 状态时序 · accent-color · 纯 CSS 开关 | 难看的控件怎么驯服 |
| [25 表格、列表与计数](25-tables-lists.md) | 边框模型 · table-layout · counters() | 表格的视觉由谁决定 |
| [26 现代平台特性](26-modern-platform.md) | 滚动驱动动画 · 视图过渡 · Popover · 锚点定位 | 把每帧计算交给浏览器 |
| [27 打印与分页媒体](27-print.md) | @page · break-* · 打印专属配方 | 无限画布变有限纸张 |
| [28 多列、形状与混合](28-shapes-multicol.md) | 多列 · shape-outside · 混合模式 · filter | 杂志级排版的进阶属性 |

## 怎么学

- 顺读基础篇；有经验的读者可以从 [04 盒模型](04-box-model.md) 直接进入。
- 每章的 demo 都能点击链接单独打开，也内嵌在页面里；改参数 → 看读数 → 对照正文算式。
- 查属性用 [附录 A 速查表](../course/appendix-a-cheatsheet.md)，查坑用 [附录 D 常见问题](../course/appendix-d-pitfalls.md)。
