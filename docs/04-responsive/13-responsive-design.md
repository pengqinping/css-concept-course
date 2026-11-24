# 13 · 响应式设计

> 学习目标：用内容而不是设备名称决定断点，掌握视口、媒体查询、流式布局与响应式资源的协作方式，并避免移动端视口高度、图片选择、触控与用户偏好方面的常见问题。

## 1. 响应式不是“为手机写另一套页面”

响应式设计的核心是：**同一份语义内容，在不同空间、输入方式和用户偏好下仍能完成任务。** 它不是把桌面页面等比例缩小，也不是为每个手机型号增加一条媒体查询。

```text
内容与任务
    │
    ├─▶ 可用宽度变化 ──▶ 流式布局 + 内容断点
    ├─▶ 输入方式变化 ──▶ 触控目标 + 指针能力
    ├─▶ 视口高度变化 ──▶ 小视口/动态视口单位
    ├─▶ 屏幕密度变化 ──▶ srcset/sizes 选择资源
    └─▶ 用户偏好变化 ──▶ 动画、对比度、主题
```

先保证内容在没有断点时也能流动，再在确实出现挤压、断裂或阅读效率下降的位置增加布局变化。

## 2. 移动优先与桌面优先

### 2.1 移动优先

移动优先先写结构最简单、空间最少的布局，再用 `min-width` 逐步增强：

```css
.stack { display: grid; gap: 1rem; }

@media (width >= 48rem) {
  .stack { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
```

优点：

- 默认样式通常更简单，容易形成清晰的内容层级。
- 增强规则是在已经可用的布局上增加能力。
- 与现代 CSS 的流式布局、内在尺寸和渐进增强思路一致。

代价是复杂桌面组件可能需要多次覆盖，或者基础布局为了兼顾手机而过度简化。

### 2.2 桌面优先

桌面优先先写宽屏布局，再用 `max-width` 降级：

```css
.stack { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }

@media (width < 48rem) {
  .stack { grid-template-columns: 1fr; }
}
```

它适合维护已有桌面系统，或宽屏结构确实更复杂、需要逐层削减能力的项目。不要在一个组件里不断混合 `min-width` 与 `max-width` 覆盖，否则同一尺寸下会出现相互冲突的规则。

**选择标准是改造成本和可理解性，不是立场。** 新项目通常更适合移动优先；成熟桌面产品不必为了“正确姿势”推倒重来。整个组件尽量保持一个主要方向。

## 3. meta viewport：移动布局的入口

在移动浏览器中，没有视口声明时，页面可能先按一个约 980px 宽的布局视口渲染，再缩小显示，导致手机上文字很小。

```html
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

它的含义是：

- `width=device-width`：布局视口宽度与设备宽度匹配。
- `initial-scale=1`：初始缩放比例为 1，不额外放大或缩小。

不要用 `user-scalable=no` 或 `maximum-scale=1` 禁止缩放。这会影响低视力用户，也不会解决真正的布局问题。需要适配刘海或全面屏时，再增加 `viewport-fit=cover`，并配合安全区内边距使用；它与禁止缩放无关。

## 4. 媒体查询完整语法

### 4.1 媒体类型

```css
@media screen { /* 屏幕输出 */ }
@media print { /* 打印预览与打印 */ }
@media all { /* 所有媒体 */ }
```

实际项目常用的是 `screen`、`print` 和不限定类型。不要为每一种理论媒体类型都写样式。

### 4.2 媒体特性

```css
@media (min-width: 48rem) { /* 宽度至少 48rem */ }
@media (orientation: landscape) { /* 横屏 */ }
@media (resolution: 2dppx) { /* 至少约 2 个设备像素/ CSS 像素 */ }
@media (hover: hover) and (pointer: fine) { /* 主要输入支持悬停且精确 */ }
```

`dppx` 表示每个 CSS 像素对应的设备像素数；`1dppx` 约为标准密度，`2dppx` 常对应所谓 Retina 屏幕。高密度不意味着应显示更多内容，通常只意味着需要更清晰的图片资源。

### 4.3 范围语法

```css
@media (width >= 48rem) { /* ... */ }
@media (width < 48rem) { /* ... */ }
@media (40rem <= width < 64rem) { /* 左闭右开区间 */ }
@media (48rem < width <= 72rem) { /* 左开右闭区间 */ }
```

范围语法没有 `=`。传统 `min-width`/`max-width` 仍然有效，两种写法表达同一类条件，但现代范围语法更接近自然语言。

### 4.4 组合：`and`、`,` 与 `not`

```css
@media screen and (width >= 48rem) and (orientation: landscape) {
  /* 屏幕、宽度、方向同时满足 */
}

@media (prefers-reduced-motion: reduce), (prefers-contrast: more) {
  /* 任意一个条件满足就应用 */
}

@media not all and (monochrome) {
  /* 不是单色设备 */
}
```

逗号是“或”，不是“和”。`not` 否定的是它所在的整个媒体查询，写错位置会改变语义。

## 5. 断点由内容决定

设备列表变化快，内容也会变化。为“iPhone 15”“iPad Pro”命名断点，无法解释为什么该规则存在。

更可靠的方法：

1. 先把浏览器窗口调窄，不使用任何断点。
2. 找到内容开始溢出、标题过度换行、导航难以扫描或操作按钮互相挤压的位置。
3. 在该位置之前加入最小断点。
4. 用注释记录内容原因，而不是设备名称。

```css
/* 导航链接与品牌标识在约 42rem 处开始争夺同一行 */
@media (width >= 42rem) {
  .site-header { justify-content: space-between; }
}
```

断点不是越多越好。Grid 的 `auto-fit`、Flex 的换行、`minmax()` 和 `max-inline-size` 能消除大量无意义断点。

### 完整示例 1：内容驱动的响应式页面

保存为 `responsive-page.html`。逐渐改变窗口宽度，观察导航、卡片网格和正文列宽如何变化。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>内容驱动的响应式页面</title>
  <style>
    * { box-sizing: border-box; }

    :root {
      font-family: system-ui, sans-serif;
      color: #22313f;
      background: #f5f7fa;
      --gutter: clamp(1rem, 4vw, 2.5rem);
    }

    body { margin: 0; }

    .site-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem 1.5rem;
      padding: 1rem var(--gutter);
      color: #fff;
      background: #203a43;
    }

    .brand { font-size: 1.25rem; font-weight: 750; }

    .nav {
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem 1rem;
    }

    .nav a {
      min-block-size: 2.75rem;
      display: grid;
      place-items: center;
      color: inherit;
      text-underline-offset: 0.2em;
    }

    .hero {
      max-inline-size: 72rem;
      margin-inline: auto;
      padding: clamp(2rem, 8vw, 5rem) var(--gutter);
    }

    .hero h1 {
      max-inline-size: 18ch;
      margin: 0 0 1rem;
      font-size: clamp(2rem, 7vw, 4rem);
      line-height: 1.05;
      letter-spacing: -0.03em;
    }

    .hero p {
      max-inline-size: 58ch;
      margin: 0;
      font-size: clamp(1rem, 2vw, 1.25rem);
      color: #526574;
    }

    .card-grid {
      display: grid;
      gap: 1rem;
      max-inline-size: 72rem;
      margin-inline: auto;
      padding: 0 var(--gutter) var(--gutter);
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
    }

    .card {
      min-inline-size: 0;
      padding: 1.25rem;
      border: 1px solid #cad5dd;
      border-radius: 0.75rem;
      background: #fff;
    }

    .card h2 { margin: 0 0 0.5rem; font-size: 1.25rem; }
    .card p { margin: 0; color: #526574; overflow-wrap: anywhere; }

    .reading-column {
      max-inline-size: 65ch;
      margin-inline: auto;
      padding: clamp(2rem, 6vw, 4rem) var(--gutter);
      border-block-start: 1px solid #cad5dd;
    }

    .reading-column h2 { margin-block-start: 0; }

    /* 宽屏时让标题和摘要并排，改善长文区域的阅读效率 */
    @media (width >= 56rem) {
      .reading-column__intro {
        display: grid;
        grid-template-columns: minmax(12rem, 0.8fr) minmax(0, 1.2fr);
        gap: 2rem;
      }
    }

    /* 示例：一个真正需要组合条件的布局变化 */
    @media screen and (width >= 48rem) and (orientation: landscape) {
      .hero { padding-block-start: 4rem; }
    }

    @media (hover: hover) and (pointer: fine) {
      .card { transition: border-color 160ms ease, transform 160ms ease; }
      .card:hover { border-color: #4c7884; transform: translateY(-2px); }
    }

    @media (prefers-reduced-motion: reduce) {
      .card { transition: none; }
    }

    @media print {
      .site-header { color: #000; background: #fff; border-bottom: 1px solid #000; }
      .card { break-inside: avoid; box-shadow: none; }
      .hero { padding-block: 1rem; }
    }
  </style>
</head>
<body>
  <header class="site-header">
    <div class="brand">流式设计</div>
    <nav class="nav" aria-label="主导航">
      <a href="#guide">指南</a>
      <a href="#cards">模式</a>
      <a href="#reading">阅读</a>
    </nav>
  </header>

  <main>
    <section class="hero" id="guide">
      <h1>先让内容流动，再处理真正的冲突</h1>
      <p>响应式布局不是设备清单，而是一组可解释的空间决策。</p>
    </section>

    <section class="card-grid" id="cards" aria-label="布局模式">
      <article class="card"><h2>内在尺寸</h2><p>让 Grid 根据内容决定列数与最小宽度。</p></article>
      <article class="card"><h2>流式排版</h2><p>用 clamp 控制字号范围，同时保留用户缩放能力。</p></article>
      <article class="card"><h2>按需断点</h2><p>只在内容确实无法自然排列时改变结构。</p></article>
    </section>

    <section class="reading-column" id="reading">
      <div class="reading-column__intro">
        <h2>为阅读设计</h2>
        <p>
          正文行宽需要上限，页面留白需要弹性，卡片不能被长单词撑破。
          这些约束比某个具体屏幕尺寸更稳定。
        </p>
      </div>
    </section>
  </main>
</body>
</html>
```

## 6. 流式布局：不要写死每一列

固定宽度会让内容在小屏溢出，在宽屏留下空洞。更稳健的方式是给内容设置最小可读尺寸，再让多余空间参与分配。

```css
.content {
  inline-size: 100%;
  max-inline-size: 65ch;
  margin-inline: auto;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
}

.long-word { overflow-wrap: anywhere; }
```

`min(100%, 18rem)` 避免窄于 `18rem` 的容器仍强制产生横向滚动。Grid/Flex 子项还应考虑 `min-inline-size: 0`，否则长文本或固有内容可能拒绝收缩。

百分比、`vw`、`clamp()` 适合参与流式变化，但都需要边界。一个常见组合是：

```css
.section {
  padding-inline: clamp(1rem, 4vw, 3rem);
}
```

留白随视口增长，但不会无限变大。媒体查询则用于真正改变结构，而不是给每个属性都补一条规则。

## 7. 响应式图片：`srcset`、`sizes` 与 `picture`

### 7.1 `srcset` 的两种描述方式

宽度描述符使用 `w`，必须配合 `sizes` 告诉浏览器图片在各种视口下大约占多宽：

```html
<img
  src="photo-800.jpg"
  srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1200.jpg 1200w"
  sizes="(min-width: 48rem) 33vw, 100vw"
  width="800"
  height="450"
  alt="山间湖面的日出"
/>
```

像素密度描述符使用 `x`，适合尺寸基本固定的图片：

```html
<img
  src="avatar.jpg"
  srcset="avatar.jpg 1x, avatar@2x.jpg 2x, avatar@3x.jpg 3x"
  width="64"
  height="64"
  alt="用户头像"
/>
```

一个 `srcset` 中不要混用 `w` 与 `x`。`sizes` 不会强制下载某张图片，它只是候选信息；浏览器还会考虑设备像素比、缓存、网络和自身策略。使用 `w` 描述符却省略 `sizes` 时，浏览器通常按 `100vw` 估算，容易下载过大的图片。

### 7.2 `picture` 用于艺术指导或格式选择

```html
<picture>
  <source srcset="hero-wide.avif" type="image/avif" media="(min-width: 48rem)" />
  <source srcset="hero-wide.webp" type="image/webp" media="(min-width: 48rem)" />
  <source srcset="hero-square.webp" type="image/webp" />
  <img src="hero-square.jpg" width="800" height="800" alt="..." />
</picture>
```

`source` 按顺序匹配，第一个满足条件的来源生效。它适合：

- 手机使用竖图、桌面使用宽图的艺术指导。
- 为支持的浏览器提供 AVIF/WebP，同时保留 JPEG 回退。
- 根据透明背景、色彩能力等条件选择资源。

它不适合仅为了“换更大尺寸”而堆叠多个 `media`；尺寸选择应交给 `srcset` 与 `sizes`。

### 完整示例 2：可运行的响应式图片

示例使用内联 SVG 作为真实可加载的候选资源，因此不需要额外图片文件也能运行。实际项目应替换成经过压缩的位图或矢量资源。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>响应式图片</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; font: 1rem/1.6 system-ui, sans-serif; color: #18332b; background: #eef4f0; }

    main {
      max-inline-size: 72rem;
      margin-inline: auto;
      padding: clamp(1rem, 4vw, 2.5rem);
    }

    .media-grid {
      display: grid;
      gap: 1.5rem;
      grid-template-columns: 1fr;
    }

    @media (width >= 48rem) {
      .media-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (width >= 72rem) {
      .media-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }

    figure { margin: 0; }
    .image-frame { overflow: hidden; border-radius: 0.75rem; background: #d7e5df; }

    .fluid-image {
      display: block;
      inline-size: 100%;
      block-size: auto;
    }

    .art-directed {
      block-size: 15rem;
      inline-size: 100%;
      object-fit: cover;
    }

    .avatar { display: block; inline-size: 4rem; block-size: 4rem; border-radius: 50%; }
    figcaption { margin-block-start: 0.5rem; color: #456158; font-size: 0.9rem; }
    h1 { font-size: clamp(1.75rem, 5vw, 2.75rem); }
  </style>
</head>
<body>
  <main>
    <h1>按用途选择图片</h1>
    <div class="media-grid">
      <figure>
        <div class="image-frame">
          <img
            class="fluid-image"
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='240'%3E%3Crect width='400' height='240' fill='%23256d5b'/%3E%3Ctext x='200' y='132' text-anchor='middle' fill='white' font-size='36'%3E400w%3C/text%3E%3C/svg%3E"
            srcset="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='240'%3E%3Crect width='400' height='240' fill='%23256d5b'/%3E%3Ctext x='200' y='132' text-anchor='middle' fill='white' font-size='36'%3E400w%3C/text%3E%3C/svg%3E 400w, data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='480'%3E%3Crect width='800' height='480' fill='%23256d5b'/%3E%3Ctext x='400' y='262' text-anchor='middle' fill='white' font-size='64'%3E800w%3C/text%3E%3C/svg%3E 800w, data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='720'%3E%3Crect width='1200' height='720' fill='%23256d5b'/%3E%3Ctext x='600' y='392' text-anchor='middle' fill='white' font-size='88'%3E1200w%3C/text%3E%3C/svg%3E 1200w"
            sizes="(min-width: 72rem) 30vw, (min-width: 48rem) 45vw, 100vw"
            width="800"
            height="480"
            alt="绿色背景上标示当前候选宽度的图片"
          />
        </div>
        <figcaption>流式内容图：由 sizes 和 srcset 协商候选资源。</figcaption>
      </figure>

      <figure>
        <picture>
          <source
            media="(min-width: 48rem)"
            srcset="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='400'%3E%3Crect width='800' height='400' fill='%239b4dca'/%3E%3Ctext x='400' y='220' text-anchor='middle' fill='white' font-size='52'%3E宽图%3C/text%3E%3C/svg%3E"
          />
          <img
            class="art-directed"
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='500'%3E%3Crect width='500' height='500' fill='%239b4dca'/%3E%3Ctext x='250' y='272' text-anchor='middle' fill='white' font-size='52'%3E方图%3C/text%3E%3C/svg%3E"
            width="500"
            height="500"
            alt="根据视口选择宽图或方图的示例"
          />
        </picture>
        <figcaption>艺术指导：宽屏使用宽图，窄屏使用方图。</figcaption>
      </figure>

      <figure>
        <img
          class="avatar"
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Ccircle cx='32' cy='32' r='32' fill='%23c47f17'/%3E%3Ctext x='32' y='42' text-anchor='middle' fill='white' font-size='30'%3E1x%3C/text%3E%3C/svg%3E"
          srcset="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Ccircle cx='32' cy='32' r='32' fill='%23c47f17'/%3E%3Ctext x='32' y='42' text-anchor='middle' fill='white' font-size='30'%3E1x%3C/text%3E%3C/svg%3E 1x, data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='128' height='128'%3E%3Ccircle cx='64' cy='64' r='64' fill='%23c47f17'/%3E%3Ctext x='64' y='84' text-anchor='middle' fill='white' font-size='60'%3E2x%3C/text%3E%3C/svg%3E 2x"
          width="64"
          height="64"
          alt="固定尺寸头像的 1x 与 2x 资源"
        />
        <figcaption>固定尺寸图：使用像素密度描述符。</figcaption>
      </figure>
    </div>
  </main>
</body>
</html>
```

## 8. 字体、触控与输入方式

### 字体与文字

- 正文字号和控件字号不要写死过小；iOS Safari 在输入框字号小于约 `16px` 时可能自动放大页面。
- 使用相对单位和 `clamp()` 控制流式字号，但保留用户调整默认字号后的可读性。
- 避免用固定高度承载文本；长文案、翻译和用户字体设置都会改变高度。
- 自定义字体应设置合理的 `font-display`，并让回退字体的度量尽量接近，减少布局跳动。
- 不要为了“统一”而禁用系统的文字自动缩放，除非有明确证据和更严重的可用性问题。

### 触控与指针

```css
.icon-button {
  display: inline-grid;
  min-inline-size: 2.75rem;
  min-block-size: 2.75rem;
  place-items: center;
}
```

`2.75rem` 约为 44px，是移动端常见的舒适触控目标。WCAG 2.2 的 AA 级目标尺寸要求是至少 24×24 CSS 像素，并允许通过间距等方式满足特定例外；不要把这个最低要求误当成最佳体验。

用 `@media (hover: hover) and (pointer: fine)` 承载只在鼠标环境中有意义的悬停效果。触屏也会报告某种 `pointer` 能力，仅凭 `pointer: coarse` 不能穷尽所有设备。

## 9. 方向、密度与用户偏好

媒体查询也可以响应用户主动选择或环境能力：

```css
@media (orientation: portrait) {
  .gallery { grid-template-columns: 1fr; }
}

@media (prefers-color-scheme: dark) {
  :root { color-scheme: dark; }
}

@media (prefers-reduced-motion: reduce) {
  .carousel__track { scroll-behavior: auto; }
  .spinner { animation: none; }
}

@media (prefers-contrast: more) {
  .card { border-color: currentColor; }
}
```

方向只能说明视口当前相对方向，不能说明设备一定有足够空间；横屏手机可能比竖屏平板更窄。密度适合选择图片资源，不应直接决定信息密度或字号。

## 10. 移动端视口与 `100vh` 陷阱

移动浏览器的地址栏、工具栏会展开或收起，传统 `100vh` 在很多环境中指**大视口**，因此可能高于当前实际可见区域，底部内容被遮住。

```text
100vh：历史上常按大视口计算
100svh：小视口，工具栏展开时的稳定高度
100lvh：大视口，工具栏收起时的最大高度
100dvh：动态视口，随工具栏变化
```

按用途选择：

```css
/* 回退 */
.app { min-height: 100vh; }

/* 希望底部导航初始就完整可见 */
@supports (height: 100svh) {
  .app { min-height: 100svh; }
}

/* 确实希望始终贴合当前可见区域 */
@supports (height: 100dvh) {
  .app { min-height: 100dvh; }
}
```

`100dvh` 会在工具栏变化时反复改变高度，可能引起内容重排、滚动位置跳动和图片重新布局。阅读页通常更适合 `svh` 或让内容自然增长；全屏地图、聊天输入区才更需要动态高度。

还要注意：

- `vh` 与动态视口单位描述视口，不等于键盘弹出后的可用空间。
- 固定定位元素仍可能被软键盘遮挡，需要真实设备测试。
- `vw` 通常能规避纵向工具栏问题，但仍不能替代响应式断点。
- 不要用 `height: 100dvh` 强制裁切所有内容；应使用 `min-height` 并允许溢出。

## 11. 易错点

| 易错点 | 原因与正确做法 |
| --- | --- |
| 为具体手机型号命名断点 | 设备层出不穷；根据内容开始失效的位置命名和设断点 |
| 只写桌面断点，没有基础移动布局 | 不支持或未命中断点时页面不可用；先完成基础布局 |
| 禁止用户缩放 | 伤害可访问性；修复布局，而不是限制手势 |
| 在 `srcset` 中混用 `w` 和 `x` | 两种描述符不能混用；按内容图或固定图选择 |
| 认为 `sizes` 指定了实际下载宽度 | 它只是候选提示；浏览器仍会考虑 DPR 和缓存等 |
| 高 DPR 下把所有字号放大 | 密度影响资源清晰度，不直接决定文字大小 |
| 到处使用 `100vh` 做移动端满屏 | 工具栏可能遮挡内容；根据稳定性需求选择 `svh`/`dvh` |
| 只测设备方向，不测可用空间 | 横屏手机可能比竖屏平板更窄；尺寸与内容才是依据 |
| 用固定高度解决文字溢出 | 翻译、缩放、用户字体都会破坏布局；让容器随内容增长 |

## 12. 验证与 DevTools

1. **确认 meta viewport。** 在 Elements 中检查声明，关闭设备模拟后用窄窗口复测。
2. **拖动宽度找内容断点。** 观察标题、导航、图片和按钮何时开始挤压，再核对媒体查询是否在合适位置生效。
3. **查看当前命中条件。** Styles 面板会标记媒体查询；确认 `and`、逗号和范围边界没有写错。
4. **检查图片候选。** Network 面板按宽度、DPR 和缓存状态查看实际下载资源；Elements 中查看 `currentSrc`。
5. **模拟不同输入。** DevTools 设备工具栏可模拟触控与移动视口；真实设备还要测试横竖屏、软键盘和安全区。
6. **测试文字与缩放。** 放大浏览器到 200%，桌面端再验证 400% 时约 320 CSS 像素宽的重排表现。
7. **模拟用户偏好。** Rendering 面板可模拟 reduced motion、color scheme 等；同时检查系统级设置是否被尊重。
8. **测试打印。** 使用打印预览确认导航隐藏、卡片不被切断、颜色在单色打印中仍可辨认。

## 关联示例

- [媒体特性与用户偏好](../../examples/responsive/media-preference.html)：hover/pointer、深色、对比度、减弱动态和强制颜色。
- [视口高度与安全区](../../examples/responsive/safe-area-viewport.html)：`svh` / `lvh` / `dvh` 与 `env()`。

## 13. 练习

1. 将一个固定宽度的页面改为移动优先，在不使用设备名称的前提下记录三个内容断点及触发原因。
2. 用 Grid 的 `auto-fit` 与 `minmax()` 实现卡片网格，再放入超长 URL，确保窄屏不横向溢出。
3. 为一张内容图片编写 `srcset`/`sizes`，并在 Network 面板比较 1x、2x 和不同视口下的实际请求。
4. 实现一个移动端底部操作栏，分别测试 `100vh`、`100svh` 和 `100dvh` 在地址栏收起时的表现。
5. 为组件补充 `prefers-reduced-motion` 与 `(hover: hover) and (pointer: fine)`，验证触屏不会依赖悬停。

> 上一篇：[容器查询与自适应布局](../03-layout/12-container-queries.md)。下一篇：[现代 CSS 单位与函数](14-units-functions.md)。
