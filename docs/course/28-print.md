# 28 · 屏幕上的长页，怎么落到有限的纸上

> 一句话模型：屏幕是一块可无限向下滚动的画布，打印是一叠尺寸固定的纸；`@media print` 决定"画什么"，`@page` 决定"每张纸多大、页边放什么"，而分页点只能请求、不能保证。

## 先看一个现象

一份长报告页：深色背景、固定在顶部的导航、鼠标悬停才显示的工具提示、一张带图注的插图。你在屏幕上滚动顺畅，点打印，预览里却变成这样：深色背景没印出来（或印出一整版墨），导航条占着正文空间，悬停提示消失，图注被切成上下两半分在两页，标题孤零零落在上一页底。

```css
body { background: #14231b; color: #f4f1e9; }
.nav { position: sticky; top: 0; }
.tip { display: none; }
.card:hover .tip { display: block; }
```

你以为打印只是"把屏幕缩小到 A4"；实际是排版引擎换了一套规则：画布从连续变成离散的页，交互状态不复存在，颜色由用户和设备共同决定。你写的 CSS 仍在，但一部分东西失去了成立的前提。

## 先建立直觉

![一张纸的剖面：页边距盒与页面区](figures/28-print.svg)

*图 28-1 · 一张纸的剖面：页边距盒与页面区*

图说明：从外到内三层——最外是纸张（A4，210mm × 297mm），中间一圈是页边距，最内是页面区。页边距被划成 16 个槽位，上中放页码、右下放章节名等，正文只进入页面区。图上标两条边界：`@page` 管外圈——`size` 定纸张、`margin` 定页边、槽位用 `content: counter(page)` 填；`@media print` 管进入页面区的内容。还有一条虚线穿过页面区：正文流被切成一页一页，切点由分页算法决定，CSS 只能递建议。

图要记住的一句话：**纸张的物理边界不属于正文流**。页边距盒里放的是页码和页眉页脚，它们不参与正文排版；正文只能在页面区里被切分。

## 机制拆成四步

### 1. @media print 与 @page 管的是两个对象

`@media print` 是一条媒体查询：当输出目标是打印或打印预览时，它内部的规则才参与层叠。它管的是元素——隐藏导航、展平阴影、把链接地址显示出来。

```css
@media print {
  .nav, .toolbar { display: none; }
  a[href^="http"]::after { content: " (" attr(href) ")"; }
  body { color: #000; background: #fff; }
}
```

`@page` 不是选择器，它无法选中任何 DOM 元素。它描述的是页面盒：纸张尺寸、页边距，以及页边距盒里放什么。

```css
@page {
  size: A4;
  margin: 18mm 16mm;
}
```

**为什么必须分开？** "哪些内容出现"是内容问题，交给能命中元素的 `@media print`；"每张纸多大"是输出设备和页面盒问题，页面盒没有 DOM 对应物，只能由 `@page` 表达。把 `size` 写进 `.page` 类不会改变打印纸张；想让打印规则与屏幕规则分开维护，就把 `@page` 嵌进 `@media print`。

### 2. 页边距盒与 @page :first

页边距不是空白，它被切成 16 个槽位：上下左右各有角、中、边三类位置。槽位用 `content` 填，页码由页面计数器提供：

```css
@page {
  margin: 18mm 16mm;
  @bottom-center { content: counter(page) " / " counter(pages); }
}
@page :first {
  margin-top: 24mm;                  /* 首页留出标题空间 */
  @bottom-center { content: none; }  /* 首页不显示页码 */
}
```

`:first` 只命中第一页；同一组里还有 `:left`、`:right`、`:blank`。**为什么首页要单独写？** 封面或报告首页的排版需求和正文页不同——更大的上边距、没有页码——但 `@page` 默认作用于所有页，只有伪类能把它收窄到某一类页。

这里的 `content` 是页边距盒的排版指令，不是给普通元素生成文字；`counter(page)`、`counter(pages)` 也是页上下文里的计数器。另外，浏览器打印对话框里的纸张、缩放、页眉页脚选项仍可能覆盖这些设定——CSS 不能独占最终输出。

### 3. 分页只能请求，不能保证

正文进入页面区后被切成多页。你可以在切点附近递建议：

```css
h2, h3 { break-after: avoid; }           /* 标题别留在页底 */
figure, pre, tr { break-inside: avoid; } /* 整块别被切开 */
.chapter { break-before: page; }         /* 从这里另起一页 */
p { orphans: 3; widows: 3; }             /* 页底/页顶至少保留的行数 */
```

**为什么是"建议"？** 分页发生在布局之后，引擎要在有限高度里放下连续的盒。如果一张图比整页还高，`break-inside: avoid` 根本无法满足，引擎仍会切开它；如果两个建议冲突，规范定义了取舍规则（例如强制分页压过 `avoid`），而不是两个都照办。你能做的是降低无意义切断的概率，不是钉死每一页。

`orphans` 和 `widows` 是同类请求：分别规定页底、页顶至少保留几行文字，避免只剩一行的段落。它们初始值是 2，写成 3 是更严格的要求，同样可能被空间挤掉。

### 4. 跨页后仍要读得懂：表头与颜色

长表格跨页时，重复表头靠的是显示角色，而不是复制一份 DOM：

```css
@media print {
  thead { display: table-header-group; } /* 每页顶部重复 */
  tfoot { display: table-footer-group; }
  tr { break-inside: avoid; }            /* 行不被拆开 */
}
```

**为什么这样就能重复？** 浏览器把 `table-header-group` 识别为"表头组"，分页时会在每一页的表格顶部重画它。所以别把 `thead` 改成 `display: block` 或 `none`，那会同时取消重复能力。多数浏览器默认就是这个值，显式写出是为了不被别的规则覆盖。

颜色是另一类取舍：

```css
@media print {
  * { print-color-adjust: exact; }
}
```

`print-color-adjust: economy`（初始）允许引擎为省墨丢掉背景；`exact` 是"尽量保留"的请求，用户仍可在打印对话框里关掉背景图形。**为什么关键状态不能只靠颜色？** 黑白打印或用户关掉背景后，绿色"通过"和红色"失败"可能变成同一个灰。状态要同时有文字或符号，背景色只做加强——`exact` 不能替你保证这一点。

## 动手验证

[打开 demo：段落数与 break-inside，看断点落在哪里](../../examples/minimal/28-print.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/28-print.html" title="段落数与 break-inside，看断点落在哪里" loading="lazy"></iframe>

> **先预测**：模拟页面区高 480px，每段 40px，图块 160px。段落从 12 段增到 13 段时，页数会变吗？打开「图块不可拆分」后，图块还会被切在页边界吗？先写下答案。
>
> **验证**：打开 demo 调节参数，用页面显示的实时读数核对你的预测。

验证：拖动段落滑块（4–20），切换 `break-inside: avoid` 开关，状态文本显示当前段数、页面区高度、预计页数与图块是否被拆。demo 用固定高度容器模拟分页，真实分页仍要在打印预览里核对。

## 容易误判的地方

- **"`@page` 里能选中元素设置样式"** → 它描述页面盒，不是选择器；元素样式写在 `@media print` 里，页面尺寸与页边距写在 `@page` 里。
- **"`break-inside: avoid` 保证不拆开"** → 元素高于一页时照样拆；它是降低切断概率的请求，不是硬约束。
- **"`print-color-adjust: exact` 保证背景被打印"** → 用户仍可关闭背景图形；黑白打印下只能用文字和符号承载关键状态。

## 自己再做一次

1. 给一份带导航、深色背景和悬停提示的报告写 `@media print`：隐藏导航、白底黑字、展开外部链接地址。**预期结果：预览里看不到导航与深色背景；每个 http 链接后多出 ` (地址)`，页内锚点不追加。**
2. 写一个跨 3 页的表格，设置 `thead { display: table-header-group }` 与 `tr { break-inside: avoid }`。**预期结果：每一页的表格顶部都重复表头；没有任何一行被页边界切成上下两半。**
3. 用 `@page { size: A4; margin: 18mm 16mm; @bottom-center { content: counter(page) } }` 加 `@page :first { @bottom-center { content: none } }`。**预期结果：第二页起底部居中显示页码，首页底部没有页码；把 `size` 改成 `letter` 后打印对话框的纸张随之变化（若未被用户选项覆盖）。**

> 下一篇：[多列、形状与混合](29-shapes-mix.md)
