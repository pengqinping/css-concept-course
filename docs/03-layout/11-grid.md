# 11 · Grid 网格布局

> 学习目标：用轨道、网格线和区域描述二维布局，掌握自动放置、minmax、子网格与常见页面骨架。

## 1. 什么时候用 Grid

Grid 同时控制行与列，适合二维结构。

```text
            列 1        列 2        列 3
行 1      ┌──────────┬──────────┬──────────┐
          │ header（跨 3 列）                  │
行 2      ├──────────┼──────────┼──────────┤
          │ sidebar  │ main（跨 2 列）         │
行 3      ├──────────┼──────────┼──────────┤
          │ footer（跨 3 列）                  │
          └──────────┴──────────┴──────────┘
```

典型场景：页面骨架、卡片墙、图片画廊、仪表盘、表单二维布局。

## 2. 建立网格

```html
<div class="cards">
  <article>A</article>
  <article>B</article>
  <article>C</article>
</div>
```

```css
.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
```

容器直接子元素成为 grid item。与 Flex 一样，`display: inline-grid` 可创建行内级网格容器。

## 3. 轨道尺寸

```css
.container {
  grid-template-columns: 200px 1fr 2fr;
  grid-template-rows: auto 1fr auto;
}
```

- `200px`：固定轨道。
- `1fr`：分配一份剩余空间。
- `auto`：根据内容与可用空间确定。
- `min-content`：内容最小宽度。
- `max-content`：内容最大宽度。
- `fit-content(20rem)`：在 min-content 与 20rem 之间限制。

```text
固定 200px + 剩余空间按 1:2 分配
```

`fr` 不是简单百分比。它是在扣除固定尺寸、gap、内容最小尺寸后分配剩余空间。

## 4. repeat()、minmax() 与 auto-fit

```css
.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}
```

自动填充列：

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr));
  gap: 1rem;
}
```

```text
宽容器：[卡][卡][卡]
中等宽：[卡][卡]
窄容器：[卡]
```

### auto-fit vs auto-fill

- `auto-fit`：折叠空轨道，已有项目拉伸填满。
- `auto-fill`：保留空轨道，已有项目不拉伸填满全部空间。

需要紧凑卡片墙时通常用 auto-fit；需要保持项目宽度稳定时考虑 auto-fill。

## 5. 网格线与跨度

```css
.item {
  grid-column: 1 / 3;  /* 从列线 1 到列线 3，占 2 列 */
  grid-row: 2 / 4;     /* 占 2 行 */
}
```

```text
列线：  1   2   3   4
轨道：    A │   B   │ C
```

- `1 / 3` 跨越轨道 1 和 2。
- `span 2` 表示跨 2 个轨道。
- 负数从末尾计数：`-1` 是显式网格最后一条线。

```css
.full { grid-column: 1 / -1; }
.two-cols { grid-column: span 2; }
```

## 6. 命名网格线

```css
.layout {
  display: grid;
  grid-template-columns:
    [sidebar-start] 15rem
    [sidebar-end main-start] minmax(0, 1fr)
    [main-end];
}

.sidebar { grid-column: sidebar; }
.main { grid-column: main; }
```

命名能提升复杂布局可读性，但名称不要过多。重复名称可用于自动匹配，需要控制复杂度时保持少量清晰名称。

## 7. 命名区域

```css
.layout {
  display: grid;
  grid-template-columns: 15rem minmax(0, 1fr);
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; }
.footer { grid-area: footer; }
```

区域必须组成矩形；`.` 表示空单元格：

```css
grid-template-areas:
  "header header"
  "main   ."
  "footer footer";
```

响应式重排可以直接改变区域字符串：

```css
@media (max-width: 48rem) {
  .layout {
    grid-template-columns: 1fr;
    grid-template-areas:
      "header"
      "main"
      "sidebar"
      "footer";
  }
}
```

## 8. 自动放置

默认按行填充：

```css
.container {
  grid-auto-flow: row;
  grid-auto-columns: minmax(8rem, 1fr);
  grid-auto-rows: minmax(4rem, auto);
}
```

```css
.dense {
  grid-auto-flow: row dense;
}
```

`dense` 会尝试用较小项目填补前面空洞，但可能改变视觉顺序与 DOM 阅读顺序不一致，无障碍场景需谨慎。

固定列数的自动流：

```css
.container {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(12rem, 1fr);
  overflow-x: auto;
}
```

## 9. 对齐

```css
.container {
  justify-items: start;   /* 项目在单元格内沿 inline 轴 */
  align-items: start;     /* 项目在单元格内沿 block 轴 */
}

.item {
  justify-self: center;
  align-self: center;
}
```

轨道整体在容器中的分布使用：

```css
.container {
  justify-content: space-between;
  align-content: center;
}
```

这些属性只有网格尺寸未填满容器时才明显。

## 10. gap 与间距

```css
.container {
  gap: 1rem;
  row-gap: 1.5rem;
  column-gap: 1rem;
}
```

不要在 Grid 项目上再用 margin 模拟 gap，否则换行与区域跨度时间距会失控。

## 11. minmax(0, 1fr) 的意义

```css
.layout {
  grid-template-columns: 15rem minmax(0, 1fr);
}
```

默认 `1fr` 的最小值可能是 min-content，长 URL、代码块、表格会把主栏撑破容器。`minmax(0, 1fr)` 明确允许轨道收缩。

项目内部也常需要：

```css
.card {
  min-width: 0;
  overflow-wrap: anywhere;
}
```

## 12. subgrid：让子网格与外层轨道对齐

```html
<div class="cards">
  <article class="card">
    <img src="a.jpg" alt="" />
    <h2>标题 A</h2>
    <p>说明 A</p>
    <footer>操作 A</footer>
  </article>
</div>
```

```css
.cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.card {
  display: grid;
  grid-row: span 4;
  grid-template-rows: subgrid;
}
```

```text
外层行轨道被卡片继承
├── 图片行
├── 标题行
├── 正文行
└── 操作行
```

即使某张卡片标题行数不同，所有卡片的图片、标题、正文和页脚仍对齐。subgrid 适合卡片列表和表单布局；不需要跨项目对齐时，普通 Grid 更简单。

## 13. 完整页面骨架

```html
<div class="layout">
  <header class="header">页头</header>
  <aside class="sidebar">导航</aside>
  <main class="main">正文</main>
  <footer class="footer">页脚</footer>
</div>
```

```css
.layout {
  min-height: 100dvh;
  display: grid;
  grid-template-columns: 15rem minmax(0, 1fr);
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
}

.header { grid-area: header; padding: 1rem; }
.sidebar { grid-area: sidebar; padding: 1rem; background: #ebe7dd; }
.main { grid-area: main; min-width: 0; padding: clamp(1rem, 4vw, 2rem); }
.footer { grid-area: footer; padding: 1rem; }

@media (max-width: 48rem) {
  .layout {
    grid-template-columns: 1fr;
    grid-template-areas: "header" "main" "sidebar" "footer";
  }
}
```

## 14. Grid 常见问题

| 症状 | 原因 |
| --- | --- |
| 子项溢出 | 轨道最小尺寸、长内容、缺少 min-width: 0 |
| grid-area 名称无效 | 未定义对应 grid-template-areas |
| 自动排列顺序意外 | grid-auto-flow、显式位置或 dense |
| 1fr 不等于等比例剩余空间 | 内容最小尺寸和固定轨道影响分配 |
| align-content 看起来无效 | 网格已填满容器或只有单行 auto 轨道 |
| 子网格不对齐 | 子项未继承正确的行轨道或跨度 |

## 关联示例

- [Grid 模式](../../examples/layout/grid-patterns.html)：命名区域、`minmax()`、span、dense 与 subgrid。
- [布局实验台](../../examples/layout-playground.html)：跨列项目、单列强制与容器查询的组合实验。

## 15. 练习

1. 用 Grid 实现三列卡片墙，容器变窄时自动减为两列、一列。
2. 制作 header/sidebar/main/footer 页面骨架，并在移动端重排区域。
3. 解释 `1fr` 与 `minmax(0, 1fr)` 在长代码块场景中的区别。
4. 用 subgrid 对齐多张卡片的图片、标题和页脚。
5. 比较 auto-fit 与 auto-fill 在只有两个项目时的表现。

> 下一篇：[容器查询与自适应布局](12-container-queries.md)。
