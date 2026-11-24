# 22 · 练习与参考答案

> 练习按难度递进。先独立完成并记录预测结果，再查看答案；答案只是可行实现之一，不是唯一模板。

## 第一阶段：基础与盒模型

### 练习 1：计算实际尺寸

一个元素设置 `width: 300px`、`padding: 20px`、`border: 5px`、`margin: 10px`。

**问题：** content-box 与 border-box 下，元素实际宽度和外部占位宽度分别是多少？

<details>
<summary>查看答案</summary>

- content-box：实际宽度 `300 + 40 + 10 = 350px`；外部占位 `350 + 20 = 370px`。
- border-box：实际宽度 `300px`；内容宽度 `300 - 40 - 10 = 250px`；外部占位 `320px`。

</details>

### 练习 2：阻止 margin 折叠

父子元素中子元素有 `margin-top: 2rem`，导致父元素位置意外。

**要求：** 不用 `!important`，给出两种修复方式。

<details>
<summary>查看答案</summary>

```css
.parent-a { padding-block-start: 1px; }
.parent-b { display: flow-root; }
```

也可给父元素添加 border、改用 Flex/Grid 布局。优先 `flow-root`，语义最明确。

</details>

### 练习 3：层叠判断

```css
p { color: red; }
.card p { color: blue; }
#intro { color: green; }
```

元素为 `<p id="intro" class="card">`，最终颜色是什么？再添加 `p { color: purple !important; }` 呢？

<details>
<summary>查看答案</summary>

初始为绿色，因为 ID 优先级最高。添加 important 后为紫色，重要性优先于普通声明的优先级。

</details>

## 第二阶段：视觉与溢出

### 练习 4：响应式标题

**要求：** 标题最小 1.5rem、最大 3rem，中间值随 4vw 增长，并保持良好换行。

<details>
<summary>查看答案</summary>

```css
.title {
  font-size: clamp(1.5rem, 4vw, 3rem);
  line-height: 1.15;
  text-wrap: balance;
}
```

</details>

### 练习 5：修复长 URL

Flex 子项中的长 URL 把页面撑出横向滚动条。

<details>
<summary>查看答案</summary>

```css
.flex-item {
  min-width: 0;
  overflow-wrap: anywhere;
}
```

若 URL 必须单行显示，使用 `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`。

</details>

### 练习 6：单行与三行省略

分别实现文件名单行省略、摘要三行省略。

<details>
<summary>查看答案</summary>

```css
.filename {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.summary {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  overflow: hidden;
}
```

需要受约束宽度；Flex/Grid 子项通常还要 `min-width: 0`。

</details>

## 第三阶段：Flex 布局

### 练习 7：两端工具栏

左侧标题，右侧一组按钮；窄屏时按钮组换行。

<details>
<summary>查看答案</summary>

```css
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.actions { display: flex; gap: 0.5rem; }
```

若需要按钮组始终贴右，可加 `margin-inline-start: auto`。

</details>

### 练习 8：2:1 主侧布局

主栏与侧栏比例为 2:1，侧栏不能被内容压缩到不可读。

<details>
<summary>查看答案</summary>

```css
.panes { display: flex; gap: 1rem; }
.main { flex: 2 1 0; min-width: 0; }
.sidebar { flex: 1 1 16rem; }
```

如果比例必须严格为 2:1，两侧都用 `flex: 2 1 0` 与 `flex: 1 1 0`；需要最小可读宽度时 Grid 的 `minmax()` 更直观。

</details>

### 练习 9：垂直步骤条

圆点与文字顶部对齐，连接线填满两项之间剩余空间。

<details>
<summary>查看答案</summary>

```css
.steps { display: flex; flex-direction: column; }
.step {
  display: grid;
  grid-template-columns: 1.5rem minmax(0, 1fr);
  gap: 0.75rem;
  padding-block-end: 1.5rem;
  position: relative;
}
.step:not(:last-child)::after {
  content: "";
  position: absolute;
  inset-inline-start: 0.65rem;
  inset-block-start: 1.5rem;
  inset-block-end: 0;
  width: 2px;
  background: #d7d3c8;
}
.step__dot {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: #c8f35c;
}
```

</details>

## 第四阶段：Grid 布局

### 练习 10：自动卡片墙

三列起步，空间不足自动减列，每张卡最小 16rem，窄屏不溢出。

<details>
<summary>查看答案</summary>

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr));
  gap: 1rem;
}
```

</details>

### 练习 11：页面骨架

实现页头、侧栏、主栏、页脚；主栏包含长代码块时不能撑破页面。

<details>
<summary>查看答案</summary>

```css
.layout {
  min-height: 100dvh;
  display: grid;
  grid-template-columns: 16rem minmax(0, 1fr);
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
}
.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; min-width: 0; overflow-wrap: anywhere; }
.footer { grid-area: footer; }

@media (max-width: 48rem) {
  .layout {
    grid-template-columns: 1fr;
    grid-template-areas: "header" "main" "sidebar" "footer";
  }
}
```

</details>

### 练习 12：subgrid 对齐

四张卡片标题行数不同，要求图片、标题、正文、操作区仍跨卡片对齐。

<details>
<summary>查看答案</summary>

```css
.cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
.card {
  display: grid;
  grid-row: span 4;
  grid-template-rows: subgrid;
  row-gap: 0.75rem;
}
```

外层行轨道会跨所有卡片共享，子卡片继承这些轨道。每个卡片必须正好包含四个对应的直接子项。

</details>

## 第五阶段：定位与动效

### 练习 13：修复 fixed 错位

弹层使用 `position: fixed`，但页面某个祖先增加 `transform: translateZ(0)` 后，弹层只覆盖祖先区域。

<details>
<summary>查看答案</summary>

transform 祖先建立了 fixed 的包含块。可将弹层通过 portal/Teleport 移到 body 下，或移除不必要的祖先 transform。不要依赖更大的 top/left 硬修位置。

</details>

### 练习 14：可访问的折叠动画

使用 Grid 实现高度未知的内容展开/收起，并尊重 reduced-motion。

<details>
<summary>查看答案</summary>

```css
.collapse {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 250ms ease;
}
.collapse > div { overflow: hidden; }
.collapse.is-open { grid-template-rows: 1fr; }

@media (prefers-reduced-motion: reduce) {
  .collapse { transition: none; }
}
```

同时用 JavaScript 管理 `aria-expanded`、`aria-hidden` 与焦点，不能只做视觉动画。

</details>

### 练习 15：列表展开

点击按钮后列表从透明、轻微上移变为可见，使用 transform/opacity 而非 top。

<details>
<summary>查看答案</summary>

```css
.menu {
  opacity: 0;
  transform: translateY(-0.5rem) scale(0.98);
  transform-origin: top;
  visibility: hidden;
  transition: opacity 180ms ease, transform 180ms ease, visibility 180ms;
}
.menu.is-open {
  opacity: 1;
  transform: none;
  visibility: visible;
}
```

收起后根据需要设置 `inert` 或 `hidden`，避免隐藏内容仍能聚焦。

</details>

## 第六阶段：响应式与组件查询

### 练习 16：容器查询卡片

同一卡片在宽主栏中横向排列，在窄侧栏中纵向排列。

<details>
<summary>查看答案</summary>

```css
.card-slot { container-type: inline-size; }
.card { display: grid; gap: 1rem; }
.card img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }

@container (min-width: 32rem) {
  .card { grid-template-columns: 10rem minmax(0, 1fr); align-items: center; }
}
```

</details>

### 练习 17：移动端视口

制作一个聊天页，底部输入栏不被移动浏览器地址栏遮挡。

<details>
<summary>查看答案</summary>

```css
.chat {
  height: 100dvh;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
}
.chat__messages { overflow-y: auto; }
.chat__composer { padding-block-end: max(1rem, env(safe-area-inset-bottom)); }
```

需要兼容旧环境时提供 vh 回退，并在真机测试键盘弹出后的表现。

</details>

## 第七阶段：综合项目

### 项目 A：响应式文档站

**要求：**

- 粘性页头、桌面侧栏、移动端折叠目录。
- 文章最大宽度约 72ch，代码块可横向滚动。
- 标题、段落、图片、表格、引用、提示框具有完整排版。
- 支持深浅主题与 reduced-motion。
- 所有交互可键盘操作。

**验收：** 320px、768px、1440px 无横向页面滚动；主题切换不闪烁；焦点清晰；截断内容不隐藏关键操作。

### 项目 B：仪表盘

**要求：**

- 使用 Grid 完成页面区域。
- 卡片墙使用 auto-fit + minmax。
- 至少一个组件使用容器查询。
- 表格在窄屏可滚动，且滚动区域有可访问名称。
- 加载骨架屏使用 reduced-motion 降级。

### 项目 C：动效作品集

**要求：**

- 卡片 hover 只动画 transform/opacity/少量颜色。
- 使用 view-timeline 或 IntersectionObserver 实现滚动显现。
- 所有动画在 reduced-motion 下直接显示最终状态。
- 检查 200% 缩放与高对比度模式。

## 自评清单

- [ ] 我能解释为什么某个声明生效或被覆盖。
- [ ] 我能计算盒模型尺寸与 margin 折叠结果。
- [ ] 我能判断使用 Flex、Grid 还是普通流。
- [ ] 我能处理长文本、图片和代码块溢出。
- [ ] 我能解释 position、包含块和层叠上下文。
- [ ] 我能用容器查询解决组件级响应式。
- [ ] 我能避免布局抖动并优先使用高性能动画属性。
- [ ] 我的样式有明确作用域、变量和覆盖顺序。
- [ ] 我验证了键盘、缩放、减弱动画和深浅主题。
- [ ] 我能在不同浏览器与真实设备上复现并定位问题。

> 回到 [文档首页](../README.md) 补齐薄弱章节。
