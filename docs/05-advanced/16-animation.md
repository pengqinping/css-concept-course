# 16 · 过渡与动画

> 学习目标：能区分 transition 与 animation 的触发模型，准确设置时长、延迟、缓动、填充与迭代，使用滚动时间轴做渐进增强，并为列表展开、骨架屏等真实组件设计可访问、可暂停或可关闭的运动。

## 1. 先选时间模型，再选属性

过渡和动画都能改变属性，但解决的问题不同：

```text
transition                            animation
状态 A ──用户交互/样式变化──▶ 状态 B       @keyframes ──时间轴──▶ 关键帧序列
一次前后状态插值                    可重复、可暂停、可多关键帧
依赖触发                            可自动开始或由滚动驱动
```

- **过渡**：描述“从当前状态到新状态如何变化”，例如按钮悬停、弹层打开、主题切换。
- **动画**：描述“一段时间内按什么节奏演进”，例如加载指示、骨架流光、循环提示、滚动进度。
- **滚动驱动动画**：把进度映射到滚动位置或元素进入视口的过程，而不是墙上时钟。

不要用无限 animation 模拟一次性的菜单展开，也不要用 transition 表达多段关键帧。先明确时间来源，才能正确解释延迟、循环、填充和暂停。

## 2. `transition`：触发条件与子属性

### 2.1 五个核心子属性

```css
.button {
  transition-property: background-color, translate;
  transition-duration: 180ms;
  transition-timing-function: ease-out;
  transition-delay: 0ms;
}
```

| 属性 | 作用 | 常见陷阱 |
| --- | --- | --- |
| `transition-property` | 哪些属性参与过渡 | 默认 `all` 会过渡许多意外属性 |
| `transition-duration` | 每个属性变化持续多久 | `0s` 表示没有过渡；默认就是 0s |
| `transition-timing-function` | 进度如何映射到属性值 | 同一个 ease 对不同距离感受不同 |
| `transition-delay` | 变化开始前等待多久 | 负值会立即从过渡中途开始 |
| 简写 `transition` | 一次设置上述属性 | 会重置未写出的长属性 |

多个属性可以共享时长，也可以分别设置：

```css
.panel {
  transition:
    opacity 180ms ease-out,
    translate 260ms cubic-bezier(0.2, 0.7, 0.2, 1),
    box-shadow 180ms ease-out;
}
```

每个逗号项依次是 property、duration、timing-function、delay。列表数量需要能正确配对；不要在一个列表中混入无法解析的值，否则整条声明可能失效。

### 2.2 过渡什么时候触发

过渡需要浏览器先得到“变化前”的已计算样式，再看到“变化后”的样式。以下情况通常不会产生过渡：

- 页面首次加载时元素直接以某个状态出现，没有前后状态变化。
- 元素处于 `display: none`，布局与样式计算被跳过。
- 样式在首帧前连续变化，浏览器没有机会建立起始状态。
- 属性不可插值，例如从 `none` 到某种结构值，且没有使用离散过渡机制。
- 没有设置正的 `transition-duration`，或属性未列入 `transition-property`。

过渡也会在“离开状态”时发生。例如 hover 规则中定义了 transition，鼠标移出后通常仍使用该规则声明的过渡参数回到基础状态。因此 transition 一般写在基础状态，而不是只写在 `:hover` 中。

```css
.button {
  transition: background-color 180ms ease; /* 进入和离开都有效 */
}
.button:hover { background-color: #315b24; }
```

### 2.3 `display`、`none` 与离散变化

`display: none` 到 `block` 传统上不能平滑插值。现代 CSS 提供离散过渡与进入样式：

```css
.dialog {
  display: none;
  opacity: 0;
  transition:
    opacity 180ms ease,
    display 180ms allow-discrete,
    overlay 180ms allow-discrete;
}

.dialog[open] {
  display: block;
  opacity: 1;
}

@starting-style {
  .dialog[open] { opacity: 0; }
}
```

`transition-behavior: allow-discrete` 允许特定离散属性在过渡期间切换。`overlay` 适用于弹层类属性，不是所有浏览器都完整支持；必须做渐进增强。`@starting-style` 为“首次出现”提供起始值，解决弹层刚显示时 opacity 过渡缺少起点的问题。

`auto` 尺寸也不能在普通过渡中直接插值。支持 `interpolate-size: allow-keywords` 的环境可以让 `block-size: 0` 到 `block-size: auto` 产生过渡；不支持时应确保最终展开状态正确，不要依赖动画才能使用功能。

## 3. 哪些属性可以动画

### 3.1 按值类型判断

| 类型 | 例子 | 行为 |
| --- | --- | --- |
| 长度、百分比、数值 | `width`、`opacity`、`line-height` | 通常可插值，但不代表性能好 |
| 颜色 | `color`、`background-color`、`border-color` | 在现代颜色空间中插值，结果需验证 |
| 变换 | `transform`、`translate`、`rotate`、`scale` | 通常可插值，适合视觉运动 |
| 梯度、阴影、滤镜 | `box-shadow`、`filter`、渐变 | 可动画，但结构和绘制成本较高 |
| 离散值 | `display`、位置策略、部分关键字 | 通常不连续变化，需要特殊机制 |
| 自定义属性 | `--x` | 默认按 token 处理；注册类型后才能可靠插值 |

`@property` 可以注册自定义属性的类型、初始值与继承性：

```css
@property --progress {
  syntax: "<percentage>";
  inherits: false;
  initial-value: 0%;
}

.bar {
  --progress: 0%;
  inline-size: var(--progress);
  transition: --progress 300ms ease;
}

.bar.is-complete { --progress: 100%; }
```

没有注册的 `--progress` 往往会在某个离散点突然跳变，而不是从 0% 平滑增长。注册后还要注意：自定义属性参与的是元素样式计算，最终 `inline-size` 改变仍可能触发布局。

### 3.2 “可动画”不等于“应该动画”

`width`、`height`、`top`、`left`、`margin` 等属性可动画，但通常每帧触发布局。`transform` 与 `opacity` 更容易保持流畅；`box-shadow`、`filter`、`background` 可能增加绘制成本，尤其在大面积元素上。

选择属性时按以下顺序判断：

1. 能否用布局状态直接完成，而不需要动画？
2. 能否用 transform / opacity 表达同样的视觉变化？
3. 动画区域是否足够小，绘制成本是否可接受？
4. 动画是否影响阅读、操作或引发不适？

动画越复杂，越应该减少同时变化的属性。一个按钮同时改变 width、height、padding、box-shadow、border-radius 和 transform，往往比“轻微上移 + 阴影变化”更难调试，也更昂贵。

## 4. `@keyframes` 与 `animation`

### 4.1 关键帧定义时间轴

```css
@keyframes pulse {
  0%   { opacity: 0.55; scale: 0.98; }
  50%  { opacity: 1; scale: 1.02; }
  100% { opacity: 0.55; scale: 0.98; }
}

.loading-dot {
  animation: pulse 900ms ease-in-out infinite;
}
```

- `from` 等价于 `0%`，`to` 等价于 `100%`。
- 未写出的 0% 或 100% 会使用元素 underlying style，也就是没有该动画时的计算值。
- 同一百分比可以出现多次，用于在同一时刻快速切换值。
- 关键帧中的属性必须能够插值；不同浏览器对复杂结构值的处理可能不同。
- `@keyframes` 名称区分大小写，应避免使用会与 CSS 全局关键字混淆的名称。

每个关键帧可以单独设置 `animation-timing-function`，作用于该关键帧到下一个关键帧之间的区间。若某帧没写，则继承 animation 的默认缓动。

### 4.2 长属性各自负责什么

```css
.card {
  animation-name: rise-in;
  animation-duration: 400ms;
  animation-timing-function: cubic-bezier(0.2, 0.7, 0.2, 1);
  animation-delay: 100ms;
  animation-iteration-count: 1;
  animation-direction: normal;
  animation-fill-mode: both;
  animation-play-state: running;
}
```

| 属性 | 作用 |
| --- | --- |
| `animation-name` | 使用哪个 `@keyframes`，`none` 表示不应用 |
| `animation-duration` | 单次迭代时长；滚动时间轴可使用 `auto` |
| `animation-timing-function` | 单次迭代内的缓动 |
| `animation-delay` | 正延迟等待；负延迟从迭代中途开始 |
| `animation-iteration-count` | 迭代次数，可小数或 `infinite` |
| `animation-direction` | 正向、反向或交替 |
| `animation-fill-mode` | 延迟前和结束后的关键帧应用方式 |
| `animation-play-state` | running 或 paused |
| `animation-timeline` | 时间、滚动或视图时间轴 |
| `animation-range` | 在时间轴哪一段应用动画 |

### 4.3 简写与顺序

```css
.fade-in {
  animation: fade-in 300ms ease-out 80ms 1 normal both running;
}
```

简写可以解析 name、duration、timing-function、delay、iteration-count、direction、fill-mode、play-state 等部分。两个时间值中，第一个是 duration，第二个是 delay：

```css
animation: fade-in 300ms 100ms ease-out; /* duration 300ms，delay 100ms */
```

简写会重置未写出的动画长属性。不要把基础 `animation` 简写放在组件末尾，又期望它保留之前声明的 iteration-count 或 timeline。对于复杂动画，分开写长属性通常更清晰；简单动画用简写更紧凑。

### 4.4 `fill-mode` 不是“永远保留最终值”

- `none`：延迟期间和结束后都不额外应用关键帧。
- `forwards`：结束后保留最后一帧。
- `backwards`：在延迟期间应用第一帧。
- `both`：延迟期间应用第一帧，结束后保留最后一帧。

`forwards` 只在 animation 仍然应用时保留结果。移除动画、改变 `animation-name: none` 或元素被隐藏，都可能让样式回到 underlying value。若最终状态需要长期存在，直接写基础状态通常比依赖填充模式更可靠。

### 4.5 方向与迭代

- `normal`：每次从 0% 到 100%。
- `reverse`：每次从 100% 到 0%。
- `alternate`：奇数次正向，偶数次反向。
- `alternate-reverse`：从反向开始，然后交替。

小数迭代次数表示完成部分迭代，例如 `2.5` 会在第三次迭代的一半停止。无限循环必须谨慎：它可能持续占用绘制资源，也会让部分用户分心或不适。加载动画应在数据就绪后移除，而不是让整个页面永久运动。

## 5. 缓动：时间进度到值进度的映射

```css
transition: transform 300ms cubic-bezier(0.2, 0.8, 0.2, 1);
```

`cubic-bezier(x1, y1, x2, y2)` 定义一条曲线：横轴是时间进度，纵轴是属性值进度。两个 x 值必须在 0–1 之间；y 可以小于 0 或大于 1，从而产生回弹或过冲。

| 关键字 | 常见感受 |
| --- | --- |
| `linear` | 匀速，适合持续进度或循环 |
| `ease` | 慢启动、加速、减速 |
| `ease-in` | 开始慢，适合离开或加速 |
| `ease-out` | 开始快，适合进入或响应 |
| `ease-in-out` | 两端慢，适合位置切换 |
| `steps()` | 阶梯式变化，适合逐帧精灵图等 |

曲线并不直接等于“速度”：属性值可能先反向或过冲，再到达终点。按钮和菜单通常适合较短的 ease-out；大范围位移动画过冲会让界面显得不稳定。不要给每个组件使用不同缓动，建立少量共享 token 更容易保持一致。

现代 `linear()` 可以描述多段线性缓动，适合精确复刻设计曲线，但可读性不如一个清晰命名的 cubic-bezier。过度精细的曲线不会弥补错误的时长与运动距离。

## 6. 时间轴、范围与滚动驱动入门

### 6.1 默认时间轴

没有指定 `animation-timeline` 时，动画使用文档时间轴，`animation-duration` 与 delay 以秒或毫秒计量。`auto` 是默认 timeline 值。

滚动时间轴把滚动进度映射为动画进度；视图时间轴把元素进入、穿过和离开视口的过程映射为动画进度。

### 6.2 进度条：滚动多少，就动画多少

```css
.progress {
  animation: grow-progress linear both;
  animation-duration: auto;
  animation-timeline: scroll(root block);
  animation-range: 0% 100%;
}

@keyframes grow-progress {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
```

`scroll(root block)` 表示根滚动容器的块方向进度。滚动时间轴下，时长由滚动范围决定，因此使用 `animation-duration: auto`。`animation-range: 0% 100%` 表示使用完整时间轴；只使用其中一段时，可以写成两个百分比。

### 6.3 视图时间轴：元素进入视口时揭示

```css
.reveal {
  animation: reveal linear both;
  animation-duration: auto;
  animation-timeline: view(block);
  animation-range: entry 0% entry 100%;
}

@keyframes reveal {
  from { opacity: 0; transform: translateY(1.5rem); }
  to { opacity: 1; transform: none; }
}
```

`view(block)` 以元素在块方向上的视口进度为时间轴。常见命名范围：

- `cover`：从元素开始进入到完全离开的完整范围。
- `entry`：元素进入视口的过程。
- `exit`：元素离开视口的过程。
- `entry-crossing` / `exit-crossing`：以元素边界穿过视口边界为中心的交叉范围。

`entry 0% entry 100%` 只使用“进入”范围。不同浏览器对范围名称与滚动的细节可能不同，必须用真实容器验证。

### 6.4 渐进增强与旧语法

旧实现可能使用命名 `scroll-timeline` / `view-timeline`，再通过 `animation-timeline: --name` 引用。现代函数式语法更直接。项目应按最低目标版本选择，不要同时维护多套互相冲突的声明。

推荐默认让内容可见，只在支持时添加滚动动画：

```css
.reveal { opacity: 1; transform: none; }

@supports (animation-timeline: scroll()) {
  .reveal {
    animation: reveal linear both;
    animation-duration: auto;
    animation-timeline: view(block);
    animation-range: entry 0% entry 100%;
  }
}
```

不支持时，`@supports` 内的规则被忽略，用户直接看到稳定内容。滚动驱动动画不是免费性能优化：快速滚动、长页面和大量元素仍可能造成绘制压力。仅给关键内容添加，避免每个段落都位移和模糊。

## 7. `prefers-reduced-motion` 与真实组件策略

### 7.1 减弱动画不是“全部瞬间完成”

```css
@media (prefers-reduced-motion: reduce) {
  .skeleton::after { animation: none; }

  .panel,
  .button {
    transition-duration: 0.01ms;
  }

  .reveal,
  .progress-bar {
    animation: none;
    opacity: 1;
    transform: none;
  }
}
```

目标是减少前庭刺激、大规模位移、缩放和视差，同时保留状态反馈。不要只把 2 秒动画改成 0.01 秒，却仍让卡片飞过整个屏幕。可以保留不明显的透明度变化，或改为即时但清晰的状态切换。

需要区分的运动类型：

- **装饰运动**：背景流光、漂浮、粒子，reduce 下通常直接关闭。
- **反馈运动**：按钮按下、焦点出现，使用极短或即时变化。
- **状态揭示**：展开、进入视口，reduce 下直接呈现最终内容。
- **进度提示**：加载指示可以保留静态或低频提示，但不能消失到让用户不知道仍在等待。

`prefers-reduced-motion` 是用户偏好，不是设备性能检测。性能差的设备可能没有开启该偏好，仍应通过减少动画范围与绘制成本保证可用。

### 7.2 列表展开：原生语义优先

`<details>` / `<summary>` 自带键盘交互与展开语义，适合 FAQ 和说明列表。CSS 负责视觉过渡，不应接管焦点与展开状态。

现代浏览器可以用 `::details-content`、`interpolate-size` 和离散过渡实现展开与收起；不支持时直接显示内容即可。不要用 `max-height: 999px` 假装动画，因为实际内容高度未知，延迟和速度会失真；也不要用 `display: none` 到 block 的普通 transition 期待连续变化。

### 7.3 骨架屏：表达等待，不制造忙乱

骨架屏适合已知内容结构的首屏占位。它应该：

- 有 `role="status"` 或等价方式告知正在加载，视觉骨架本身可 `aria-hidden`。
- 与真实布局接近，减少加载完成后的跳动；必要时为媒体区域预留 aspect-ratio。
- 流光幅度小、速度适中，reduce 下停止。
- 不无限替代错误状态、空状态和真实内容。超时后应提供重试或说明。

无限骨架动画如果没有加载结束机制，会永久消耗资源并误导用户。动画的生命周期应与数据状态绑定。

## 8. 完整示例一：按钮过渡与可访问列表展开

保存为 `animation-accordion.html`。键盘可操作 summary，展开内容使用原生语义；支持现代尺寸插值时，打开与收起都有动画。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>过渡与列表展开</title>
  <style>
    :root { font-family: system-ui, "PingFang SC", sans-serif; color: #23291e; }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 2rem 1rem; background: #f6f4ed; }
    main { max-inline-size: 42rem; margin-inline: auto; }
    h1 { text-wrap: balance; }

    .button {
      padding: 0.75rem 1.1rem;
      border: 1px solid #315b24;
      border-radius: 0.625rem;
      color: white;
      background: #466a2b;
      box-shadow: 0 0.25rem 0 #315b24;
      font: inherit;
      font-weight: 700;
      translate: 0 0;
      cursor: pointer;
      transition:
        background-color 160ms ease-out,
        box-shadow 160ms ease-out,
        translate 160ms ease-out;
    }

    .button:hover { background: #315b24; translate: 0 -1px; }
    .button:active { translate: 0 3px; box-shadow: 0 0.0625rem 0 #315b24; }
    .button:focus-visible { outline: 3px solid #1f3d16; outline-offset: 4px; }

    .faq { display: grid; gap: 0.75rem; margin-block-start: 2rem; }

    details {
      border: 1px solid #d2d8c9;
      border-radius: 0.75rem;
      background: white;
    }

    summary {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 1rem;
      font-weight: 700;
      cursor: pointer;
      list-style: none;
    }

    summary::-webkit-details-marker { display: none; }
    summary::after { content: "+"; color: #466a2b; }
    details[open] summary::after { content: "−"; }
    summary:focus-visible { outline: 3px solid #466a2b; outline-offset: -3px; border-radius: 0.75rem; }

    .answer { padding: 0 1rem 1rem; color: #5d6556; line-height: 1.7; }

    @supports (interpolate-size: allow-keywords) {
      :root { interpolate-size: allow-keywords; }

      details::details-content {
        block-size: 0;
        overflow: clip;
        opacity: 0;
        content-visibility: hidden;
        transition:
          block-size 260ms cubic-bezier(0.2, 0.7, 0.2, 1),
          opacity 180ms ease-out,
          content-visibility 260ms allow-discrete;
      }

      details[open]::details-content {
        block-size: auto;
        opacity: 1;
        content-visibility: visible;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .button, details::details-content { transition-duration: 0.01ms; }
      .button:hover, .button:active { translate: 0 0; }
    }
  </style>
</head>
<body>
  <main>
    <h1>状态变化与内容展开</h1>
    <button class="button" type="button">保存设置</button>

    <section class="faq" aria-label="常见问题">
      <details>
        <summary>过渡为什么需要基础状态？</summary>
        <div class="answer">因为鼠标移出时也要平滑回到原状态。把 transition 写在基础选择器中，进入和离开都能使用同一组参数。</div>
      </details>
      <details>
        <summary>为什么不使用 max-height 假装高度动画？</summary>
        <div class="answer">内容高度未知时，过大的 max-height 会让动画提前结束，过小则会裁切。现代尺寸插值可以直接处理 auto，不支持时应保留稳定的最终状态。</div>
      </details>
      <details>
        <summary>减弱动画后还能使用列表吗？</summary>
        <div class="answer">可以。列表仍立即展开或收起，键盘与语义不变；减少的是运动，而不是功能。</div>
      </details>
    </section>
  </main>
</body>
</html>
```

## 9. 完整示例二：骨架屏、滚动进度与视图动画

保存为 `animation-scroll-demo.html`。向下滚动观察进度条和卡片揭示；不支持滚动时间轴时，所有内容默认可见。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>骨架屏与滚动动画</title>
  <style>
    :root { font-family: system-ui, "PingFang SC", sans-serif; color: #22291e; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #f7f5ef; }

    .progress {
      position: fixed;
      inset-block-start: 0;
      inset-inline: 0;
      z-index: 10;
      block-size: 0.375rem;
      background: #466a2b;
      transform: scaleX(1);
      transform-origin: left center;
    }

    main { max-inline-size: 44rem; margin-inline: auto; padding: 3rem 1rem; }
    h1 { text-wrap: balance; }
    p { line-height: 1.75; color: #596151; }

    .skeleton-card {
      display: grid;
      gap: 0.75rem;
      margin-block: 1.5rem;
      padding: 1.25rem;
      border: 1px solid #d9ddd2;
      border-radius: 0.875rem;
      background: white;
    }

    .skeleton {
      position: relative;
      overflow: hidden;
      block-size: 1rem;
      border-radius: 0.25rem;
      background: #e2e6dc;
    }

    .skeleton.title { inline-size: 55%; block-size: 1.5rem; }
    .skeleton.short { inline-size: 75%; }
    .skeleton.media { block-size: 9rem; }

    .skeleton::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, transparent, rgb(255 255 255 / 70%), transparent);
      transform: translateX(-100%);
      animation: shimmer 1.4s linear infinite;
    }

    .sr-only {
      position: absolute;
      inline-size: 1px;
      block-size: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip-path: inset(50%);
      white-space: nowrap;
      border: 0;
    }

    .section {
      min-block-size: 70vh;
      display: grid;
      align-content: center;
      margin-block-start: 3rem;
      padding: 1.5rem;
      border-radius: 1rem;
      background: white;
      opacity: 1;
      transform: none;
    }

    @keyframes shimmer {
      to { transform: translateX(100%); }
    }

    @keyframes grow-progress {
      from { transform: scaleX(0); }
      to { transform: scaleX(1); }
    }

    @keyframes reveal {
      from { opacity: 0; transform: translateY(1.5rem); }
      to { opacity: 1; transform: none; }
    }

    @supports (animation-timeline: scroll()) {
      .progress {
        animation: grow-progress linear both;
        animation-duration: auto;
        animation-timeline: scroll(root block);
        animation-range: 0% 100%;
      }

      .section {
        animation: reveal linear both;
        animation-duration: auto;
        animation-timeline: view(block);
        animation-range: entry 0% entry 100%;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .skeleton::after { animation: none; display: none; }
      .progress, .section { animation: none; transform: none; opacity: 1; }
    }
  </style>
</head>
<body>
  <div class="progress" aria-hidden="true"></div>
  <main>
    <h1>骨架屏与滚动驱动动画</h1>
    <div class="skeleton-card" role="status">
      <span class="sr-only">正在加载示例内容</span>
      <div class="skeleton title" aria-hidden="true"></div>
      <div class="skeleton" aria-hidden="true"></div>
      <div class="skeleton short" aria-hidden="true"></div>
      <div class="skeleton media" aria-hidden="true"></div>
    </div>

    <section class="section">
      <h2>进入视口</h2>
      <p>卡片只在进入视口的过程中改变透明度和位置。滚动停止时动画也停止，因为它由视图进度驱动，而不是独立计时。</p>
    </section>

    <section class="section">
      <h2>滚动进度</h2>
      <p>顶部进度条把根滚动容器的进度映射为 scaleX。它不改变布局宽度，因此不会每帧触发页面重排。</p>
    </section>

    <section class="section">
      <h2>渐进增强</h2>
      <p>不支持滚动时间轴时，动画规则不会生效，内容保持可见。减弱动画偏好下，进度条、骨架流光和位移动画都会关闭。</p>
    </section>
  </main>
</body>
</html>
```

## 10. 易错点

| 误区 | 原因与正确做法 |
| --- | --- |
| 页面一加载就会播放 transition | 没有变化前的计算样式，通常不会触发初始过渡 |
| 把 transition 只写在 hover 里 | 离开状态时可能没有过渡；基础状态也应声明 |
| 两个时间值顺序随便写 | 第一个是 duration，第二个是 delay |
| `animation-fill-mode: forwards` 永久固定状态 | 只在 animation 仍应用时保留；移除动画后样式会恢复 |
| `animation-delay: -1s` 表示提前一秒结束 | 负延迟让动画立即从对应迭代位置开始 |
| 可动画的属性都值得动画 | width/height 等可能触发布局；优先 transform/opacity |
| reduce 模式下只缩短时长 | 大幅位移与缩放仍可能不适；应关闭或替换运动 |
| 骨架屏可以永远显示 | 它必须与加载状态绑定，并处理错误、超时和空状态 |
| 滚动动画需要 JS 才能做 | 现代 CSS 支持 scroll()/view()，但应渐进增强并验证 |
| 用 max-height 猜一个展开高度 | 内容变化会导致速度失真；现代尺寸插值更可靠 |

## 11. DevTools 与验证方法

1. **Animations 面板**：查看 transition / animation 的时间轴、关键帧、延迟、缓动和播放状态；可暂停并逐帧检查。
2. **Computed 面板**：确认最终 duration、delay、fill-mode、direction、timeline、range 和 play-state。
3. **Events 面板**：监听 transitionend、animationend、animationiteration、animationcancel，确认事件数量与预期一致。
4. **Styles 面板**：逐个禁用 transition 属性，判断是哪个属性产生意外布局或绘制。
5. **Performance 面板**：观察动画期间的 Layout、Paint、Composite；不要仅凭 DevTools 中的“GPU”标识判断流畅度。
6. **Rendering → Animations**：部分浏览器提供动画减速与闪烁工具，便于发现跳帧与起始状态问题。
7. **Network 与 CPU 限制**：在慢速设备和低端 CPU 下测试，避免只在开发机上得出性能结论。
8. **系统偏好**：模拟 prefers-reduced-motion，确认关闭动画后信息、焦点和状态反馈仍然完整。

## 关联示例

- [动效实验台](../../examples/animation-playground.html)：transform 过渡与 Grid `0fr → 1fr` 折叠。
- [过渡、时间轴与滚动动画](../../examples/motion/transitions-scroll-timeline.html)：缓动、keyframes、`scroll()` / `view()` 与 `@starting-style`。
- [滚动驱动动画](../../examples/modern/scroll-driven-animation.html)：阅读进度与进入视口范围。

## 12. 练习

1. 为一个卡片设置 background-color、translate、box-shadow 三个过渡，分别调整 duration、delay 和缓动，记录进入与离开是否一致。
2. 用 @keyframes 制作一个三阶段加载动画，分别测试 none、forwards、backwards、both 在延迟和结束后的样式。
3. 对比 `rotate(0deg)` 到 `rotate(350deg)` 与显式中间关键帧的旋转方向，解释为什么起止角度不能完全决定轨迹。
4. 用 `@property` 注册一个百分比自定义属性并过渡进度条，再移除注册观察差异。

> 上一篇：[变换与视觉状态](15-transforms.md)。
>
> 下一篇：[渲染性能与调试](17-performance-debugging.md)。
5. 为列表展开和骨架屏实现 reduce 回退；使用 Animations 面板验证滚动时间轴暂停、范围与填充行为。

> 上一篇：[变换与视觉状态](15-transforms.md)。变换决定运动的空间结果，动画决定这个结果如何随时间变化。
>
> 下一篇：[渲染性能与调试](17-performance-debugging.md)。把动画体验纳入布局、绘制、合成与可访问性的完整调试流程。
