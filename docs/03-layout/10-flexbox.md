# 10 · Flexbox 弹性布局

> 学习目标：能根据主轴、交叉轴和剩余空间解释每一个 flex 行为，并熟练处理伸缩、换行与常见对齐。

## 1. 什么时候用 Flex

Flex 适合**一维布局**：元素主要沿一个方向排列，空间分配和对齐围绕这个方向进行。

```text
导航：[Logo]   [文档] [示例] [关于]      [搜索]
└──────────── 主轴 inline ────────────┘
```

典型场景：导航、按钮组、工具栏、表单行、垂直步骤条、卡片内部排列。

## 2. 建立 Flex 容器

```html
<div class="toolbar">
  <button>取消</button>
  <button>保存</button>
</div>
```

```css
.toolbar {
  display: flex;
  gap: 0.75rem;
}
```

容器直接子元素成为 flex item。容器内部的 `::before`、`::after` 也会成为 flex item；匿名文本会包装成匿名 item。

### 两个方向

```css
.row { flex-direction: row; }
.column { flex-direction: column; }
.row-reverse { flex-direction: row-reverse; }
.column-reverse { flex-direction: column-reverse; }
```

```text
row:          [A] → [B] → [C]
row-reverse:  [C] → [B] → [A]   （视觉反转，不改 DOM 顺序）
```

主轴方向由 flex-direction 决定；交叉轴与主轴垂直。书写模式会影响主轴起点，`row` 不一定永远从左到右。

## 3. 主轴属性

| 属性 | 作用对象 | 作用 |
| --- | --- | --- |
| `flex-direction` | 容器 | 决定主轴方向 |
| `flex-wrap` | 容器 | 是否换行及方向 |
| `justify-content` | 容器 | 主轴上的剩余空间分配与对齐 |
| `flex-basis` | item | 主轴初始尺寸 |
| `flex-grow` | item | 正剩余空间的放大系数 |
| `flex-shrink` | item | 负剩余空间的收缩系数 |
| `flex` | item | grow/shrink/basis 简写 |

### justify-content

```css
.start { justify-content: flex-start; }
.end { justify-content: flex-end; }
.center { justify-content: center; }
.between { justify-content: space-between; }
.around { justify-content: space-around; }
.evenly { justify-content: space-evenly; }
```

```text
space-between: [A]      [B]      [C]
space-around:  [A]   [B]   [C]  （每项两侧都有半个间距）
space-evenly:  [A]    [B]    [C] （间距完全相等）
```

## 4. 交叉轴属性

| 属性 | 作用 |
| --- | --- |
| `align-items` | 单行 flex line 内所有 item 的交叉轴对齐 |
| `align-self` | 覆盖单个 item |
| `align-content` | 多行时 flex line 之间如何分配空间 |
| `row-gap` / `column-gap` | 项目与行间距 |

```css
.toolbar {
  align-items: center;
}
```

```css
.card__icon {
  align-self: flex-start;
}
```

只有 flex-wrap 产生多行时，`align-content` 才明显影响行间布局。单行时使用 `align-items`。

## 5. flex 简写

```css
.item {
  flex: 1;
}
```

等价于：

```css
.item {
  flex-grow: 1;
  flex-shrink: 1;
  flex-basis: 0%;
}
```

常见形式：

```css
flex: none;       /* 0 0 auto：不伸缩 */
flex: auto;       /* 1 1 auto：按内容基准伸缩 */
flex: initial;    /* 0 1 auto */
flex: 2;          /* 2 1 0% */
flex: 1 1 12rem;  /* 可伸缩，初始基准 12rem */
```

### 不要只写 flex-grow

```css
.sidebar { flex-grow: 1; }
```

默认 flex-basis 是 auto，sidebar 会先按内容占位，再分配剩余空间，结果可能不符合预期。希望等分时用 `flex: 1`；希望保持内容宽度时用 `flex: none`。

## 6. 伸缩计算

```text
可用空间 = 容器主轴尺寸 - 所有 item 的 flex-basis 总和 - gap

flex-grow > 0：按系数分配正剩余空间
flex-shrink > 0：空间不足时按加权基准收缩
```

```html
<div class="panes">
  <section>主内容</section>
  <aside>侧栏</aside>
</div>
```

```css
.panes { display: flex; gap: 1rem; }
.panes > section { flex: 2 1 0; }
.panes > aside { flex: 1 1 0; }
```

主内容与侧栏按 2:1 分配，gap 单独占据空间。当空间过小时，可让布局换行或改为 Grid。

## 7. 换行

```css
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
```

给 item 一个基准尺寸：

```css
.tags > * {
  flex: 1 1 8rem;
}
```

避免使用固定 margin 计算换行后的间距；`gap` 会自动作用于行与列。

## 8. 自动 margin

```css
.toolbar {
  display: flex;
}

.toolbar__spacer {
  margin-inline-start: auto;
}
```

```css
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
```

自动 margin 会吸收主轴剩余空间。一个方向使用多个 auto margin 时，空间均分。

## 9. min-width 与内容收缩

```html
<div class="row">
  <div class="url">https://example.com/a-very-long-unbreakable-path</div>
  <button>打开</button>
</div>
```

```css
.row { display: flex; gap: 1rem; }
.url { min-width: 0; overflow-wrap: anywhere; }
.row button { flex: none; }
```

默认自动最小尺寸可能让长 URL 撑破容器。Flex item 需要收缩时，通常同时考虑 `min-width: 0` 和文本换行策略。

## 10. 图片与基线对齐

```css
.icon {
  width: 1.25rem;
  height: 1.25rem;
  flex: none;
}
```

图标会被压缩是常见问题。使用 `flex: none` 保持尺寸，并用 `align-items: center` 对齐。

## 11. 完整示例：响应式工具栏

```html
<header class="toolbar">
  <a class="brand" href="/">Field Notes</a>
  <nav class="toolbar__nav" aria-label="主导航">
    <a href="/docs">文档</a>
    <a href="/examples">示例</a>
    <a href="/about">关于</a>
  </nav>
  <button class="toolbar__menu" type="button">菜单</button>
</header>
```

```css
.toolbar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem;
}

.brand { font-weight: 800; }
.toolbar__nav { display: flex; gap: 1rem; margin-inline-start: auto; }
.toolbar__menu { display: none; }

@media (max-width: 40rem) {
  .toolbar { flex-wrap: wrap; gap: 0.75rem; }
  .toolbar__nav { order: 3; width: 100%; margin-inline-start: 0; }
  .toolbar__menu { display: inline-flex; margin-inline-start: auto; }
}
```

## 12. Flex 与 Grid 的选择

| 需求 | 优先选择 |
| --- | --- |
| 一行按钮按内容分布 | Flex |
| 导航两端对齐 | Flex |
| 页面同时控制行列 | Grid |
| 卡片自动填充列 | Grid |
| 组件内部图标、文字、操作按钮 | Flex |
| 复杂二维区域命名 | Grid |

很多组件是 **Grid 外层 + Flex 内层**，两者并不互斥。

## 13. 常见问题

| 症状 | 原因 |
| --- | --- |
| flex: 1 的子项不等宽 | basis 不是 0，或内容最小尺寸限制 |
| 图片被压扁 | 默认 flex-shrink: 1 |
| align-content 无效 | 只有一行 |
| row-reverse 后焦点顺序异常 | 视觉顺序与 DOM 顺序不一致 |
| gap 不生效 | 浏览器过旧，或不是 Flex/Grid 容器 |
| 子元素不收缩 | min-width: auto 或 overflow 策略缺失 |

## 关联示例

- [Flexbox 模式](../../examples/layout/flex-patterns.html)：伸缩、换行、对齐、顺序和 `min-width: 0`。
- [布局实验台](../../examples/layout-playground.html)：把同一组项目切换到 Flex 与 Grid 中比较。

## 14. 练习

1. 实现左 logo、中间导航、右按钮的工具栏，空间不足时导航换到第二行。
2. 创建 2:1 的主栏与侧栏，并解释 `flex: 2` 与 `flex: 2 1 12rem` 的差别。
3. 用 `space-between`、`space-around`、`space-evenly` 排列三项，比较结果。
4. 修复一个长 URL 把 Flex 容器撑破的问题。
5. 制作垂直步骤条，让圆点对齐且连接线填满剩余高度。

> 下一篇：[Grid 网格布局](11-grid.md)。
