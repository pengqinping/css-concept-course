# 08 · 文档流与格式化上下文

> 学习目标：理解元素为什么换行、为什么会互相影响，以及 BFC 如何隔离布局，为 Flex 和 Grid 打牢基础。

## 1. 什么是文档流

普通文档流是浏览器默认的内容排列方式。块级盒子通常从上到下排列，行内盒子沿着文字方向排列。

```text
block A
┌────────────────────────┐
│ 内容 A                 │
└────────────────────────┘
        ↕ margin
block B
┌────────────────────────┐
│ 内容 B                 │
└────────────────────────┘
```

```html
<div>块 A</div>
<div>块 B</div>
<span>行内 A</span>
<span>行内 B</span>
```

块级 div 各占一行；两个 span 通常在同一行连续排列，是否换行取决于可用宽度和空白处理。

## 2. display 决定外部与内部布局

```css
.block { display: block; }
.inline { display: inline; }
.inline-block { display: inline-block; }
.flex { display: flex; }
.grid { display: grid; }
```

现代语法把 display 拆成两个部分：

```css
.item { display: inline flex; }
.container { display: block flow-root; }
```

- 外部值：决定元素自身如何参与父级布局，如 block、inline。
- 内部值：决定子元素如何布局，如 flow、flex、grid。

| 值 | 外部表现 | 可设置 width/height | 典型场景 |
| --- | --- | --- | --- |
| `block` | 独占一行 | 可以 | section、div |
| `inline` | 与文字同行 | 通常无效 | span、a |
| `inline-block` | 外部像行内，内部像块 | 可以 | 徽章、图标 |
| `flex` | 块级弹性容器 | 可以 | 工具栏、导航 |
| `inline-flex` | 行内弹性容器 | 可以 | 按钮内容 |
| `grid` | 块级网格容器 | 可以 | 页面布局、卡片墙 |
| `none` | 不生成盒子 | — | 隐藏 |

## 3. 行内布局的细节

行内盒子由多个片段组成。多行文本中，同一个 span 可能被拆成多个片段。

```text
第一行：[文字][span 片段 A]
第二行：[span 片段 B][文字]
```

以下属性对非替换行内元素通常无效：

```css
span {
  width: 100px;   /* 无效 */
  height: 50px;   /* 无效 */
  margin-block: 10px; /* 垂直 margin 不推开行盒 */
}
```

需要尺寸时使用 `inline-block`、Flex 或 Grid。行内元素仍可设置颜色、字体、背景、水平 padding 等，但 padding/边框可能覆盖相邻行而不改变行高。

## 4. 匿名盒子

```html
<div class="box">直接文字<span>行内内容</span></div>
```

父级块容器会为裸露文字建立匿名块盒，使块级子元素与文本可以共存。匿名盒子没有类名，不能直接用 CSS 选择，因此需要样式时应显式包裹元素。

## 5. 块级布局的关键规则

普通流中，块级盒子的 width: auto 会填充包含块可用宽度，并减去 margin、border、padding。

```css
.box {
  width: auto;
  margin-inline: 2rem;
  padding-inline: 1rem;
}
```

宽度为 auto 不等于没有尺寸，而是“吸收剩余空间”。这也是为什么块级元素默认看起来占满一行。

## 6. 什么是格式化上下文

格式化上下文定义一组盒子如何布局。常见类型：

- **BFC**：块级格式化上下文。
- **IFC**：行内格式化上下文。
- **FFC**：Flex 格式化上下文。
- **GFC**：Grid 格式化上下文。

父元素建立 BFC 的常见方式（**任选其一**，不是同时声明）：

```css
.a { display: flow-root; }  /* 最清晰，无额外副作用 */
.b { overflow: hidden; }    /* 会裁剪溢出内容 */
.c { float: left; }         /* 改变自身参与布局的方式 */
.d { position: absolute; }  /* 脱离普通流 */
.e { contain: layout; }     /* 附带布局隔离语义 */
```

**`display: flow-root` 是最清晰的 BFC 创建方式**，它不附带裁剪或定位副作用。上面几种写法彼此独立，混在一条规则里会互相干扰。

## 7. BFC 如何隔离 margin 折叠

```html
<div class="parent">
  <div class="child">内容</div>
</div>
```

```css
.parent {
  padding-block-start: 1px; /* 阻止父子 margin 穿出 */
}

.child {
  margin-block-start: 2rem;
}
```

更推荐：

```css
.parent {
  display: flow-root;
}

.child {
  margin-block-start: 2rem;
}
```

```text
未隔离：child 的 margin 可能“穿过” parent 顶部
建立 BFC：margin 被限制在 parent 内部
```

BFC 还会让容器包含浮动子元素，避免父级高度塌陷。现代布局优先使用 `display: flow-root` 或 Grid/Flex 清除浮动影响。

## 8. margin 折叠深入

### 相邻兄弟

```css
.a { margin-block-end: 24px; }
.b { margin-block-start: 16px; }
```

间距为 24px。

### 父子

父元素没有 border、padding、高度或 BFC 隔离时，首个子元素的 margin-top 可能与父元素 margin-top 折叠。

### 空块

空块自身的 margin-top 与 margin-bottom 也可能互相折叠。

### 折叠限制

- 只影响普通流的垂直 margin。
- 不影响水平 margin。
- 不影响 Flex/Grid 项目。
- 根元素 margin 不与其子元素折叠。

## 9. 浮动

浮动曾用于图文环绕和多列布局，现在主要保留其文本环绕语义。

```html
<figure class="quote">
  <img src="avatar.jpg" alt="" />
  <blockquote>文字会环绕在浮动图片周围。</blockquote>
</figure>
```

```css
.quote img {
  float: inline-start;
  width: 4rem;
  margin-inline-end: 1rem;
}
```

浮动元素脱离普通流，父级可能不包含它。用 `display: flow-root` 让父级包含浮动，或精确控制清除：

```css
.clear {
  clear: both;
}
```

新页面布局优先使用 Flex/Grid，不要为了多列效果堆叠 float 和 clearfix。

## 10. 常见问题排查

| 症状 | 常见原因 | 检查方式 |
| --- | --- | --- |
| div 没有占满预期宽度 | 父容器、margin 或 max-width 限制 | 查看 computed width 与包含块 |
| 子元素 margin 把父元素“顶开” | 父子 margin 折叠 | 添加 `display: flow-root` |
| 父元素高度为 0 | 子元素全部浮动/绝对定位 | 检查子元素 position/float |
| 行内 span 宽高不生效 | display 为 inline | 改为 inline-block/Flex |
| 两个块间距变成较大值 | margin 折叠 | 计算两个 margin 的合并结果 |
| 长内容撑破网格 | Grid 子项自动最小尺寸 | 设置 `min-width: 0` |

## 关联示例

- [盒模型与 margin 折叠](../../examples/foundations/box-model-margin.html)：对比普通流、BFC 与 `contain: layout` 的折叠差异。
- [多列与形状环绕](../../examples/visual/shape-multicol.html)：多栏内容流、`float` 与现代 `shape-outside` 环绕。
- [补充属性与专题](../07-reference/27-additional-properties.md)：多列与形状属性的完整决策说明。

## 11. 练习

1. 创建两个块元素，验证 margin 折叠；再改为 Flex 容器，比较结果。
2. 用 `display: flow-root` 让父元素包含一个浮动图片。
3. 给同一个 span 分别设置 inline 和 inline-block，比较宽高与垂直 margin。
4. 制作一个首个子元素带 margin-top 的卡片，并分别用 padding 和 BFC 阻止折叠。
5. 解释为什么绝对定位元素的父级可能没有高度。

> 下一篇：[定位与层叠](09-positioning-stacking.md)。
