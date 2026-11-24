# 07 · 视觉格式与溢出

> 学习目标：能预测元素如何生成盒子、在文档流中占据什么位置，正确使用 display、visibility、opacity、overflow 与 contain，并建立一套从尺寸约束入手排查溢出的方法。

## 1. 格式化的核心问题

一个元素出现在页面上之前，浏览器要回答三个问题：

```text
HTML 元素
   │
   ├─▶ 是否生成盒子？ display: none / contents
   │
   ├─▶ 生成什么盒子？ block / inline / flex / grid / table ...
   │
   └─▶ 盒子怎样参与布局？ normal flow / float / absolute / flex item ...
```

“是否显示”“是否占空间”“是否可点击”“是否被辅助技术读取”是四个不同问题。CSS 没有一条属性能同时回答它们，因此调试时要分别检查布局盒、绘制结果、命中测试与可访问性树。

`display` 也不只是“块级或行内”。现代 CSS 把外部显示类型与内部显示类型分开：外部类型决定元素自身如何参与父级布局，内部类型决定其子元素如何排列。

## 2. `display`：从外部布局到内部格式

### 2.1 基础显示类型

| 值 | 生成盒子的行为 | 常见用途与限制 |
| --- | --- | --- |
| `block` | 生成块级盒，默认占满可用宽度 | 段落、分区；宽高通常有效 |
| `inline` | 生成行内盒，不打断行 | 少量文字、链接；宽高与垂直 margin 表现受限 |
| `inline-block` | 外部像行内，内部像块级盒 | 徽章、小控件；仍属于行内格式化上下文 |
| `none` | 不生成盒子 | 条件隐藏；通常也从可访问性树移除 |
| `list-item` | 类似块级，并生成列表标记 | 自定义列表样式 |
| `flow-root` | 建立独立块级格式化上下文 | 包含浮动、阻止 margin 折叠 |
| `contents` | 元素自身不生成盒子，子元素参与父级布局 | 语义包装；可访问性与浏览器差异需验证 |

行内元素的“内部是行内”并不意味着不能包含块级后代并造成异常匿名盒。例如在 `<span>` 中放 `<div>`，浏览器会拆分行内盒并生成匿名块盒，结果通常难以预测。HTML 内容模型本来就应保持语义与结构一致，不要用 CSS display 掩盖错误嵌套。

### 2.2 Flex、Grid、Table 与 Ruby

| 值 | 含义 |
| --- | --- |
| `flex` / `inline-flex` | 建立 Flex 格式化上下文；外部分别为块级、行内级 |
| `grid` / `inline-grid` | 建立 Grid 格式化上下文 |
| `table`、`table-row`、`table-cell` 等 | 使用表格布局算法；CSS 表格不等于语义 `<table>` |
| `inline-table` | 外部行内级、内部表格布局 |
| `ruby`、`ruby-base`、`ruby-text` 等 | 用于注音等 Ruby 排版 |
| `run-in` | 历史实验性值，浏览器支持不一致，不应依赖 |

表格布局中，单元格尺寸受整行整列约束；CSS 的 `table-cell` 也不会自动补出 `<table>` 的语义。读屏导航依赖真实表格结构，数据表应使用 HTML 表格元素。

Ruby 值适合构建语言注音组件，但它们与普通 inline、flex 的尺寸计算不同。若目标语言包含 Ruby 文本，必须使用真实内容检查基线、注音大小和换行，而不是仅凭单个方块判断。

### 2.3 单值与双值语法

```css
.card { display: block flow; }   /* 外部 block，内部 flow */
.inline-card { display: inline flow-root; }
```

双值语法让意图更明确：第一个是 outer，第二个是 inner。`block flex` 通常与 `display: flex` 等价，`inline grid` 与 `inline-grid` 等价。旧单值仍在广泛使用，但在复杂组件中明确写出内部格式化上下文能减少误读。

### 2.4 `display: contents` 的取舍

```html
<div class="semantic-wrapper">
  <p>标题</p>
  <p>正文</p>
</div>
```

```css
.semantic-wrapper { display: contents; }
```

包装元素自身的盒消失，两个 `<p>` 在布局上表现得像直接位于父容器中。适合让语义包装不干扰 Grid 或 Flex 轨道。

但“盒消失”不代表所有副作用消失：

- 原元素上的背景、边框、padding 无法按原盒绘制。
- 一些浏览器曾错误地从可访问性树移除该元素；现代实现已有改善，仍需用实际屏幕阅读器验证。
- 如果包装承担焦点、测量或脚本定位职责，`display: contents` 可能让这些逻辑失效。
- 它不会自动修复 DOM 顺序与视觉顺序不一致的问题。

因此，它适合“只提供语义、不提供视觉盒”的包装，不适合承载视觉样式的普通卡片容器。

## 3. 可见性的四种工具

### 3.1 `display: none`、`visibility`、`opacity` 与 `content-visibility`

| 属性/值 | 是否占布局空间 | 是否绘制 | 命中测试 | 可访问性常见表现 |
| --- | --- | --- | --- | --- |
| `display: none` | 否 | 否 | 否 | 通常从树中移除 |
| `visibility: hidden` | 是 | 否 | 通常否 | 通常不暴露给辅助技术 |
| `opacity: 0` | 是 | 视觉不可见 | 是 | 通常仍在树中 |
| `content-visibility: hidden` | 元素盒仍在，内容跳过 | 内容不绘制 | 内容通常不可命中 | 跳过内容通常不可访问 |
| `content-visibility: auto` | 是 | 屏外可跳过 | 屏内正常 | 可用于性能优化，仍需验证 |

这些差异解释了常见 bug：

- 用 `opacity: 0` 隐藏弹层后，透明层仍会挡住页面点击。应同时设置 `visibility: hidden`、`pointer-events: none`，或使用 `hidden` 与 `inert` 管理交互。
- 用 `visibility: hidden` 隐藏元素后，其占位不会消失，页面可能留下空白。
- 用 `display: none` 隐藏可聚焦控件时，焦点会跳过它；反过来，仅用透明度隐藏的按钮仍可能被 Tab 聚焦。
- `visibility` 可被子元素覆盖：父元素 hidden，子元素显式 visible 时可能重新显示，但父级布局空间仍保留。

`visibility: collapse` 主要用于表格行、行组等可折叠对象。对普通块级元素，很多浏览器把它当作 hidden，而不是真正压缩尺寸。跨表格与普通元素使用该值时，必须验证目标浏览器行为。

### 3.2 `opacity` 会形成层叠上下文

```css
.faded { opacity: 0.99; } /* 即使几乎不透明，也会创建层叠上下文 */
```

透明度小于 1 时，整个元素及其后代作为组合结果参与层叠，子元素的 `z-index` 不能逃到外部层叠规则中。它也会影响绘制性能，但并不像 `display: none` 那样跳过布局。

渐显动画常用 opacity，因为它通常能高效合成；但动画结束后不要把已完成隐藏的弹层永久留在 `opacity: 0` 状态，否则仍可能拦截交互。需要动画时，在结束后切换到 hidden，或在打开前恢复可见性并管理 inert。

## 4. `overflow`：两轴裁剪与滚动

### 4.1 四个主要值

```css
.scroll-box {
  inline-size: 20rem;
  block-size: 12rem;
  overflow: auto;
}
```

- `visible`：溢出内容可见，可能绘制到元素外。
- `hidden`：裁剪溢出，不提供用户滚动条；程序仍可改变 `scrollLeft` / `scrollTop`。
- `clip`：像 hidden 一样裁剪，但该元素不是滚动容器；也不支持程序滚动。
- `scroll`：裁剪并提供滚动条。是否始终显示取决于平台；桌面环境通常会出现滚动条轨道。
- `auto`：只在需要时提供滚动条。

`overflow-x` 与 `overflow-y` 可以分别控制，但二者并非完全独立。当一个轴是 `hidden` / `scroll` / `auto`，另一个轴是 `visible` 时，浏览器通常会把 visible 计算为 auto，避免出现“一个方向裁掉、另一个方向却溢出”的混合状态。应检查 Computed，而不是只读源码。

### 4.2 为什么内容会撑破容器

overflow 的根源通常是尺寸约束失败，而不是 overflow 属性缺失：

```text
容器宽度 300px
┌──────────────────────────────┐
│ 图片设置 width: 500px         │ → 横向溢出
│ 或长字符串没有断行机会        │ → 横向溢出
│ 或 flex/grid 子项 min-width:auto│ → 子项拒绝收缩
└──────────────────────────────┘
```

先判断是内容固有宽度过大，还是盒子的总宽度超过包含块。不要一上来就写 `overflow: hidden`：它会同时隐藏焦点环、下拉菜单和错误提示，掩盖真正的问题。

### 4.3 单行省略与滚动容器

```css
.truncated {
  max-inline-size: 20ch;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
```

`text-overflow` 需要满足三个前提：容器是块容器、行内方向溢出被裁剪、文本不换行。它不会处理纵向溢出，也不会自动作用于多行文本。多行截断与书写模式组合时，“行内轴”未必是屏幕上的水平方向，需结合 `writing-mode` 判断。

`overflow: hidden` 创建的裁剪容器会影响后代定位与滚动。例如 `position: sticky` 会受最近滚动祖先影响，绝对定位元素可能被裁切。对确实需要滚动的区域，优先 `overflow: auto`，并保证键盘可聚焦、滚动条可见、屏幕阅读器能发现。

实用补充：

```css
.scroll-box {
  overflow: auto;
  scrollbar-gutter: stable; /* 预留滚动条空间，减少内容宽度跳动 */
  overscroll-behavior: contain; /* 阻止滚动到边界时把页面滚动传递出去 */
}
```

`scrollbar-gutter` 的兼容性和双向布局表现需验证；不要用它替代明确的布局尺寸。自定义滚动条还要保证轨道、滑块与焦点对比度。

## 5. `white-space`：空格、换行与文本保留

`white-space` 是多个换行行为的简写。理解各列，比背单个值更可靠：

| 值 | 换行 | 合并空格/制表符 | 行尾空格 | 段尾换行 |
| --- | --- | --- | --- | --- |
| `normal` | 折叠 | 合并 | 折叠 | 折叠 |
| `nowrap` | 折叠 | 合并 | 折叠 | 折叠 |
| `pre` | 保留 | 保留 | 保留 | 保留 |
| `pre-wrap` | 保留 | 保留 | 保留 | 保留并挂起 |
| `pre-line` | 保留 | 合并 | 折叠 | 保留 |
| `break-spaces` | 保留 | 保留 | 保留 | 换行 |

典型用法：

```css
pre, code { white-space: pre; }       /* 代码需要横向滚动容器 */
.notice { white-space: pre-line; }    /* 保留用户输入的换行，折叠多余空格 */
```

`nowrap` 只禁止自动换行，不隐藏溢出，也不自动产生省略号。`pre` 保留所有空白，因此在窄屏很容易产生横向滚动；代码块应设置 `overflow-x: auto`，而不是用 `white-space: normal` 破坏代码结构。

用户输入文本渲染时，`pre-line` 常比 `pre-wrap` 更合适，但仍需处理控制字符、超长 URL 和安全转义。CSS 空白处理不能替代服务端文本清理。

## 6. 媒体尺寸：`object-fit` 与 `aspect-ratio`

### 6.1 `object-fit` 处理替换元素的内容

`<img>`、`<video>`、`<iframe>` 等替换元素有“元素盒子”和“内部内容”两层尺寸。`object-fit` 决定内部内容如何适应盒子，`object-position` 决定对齐位置。

| 值 | 行为 |
| --- | --- |
| `fill` | 拉伸以填满盒子，可能变形，默认值 |
| `contain` | 等比缩放，完整放入盒子，可能留白 |
| `cover` | 等比缩放，完全覆盖盒子，可能裁切 |
| `none` | 保持固有尺寸，可能溢出或留白 |
| `scale-down` | 等效于 contain 与 none 中结果较小的缩放 |

```css
.thumbnail {
  inline-size: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  object-position: 50% 35%;
}
```

`object-position` 的百分比偏移并不是简单的“图像移动百分之几”，它涉及内容尺寸与盒子尺寸的差值。人物焦点靠上时，`50% 30%` 往往比居中更能保住脸部；最终仍应用真实图片验证。

如果图片是普通文档流中的 `<img>`，仅设置 `width: 100%; height: auto` 通常就能保持比例，不需要 `aspect-ratio` 或 `object-fit`。需要统一卡片占位、裁切焦点或固定盒子时，这两组属性才真正发挥作用。

### 6.2 `aspect-ratio` 是首选比例，不是不可突破的锁

```css
.video-frame {
  inline-size: 100%;
  aspect-ratio: 16 / 9;
  background: #111;
}
```

宽高比例会在自动尺寸计算中提供偏好。`auto 16 / 9` 表示优先使用替换元素的固有比例，其次使用指定比例；仅写 `16 / 9` 时，通常优先使用指定比例。

约束仍然成立：

- `min-width`、`max-height`、内容最小尺寸和父布局算法可能让最终比例偏离目标。
- 内容可能溢出比例盒子。视频画布、按钮文字、错误信息都需要测试，必要时配合 padding 或内部滚动。
- 宽高都显式设置时，最终尺寸由这些声明与布局算法决定，aspect-ratio 不会强行覆盖。
- 百分比高度仍需要可解析的包含块高度；aspect-ratio 不会让所有百分比高度突然变得有效。

## 7. `contain`：主动限制布局影响范围

```css
.widget {
  contain: layout paint;
}
```

`contain` 告诉浏览器：这个元素的某些影响不会超出自身边界，从而缩小样式、布局与绘制计算范围。

| 值 | 主要效果 | 使用前提 |
| --- | --- | --- |
| `none` | 不限制 | 默认 |
| `strict` | 等价于 `size layout style paint` | 必须能明确控制尺寸，否则容易塌陷 |
| `content` | `layout style paint` | 常用于独立组件 |
| `size` | 元素尺寸不依赖后代内容 | 必须自己提供可靠尺寸 |
| `inline-size` | 只限制行内轴尺寸 | 适合纵向列表项、宽度由容器决定 |
| `layout` | 建立独立格式化上下文与包含块，隔离部分布局影响 | 会改变 float、margin 折叠与定位参照 |
| `style` | 隔离计数器、引号等样式作用域 | 不常见，需理解副作用 |
| `paint` | 后代绘制被裁剪到溢出边界 | 下拉菜单、阴影等外部绘制会被裁掉 |

最典型的错误是给未知高度卡片添加 `contain: strict` 或 `contain: size`，然后发现高度变成 0。因为尺寸包含意味着浏览器无需为后代计算内在高度，元素又没有显式高度，就会塌陷。对高度由内容决定的组件，通常使用 `contain: layout paint` 或 `contain: content`，并确认没有需要绘制到外部的子层。

`contain: paint` 与 `overflow: hidden` 都能裁剪，但目的不同：前者承诺绘制影响范围，后者通常用于内容溢出管理。两者都不适合承载需要突破组件边界的弹窗。

## 8. 层叠上下文入门

### 8.1 `z-index` 不是全局排名

当多个元素重叠时，浏览器不是把所有 `z-index: 9999` 放在同一张表里排序。层叠上下文把参与者分组：

```text
根层叠上下文
├─ 文档流中的普通块
├─ 定位元素 A（z-index: 1，建立上下文）
│    ├─ 子元素 z-index: 999
│    └─ 子元素 z-index: -1
├─ 定位元素 B（z-index: 2，建立上下文）
│    └─ 子元素 z-index: 0
└─ 元素 C（z-index: 3，建立上下文）
```

A 的整个上下文会作为一个整体参与根层级排序。A 的子元素即使写 `z-index: 9999`，也不会越过 z-index 为 2 的 B。这个模型解释了“弹层已经设了很大 z-index，却被兄弟组件挡住”。

常见创建层叠上下文的方式包括：

- 根元素。
- `position` 为 absolute / relative 且 `z-index` 不是 auto。
- Flex / Grid 子项且 `z-index` 不是 auto。
- `opacity` 小于 1。
- `transform`、`filter`、`perspective` 不为 none。
- `isolation: isolate`。
- `mix-blend-mode` 不是 normal。
- 部分 `contain`、`will-change` 与 `clip-path` 等条件。

`isolation: isolate` 能主动建立上下文，常用于需要混合模式或裁剪又不想依赖偶然 z-index 的组件。不要把 z-index 当成修复所有遮挡的方法；先确认元素是否定位、属于哪个上下文、祖先是否建立上下文，以及负 z-index 是否落到祖先背景之后。

完整的定位与层叠算法见后续文档，本篇先建立“上下文分组”这一核心模型。

## 9. 常见尺寸与溢出排查

### 9.1 尺寸约束的先后顺序

```text
包含块提供参照
   │
   ├─▶ width / height / margin / padding / border
   │
   ├─▶ min-* / max-* 限制
   │
   ├─▶ box-sizing 决定宽度是否包含 padding/border
   │
   ├─▶ 布局算法分配 flex/grid 空间
   │
   └─▶ 内容最小尺寸可能阻止收缩
```

常见原因与修复方向：

| 现象 | 常见原因 | 优先检查 |
| --- | --- | --- |
| `width: 100%` 加 padding 后超出 | 默认 content-box | 是否设置 `box-sizing: border-box` |
| Flex 子项拒绝变窄 | `min-width: auto` 使用内容最小尺寸 | 子项是否可设 `min-inline-size: 0` |
| Grid 内容撑出轨道 | 轨道最小尺寸与长内容冲突 | 是否使用 `minmax(0, 1fr)` |
| 百分比高度无效 | 包含块高度未确定 | 父级是否有明确高度或布局约束 |
| 绝对定位元素超出卡片 | 卡片不是定位包含块 | 最近的 `position` 祖先 |
| transform 后仍触发横向滚动条 | transform 不改变布局，但视觉溢出可影响滚动区域 | 滚动容器、溢出方向与边界 |
| 图片突然撑高 | 只设宽度未保持比例 | 固有尺寸、height、aspect-ratio |
| 子元素 margin 跑到容器外 | margin 折叠或包含关系 | 父级是否建立格式化上下文 |
| 圆角没有裁住图片 | 圆角不裁所有后代 | overflow、clip-path 或对象本身圆角 |

`min-width: 0` 不是万能的。它允许 Flex/Grid 子项收缩，但子项内部仍可能溢出；还需在真正的内容层处理长文本、图片或滚动。反过来，不要全局清除所有 `min-width`，表单控件与可点击区域可能需要最小尺寸。

### 9.2 一套可复用的排查顺序

1. **确定包含块与主轴**：百分比参照谁，书写方向是哪条轴。
2. **检查盒子总尺寸**：content、padding、border、margin 与 box-sizing。
3. **检查最小/最大约束**：min-width、min-height、max-inline-size 等。
4. **检查布局算法**：Flex/Grid 的自动最小尺寸、轨道与收缩规则。
5. **检查内容固有尺寸**：图片、代码、长 URL、white-space。
6. **最后选择溢出策略**：允许换行、允许滚动、裁切，还是重构布局。
7. **验证交互**：焦点环、下拉层、键盘滚动和屏幕阅读器是否仍可用。

## 10. 完整示例一：媒体卡片与独立滚动区

保存为 `formatting-card.html`。缩窄窗口，观察图片比例、卡片网格与代码区滚动。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>媒体卡片与滚动区</title>
  <style>
    :root { font-family: system-ui, "PingFang SC", sans-serif; color: #22271f; }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 1.5rem; background: #f2f1eb; }
    main { max-inline-size: 56rem; margin-inline: auto; }

    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
      gap: 1rem;
    }

    .card {
      display: flow-root;
      min-inline-size: 0;
      border: 1px solid #d5d9ce;
      border-radius: 1rem;
      background: white;
      overflow: hidden;
    }

    .thumb {
      display: block;
      inline-size: 100%;
      aspect-ratio: 16 / 9;
      object-fit: cover;
      object-position: center 35%;
      background: #dce8d2;
    }

    .body { padding: 1rem; }
    h2 { margin-block: 0 0.5rem; font-size: 1.15rem; }
    p { margin-block: 0; color: #62685c; line-height: 1.6; overflow-wrap: anywhere; }

    .code-panel {
      margin-block-start: 1.5rem;
      padding: 1rem;
      border-radius: 0.875rem;
      color: #eaf2e4;
      background: #1e281a;
    }

    pre {
      max-inline-size: 100%;
      margin-block: 0;
      overflow-x: auto;
      white-space: pre;
      scrollbar-gutter: stable;
    }

    code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }

    @media (max-width: 34rem) {
      body { padding: 0.75rem; }
      .cards { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <h1>图片、比例与滚动</h1>
    <section class="cards">
      <article class="card">
        <img class="thumb" alt="绿色山丘上的天空" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4MDAgNDUwIj48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjQ1MCIgZmlsbD0iI2RjZThkMiIvPjxjaXJjbGUgY3g9IjY1MCIgY3k9IjkwIiByPSI1NSIgZmlsbD0iI2Y4ZjRkOCIvPjxwYXRoIGQ9Ik0wIDM1MEwxODAgMTcwbDE3MCAxODAgMTIwLTEzMCAzMzAgMTgwdjUwSDB6IiBmaWxsPSIjNjc4NjUxIi8+PC9zdmc+" />
        <div class="body">
          <h2>统一比例的媒体卡片</h2>
          <p>object-fit: cover 保持图片比例并填满盒子，object-position 决定裁切焦点。</p>
        </div>
      </article>
      <article class="card">
        <img class="thumb" alt="蓝色背景与圆形图案" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4MDAgNDUwIj48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjQ1MCIgZmlsbD0iI2Q5ZTdmMCIvPjxjaXJjbGUgY3g9IjQwMCIgY3k9IjIyNSIgcj0iMTUwIiBmaWxsPSIjNWE3ZjljIi8+PHJlY3QgeD0iODAiIHk9IjMzMCIgd2lkdGg9IjY0MCIgaGVpZ2h0PSIxMjAiIGZpbGw9IiMzZTVjNzMiLz48L3N2Zz4=" />
        <div class="body">
          <h2>可收缩的网格子项</h2>
          <p>min-inline-size: 0 允许网格子项收缩，长链接则通过 overflow-wrap 安全断行。</p>
        </div>
      </article>
    </section>
    <section class="code-panel" aria-label="代码示例">
      <pre tabindex="0"><code>/* 这个代码行故意很长，用于测试水平滚动 */
const readableLayout = (container) =&gt; container.querySelectorAll('[data-overflow]');</code></pre>
    </section>
  </main>
</body>
</html>
```

## 11. 完整示例二：长列表、可见性状态与层叠隔离

保存为 `content-visibility-demo.html`。这个示例演示性能容器、透明层拦截和隔离上下文，不依赖 JavaScript。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>格式与可见性实验</title>
  <style>
    :root { font-family: system-ui, "PingFang SC", sans-serif; color: #24291f; }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 1.5rem; background: #f7f5ef; }
    main { max-inline-size: 42rem; margin-inline: auto; }
    h1 { text-wrap: balance; }

    .feed { display: grid; gap: 1rem; }

    .feed-item {
      contain: layout paint;
      padding: 1rem 1.25rem;
      border: 1px solid #d6dacd;
      border-radius: 0.875rem;
      background: white;
    }

    .feed-item h2 { margin-block: 0 0.5rem; font-size: 1.1rem; }
    .feed-item p { margin-block: 0; color: #62685c; line-height: 1.65; }

    .visibility-demo {
      display: grid;
      gap: 0.75rem;
      margin-block-start: 1.5rem;
    }

    .stage {
      position: relative;
      isolation: isolate;
      min-block-size: 7rem;
      border: 1px dashed #8e9983;
      border-radius: 0.75rem;
      overflow: hidden;
    }

    .stage p { margin: 0; padding: 1rem; }

    .ghost {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      opacity: 0;
      background: rgb(63 107 42 / 20%);
    }

    .stage:hover .ghost,
    .stage:focus-within .ghost { opacity: 1; }

    .stage button {
      padding: 0.5rem 1rem;
      border: 2px solid #315b24;
      border-radius: 0.5rem;
      color: #203d16;
      background: white;
      font: inherit;
    }

    .stage button:focus-visible { outline: 3px solid #6d9258; outline-offset: 3px; }

    .scroll-panel {
      max-block-size: 12rem;
      margin-block-start: 1rem;
      padding: 1rem;
      overflow-y: auto;
      overscroll-behavior: contain;
      border: 1px solid #cbd1c2;
      border-radius: 0.75rem;
      background: white;
    }
  </style>
</head>
<body>
  <main>
    <h1>内容隔离与可见性</h1>
    <section class="feed">
      <article class="feed-item"><h2>独立格式化上下文</h2><p>contain: layout paint 隔离布局与绘制，但元素高度仍由内容决定，不会因为 size containment 塌陷。</p></article>
      <article class="feed-item"><h2>隔离的层叠上下文</h2><p>isolation: isolate 让子元素的层叠关系留在当前组件内部，避免影响兄弟组件。</p></article>
      <article class="feed-item"><h2>透明的交互层</h2><p>opacity: 0 不会移除命中测试。键盘用户仍能聚焦下方按钮，悬停或聚焦时遮罩才显现。</p></article>
    </section>

    <div class="visibility-demo">
      <div class="stage">
        <p>将鼠标移入，或按 Tab 聚焦按钮。</p>
        <div class="ghost"><button type="button">我仍然可以聚焦</button></div>
      </div>
    </div>

    <section class="scroll-panel" tabindex="0" aria-label="可滚动说明">
      <h2>有边界的滚动区域</h2>
      <p>overflow-y: auto 只在内容超出时提供滚动。overscroll-behavior: contain 避免滚动到边界后继续带动页面。</p>
      <p>键盘可以聚焦这个区域，然后使用方向键或 Page Down 滚动。不要只依赖鼠标滚轮验证可访问性。</p>
      <p>content-visibility: auto 适合屏外内容较多的长页面，但它需要配合可靠尺寸和滚动锚点验证，不能替代分页或数据按需加载。</p>
    </section>
  </main>
</body>
</html>
```

## 12. 易错点

| 误区 | 正确理解与做法 |
| --- | --- |
| `display: none` 与 `visibility: hidden` 一样 | 前者不生成盒子，后者保留布局空间 |
| `opacity: 0` 就是彻底隐藏 | 它仍占空间、可命中、可聚焦，通常仍在可访问性树中 |
| `overflow-x: hidden` 与 `overflow-y: auto` 完全独立 | visible 轴可能被计算为 auto，需检查 Computed |
| `text-overflow` 会自动处理多行 | 它只处理行内轴单行溢出，需配合 nowrap 与裁剪 |
| `object-fit` 会改变 `<img>` 盒子大小 | 它只控制内部内容如何适应盒子，盒子尺寸由布局属性决定 |
| `aspect-ratio` 强制固定最终比例 | 它只是首选比例，内容、min/max 与布局算法仍可影响结果 |
| `contain: strict` 适合所有卡片 | size containment 会让无显式高度的卡片塌陷 |
| z-index 越大就越靠前 | z-index 只在同一层叠上下文内比较 |
| 所有溢出都该用 hidden | 先判断尺寸、最小约束和内容来源，再选择换行、滚动或裁切 |

## 13. DevTools 与验证方法

1. **Computed 面板**：检查 display 的双值结果、overflow 两轴计算值、visibility、opacity、contain 与 aspect-ratio。
2. **盒模型检查器**：确认内容尺寸、padding、border、margin 与包含块，区分“内容太宽”和“盒子总宽太大”。
3. **Layout 面板**：开启 Grid/Flex 轨道覆盖层与 overflow 标记，找到真正撑出容器的子元素。
4. **Elements 面板**：临时为后代加 `outline`，或使用 DevTools 的溢出高亮，定位绘制越界元素。
5. **Layers / Rendering 面板**：观察层叠上下文、paint containment 与合成层，不要仅凭截图判断遮挡。
6. **键盘验证**：Tab 遍历隐藏控件、滚动区和弹层；检查焦点是否被裁剪，方向键能否滚动。
7. **可访问性树**：对比 display:none、visibility:hidden、opacity:0 与 content-visibility 的差异。
8. **极端内容测试**：长 URL、无空格字符串、200% 缩放、多语言文本、图片加载失败和超长错误消息。

## 关联示例

- [性能容器与长列表](../../examples/engineering/performance-containment.html)：切换 `contain`，观察尺寸、裁剪和层叠副作用。
- [定位与层叠上下文](../../examples/layout/positioning-stacking.html)：验证 `z-index` 为什么不能逃出父级层叠上下文。

## 14. 练习

1. 用 block、inline、inline-block、flow-root 和 contents 包裹同一组内容，记录盒子、margin 折叠与可访问性差异。
2. 制作一个 `overflow-x: hidden; overflow-y: auto` 容器，在 Computed 中查看 x 轴最终值，并解释原因。
3. 分别用 display:none、visibility:hidden、opacity:0 隐藏一个按钮，测试占位、Tab 顺序与鼠标点击。
4. 修复一个被长文本撑破的 Flex 卡片：先观察 min-width，再分别尝试断行、`min-inline-size: 0` 和内部滚动。
5. 为统一比例图片设置 object-fit 与 object-position，改变焦点位置；再为同一卡片添加 contain，验证高度不会塌陷。

> 上一篇：[颜色、背景与边框](06-color-background-border.md)。背景裁剪与 overflow 都是绘制边界，但创建的是不同约束。
>
> 下一篇：[文档流与格式化上下文](../03-layout/08-normal-flow.md)。继续深入块级、行内布局与 margin 折叠。
