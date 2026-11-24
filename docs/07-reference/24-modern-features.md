# 24 · 现代 CSS 特性

> 学习目标：理解原生嵌套与 `@scope` 如何组织选择器，锚点定位如何替代部分坐标计算，`@starting-style` 如何补全进入/退出过渡，滚动时间轴如何把动画交给滚动位置，以及视图过渡和 Houdini 如何扩展 CSS。所有新特性都以“先验证、再增强、保留降级”为使用前提。

## 1. 现代 CSS 的正确使用姿势：能力检测 + 渐进增强

现代特性往往呈现三种状态：

1. **完全支持**：可以使用；
2. **解析支持但行为不完整**：`CSS.supports()` 为真，实际仍有差异；
3. **不支持**：整条规则或某个值被忽略。

因此不能把“认识属性名”当作“功能可用”。推荐结构是：

```css
/* 1. 所有浏览器都能工作的基础状态 */
.card {
  background: #eef1f6;
  color: #172033;
}

/* 2. 支持后再增加新能力 */
@supports (animation-timeline: view()) {
  .card {
    animation: reveal linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 100%;
  }
}
```

JS API 还要单独检测：

```js
console.log({
  nestedSelector: CSS.supports("selector(&)"),
  anchor: CSS.supports("anchor-name: --card"),
  viewTimeline: CSS.supports("animation-timeline: view()"),
  scrollTimeline: CSS.supports("animation-timeline: scroll()"),
  discreteTransition: CSS.supports(
    "transition",
    "opacity 180ms allow-discrete",
  ),
  viewTransitionName: CSS.supports(
    "view-transition-name",
    "hero",
  ),
  viewTransitionAPI: "startViewTransition" in document,
  paintWorklet: "paintWorklet" in CSS,
});
```

`@supports` 无法直接证明 `@scope`、`@starting-style` 或 View Transition 的完整运行行为。对于 API，可以检测 `document.startViewTransition`、`CSS.paintWorklet`；对于纯 CSS at-rule，应结合兼容表、真实页面和开发工具验证。

## 2. CSS 原生嵌套与 `&`

### 2.1 它解决什么问题

嵌套把组件内部规则收拢在一起，减少重复类名，并让状态规则靠近组件定义。它不是新的作用域，也不会自动降低选择器权重。

```css
.card {
  padding: 1rem;
  border: 1px solid #d5d9e0;
  border-radius: 0.6rem;

  & > h2 {
    margin-block: 0 0.5rem;
    font-size: 1.25rem;
  }

  & > a {
    color: #2548bd;
  }

  &:hover,
  &:focus-within {
    border-color: #3157d5;
  }
}
```

大致等价于：

```css
.card {
  /* ... */
}

.card > h2 {
  /* ... */
}

.card > a {
  /* ... */
}

.card:hover,
.card:focus-within {
  /* ... */
}
```

### 2.2 `&` 的三种位置

```css
.card {
  /* 当前元素本身的状态 */
  &:hover {
    outline: 2px solid #3157d5;
  }

  /* 当前元素的后代 */
  & .title {
    font-weight: 700;
  }

  /* 当前元素作为选择器的一部分 */
  .theme-dark & {
    background: #171a21;
    color: #f4f6fa;
  }
}
```

- `&:hover` 匹配 `.card:hover`，不是 `.card :hover`。
- `.theme-dark &` 大致成为 `.theme-dark .card`。
- 不写 `&` 的 `a { … }` 会成为后代选择器 `.card a`。
- `&` 不能解决所有选择器组合问题，尤其涉及伪元素时不要依赖难以理解的变换。

### 2.3 特异性仍然是级联核心

嵌套选择器的特异性类似放入 `:is()`：取内部列表中最高的特异性，而不是把每个类简单相加到失控。但它不会让规则自动“组件隔离”。

**反例**：

```css
/* 嵌套让规则看起来局部，实际仍会命中所有后代 */
.card {
  & button {
    padding: 0.5rem;
  }
}
```

如果组件内嵌了另一个组件，这条规则仍可能影响内部按钮。现代原生嵌套不要求 `@nest`；如果必须兼容很旧的构建链，应由编译器处理，而不是手写预处理语法。

## 3. `@scope`：按 DOM 子树限定规则

### 3.1 根、下限与“甜甜圈”

```css
@scope (.article) {
  img {
    border: 2px solid #3157d5;
  }
}

@scope (.article) to (figure) {
  img {
    border: 2px solid #16805a;
  }
}
```

第一个 scope 选中 `.article` 内的图片；第二个 scope 选中 `.article` 内、但不进入 `figure` 子树的图片。上限包含 scope root，下限默认排除 limit 元素及其子树，形成“甜甜圈”。

```text
.article（scope root，包含）
├─ p
│  └─ img       ✔ 可匹配
├─ figure（scope limit，默认排除）
│  └─ img       ✘ 不匹配
└─ footer
   └─ img       ✔ 可匹配
```

可以用 `> *` 调整边界包含性：

```css
@scope (.article > *) to (figure > *) {
  img {
    /* root 本身与 figure 本身都排除，figure 的后代反而包含 */
  }
}
```

### 3.2 `:scope` 与作用域特异性

```css
@scope (.theme-card) {
  :scope {
    padding: 1rem;
    border-radius: 0.6rem;
  }

  & a {
    color: #2548bd;
  }
}
```

- 在 scope 内，`:scope` 指向 scope root。
- bare selector 和 `&` 的行为类似前面隐式加了零特异性的 `:where(:scope)`。
- 显式写 `:scope` 会引入类级别特异性。
- 浏览器与版本对 `&` 在 scope 中的处理曾有差异，复杂级联必须实测。

scope 不是样式沙箱：`color`、`font-family` 等继承属性仍可能越过下限影响子树外部。它也不能用 `:scope + p` 逃出 scope 去选择外部兄弟节点。

### 3.3 作用域邻近性

嵌套的相同主题发生冲突时，离元素更近的 scope 优先；这发生在特异性、`!important`、cascade layers 等更高优先级规则之后。

```text
.light-theme
└─ .dark-theme
   └─ .light-theme
      └─ p  → 最近的 light-theme 规则优先
```

### 3.4 完整示例：嵌套 + scope 组织一张卡片

```html
<article class="theme-card">
  <header class="theme-card__header">
    <p class="eyebrow">CSS 组件</p>
    <h2>可维护的卡片</h2>
  </header>
  <p>作用域限定选择器范围，但不替代继承与级联。</p>
  <aside class="theme-card__note">
    <p>这个备注使用独立的内部样式。</p>
  </aside>
  <a href="#details">查看详情</a>
  <figure>
    <div class="placeholder" aria-hidden="true">图片</div>
    <figcaption>图片说明不属于正文强调色。</figcaption>
  </figure>
</article>
```

```css
.theme-card {
  max-inline-size: 38rem;
  padding: 1.2rem;
  border: 1px solid #c8ced8;
  border-radius: 0.75rem;
  background: #fff;
  color: #172033;
}

@scope (.theme-card) {
  :scope {
    container-type: inline-size;
  }

  .eyebrow {
    margin: 0;
    color: #525c6b;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  h2 {
    margin-block: 0.3rem 0.8rem;
  }

  & > a {
    display: inline-block;
    margin-block: 0.8rem;
    color: #2548bd;
    font-weight: 650;
  }

  .theme-card__note {
    padding: 0.8rem;
    border-inline-start: 3px solid #3157d5;
    background: #eef3ff;
  }

  figure {
    margin: 1rem 0 0;
  }
}

@scope (.theme-card) to (figure) {
  & > p,
  & > a {
    line-height: 1.65;
  }
}

.placeholder {
  display: grid;
  place-items: center;
  min-block-size: 8rem;
  background: #e3e6eb;
  color: #525c6b;
}

figcaption {
  padding-block-start: 0.4rem;
  color: #525c6b;
  font-size: 0.875rem;
}
```

不支持 `@scope` 时，基础 `.theme-card` 外观仍存在，但部分内部样式不会应用。不要把关键布局或可读性完全交给 scope；需要时同时提供普通选择器降级。

## 4. 锚点定位：让浮层跟随元素，而不是跟随手算坐标

### 4.1 三个角色

- **anchor**：被跟随的元素，用 `anchor-name: --name` 命名；
- **positioned element**：使用 `position: absolute` 或 `fixed` 的浮层；
- **关联**：浮层通过 `position-anchor: --name` 指向 anchor。

```text
              3 × 3 position-area 网格
              ┌──────┬──────┬──────┐
              │ top  │ top  │ top  │
              │ left │      │ right│
              ├──────┼──────┼──────┤
              │left  │anchor│right │
              ├──────┼──────┼──────┤
              │bottom│bottom│bottom│
              │left  │      │right│
              └──────┴──────┴──────┘
```

仅写 `anchor-name` 与 `position-anchor` 不会自动摆放浮层，还必须使用 `position-area` 或 `anchor()`。

### 4.2 `position-area` 与 `anchor()`

`position-area` 把浮层放到 anchor 周围的网格区域：

```css
.menu {
  position: absolute;
  position-anchor: --menu-trigger;
  position-area: bottom span-right;
  margin-block-start: 0.5rem;
}
```

`anchor()` 返回 anchor 某条边或尺寸对应的长度，可带 fallback：

```css
.tooltip {
  position: absolute;
  position-anchor: --tip;
  inset-block-start: anchor(bottom, 4rem);
  inset-inline-start: anchor(start, 0);
}
```

`anchor-size()` 可把浮层尺寸与 anchor 关联：

```css
.same-width {
  inline-size: anchor-size(width, 12rem);
}
```

fallback 值不是“无锚点时自动换一套布局”的完整策略，只是函数无法解析时的值。基础定位仍应独立可用。

### 4.3 名称冲突与 `anchor-scope`

`anchor-name` 使用 dashed-ident，例如 `--card-1`。同一作用域出现重复名称时，默认可能按源码顺序解析，导致一个浮层意外绑定最后一个 anchor。

```css
.list-item {
  anchor-name: --item;
  anchor-scope: --item;
}
```

`anchor-scope` 可把名称限制在相关子树内，但支持与细节需逐项验证。动态列表更应确保名称唯一，或在每个列表项内建立独立作用域。

### 4.4 `position-try`、fallback 与 `@position-try`

```css
.menu {
  position-try: flip-block, flip-inline, flip-block flip-inline;
}
```

浏览器按顺序尝试：

1. 初始位置溢出；
2. 尝试 `flip-block`；
3. 尝试 `flip-inline`；
4. 尝试两个轴同时翻转；
5. 都不行时回到默认位置，或按 `position-visibility` 等策略隐藏。

`position-try` 是简写，可设置 `position-try-fallbacks` 与 `position-try-order`。只关心兼容旧实现时可重复声明 longhand：

```css
.menu {
  position-try-fallbacks:
    flip-block,
    flip-inline,
    flip-block flip-inline;
}
```

命名选项可封装更完整的候选位置：

```css
@position-try --compact-menu {
  position-area: bottom span-right;
  inline-size: min(14rem, calc(100vw - 2rem));
}

.menu {
  position-try-fallbacks: --compact-menu, flip-block;
}
```

候选方案不是无限重排引擎。浮层太大、没有可用空间、滚动容器裁剪或安全区域受限时，仍可能无法完整显示。

### 4.5 完整示例：带边缘翻转的提示框

```html
<div class="anchor-demo">
  <p>把页面滚动到边缘，提示框会尝试翻转。</p>
  <button class="tip-trigger" type="button" aria-describedby="tip">
    悬停或聚焦查看说明
  </button>
  <div class="tip" id="tip" role="tooltip">
    这里的内容跟随按钮，并使用 CSS 锚点定位。
  </div>
</div>
```

```css
.anchor-demo {
  min-block-size: 65vh;
  padding: 2rem 1rem;
}

.tip-trigger {
  position: relative;
  anchor-name: --tip-anchor;
  padding: 0.65rem 0.9rem;
  border: 1px solid #2548bd;
  border-radius: 0.4rem;
  background: #eef3ff;
  color: #172033;
  font: inherit;
  cursor: help;
}

/* 基础定位：没有锚点定位时仍然可读 */
.tip {
  position: absolute;
  inset-block-start: calc(100% + 0.5rem);
  inset-inline-start: 0;
  inline-size: min(16rem, calc(100vw - 2rem));
  padding: 0.7rem 0.8rem;
  border-radius: 0.4rem;
  background: #172033;
  color: #fff;
  font-size: 0.9rem;
  line-height: 1.5;
  visibility: hidden;
  opacity: 0;
  transition: opacity 120ms ease;
}

@supports (anchor-name: --tip-anchor) {
  .tip {
    position: fixed;
    inset: auto;
    position-anchor: --tip-anchor;
    position-area: bottom span-right;
    margin-block-start: 0.5rem;
    position-try-fallbacks:
      flip-block,
      flip-inline,
      flip-block flip-inline;
  }
}

.tip-trigger:hover + .tip,
.tip-trigger:focus-visible + .tip {
  visibility: visible;
  opacity: 1;
}

.tip-trigger:focus-visible {
  outline: 3px solid #3157d5;
  outline-offset: 3px;
}
```

这个提示框通过相邻选择器显示。真实产品若需要 Esc 关闭、悬停延迟、支持触摸或动态内容，应由 JS 组件补齐；锚点定位只负责几何关系。

## 5. `@starting-style` 与离散属性过渡

### 5.1 为什么普通 transition 不够

```css
.panel {
  opacity: 0;
}

.panel.is-open {
  opacity: 1;
  transition: opacity 180ms ease;
}
```

打开时通常能过渡，但从 `display: none` 变为可见时，浏览器没有可插值的“前一个渲染状态”。`@starting-style` 提供首次进入的起点：

```css
@starting-style {
  .panel.is-open {
    opacity: 0;
  }
}
```

三个状态要分开理解：

```text
默认/退出状态         进入起点              打开状态
opacity: 0      →    opacity: 0      →    opacity: 1
translate: 0     →    translate: 0 -1rem → translate: 0
display: none    →    display: block   →   display: block
```

### 5.2 离散属性与 `allow-discrete`

`display`、`overlay` 等属性的值不是连续数字，不能像 `opacity` 一样插值。`transition-behavior: allow-discrete` 允许这类属性参与过渡。

- 普通离散属性通常在 50% 切换；
- `display: none` → 可见值在 0% 切换，保证进入过程有内容；
- 可见值 → `display: none` 在 100% 切换，保证退出过程不提前消失；
- `overlay` 可让 popover/dialog 延迟退出 top layer，直到退出动画结束。

`transition-behavior` 的初始值是 `normal`。并非所有浏览器都支持 `allow-discrete`，不要把包含它的简写当作唯一 transition 声明：

```css
.toast {
  /* 老浏览器可解析的基础声明 */
  transition:
    opacity 180ms ease,
    translate 180ms ease,
    display 180ms,
    overlay 180ms;

  /* 支持 allow-discrete 时覆盖简写 */
  transition:
    opacity 180ms ease,
    translate 180ms ease,
    display 180ms allow-discrete,
    overlay 180ms allow-discrete;
}
```

`transition` 简写会重置 `transition-behavior`，声明顺序很重要。也可以先写简写，再单独写 `transition-behavior: allow-discrete`。

### 5.3 `@starting-style` 的顺序与嵌套

独立 `@starting-style` 与目标规则具有相同来源、相同特异性时，后出现的声明获胜。因此通常把目标规则写在前面，把 starting-style 放在后面。

```css
.panel {
  opacity: 0;
  transition: opacity 180ms ease;
}

.panel.is-open {
  opacity: 1;
}

@starting-style {
  .panel.is-open {
    opacity: 0;
  }
}
```

也可以嵌套书写：

```css
.panel {
  opacity: 0;
  transition: opacity 180ms ease;

  &.is-open {
    opacity: 1;

    @starting-style {
      opacity: 0;
    }
  }
}
```

`@starting-style` 服务于 transition，不是 `@keyframes` 动画的替代品。

### 5.4 完整示例：可退场的 popover 通知

```html
<button type="button" popovertarget="notice">显示通知</button>

<div id="notice" popover class="toast" role="status">
  <strong>设置已保存</strong>
  <p>你可以继续编辑个人资料。</p>
  <button type="button" popovertarget="notice" popovertargetaction="hide">
    关闭
  </button>
</div>
```

```css
.toast {
  position: fixed;
  inset: auto 1rem 1rem auto;
  inline-size: min(20rem, calc(100% - 2rem));
  margin: 0;
  padding: 1rem;
  border: 1px solid #c8ced8;
  border-radius: 0.6rem;
  background: #fff;
  color: #172033;
  box-shadow: 0 12px 32px rgb(16 24 40 / 20%);
  opacity: 0;
  translate: 0 0.75rem;
  transition:
    opacity 180ms ease,
    translate 180ms ease,
    display 180ms,
    overlay 180ms;
  transition:
    opacity 180ms ease,
    translate 180ms ease,
    display 180ms allow-discrete,
    overlay 180ms allow-discrete;
}

.toast:popover-open {
  opacity: 1;
  translate: 0;
}

.toast::backdrop {
  background: transparent;
}

@starting-style {
  .toast:popover-open {
    opacity: 0;
    translate: 0 0.75rem;
  }
}

.toast p {
  margin-block: 0.4rem 0.8rem;
}

.toast button {
  padding: 0.45rem 0.7rem;
  border: 1px solid #767e8c;
  border-radius: 0.35rem;
  background: #fff;
  color: inherit;
  font: inherit;
}

@media (prefers-reduced-motion: reduce) {
  .toast {
    translate: none;
    transition-duration: 0.01ms;
  }
}
```

不支持离散过渡时，通知仍能打开和关闭，只是可能突然出现或消失。不要为了动画延迟关键错误提示，也不要让 `overlay` 过渡把已关闭的 UI 长时间留在顶层。

## 6. 滚动驱动动画：`view()`、`scroll()` 与 `animation-range`

### 6.1 两种时间轴

- `scroll()`：动画进度由滚动容器的滚动位置决定，适合阅读进度条；
- `view()`：动画进度由元素进入、位于、离开 scrollport 的过程决定，适合卡片揭示。

```css
.progress__bar {
  animation: grow linear both;
  animation-timeline: scroll(root block);
}

.reveal {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

`animation` 简写可能重置 `animation-timeline` 与 `animation-range`，所以通常先写简写，再写时间轴和范围。滚动停止时动画暂停；向上滚动会反向推进。

### 6.2 时间轴范围图

```text
向下滚动方向
                         view() 的命名范围
┌─────────────────────────────────────────────────────┐
│ entry 0%                                            │
│   元素开始进入 scrollport 底部                       │
│                    ↓                                 │
│ entry 100%                                          │
│   元素完全进入（或先到达 scrollport 顶部）            │
│                    ↓                                 │
│ contain / exit 0% 附近                               │
│                    ↓                                 │
│ exit 100%                                           │
│   元素完全离开 scrollport 顶部                       │
└─────────────────────────────────────────────────────┘
```

- `cover`：完整范围，从开始进入到完全离开；
- `contain`：元素位于 scrollport 内、可完全包含的阶段；
- `entry`：进入过程，范围不超过 scrollport；
- `exit`：离开过程；
- `entry-crossing` / `exit-crossing`：元素比 scrollport 更大时，完整跨越边界的进入/离开过程。

`animation-range: entry 0% entry 100%` 表示只让动画在进入阶段运行。还可以写百分比或长度 inset，例如 `entry 10% entry 90%`。元素比容器大时，`entry` 与 `entry-crossing` 的结果可能明显不同。

命名滚动时间轴适合局部容器：

```css
.gallery {
  overflow-x: auto;
  scroll-timeline: --gallery x;
}

.gallery__bar {
  animation: grow linear both;
  animation-timeline: --gallery;
}
```

命名时间轴、范围等子特性应分别检测，不能只验证 `animation-timeline` 属性名。

### 6.3 完整示例：阅读进度与进入视口卡片

```html
<div class="reading-progress" aria-hidden="true">
  <div class="reading-progress__bar"></div>
</div>

<main class="story">
  <h1>滚动驱动的页面</h1>
  <p>向下滚动，顶部进度条与卡片揭示都由滚动位置控制。</p>

  <article class="reveal-card">
    <h2>01 · 进入</h2>
    <p>卡片从下方淡入，动画只在 entry 范围运行。</p>
  </article>

  <article class="reveal-card">
    <h2>02 · 包含</h2>
    <p>停止滚动时动画也会暂停，不会自动继续播放。</p>
  </article>

  <article class="reveal-card">
    <h2>03 · 离开</h2>
    <p>反向滚动时，时间轴进度也会反向。</p>
  </article>

  <article class="reveal-card">
    <h2>04 · 降级</h2>
    <p>不支持时，所有内容仍以完整可读状态显示。</p>
  </article>
</main>
```

```css
.reading-progress {
  position: sticky;
  inset-block-start: 0;
  z-index: 10;
  block-size: 4px;
  background: #dbe1ec;
}

.reading-progress__bar {
  block-size: 100%;
  background: #3157d5;
  transform: scaleX(1);
  transform-origin: left center;
}

.story {
  max-inline-size: 46rem;
  margin-inline: auto;
  padding: 2rem 1rem 50vh;
}

.story > h1,
.story > p {
  margin-block-end: 2rem;
}

.reveal-card {
  min-block-size: 14rem;
  margin-block: 3rem;
  padding: 1.5rem;
  border: 1px solid #c8ced8;
  border-radius: 0.75rem;
  background: #fff;
  color: #172033;
}

@keyframes grow {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

@keyframes card-reveal {
  from {
    opacity: 0;
    translate: 0 2rem;
  }
  to {
    opacity: 1;
    translate: 0;
  }
}

@supports (animation-timeline: scroll(root)) {
  .reading-progress__bar {
    animation: grow linear both;
    animation-timeline: scroll(root block);
  }
}

@supports (animation-timeline: view()) {
  .reveal-card {
    animation: card-reveal linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .reading-progress__bar,
  .reveal-card {
    animation: none;
  }
}
```

基础状态 deliberately 保持可见。若阅读进度是核心功能，应在不支持时用 JS 更新进度条，而不是让静态满条误导用户。滚动动画优先使用 `transform`、`opacity`、`filter` 等可合成属性，避免每帧触发布局。

## 7. 滚动交互：snap、overscroll 与滚动条

### 7.1 `scroll-snap`：定义停止点，不是分页逻辑

```css
.rail {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: min(82%, 22rem);
  gap: 1rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 1rem;
  overscroll-behavior-inline: contain;
  scrollbar-width: thin;
  scrollbar-color: #7c879b #eef1f6;
}

.rail > * {
  scroll-snap-align: center;
  scroll-snap-stop: always;
}
```

- `scroll-snap-type` 定义在滚动容器上；
- `scroll-snap-align` 定义在项目上，常用 `start`、`center`、`end`；
- `scroll-snap-stop: always` 阻止快速滑动跳过该停止点，但过多使用会让滚动显得迟钝；
- `mandatory` 总会吸附，`proximity` 更宽松；
- `scroll-padding` 考虑容器 padding/固定遮挡，避免项目贴边或被遮住。

### 7.2 `overscroll-behavior`：控制滚动链

```css
.drawer__content {
  overflow-y: auto;
  overscroll-behavior: contain;
}
```

`contain` 阻止滚动传播到祖先滚动容器，减少抽屉或弹层滚动到底后带动背景的情况。`none` 还会抑制默认 overscroll 效果。它不是背景滚动锁的完整替代，也不保证所有平台都关闭浏览器级下拉刷新。

### 7.3 `scrollbar-width` / `scrollbar-color`

```css
.panel {
  overflow: auto;
  scrollbar-width: thin;       /* auto | thin | none */
  scrollbar-color: #7c879b #eef1f6;
}
```

标准属性比 `::-webkit-scrollbar` 更适合跨引擎主题化，但不同平台可能采用系统覆盖层滚动条，实际可见效果并不完全一致。不要用 `scrollbar-width: none` 隐藏唯一的滚动提示；如果隐藏，应提供清晰的替代导航与焦点样式。

### 7.4 完整示例：可键盘操作的吸附卡片轨道

```html
<section class="rail-section" aria-labelledby="rail-title">
  <h2 id="rail-title">选择课程</h2>
  <div class="rail-nav">
    <button type="button" id="rail-prev" aria-label="上一组课程">←</button>
    <button type="button" id="rail-next" aria-label="下一组课程">→</button>
  </div>

  <div class="rail" tabindex="0" aria-label="课程列表，可横向滚动">
    <article class="course">CSS 基础</article>
    <article class="course">布局系统</article>
    <article class="course">响应式设计</article>
    <article class="course">动效与交互</article>
    <article class="course">工程实践</article>
  </div>
</section>

<script>
  const rail = document.querySelector(".rail");

  document.querySelector("#rail-prev").addEventListener("click", () => {
    rail.scrollBy({ left: -rail.clientWidth * 0.85, behavior: "smooth" });
  });

  document.querySelector("#rail-next").addEventListener("click", () => {
    rail.scrollBy({ left: rail.clientWidth * 0.85, behavior: "smooth" });
  });
</script>
```

```css
.rail-section {
  max-inline-size: 52rem;
  margin-inline: auto;
  padding: 2rem 1rem;
}

.rail-nav {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-block-end: 0.8rem;
}

.rail-nav button {
  inline-size: 2.5rem;
  block-size: 2.5rem;
  border: 1px solid #767e8c;
  border-radius: 0.4rem;
  background: #fff;
  color: #172033;
  font: inherit;
  cursor: pointer;
}

.rail {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: min(82%, 22rem);
  gap: 1rem;
  padding: 0.5rem 1rem 1rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 1rem;
  overscroll-behavior-inline: contain;
  scrollbar-width: thin;
  scrollbar-color: #7c879b #eef1f6;
}

.rail:focus-visible,
.rail-nav button:focus-visible {
  outline: 3px solid #3157d5;
  outline-offset: 3px;
}

.course {
  display: grid;
  place-items: center;
  min-block-size: 12rem;
  border: 1px solid #c8ced8;
  border-radius: 0.7rem;
  background: #eef3ff;
  color: #172033;
  font-size: 1.2rem;
  font-weight: 700;
  scroll-snap-align: center;
  scroll-snap-stop: always;
}

@media (prefers-reduced-motion: reduce) {
  .rail {
    scroll-behavior: auto;
  }
}
```

这个示例的按钮使用平滑滚动；生产项目应在减少动态效果偏好下改为自动滚动，并在首尾禁用按钮或给出状态。

## 8. View Transitions：旧视图与新视图之间的过渡

### 8.1 它不是普通 transition

View Transition API 会捕获旧状态、执行 DOM 更新、捕获新状态，再用一组伪元素播放过渡。它适合“状态确实改变”的页面切换，不适合每一个 hover 或每个属性变化。

```text
startViewTransition(update)
        │
        ├─ 捕获旧快照
        ├─ 执行 update()
        ├─ 捕获新状态
        ├─ 构建伪元素树并播放动画
        └─ 清理快照，finished 完成
```

伪元素树：

```text
::view-transition
└─ ::view-transition-group(root)
   └─ ::view-transition-image-pair(root)
      ├─ ::view-transition-old(root)
      └─ ::view-transition-new(root)
```

每个拥有唯一 `view-transition-name` 的元素会多出一组对应伪元素。`root` 是默认整页快照；old 是静态旧快照，new 是新视图区域。

### 8.2 `document.startViewTransition()` 与 CSS 分工

```js
const update = () => {
  title.textContent = "新标题";
};

if (document.startViewTransition) {
  document.startViewTransition(update);
} else {
  update();
}
```

CSS 负责 `view-transition-name` 与 `::view-transition-*` 动画；JS 负责触发和 DOM 更新。两者同名元素必须在同一时刻唯一，否则 `ready` 可能拒绝，过渡被跳过。

### 8.3 完整示例：内容切换与共享标题元素

```html
<div class="view-demo">
  <div class="view-demo__actions">
    <button type="button" data-view="intro" aria-pressed="true">介绍</button>
    <button type="button" data-view="detail" aria-pressed="false">详情</button>
  </div>

  <article class="view-demo__panel" aria-live="polite">
    <p id="view-eyebrow" class="view-demo__eyebrow">概览</p>
    <h1 id="view-title">可维护的界面状态</h1>
    <p id="view-copy">切换按钮会在支持的浏览器中播放视图过渡。</p>
  </article>
</div>

<script>
  const views = {
    intro: {
      eyebrow: "概览",
      title: "可维护的界面状态",
      copy: "DOM 更新由 JavaScript 执行，过渡动画由 CSS 定义。",
    },
    detail: {
      eyebrow: "详情",
      title: "先保证功能，再增加动效",
      copy: "不支持 View Transition API 时，内容仍然立即更新。",
    },
  };

  const buttons = document.querySelectorAll("[data-view]");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const view = views[button.dataset.view];

      const update = () => {
        document.querySelector("#view-eyebrow").textContent = view.eyebrow;
        document.querySelector("#view-title").textContent = view.title;
        document.querySelector("#view-copy").textContent = view.copy;
        buttons.forEach((item) => {
          item.setAttribute(
            "aria-pressed",
            String(item === button),
          );
        });
      };

      if (
        document.startViewTransition &&
        !matchMedia("(prefers-reduced-motion: reduce)").matches
      ) {
        document.startViewTransition(update);
      } else {
        update();
      }
    });
  });
</script>
```

```css
.view-demo {
  max-inline-size: 42rem;
  margin-inline: auto;
  padding: 2rem 1rem;
}

.view-demo__actions {
  display: flex;
  gap: 0.6rem;
  margin-block-end: 1rem;
}

.view-demo__actions button {
  padding: 0.6rem 0.9rem;
  border: 1px solid #767e8c;
  border-radius: 0.4rem;
  background: #fff;
  color: #172033;
  font: inherit;
  cursor: pointer;
}

.view-demo__actions button[aria-pressed="true"] {
  border-color: #2548bd;
  background: #eef3ff;
}

.view-demo__panel {
  min-block-size: 16rem;
  padding: 1.5rem;
  border: 1px solid #c8ced8;
  border-radius: 0.75rem;
  background: #fff;
  color: #172033;
}

.view-demo__eyebrow {
  margin-block: 0 0.4rem;
  color: #525c6b;
  font-size: 0.85rem;
  font-weight: 700;
}

#view-title {
  margin-block: 0 0.8rem;
  view-transition-name: demo-title;
}

@keyframes title-in {
  from {
    opacity: 0;
    transform: translateY(0.5rem);
  }
}

::view-transition-group(demo-title) {
  animation-duration: 280ms;
  animation-timing-function: ease-out;
}

::view-transition-old(demo-title) {
  animation: 140ms ease-out both fade-out;
}

::view-transition-new(demo-title) {
  animation: 180ms ease-out both title-in;
}

@keyframes fade-out {
  to { opacity: 0; }
}

@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation-duration: 0.01ms;
  }
}
```

视图过渡期间要特别测试焦点、读屏与滚动位置。旧快照不可交互，新视图很快可交互；不要让动画遮挡用户正在操作的控件，也不要把重要状态只放在视觉过渡中。

### 8.4 `@view-transition`：跨文档导航的 CSS 入口

```css
@view-transition {
  navigation: auto;
}
```

跨文档视图过渡要求当前与目标文档同源，并都加入上述 at-rule。`navigation: none` 表示退出。自定义伪元素动画通常只需写在目标文档；若希望两个方向都定制，则两边都写。

`@view-transition` 的支持范围比“某个浏览器支持 `startViewTransition()`”更窄，必须独立验证。MPA 过渡还不等于完整路由系统：字体、关键样式、首屏内容与快照稳定性都会影响效果。

## 9. Houdini：把 CSS 引擎的一部分开放给 JS

### 9.1 三类常见能力

| API | 能做什么 | 不能做什么 |
| --- | --- | --- |
| Properties and Values API | 给自定义属性声明类型、初始值、继承行为 | 不会自动提供新布局 |
| Painting API | 在 Worklet 中绘制 CSS 图像 | 不能访问 DOM 或执行正常页面 JS |
| Layout API | 探索自定义布局模块 | 支持有限，不能当作稳定的生产地基 |

Worklet 是与主线程隔离的 JS 模块，通过 `registerPaint()`、`registerLayout()` 等 API 扩展 CSS。使用前需要 `addModule()` 注册；它也会受到安全上下文、CSP 与浏览器支持约束。

### 9.2 `@property`：让自定义属性可类型化、可插值

未注册的自定义属性本质上是 token 流，通常只能离散变化。注册 `<number>`、`<color>` 等类型后，浏览器知道如何插值。

```html
<button class="typed-badge" type="button">悬停查看颜色过渡</button>
```

```css
@property --badge-color {
  syntax: "<color>";
  inherits: false;
  initial-value: #3157d5;
}

.typed-badge {
  --badge-color: #3157d5;
  padding: 0.75rem 1rem;
  border: 0;
  border-radius: 999px;
  background: var(--badge-color);
  color: #fff;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: --badge-color 180ms ease;
}

.typed-badge:hover {
  --badge-color: #16805a;
}
```

即使浏览器不支持 `@property`，按钮仍有背景和文字；不支持时颜色可能直接跳变。对于必须精确控制数值的动画，应使用 `CSS.registerProperty()` 并捕获异常，或提供 transform/opacity 动画作为降级。

### 9.3 Paint API：完整概念示例

Worklet 文件 `dots.js`：

```js
registerPaint(
  "dot-field",
  class {
    static get inputProperties() {
      return ["--dot-color"];
    }

    paint(ctx, size, props) {
      const color = props.get("--dot-color") || "#3157d5";
      ctx.fillStyle = color;

      for (let y = 4; y < size.height; y += 12) {
        for (let x = 4; x < size.width; x += 12) {
          ctx.beginPath();
          ctx.arc(x, y, 1.5, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
  },
);
```

页面 HTML/CSS：

```html
<div class="paint-card">背景装饰不影响文字内容。</div>
```

```css
.paint-card {
  min-block-size: 8rem;
  padding: 1rem;
  background-color: #f7f8fa;
  color: #172033;
}

.paint-ready .paint-card {
  background-image: paint(dot-field);
  --dot-color: #3157d5;
}
```

主线程注册：

```js
if ("paintWorklet" in CSS) {
  CSS.paintWorklet.addModule("dots.js")
    .then(() => document.documentElement.classList.add("paint-ready"))
    .catch(() => {
      // 保留基础背景；不要因装饰失败影响功能
    });
}
```

这个例子需要把 Worklet 作为独立 JS 文件部署，不能直接塞进普通 `<script>`。Paint Worklet 只使用受限的绘图能力，不能查询 DOM、读取布局状态或替代图片语义。装饰应在模块加载失败时自然消失，而不是让内容变空白。

### 9.4 Layout API：知道边界比追逐 demo 更重要

Layout API 试图让开发者定义新的布局算法，并通过 `display: layout(name)` 使用。它涉及子块尺寸、碎片化、可访问性与失效计算等复杂问题，支持和实验状态因引擎而异。

工程建议：

- 默认使用 Grid、Flex、容器查询等成熟能力；
- 只有现有布局确实无法表达，且团队能承担测试成本时再评估 Layout Worklet；
- 必须有完整的 Grid/Flex 降级；
- 不把“某个 Chromium 版本能跑 demo”当作跨浏览器可用。

## 10. 浏览器支持验证清单

| 特性 | 可用的快速检测 | 还必须验证 |
| --- | --- | --- |
| 原生嵌套 | `CSS.supports("selector(&)")` | 构建链、伪元素、特异性 |
| `@scope` | 检查 `CSSScopeRule` 等 API 线索 | root/limit、`:scope`、邻近性 |
| 锚点定位 | `CSS.supports("anchor-name: --a")` | `position-area`、fallback、名称冲突 |
| `@starting-style` | 无可靠的单属性检测 | 首次进入、退出、声明顺序 |
| 离散过渡 | `CSS.supports("transition", "opacity 1s allow-discrete")` | `display` 0%/100% 与 `overlay` |
| `view()` / `scroll()` | `CSS.supports("animation-timeline", "view()")` | `animation-range`、named timeline、反向滚动 |
| scroll snap | `CSS.supports("scroll-snap-type", "x mandatory")` | 惯性、键盘、项目尺寸 |
| scrollbar | `CSS.supports("scrollbar-color", "red blue")` | 系统覆盖层、高对比度 |
| View Transition API | `"startViewTransition" in document` | 焦点、重复名称、动态内容 |
| `@view-transition` | CSS + 真实 MPA 导航测试 | 同源、双方 opt-in、快照稳定 |
| `@property` | 兼容表或 `CSS.registerProperty` 试注册 | 类型、初始值、过渡 |
| Paint Worklet | `"paintWorklet" in CSS` | 模块加载、CSP、性能、降级 |
| Layout Worklet | API 与 `display: layout()` 实测 | 碎片化、交互、辅助技术 |

验证步骤：

1. 查 [MDN CSS 参考](https://developer.mozilla.org/zh-CN/docs/Web/CSS/Reference) 的 Baseline 和兼容表，再用 [Can I use](https://caniuse.com/) 对照真实用户。
2. 在一个最小页面里验证“行为”，不要只看 DevTools 中属性是否被划删除线。
3. 测试最小与最大尺寸、滚动到首尾、快速反向滚动、动态增删节点。
4. 测试键盘焦点、读屏、200% 缩放、减少动态效果偏好与高对比度模式。
5. 在真实 iOS/Android 设备上验证触摸滚动和系统主题；桌面模拟器不能代替全部测试。

不要笼统写“现代浏览器都支持”。锚点定位、滚动驱动动画、视图过渡、离散过渡和 Houdini 都包含多个子特性，同一模块的不同属性可能处于不同支持阶段。

## 11. 易错点清单

1. **嵌套等于局部作用域**：它只组织语法，仍会命中后代并参与全局级联。
2. **嵌套越多特异性越可控**：复杂嵌套仍会产生难以预测的权重。
3. **`@scope` 能阻止继承**：不能，继承属性仍可越过 scope limit。
4. **`anchor-name` 与 `position-anchor` 足以定位**：还需要 `position-area` 或 `anchor()`。
5. **重复 anchor 名称无所谓**：可能绑定到错误的元素，应唯一或限定 scope。
6. **fallback 能解决所有溢出**：候选位置都放不下时仍可能溢出。
7. **`@starting-style` 替代所有动画**：它服务于 transition 的起始状态。
8. **把 `allow-discrete` 写进唯一 transition 简写**：旧浏览器可能丢弃整条声明。
9. **`overlay` 能管理焦点或 inert**：它只影响顶层退出过渡。
10. **`animation` 简写放在时间轴之后**：可能重置 `animation-timeline`/`range`。
11. **不支持滚动动画时元素保持 `opacity: 0`**：内容消失；基础状态必须可见。
12. **所有卡片都用 `scroll-snap-stop: always`**：交互变得迟缓。
13. **overscroll 等于滚动锁**：它不能替代 inert、焦点管理和背景滚动控制。
14. **隐藏滚动条就是美观**：可能移除唯一的滚动线索。
15. **View Transition 只写 CSS 就能触发**：同文档需要 API，跨文档需要双方 opt-in。
16. **多个元素使用相同 `view-transition-name`**：过渡可能被跳过。
17. **忽略 reduced motion**：滚动与视图过渡都可能引发不适。
18. **Houdini 装饰失败导致内容不可用**：Worklet 与 Paint 必须是渐进增强。
19. **把 Layout API 当稳定布局方案**：支持有限，需完整降级与长期测试。
20. **用版本号代替验证**：兼容性会变化，应按目标用户和真实设备持续测试。

## 关联示例

- [嵌套、scope 与 :has](../../examples/modern/scope-nesting-has.html)：原生嵌套、`@scope` 与祖先状态。
- [锚点定位](../../examples/modern/anchor-positioning.html)：`anchor()`、`@position-try` 与边缘回退。
- [视图过渡](../../examples/modern/view-transition.html)：`startViewTransition()` 和共享元素。
- [滚动驱动动画](../../examples/modern/scroll-driven-animation.html)：`scroll()`、`view()` 与 `animation-range`。
- [滚动吸附轨道](../../examples/layout/scroll-snap.html)：snap、overscroll 和滚动条。

## 12. 练习

1. 把一个卡片组的选择器改写为原生嵌套，再用浏览器计算样式比较改写前后的特异性。
2. 用 `@scope (.card) to (.card__footer)` 限定正文样式，并解释为什么 footer 内的继承颜色仍可能受影响。
3. 实现一个始终在视口内的锚点提示框，分别测试初始位置、单轴翻转、双轴翻转和名称冲突。
4. 用 `@starting-style` 实现弹层进入与退出；测试 `display` 和 `overlay` 是否按预期延迟。
5. 为一张长页面添加 `scroll()` 阅读进度条，并让不支持时降级为 JS 更新或明确的静态状态。
6. 用 `view()` 与 `entry 0% entry 100%` 做卡片揭示，再对比 `entry-crossing` 在超高元素上的差异。
7. 制作吸附轨道，测试 `mandatory`/`proximity`、`scroll-snap-stop` 和键盘操作。
8. 为局部滚动容器设置 `overscroll-behavior: contain`，验证滚动到边界后是否带动页面。
9. 实现一个 View Transition 内容切换，检查重复名称、焦点、返回状态与 reduced motion。
10. 用 `@property` 注册一个 `<number>` 自定义属性，比较注册前后的过渡差异。
11. 给 Paint Worklet 示例加上加载失败与 CSP 失败路径，确认基础卡片仍可读。
12. 为本章每个新特性写一条“检测方式 + 降级方案 + 真机测试项”。

> 上一篇：[原生表单、表格与原生 UI](23-forms-tables-native-ui.md)。
>
> 相关：[定位与层叠](../03-layout/09-positioning-stacking.md)、[过渡与动画](../05-advanced/16-animation.md)、[CSS 速查](20-cheatsheet.md)。
>
> 返回：[CSS 学习手记](../README.md)。
