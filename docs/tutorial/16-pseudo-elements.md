# 16 · 伪类与伪元素进阶：不进 HTML 的绘制

> **前置**：[02 · 选择器](02-selectors.md)——知道伪类伪元素分工；[04](04-box-model.md)——盒模型；[08](08-display-flow.md)——两轴模型。
>
> 上一篇：[15](15-custom-properties.md) ｜ 下一篇：[overflow 与滚动](17-overflow-scroll.md) ｜ [教程总览](README.md)

分割线、箭头、编号、遮罩——这些视觉元素都不该进 HTML，也不该进 JS。这一章把"不进 HTML 的绘制"讲成体系：**伪元素是真盒子**（会参与布局！）、**content 的五种来源**、**counter 编号系统**，最后是包括"哪些元素上伪元素根本不生效"在内的经典事故清单。

## 伪元素是真盒子，不是"贴纸"

`::before` / `::after` 生成**货真价实的盒子**：参与盒模型、吃 display、能定位、能动画、能层叠——**还会成为 flex/grid 的子项**（这点是事故高发区，见问题 1）。默认行内盒，要尺寸先换 display：

```css
.divider::after {
  content: "";             /* 没有 content，伪元素整个不渲染 */
  display: block;
  width: 100%; height: 1px;
  background: var(--line);
}
```

## content 的五种来源

| 来源 | 写法 | 用途 |
| --- | --- | --- |
| 字符串 | `content: "→"` | 装饰符号 |
| 引号配对 | `open-quote / close-quote` + `quotes: "「" "」"` | 排版引号 |
| 属性值 | `content: attr(data-tip)` | 轻量 tooltip、打印显示链接地址 |
| 计数器 | `content: counter(step)` | 自动编号 |
| 图片 | `content: url(icon.svg)` | 伪元素塞图 |

`attr()` 的轻量 tooltip 配方：`data-tip` 属性 + `::after { content: attr(data-tip) }` + opacity 过渡——零 JS 的提示层。

## counter：纯 CSS 编号系统

```css
ol.doc { counter-reset: item; }
ol.doc li::before {
  counter-increment: step;            /* 每命中一次 +1 */
  content: counter(step) ". ";
}
ol.doc ol { counter-reset: item; }    /* 每层重置 */
/* 嵌套编号（1.1.1）：content: counters(item, ".") */
```

三步：`counter-reset` 声明 → `counter-increment` 递增 → `counter()/counters()` 展示。`::marker` 只能改颜色字体与 content 的有限部分；**完全自定义编号样式，用 ::before + counter 才是正路**。

## 哪些元素上伪元素根本不生效

一个必须背下的边界：**replaced（替换）元素与 void 元素上，::before/::after 不渲染**——`img`、`video`、`iframe`、`input`、`br` 这些元素没有"内容盒"可以挂伪元素（它们的渲染完全由 src/原生绘制决定）。"给 img 加个角标"的正确姿势：img 外面套一层 span，伪元素挂在 span 上。同理 `::first-letter` / `::first-line` 只对**块容器**生效且只接受部分属性。

## 绘制配方三则

```css
/* ① 三角箭头：透明 border 留一边 */
.tip::after {
  content: ""; display: block;
  border: 6px solid transparent;
  border-top-color: var(--ink);
}

/* ② 悬停遮罩：绝对定位铺满 */
.photo { position: relative; isolation: isolate; }
.photo::after {
  content: ""; position: absolute; inset: 0;
  background: rgb(0 0 0 / .4);
  opacity: 0; transition: opacity .2s; z-index: 1;
}
.photo:hover::after { opacity: 1; }

/* ③ 垫底装饰：负 z-index + 父级圈地 */
.card { position: relative; isolation: isolate; }
.card::before { content: ""; position: absolute; inset: -8px;
                z-index: -1; background: var(--soft); }
```

配方 ② ③ 都涉及层叠：**负 z-index 的伪元素会沉到"所在层叠上下文"的最底层**——父元素没圈地时它可能沉到页面背景之下（第 18 篇），`isolation: isolate` 把沉底范围限定在组件内。

## 常见问题

**问题 1：flex/grid 布局多出一个"看不见的格子"**
- **原因**：`::before/::after` 也会成为 flex/grid 子项——哪怕 content 为空串，它占一个格子，`gap` 里就多出一条缝。
- **修法**：纯布局容器里别用伪元素；或伪元素 `display: none` / `content: none`；或把它 `position: absolute` 移出流。

**问题 2：伪元素根本没出现**
- **原因**排序：忘了 `content`（没有 content = 不渲染）；挂在 replaced 元素上（img/input 等，见上节）；被父元素 `overflow` 裁掉；`display: none` 继承链上。
- **修法**：先补 `content: ""`；再查宿主元素类型与 overflow。

**问题 3：tooltip 被相邻元素盖住**
- **原因**：伪元素与兄弟在同一层叠上下文按 DOM 顺序比拼。
- **修法**：宿主 `position: relative` + 伪元素 `z-index: 1`；或宿主 `isolation: isolate` 抬出局部战场。

**问题 4：伪元素内容屏幕阅读器有时不读**
- **原因**：伪元素内容的可访问性支持各端不一致。
- **修法**：**语义进 HTML、装饰进伪元素**——错误提示、状态文字绝不放 content（第 23 篇原则）。

**问题 5：`::first-letter` 不生效或只改一半样式**
- **原因**：宿主不是块容器（inline 上无效）；或用了不在白名单里的属性（只有字体/颜色/背景/边距等基础属性可用）。
- **修法**：宿主设为 block；首字下沉只调 size/float/color 这些白名单属性。

## 动手验证

[打开实验台：表单伪类状态时序](../../examples/forms/form-states.html)

<iframe class="demo-frame" src="/css-concept-course/examples/forms/form-states.html" title="表单状态实验" loading="lazy"></iframe>

[打开实验台：遮罩、滤镜与伪元素绘制进阶](../../examples/visual/filters-masks-clip.html)

表单实验台观察 `:invalid` 与 `:user-invalid` 的亮灯时机差；绘制实验台里做遮罩与首字下沉，再把一个空 content 伪元素塞进 flex 容器复现问题 1。

## 本章要点

- 伪元素是真盒子且**会成为 flex/grid 子项**——布局容器慎用。
- `content` 缺失 = 不渲染；来源五件套里 `attr()` 是零 JS tooltip 的钥匙。
- replaced/void 元素（img、input…）上伪元素不生效，外面包一层再挂。
- counter 三步 + `counters()` 串联多级编号；`::marker` 只能微调。
- 负 z-index 沉底需要父级 `isolation: isolate` 圈定范围；语义不进 content。

下一篇 [17 · overflow 与滚动](17-overflow-scroll.md)：裁剪、滚动容器与"overflow 管不住 absolute"的真相。
