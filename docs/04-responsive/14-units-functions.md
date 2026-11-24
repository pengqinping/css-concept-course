# 14 · 现代 CSS 单位与函数

> 学习目标：为字号、间距、布局尺寸和视口区域选择正确的相对基准，熟练掌握 `calc()`、`min()`、`max()`、`clamp()`、`env()` 与自定义变量的组合方式，并理解单位解析时机和数学表达式的限制。

## 1. 单位是在回答“相对于谁”

绝对单位看起来确定，相对单位才能适应内容、字体和容器。先确定参照物，再选择单位：

```text
字号相对根字号 ───────────────▶ rem
字号相对当前/父级字号 ────────▶ em
行宽相对字体字形 ─────────────▶ ch / ex
布局相对包含块 ───────────────▶ %
页面排版相对视口 ─────────────▶ vw / vh / vmin / vmax
可见区域相对容器 ─────────────▶ cqw / cqh / cqi / cqb
轨道分配剩余空间 ─────────────▶ fr（Grid）
数学组合与边界约束 ───────────▶ calc / min / max / clamp
设备安全区 ───────────────────▶ env(safe-area-inset-*)
```

单位选错时，CSS 仍然是“有效”的，但结果会在某个场景失控。例如 `font-size: 10vw` 在宽屏上巨大，在窄屏上又可能小到难以阅读；`width: 50%` 在包含块宽度不确定时也无法给出稳定结果。

## 2. 长度与字体相对单位

### 2.1 `px`

`px` 是 CSS 像素，不直接等于物理设备像素。浏览器缩放、设备像素比和用户设置都会影响最终显示。

适合：

- 边框、阴影等视觉细节；
- 小尺寸图标的几何控制；
- 明确要求接近固定视觉尺寸的场景。

不适合：

- 作为所有字号和间距的唯一单位；
- 假设 1px 在所有设备上都是同一个物理大小；
- 用它锁死组件宽度，导致缩放或重排失败。

### 2.2 `%`

百分比不是固定相对于“父元素”一个统一属性，而是相对于该属性规定的参考值：

| 属性示例 | 常见参考 |
| --- | --- |
| `width: 50%` | 包含块的内容宽度 |
| `padding: 10%` | 包含块的内联尺寸，四个方向都按该基准计算 |
| `height: 50%` | 包含块高度；高度未确定时可能表现为 `auto` |
| `line-height: 150%` | 元素自身的字号 |
| `translate: 10%` | 元素自身边框盒尺寸 |

因此，百分比的可预测性依赖于包含块。嵌套百分比还会层层计算，不宜表达全局间距体系。

### 2.3 `em` 与 `rem`

`em` 的基准取决于属性：

- `font-size` 的 `em` 相对父元素计算后的 `font-size`。
- 其他属性中的 `em` 通常相对元素自身的计算字号。

```css
.component { font-size: 1.25rem; }
.component__title { font-size: 1.2em; }
.component { padding: 1em; }
```

这里标题字号相对组件的 `1.25rem`，组件 padding 也相对 `1.25rem`。改变组件字号时，二者会一起变化，适合建立局部比例。

但 `em` 嵌套容易复利：

```css
.list { font-size: 1.1em; }
.list .list { font-size: 1.1em; }
```

三层嵌套会变成 `1.1 × 1.1 × 1.1`，难以预测。需要统一缩放时优先使用 `rem`。

`rem` 相对根元素 `html` 的字号。它适合设计令牌、正文、全局间距和组件基础尺寸。把根字号改成 `62.5%` 只是为了方便计算并非必要，还可能让“以用户默认字号为准”的意图变得模糊。

### 2.4 `ch` 与 `ex`

- `ch`：当前字体中数字“0”的宽度，常用于估算文本行宽。
- `ex`：当前字体中小写字母“x”的高度，即 x-height，受字体影响很大。

```css
.prose { max-inline-size: 65ch; }
```

`65ch` 对拉丁字母通常是合理的阅读行宽参考，但中文字形、字体和字号都会改变实际效果，必须结合真实内容验证。`ex` 更依赖字体度量，不宜当作跨字体稳定的垂直节奏单位。

### 2.5 `vw`、`vh`、`vmin`、`vmax`

| 单位 | 含义 |
| --- | --- |
| `vw` | 视口宽度的 `1%` |
| `vh` | 视口高度的 `1%` |
| `vmin` | `vw` 与 `vh` 中较小者 |
| `vmax` | `vw` 与 `vh` 中较大者 |

它们适合需要跟随视口变化的全屏背景、超大标题和少量流式效果。不要把正文行宽、所有 padding 或关键布局尺寸都交给 `vw`，否则宽屏上容易失去尺度。

### 2.6 小视口、大视口与动态视口

移动浏览器工具栏会变化，因此同一视口可能有多种高度描述：

| 单位族 | 语义 |
| --- | --- |
| `svw` / `svh` | 小视口宽/高，通常对应工具栏展开时的较小可见区域 |
| `lvw` / `lvh` | 大视口宽/高，通常对应工具栏收起时的较大区域 |
| `dvw` / `dvh` | 动态视口宽/高，随浏览器界面变化 |

```css
.hero { min-height: 100vh; }
@supports (height: 100svh) { .hero { min-height: 100svh; } }
```

需要始终贴合当前可见区域时可以使用 `100dvh`，但它可能因工具栏动画反复改变尺寸。稳定阅读区域通常更适合 `svh` 或自然内容高度。

### 2.7 容器单位

| 单位 | 相对值 |
| --- | --- |
| `cqw` / `cqh` | 查询容器内容盒宽度/高度的 `1%` |
| `cqi` / `cqb` | 查询容器内联尺寸/块尺寸的 `1%` |
| `cqmin` / `cqmax` | `cqi` 与 `cqb` 的较小/较大值 |

```css
.card-region { container-type: inline-size; }
.card__title { font-size: clamp(1.25rem, 1rem + 2cqi, 2.25rem); }
```

没有合格查询容器时，容器单位会按小视口单位回退。需要控制具体容器边界时，仍应显式声明 `container-type`。容器查询的完整机制见[容器查询与自适应布局](../03-layout/12-container-queries.md)。

### 2.8 `fr` 简要说明

`fr` 是 Grid 轨道分配剩余空间的分数单位：

```css
.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(16rem, 2fr);
}
```

它不是普通长度，不能写 `width: 1fr` 或 `padding: 1fr`。轨道中的固定尺寸、最小尺寸会先被考虑，`fr` 再分配剩余空间。使用 `minmax(0, 1fr)` 可以避免内容最小尺寸阻止 Grid 子项收缩。

## 3. `calc()`：带类型检查的数学表达式

### 3.1 基本结构

`calc()` 的核心结构可以理解为：

```text
calc-sum    = calc-product ((+ | -) calc-product)*
calc-product = calc-value ((* | /) calc-value)*
calc-value   = 数值、长度、百分比、单位值或括号中的表达式
```

它允许：

- 加法与减法；
- 乘法与除法；
- 括号分组；
- 长度、百分比、角度、时间、数值等类型；
- `min()`、`max()`、`clamp()`、`var()` 等数学函数嵌套。

但必须遵守类型与语法规则：

1. `+` 和 `-` 两侧必须有空白。
2. 乘法和除法不要求空白，但至少一侧必须是纯数字。
3. 除数必须是数字，不能是 0 或带单位的长度。
4. 结果必须符合使用它的属性；不能把 `1rem + 10%` 用于只接受整数的地方。
5. 不能进行颜色字符串拼接，也不能直接执行函数或 JavaScript。
6. 百分比何时解析取决于属性；在包含块尺寸未确定时，不能假设总能得到像素值。

### 3.2 常见写法

```css
.main {
  inline-size: calc(100% - 2 * var(--gutter));
  margin-inline: var(--gutter);
}

.sidebar {
  inline-size: calc(100% / 3);
}

.ring {
  --ring-size: 2.75rem;
  inline-size: var(--ring-size);
  block-size: var(--ring-size);
  border: calc(var(--ring-size) / 12) solid currentColor;
}

.title {
  font-size: calc(clamp(1.25rem, 4vw, 2rem) + 0.25rem);
}
```

现代 CSS 的数学函数可以直接嵌套，外层不一定再写一次 `calc()`；为兼容较旧实现和改善可读性，也可以显式保留内层 `calc()`：

```css
.main { inline-size: calc(min(100%, 60rem) - 2rem); }
.main { inline-size: min(calc(100% - 2rem), calc(60rem - 2rem)); }
```

两条规则**完全等价**：减法是对 `min()` 的单调线性变换，可以先减再取最小值，也可以先取最小值再减，结果一致。差别只在书写清晰度，工程中选容易审阅的一种即可。

### 3.3 无效写法与反例

| 写法 | 问题 |
| --- | --- |
| `calc(100% - 1rem)` | 正确；减法两侧有空白 |
| `calc(100%-1rem)` | 无效；`-` 两侧缺少空白，可能被识别为其他记号 |
| `calc(100% / 3rem)` | 结果类型不合法；除数必须是数字 |
| `calc(2rem * 3rem)` | 得到面积类型，不能用于宽度 |
| `calc(1px / 0)` | 除数为零，计算值无效 |
| `calc(var(--gap)px)` | `var()` 不能与单位字符串拼接 |
| `width: calc(100%)` | 合法但没有实际组合意义，通常可直接写 `100%` |
| `height: calc(50% + 1rem)` | 包含块高度未确定时，百分比可能无法按预期解析 |

### 3.4 百分比与内在尺寸

`calc()` 不会让循环依赖变得可解。例如：

```css
.child { inline-size: calc(100% + 1rem); }
```

子元素会比包含块宽 `1rem`，如果父级没有溢出处理就会产生横向滚动。它适合精确补偿边框或间隙，不适合“猜一个宽度让内容挤进去”。

在不知道内容宽度时，优先考虑：

```css
.child { max-inline-size: 100%; min-inline-size: 0; }
```

或者使用 Grid/Flex 的弹性分配，而不是不断加减百分比。

## 4. `min()`、`max()` 与 `clamp()`

### 4.1 `min()`：取最小值

```css
.container {
  inline-size: min(100% - 2rem, 65ch);
}
```

它常用于“不超过某个设计上限，同时不能超过可用空间”。`min()` 内可以直接写数学表达式，空格规则与 `calc()` 一致。

### 4.2 `max()`：取最大值

```css
.sidebar {
  inline-size: max(16rem, 30%);
}
```

它常用于保证下限：内容不能因为容器变窄而低于某个可读尺寸。若空间真的小于下限，仍可能溢出，需要配合布局策略处理。

### 4.3 `clamp()`：最小值、首选值、最大值

```css
h1 {
  font-size: clamp(2rem, 5vw, 4rem);
}

.card {
  padding: clamp(1rem, 2.5vw, 2rem);
}
```

语法是 `clamp(MIN, PREFERRED, MAX)`：

- 首选值低于最小值时取最小值；
- 高于最大值时取最大值；
- 其他时候取首选值。

如果最小值大于最大值，最小值优先。因此不要把三个值写成互相矛盾的“保险”：

```css
/* 反例：MAX 小于 MIN，实际不会取到 2rem 以外的更小值 */
font-size: clamp(2rem, 1rem, 1.5rem);
```

`clamp()` 限制的是计算后的结果，不保证容器一定放得下。窄屏下 `clamp(2rem, 5vw, 4rem)` 仍是 `2rem`，长标题可能换行；这时需要调整内容结构或最小值，而不是继续缩小字号。

## 5. `env()` 与安全区

刘海、圆角和系统手势区域可能遮挡靠近视口边缘的内容。启用 `viewport-fit=cover` 后，页面可以绘制到这些区域，再通过 `env()` 读取安全区内边距：

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
```

```css
.bottom-bar {
  padding-block-end: 1rem;
  padding-inline: 1rem;
  padding-block-end: max(1rem, env(safe-area-inset-bottom));
  padding-inline-start: max(1rem, env(safe-area-inset-left));
  padding-inline-end: max(1rem, env(safe-area-inset-right));
}

.top-bar {
  padding-block-start: max(1rem, env(safe-area-inset-top));
}
```

`env()` 可以接受回退值：

```css
padding-block-end: env(safe-area-inset-bottom, 1rem);
```

但在使用 `max()` 时，更常见的写法是同时保证最小留白与设备安全区。注意：

- 安全区变量不是普通固定 padding；未处于覆盖绘制模式时，设备可能返回 0。
- 不要在页面四边盲目重复添加安全区，否则桌面和普通手机会出现不必要的留白。
- 使用逻辑属性处理左右，配合 RTL 才能让 `left`/`right` 的含义保持正确。
- 横竖屏变化时安全区也会变化，应在真实设备上测试，而不只依赖桌面模拟器。

## 6. 变量与函数组合

自定义属性保存“令牌”，数学函数负责组合。不要在变量里藏不可解释的表达式，也不要试图用 `var()` 拼接单位字符串。

```css
:root {
  --space-unit: 1rem;
  --content-limit: 70rem;
  --fluid-step: 2vw;
}

.section {
  --section-gutter: calc(var(--space-unit) * clamp(1, 4vw, 2.5));
  padding-inline: var(--section-gutter);
  inline-size: min(calc(100% - 2 * var(--section-gutter)), var(--content-limit));
  margin-inline: auto;
}
```

自定义属性默认是未注册的令牌流，浏览器不会自动把它当作“长度”或“颜色”解释。只有被替换到具体属性中、并通过该属性的语法检查后才参与计算。需要更严格的类型、初始值和继承行为时，可以使用 `@property` 注册：

```css
@property --space {
  syntax: "<length>";
  inherits: true;
  initial-value: 1rem;
}
```

注册后，`--space` 会按长度处理，过渡等场景更明确；但注册表是全局资源，组件命名应避免冲突，也不要为了少量变量无节制注册。

## 7. 响应式排版和间距方案

一个可维护的方案通常只有三层：

1. **全局根字号与间距刻度**：使用 `rem`，表达稳定的基础节奏。
2. **少量流式步长**：用 `clamp()` 让标题和主要区块随空间平滑变化。
3. **组件局部比例**：必要时使用 `em`，使组件内部尺寸随自身字号缩放。

```css
:root {
  --space-1: clamp(0.5rem, 0.45rem + 0.25vw, 0.75rem);
  --space-2: clamp(0.75rem, 0.65rem + 0.5vw, 1.25rem);
  --space-3: clamp(1rem, 0.85rem + 0.75vw, 1.75rem);

  --text-sm: clamp(0.875rem, 0.84rem + 0.18vw, 1rem);
  --text-base: clamp(1rem, 0.96rem + 0.2vw, 1.125rem);
  --text-2xl: clamp(1.5rem, 1.25rem + 1.25vw, 2.25rem);
}
```

使用时优先选择语义令牌，而不是在组件里临时计算：

```css
.card {
  padding: var(--space-2);
  font-size: var(--text-base);
}

.card__title {
  margin-block: var(--space-1) var(--space-2);
  font-size: var(--text-2xl);
}
```

### 完整示例 1：流式排版与间距

保存为 `fluid-type.html`。改变根字号或窗口宽度，观察正文、标题和卡片间距如何一起变化。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>流式排版与间距</title>
  <style>
    * { box-sizing: border-box; }

    :root {
      font-family: system-ui, sans-serif;
      color: #263238;
      background: #f5f4ef;
      --space-1: clamp(0.5rem, 0.45rem + 0.25vw, 0.75rem);
      --space-2: clamp(0.75rem, 0.65rem + 0.5vw, 1.25rem);
      --space-3: clamp(1rem, 0.85rem + 0.75vw, 1.75rem);
      --text-base: clamp(1rem, 0.96rem + 0.2vw, 1.125rem);
      --text-2xl: clamp(1.5rem, 1.25rem + 1.25vw, 2.5rem);
    }

    body { margin: 0; font-size: var(--text-base); line-height: 1.7; }

    .page {
      inline-size: min(calc(100% - 2 * var(--space-2)), 70rem);
      margin-inline: auto;
      padding-block: var(--space-3);
    }

    .page__header { margin-block-end: var(--space-3); }

    .page__title {
      max-inline-size: 20ch;
      margin: 0 0 var(--space-2);
      font-size: var(--text-2xl);
      line-height: 1.1;
      letter-spacing: -0.03em;
    }

    .page__intro { max-inline-size: 65ch; margin: 0; color: #59656c; }

    .card-grid {
      display: grid;
      gap: var(--space-2);
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr));
    }

    .card {
      min-inline-size: 0;
      padding: var(--space-2);
      border: 1px solid #d5d8d2;
      border-radius: 0.75rem;
      background: #fff;
    }

    .card__title {
      margin: 0 0 var(--space-1);
      font-size: 1.25em;
      line-height: 1.3;
    }

    .card p { margin: 0; overflow-wrap: anywhere; }

    .note {
      margin-block-start: var(--space-2);
      padding: var(--space-1) var(--space-2);
      border-inline-start: 0.25rem solid #477a68;
      color: #3e574e;
      background: #e8f0eb;
    }
  </style>
</head>
<body>
  <main class="page">
    <header class="page__header">
      <h1 class="page__title">用有限的尺度建立无限的变化</h1>
      <p class="page__intro">
        rem 保持全局节奏，clamp 提供流式范围，ch 约束阅读行宽，Grid 负责分配空间。
      </p>
    </header>

    <section class="card-grid" aria-label="单位策略">
      <article class="card">
        <h2 class="card__title">全局尺度</h2>
        <p>间距和基础字号使用 rem，尊重用户对根字号的调整。</p>
      </article>
      <article class="card">
        <h2 class="card__title">局部比例</h2>
        <p>组件标题使用 em，让它跟随组件字号一起缩放。</p>
      </article>
      <article class="card">
        <h2 class="card__title">阅读上限</h2>
        <p>正文使用 ch 作为参考，但需要结合中文与真实字体验证。</p>
      </article>
    </section>

    <p class="note">不要为每一个像素创建新令牌；少量可解释的刻度更容易维护。</p>
  </main>
</body>
</html>
```

### 完整示例 2：视口、容器与安全区

保存为 `viewport-safe-area.html`。页面同时演示 `svh`/`dvh` 的选择、`cqi` 缩放和 `env()` 安全区。安全区变量在普通桌面浏览器中通常为 0，刘海效果需要在真实设备上观察。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>视口、容器与安全区</title>
  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      font: 1rem/1.6 system-ui, sans-serif;
      color: #202a35;
      background: #eef2f5;
    }

    .app {
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr auto;
    }

    .top-bar {
      padding-block-start: max(1rem, env(safe-area-inset-top));
      padding-block-end: 1rem;
      padding-inline-start: max(1rem, env(safe-area-inset-left));
      padding-inline-end: max(1rem, env(safe-area-inset-right));
      color: #fff;
      background: #243b53;
    }

    .top-bar strong { font-size: 1.125rem; }

    main {
      inline-size: min(calc(100% - 2rem), 54rem);
      margin-inline: auto;
      padding-block: 2rem;
    }

    .gallery {
      container: gallery / inline-size;
      padding: clamp(1rem, 4cqi, 2rem);
      border-radius: 1rem;
      color: #fff;
      background: #256d5b;
    }

    .gallery__title {
      margin: 0 0 0.75rem;
      font-size: 1.5rem;
      font-size: clamp(1.5rem, calc(1rem + 4cqi), 2.75rem);
      line-height: 1.15;
    }

    .gallery__item {
      display: grid;
      gap: 0.5rem;
      margin-block-start: 1.5rem;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 10rem), 1fr));
    }

    .gallery__tile {
      display: grid;
      min-block-size: 7rem;
      place-items: center;
      border: 1px solid rgb(255 255 255 / 45%);
      border-radius: 0.5rem;
      background: rgb(255 255 255 / 10%);
    }

    .bottom-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem 1rem;
      padding-block-start: 1rem;
      padding-block-end: max(1rem, env(safe-area-inset-bottom));
      padding-inline-start: max(1rem, env(safe-area-inset-left));
      padding-inline-end: max(1rem, env(safe-area-inset-right));
      border-block-start: 1px solid #c7d1d9;
      background: #fff;
    }

    .bottom-bar button {
      min-block-size: 2.75rem;
      padding-inline: 1rem;
      border: 0;
      border-radius: 0.4rem;
      color: #fff;
      background: #243b53;
      font: inherit;
    }

    @supports (height: 100svh) {
      .app { min-height: 100svh; }
    }

    @supports (height: 100dvh) {
      .app { min-height: 100dvh; }
    }
  </style>
</head>
<body>
  <div class="app">
    <header class="top-bar"><strong>视口工具箱</strong></header>
    <main>
      <section class="gallery" aria-label="容器单位示例">
        <h1 class="gallery__title">同一组件，随容器空间缩放</h1>
        <p>标题使用 cqi，间距使用 clamp，外层页面使用动态视口高度。</p>
        <div class="gallery__item">
          <div class="gallery__tile">cqi</div>
          <div class="gallery__tile">clamp</div>
          <div class="gallery__tile">env</div>
        </div>
      </section>
    </main>
    <footer class="bottom-bar">
      <span>底部留白会避开设备安全区</span>
      <button type="button">继续</button>
    </footer>
  </div>
</body>
</html>
```

## 8. 易错点

| 易错点 | 原因与正确做法 |
| --- | --- |
| 所有字号都写死 `px` | 不尊重用户缩放和根字号；正文字号优先 `rem` 或流式 `clamp()` |
| 多层嵌套 `em` 后仍然按单层估算 | `em` 会逐层复利；局部比例用 `em`，全局尺度用 `rem` |
| 把 `ch` 当作固定字符数 | 它依赖字体中“0”的宽度，中文和不同字体结果不同 |
| 给普通宽度使用 `fr` | `fr` 主要用于 Grid 轨道分配，不是通用长度 |
| `calc()` 的 `+`/`-` 不写空格 | 这是语法要求；乘法、除法虽然可省略空格，也应保持风格统一 |
| `calc()` 中除以带单位的值 | 除数必须是数字；`100% / 3` 可以，`100% / 3rem` 不行 |
| 用 `var(--x)px` 拼接单位 | 变量不会自动补单位；在变量值中包含完整长度 |
| `clamp()` 的最小值大于最大值 | 最小值会胜出，导致实际结果不符合预期 |
| 认为 `clamp()` 能防止所有溢出 | 它只限制数值；长内容仍可能需要换行、滚动或结构调整 |
| 未声明容器却大量使用 `cqi` | 单位会回退到视口或寻找其他容器，产生意外缩放 |
| 桌面模拟器里验证安全区后直接上线 | 安全区依赖真实设备与方向；需要真机复测 |

## 9. 验证与 DevTools

1. **查看 authored value。** Styles 面板保留 `clamp()`、`calc()` 等源码；Computed 通常只显示解析后的结果，两者要结合看。
2. **检查计算值类型。** 无效声明会被划掉；若整个值突然变成 `auto` 或继承值，先检查单位类型和括号。
3. **修改根字号。** 在 DevTools 中把 `html` 字号调大，确认 `rem` 尺寸和流式排版仍可用。
4. **测试窄包含块。** 检查百分比、`calc()` 与最小宽度是否产生横向滚动。
5. **核对 `fr` 轨道。** 开启 Grid 轨道覆盖层，查看固定尺寸、最小尺寸和剩余空间如何分配。
6. **验证容器单位。** 改变查询容器宽度，确认后代最终字号按预期变化；移除容器观察小视口回退。
7. **模拟移动视口。** 切换地址栏可见状态，比较 `svh` 与 `dvh` 是否造成不同重排。
8. **真机检查安全区。** 横竖屏切换并打开底部手势区域，确认内容不被圆角、刘海或系统导航遮挡。

## 关联示例

- [流式单位与函数](../../examples/responsive/fluid-units.html)：rem/em、视口单位、`clamp()`、`min()`、`max()` 与容器单位。
- [视口高度与安全区](../../examples/responsive/safe-area-viewport.html)：动态视口、刘海安全区和 `viewport-fit=cover`。

## 10. 练习

1. 把一组固定 `px` 字号和间距迁移为 `rem` 令牌，再用 `clamp()` 为标题增加流式范围；记录最小、首选和最大值的依据。
2. 实现 `inline-size: min(calc(100% - 2rem), 65ch)` 的阅读区域，加入长 URL，验证窄屏不溢出。
3. 写五个 `calc()` 表达式，其中三个有效、两个无效；在 DevTools 中解释每条声明被接受或拒绝的原因。
4. 为一个 Grid 区域设计 `minmax(0, 1fr)` 与 `minmax(12rem, 2fr)` 两列，比较内容最小尺寸对轨道的影响。
5. 制作一个带安全区的底部操作栏，分别验证 `env()`、`max()` 和逻辑属性在普通桌面、刘海设备及 RTL 页面中的表现。

> 上一篇：[响应式设计](13-responsive-design.md)。下一篇：[变换与视觉状态](../05-advanced/15-transforms.md)。
