# 05 · 排版与字体

> 学习目标：能搭建可预测的中英文字体栈，解释字号与行高的计算关系，处理长文本截断、多语言书写方向和图标呈现，并控制网络字体加载带来的布局抖动。

## 1. 排版不是“选一个好看的字”

一次文字渲染至少经过四个决策：

```text
字符与语言 ──▶ 字体族回退 ──▶ 字形选择与度量 ──▶ 换行/对齐 ──▶ 绘制
  中文、数字        system-ui         ascent/descent      行盒      抗锯齿
  拉丁、标点        serif/sans        字重/字宽            overflow   光标
```

字体决定“字长什么样”，字号决定“字多大”，行高决定“行与行之间留多少呼吸空间”，换行与对齐决定“文本怎样占据一行”。把它们混成一个字号问题，往往会得到行高拥挤、数字跳动、中文标点溢出或截断不完整的页面。

排版的目标不是每行都一样长，而是建立稳定的**阅读节奏**：行长、字号、行高、段距相互匹配。通常正文每行约 35–65 个拉丁字符或 20–40 个汉字；移动端适当减小字号、缩短行长，而不是机械等比例缩放。

## 2. 字体栈：从首选字体到最终回退

### 2.1 字体栈如何工作

`font-family` 是一组按优先级排列的候选字体，而不是把多个字体拼接起来。浏览器逐个检查候选字体是否可用、是否包含当前字形，再决定使用哪一个。回退可能精确到字符：一个中文字体可能缺某个拉丁字母，这个字母就来自后面的字体。

```css
:root {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC",
    sans-serif;
}
```

选择字体栈时应考虑：

- **覆盖范围**：中文正文必须有可用的中文字体候选，否则由用户设备决定，外观不可控。
- **平台差异**：`system-ui` 会跟随操作系统，适合界面，但品牌一致性较弱。
- **分类回退**：最后写 `serif`、`sans-serif` 或 `monospace`，让浏览器至少按类别选择。
- **带空格字体名**：使用引号，例如 `"Noto Sans CJK SC"`；通用分类名不需要引号。
- **字体度量**：不同字体的字形高度和宽度不同。切换回退字体可能改变换行与元素高度。

不要写下“本机一定有某个字体”。设计稿中的字体如果只在作者电脑存在，发布后就可能完全换一套。品牌字体应通过合法授权的网络字体或本地部署提供，并保留系统回退。

### 2.2 网络字体与 `@font-face`

```css
@font-face {
  font-family: "Demo Sans";
  src: url("/fonts/demo-sans.woff2") format("woff2-variations");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

几个关键约束：

- `woff2` 通常是首选格式；同一个字体还可以为旧环境提供 `woff` 回退。
- 可变字体可以用 `font-weight: 100 900` 声明连续范围，避免为每个字重下载一个文件。
- 字体文件必须能由页面访问，并注意同源、跨域与许可。跨域字体需要正确的 CORS 响应头。
- 只加载实际需要的字符集、字重和语言子集。中文字体全量文件可能非常大。
- `font-display` 控制字体尚未下载完成时的显示行为，并不改变下载优先级。

| `font-display` | 极短阻塞期 | 交换期后的行为 | 适用场景 |
| --- | --- | --- | --- |
| `auto` | 由浏览器决定 | 浏览器决定 | 不指定时的默认策略 |
| `block` | 较短 | 无期限使用回退字体 | 品牌字形非常重要 |
| `swap` | 极短 | 无期限使用回退字体，字体到达后替换 | 优先尽快显示正文 |
| `fallback` | 较短 | 短时间内允许交换，之后固定回退 | 平衡首屏与稳定 |
| `optional` | 极短 | 直接使用回退，本次页面通常不再替换 | 弱网、缓存或性能敏感 |

`swap` 不等于“没有布局跳动”。字体替换后字宽变化仍可能改变换行。可变字体、正确的度量覆盖描述符（`size-adjust`、`ascent-override` 等）以及合理回退栈可以缓解，但不能保证完全一致。`optional` 牺牲首屏字形一致性来换取稳定，适合非关键装饰字体。

预加载只应用于确定首屏需要的字体：

```html
<link rel="preload" href="/fonts/demo-sans.woff2" as="font" type="font/woff2" crossorigin />
```

预加载一个没有立即使用的字体会浪费带宽。`preconnect` 则用于第三方字体域，减少连接成本，仍不等于减少字体文件大小。

## 3. 字号、行高与单位

### 3.1 字号不是行盒高度

```text
字号 32px，行高 48px
┌────────────────────────────┐
│          16px 上半间距     │ ← 由字体度量与半行距共同决定
│            32px 字形区域    │
│          16px 下半间距     │
└────────────────────────────┘
              48px 行盒高度
```

`line-height: 48px` 不表示字形上下各有 16px 空白；浏览器会结合字体的 ascent、descent 和 content area 计算，上图只是心智模型。行盒最终高度通常取行内元素及其 `strut`（元素自身字号与行高形成的虚拟盒子）的最大值。

### 3.2 常用单位与选择依据

| 单位 | 参照 | 适合与注意事项 |
| --- | --- | --- |
| `px` | CSS 像素 | 精确控制；不随用户或根字号缩放 |
| `rem` | 根元素 `font-size` | 组件尺度稳定；组件嵌套时仍指向根 |
| `em` | 当前元素字号 | 图标、局部间距随文字缩放；嵌套会复利 |
| `%` | 对字号属性而言是父字号 | 易读但来源不直观 |
| `ch` | 数字 `0` 的宽度 | 控制代码或等宽文本行长；受字体影响 |
| `lh` | 当前元素行高 | 与文字节奏对齐；无显式行高时回退规则较复杂 |
| `rlh` | 根元素行高 | 全局统一的垂直节奏 |
| `vw` / `vh` | 视口宽 / 高 | 流式标题；需设上下限，避免极端屏幕失控 |

`em` 的参照取决于属性。例如 `font-size: 2em` 参照父字号，`padding: 1em` 参照当前元素字号。因此嵌套元素同时使用 `font-size: 1.2em` 时，计算结果会复利增长。

### 3.3 行高的继承陷阱

推荐正文使用无单位行高：

```css
.article {
  font-size: 1rem;
  line-height: 1.75; /* 子元素按自己的字号重新计算 */
}

.article h2 {
  font-size: 1.5rem; /* 行高为 1.5rem × 1.75 = 2.625rem */
}
```

如果写成 `line-height: 28px`，继承的是固定计算值，标题仍保持 28px 行高，就会显得拥挤。百分比与无单位数在声明时的计算方式相似，但最终继承规则不同：无单位数作为数值继承，百分比通常解析为计算后的长度再继承。

### 3.4 `font` 简写

```css
font: italic 700 1.25rem/1.5 system-ui, sans-serif;
```

顺序是：`font-style`、`font-variant`、`font-weight`、`font-stretch`、`font-size/line-height`、`font-family`。其中字号与字体族必需；字号和行高之间用 `/`。也可以写 `font: menu` 等系统字体关键字。

简写会重置未写出的字体相关长属性，例如 `font-stretch`、字距和字体特性。下面两条规则并不会“只改字号”：

```css
.button { font: 700 1rem/1.4 system-ui; font-size: 1.125rem; }
```

第二条 `font-size` 能覆盖字号，但 `font` 已经先把其他长属性重置。组件样式混用简写和长属性时，应把简写放在基础规则中，后续再做局部覆盖，或干脆统一使用长属性。

## 4. 字重、字形变体与字符细节

### 4.1 字重与可变字体

常规字重使用 100–900 的数值，浏览器会把数值映射到最近可用字重。`bold` 通常对应 700，但并非所有字体都有完整九个级别。使用字体文件不存在的字重时，浏览器会合成加粗或选择邻近字重，字形质量可能不同。

```css
@font-face {
  font-family: "Demo Sans";
  src: url("/fonts/demo-sans-var.woff2") format("woff2-variations");
  font-weight: 200 800;
}

strong { font-weight: 650; }
```

`font-variant` 是多个相关特性的简写。现代代码更推荐精确控制：

- `font-variant-numeric: tabular-nums`：表格数字等宽，减少滚动数字横向抖动。
- `font-variant-numeric: oldstyle-nums`：老式数字；是否生效取决于字体。
- `font-variant-caps: small-caps`：小型大写；可能使用字体设计，也可能由浏览器模拟。
- `font-variant-ligatures: none`：关闭 fi、fl 等连字；代码或特定设计需要时使用。

不要为了“视觉上更粗”给标题任意指定未加载的字重。先确认字体提供哪些轴，再建立有限的设计令牌，例如正文 400、强调 600、标题 700。

### 4.2 字距、词距与对齐

```css
.metric { font-variant-numeric: tabular-nums; }
.heading { letter-spacing: -0.02em; }
.english { word-spacing: 0.08em; }
```

- `letter-spacing` 在字符之间增加或减少空间，也会影响行尾和截断位置。
- `word-spacing` 作用于词间空格，对没有空格的中文正文影响很有限。
- 中文与西文混排时，过大的全局正字距会破坏汉字结构；标题可轻微收紧，正文通常保持字体默认值。
- 全大写短标签常需要轻微正字距，但中文字符不应模仿这种处理。

`text-align` 的对齐起点受书写方向影响。现代排版优先使用 `start`、`end`：

```css
.logical-text {
  text-align: start;
  padding-inline-start: 1rem;
}
```

`justify` 可让两端对齐，但需要合理断词策略与足够宽度；窄栏或中文密集文本可能出现松散空隙。`text-align-last` 只控制段落最后一行。

`text-indent` 用于首行缩进，例如中文段落 `text-indent: 2em`。它缩进的是行内内容起点，不会增加元素的外边距；与浮动元素组合时，缩进行会绕开浮动，边界可能看起来不规则。使用 `hanging-punctuation` 可以让引号、标点悬挂到行外，但浏览器支持并不一致，需要视觉回退。

`text-transform` 改变显示形态，不改变 DOM 文本与可访问名称。不要依赖它把界面文案“变成”另一种语言；屏幕阅读器通常仍读取原文。大小写转换还会改变文本宽度和截断结果。

### 4.3 装饰线与可读性

```css
.link {
  color: inherit;
  text-decoration-line: underline;
  text-decoration-thickness: 0.08em;
  text-underline-offset: 0.18em;
  text-decoration-skip-ink: auto;
}
```

链接不能只靠颜色区分。`text-decoration-skip-ink` 能尽量避免下划线穿过字形降部，但长下划线、删除线等具体效果仍需检查。装饰线不占布局空间，也不会自动让链接可聚焦，键盘焦点样式必须另行提供。

## 5. 现代换行、截断与长内容

### 5.1 `text-wrap`

`text-wrap` 控制行如何形成，主要值有：

- `wrap`：默认换行。
- `nowrap`：不换行，直到显式 `<br>`；溢出不自动隐藏。
- `balance`：让多行文本行长度更均衡，适合标题。它针对的是有限行数，浏览器通常限制参与平衡的行数，不应给长正文使用。
- `pretty`：避免末行过短、孤立词和不自然断行，适合段落与说明文字。

```css
h1, h2 { text-wrap: balance; }
p { text-wrap: pretty; }
```

`pretty` 不是“完美中文排版”。标点禁则、断词与混排仍受语言、字体和浏览器算法影响。效果随宽度改变，不能按设计稿中的某一次换行写死 `<br>`。

### 5.2 单行与多行截断

单行截断需要三个条件：宽度受限、不换行、溢出隐藏。

```css
.single-line {
  max-width: 20ch;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
```

`text-overflow` 只在溢出被裁剪时产生省略号；它本身不会创建宽度限制，也不会让多行文本自动省略。

多行截断的常用方案：

```css
.multi-line {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
}
```

这是历史实现，目前在 Chromium、Safari 与 Firefox 中获得广泛支持，但仍应做目标浏览器验证。它有几个约束：

- 截断后的 DOM 和文本仍完整存在，不会减少下载或屏幕阅读器内容。
- 对块级子元素、复杂内联结构和不同语言，截断位置可能不理想。
- 不能与 `text-overflow` 配合实现“多行省略号”，也不能把显示省略误当作内容摘要。
- 如果希望用户读到全文，应提供展开按钮、标题属性或详情页。`title` 对触屏和键盘不友好，不能作为唯一补救。

长 URL 或无空格文本应显式允许断行：

```css
.user-content { overflow-wrap: anywhere; }
```

`anywhere` 会在必要时断词，并参与最小内容宽度计算；`break-word` 更接近旧行为，不一定影响内在尺寸。`word-break: break-all` 会强制在任意字符间断行，通常不适合中英文正文。代码块则更适合 `overflow-x: auto` 与 `white-space: pre`。

## 6. 书写模式与逻辑属性

### 6.1 不只从左到右

`writing-mode` 定义块方向的推进方式与行内方向：

```css
.vertical-title {
  writing-mode: vertical-rl;
  text-orientation: mixed;
}
```

常见值：

- `horizontal-tb`：块从上到下，行从左到右，默认。
- `vertical-rl`：块从右向左，行从上到下，适合中文竖排标题。
- `vertical-lr`：块从左向右，行从上到下。
- `sideways-rl` / `sideways-lr`：让文本整体侧向书写，支持范围较窄。

竖排不等于把每个汉字旋转 90 度。`text-orientation: mixed` 通常保持中日韩表意文字直立，而旋转拉丁字母和数字；`upright` 则让横排字符也直立。标点、混排与字体竖向字形会显著影响结果，必须用真实文案验证。

```text
horizontal-tb              vertical-rl
A → B → C                 A  B  C
下一行在下方               下一行在左侧
inline-size = 宽度          inline-size = 高度
block-size = 高度           block-size = 宽度
```

### 6.2 用逻辑属性替代物理方向

```css
.card {
  padding-block: 1rem 1.5rem;
  padding-inline: 1.25rem;
  margin-inline-start: 1rem;
  border-inline-end: 1px solid #ddd;
  inset-inline-start: 0;
  text-align: start;
}
```

逻辑属性的映射取决于 `writing-mode`，而不取决于 `direction`。例如 `margin-inline-start` 在 `vertical-rl` 中对应物理的 `margin-top`。`direction` 主要影响双向文本与行内起点，不应把设置 `direction: rtl` 当作完整国际化：还需要页面语言、内容翻译、图标方向、日期数字和布局镜像。

长文本国际化时，让容器尺寸跟随书写模式，比给每个语言写物理 `padding-left/right` 更稳健。`logical` 与 `physical` 混用时，后出现的相关属性可能覆盖另一组，需检查 Computed 中映射后的实际边。

## 7. 图标字体与 SVG

### 7.1 为什么界面图标通常优先 SVG

| 维度 | 图标字体 | 内联或外部 SVG |
| --- | --- | --- |
| 本质 | 把图标编码为字体字形 | 独立矢量图形 |
| 颜色 | 通常依赖 `color`，多色能力弱 | 支持 `currentColor`、`fill`、`stroke` |
| 加载 | 可能产生字体阻塞与回退方框 | 可内联、缓存或按需加载 |
| 缩放 | 矢量化，但受字体度量影响 | 由 `viewBox` 控制，易于对齐 |
| 无障碍 | 可能被读成乱码或私人区字符 | 可命名、隐藏或与文字配合 |
| 调试 | 依赖字体是否加载及码点映射 | DOM、样式和路径直接可见 |

图标字体并非一无是处：图标数量多且风格统一时，它能把多个符号合并为一次字体请求。但它不适合承载关键含义，也不适合表达多种颜色或精细渐变。SVG 更容易与 `currentColor` 联动，能跟随主题、状态与文字颜色变化。

```html
<button class="icon-button" type="button" aria-label="关闭">
  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path d="M6 6l12 12M18 6L6 18" />
  </svg>
</button>
```

```css
.icon-button svg {
  width: 1.25em;
  height: 1.25em;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}
```

装饰图标用 `aria-hidden="true"` 防止重复朗读；有含义的独立图标则给按钮或链接可访问名称。使用 SVG sprite 时注意 `viewBox` 与 `<use>` 的兼容性。用图片 `<img>` 展示 SVG 时，外部 CSS 通常不能随意改变其内部颜色；需要主题染色时优先内联 SVG 或可控的 mask 方案。

## 8. 完整示例一：响应式文章排版

保存为 `typography-article.html` 并用浏览器打开。缩小窗口，观察标题换行、正文行高和卡片内边距如何变化。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>文章排版</title>
  <style>
    :root {
      color-scheme: light;
      font-family: system-ui, -apple-system, "Segoe UI", "PingFang SC",
        "Microsoft YaHei", sans-serif;
      color: #20231d;
      background: #f6f3eb;
    }

    * { box-sizing: border-box; }

    body { margin: 0; padding: clamp(1rem, 5vw, 4rem); }

    article {
      max-inline-size: 42rem;
      margin-inline: auto;
      padding: clamp(1.25rem, 4vw, 3rem);
      border: 1px solid #ddd8cb;
      border-radius: 1rem;
      background: #fffdf7;
    }

    h1 {
      margin-block: 0 0.5em;
      font-size: clamp(1.75rem, 1rem + 3vw, 3rem);
      line-height: 1.15;
      letter-spacing: -0.02em;
      text-wrap: balance;
    }

    .meta {
      margin-block-end: 2rem;
      color: #65695e;
      font-size: 0.875rem;
      font-variant-numeric: tabular-nums;
    }

    article > p {
      margin-block: 0 1em;
      font-size: clamp(1rem, 0.95rem + 0.2vw, 1.125rem);
      line-height: 1.8;
      text-wrap: pretty;
    }

    article > p:not(:first-of-type) { text-indent: 2em; }

    blockquote {
      margin-inline: 0;
      padding: 1rem 1.25rem;
      border-inline-start: 0.25rem solid #466a2b;
      background: #eef3e7;
      line-height: 1.7;
    }

    .long-url {
      padding: 0.75rem;
      border-radius: 0.5rem;
      background: #f0eee8;
      overflow-wrap: anywhere;
    }

    @media (prefers-reduced-motion: no-preference) {
      article { animation: appear 400ms ease-out both; }
      @keyframes appear {
        from { opacity: 0; translate: 0 0.5rem; }
        to { opacity: 1; translate: 0 0; }
      }
    }
  </style>
</head>
<body>
  <article>
    <h1>让文字形成节奏，而不是堆满空间</h1>
    <p class="meta"><time datetime="2026-11-25">2026 年 11 月 25 日</time> · 6 分钟阅读</p>
    <p>字号、行高与行长共同决定阅读体验。标题可以收紧行高、平衡换行，正文则需要更宽松的垂直节奏与相对克制的行长。</p>
    <blockquote>好的排版不要求每一行完全相同，而是让读者自然地找到下一行。</blockquote>
    <p>中文段落常用首行缩进建立段落边界。空间不足时，缩进可能占据过多宽度，移动端也可以改用段间距，而不是机械保留所有桌面习惯。</p>
    <p class="long-url">长链接示例：https://example.com/a/very/long/path/that/must/wrap/safely</p>
  </article>
</body>
</html>
```

## 9. 完整示例二：标题截断、竖排标签与图标按钮

保存为 `typography-components.html`。用 DevTools 修改标题长度，并切换 `writing-mode` 观察逻辑尺寸的变化。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>排版组件</title>
  <style>
    :root { font-family: system-ui, "PingFang SC", "Microsoft YaHei", sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 2rem auto; max-inline-size: 38rem; padding-inline: 1rem; color: #222; }

    .card {
      display: grid;
      grid-template-columns: auto minmax(0, 1fr) auto;
      gap: 1rem;
      align-items: start;
      padding: 1.25rem;
      border: 1px solid #d8d8d8;
      border-radius: 0.875rem;
    }

    .vertical-label {
      writing-mode: vertical-rl;
      padding: 0.6rem 0.35rem;
      border-radius: 999px;
      color: #285221;
      background: #e6f0df;
      font-size: 0.8rem;
      letter-spacing: 0.15em;
    }

    .body { min-inline-size: 0; }

    h2 {
      margin: 0;
      font: 700 1.25rem/1.4 system-ui, "PingFang SC", sans-serif;
      text-wrap: balance;
    }

    .summary {
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
      margin-block: 0.5rem 0;
      color: #62665d;
      line-height: 1.6;
    }

    .single {
      max-inline-size: 16ch;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      color: #4f6c3a;
    }

    button {
      display: grid;
      place-items: center;
      inline-size: 2.5rem;
      block-size: 2.5rem;
      padding: 0;
      border: 1px solid #b9c5b1;
      border-radius: 50%;
      color: #315b24;
      background: white;
      cursor: pointer;
    }

    button:hover { background: #eef4e9; }
    button:focus-visible { outline: 3px solid #799d5e; outline-offset: 3px; }
    svg { inline-size: 1.25em; block-size: 1.25em; fill: none; stroke: currentColor; stroke-width: 2; }
  </style>
</head>
<body>
  <article class="card">
    <span class="vertical-label">精选文章</span>
    <div class="body">
      <h2>从字体回退到多行截断：组件排版的完整控制链</h2>
      <p class="summary">这段摘要故意写得足够长，用来观察多行截断。省略号只影响视觉，完整内容仍然留在 DOM 中，因此不要把截断当成数据权限或内容安全机制。</p>
      <div class="single">单行省略：一段不能换行的作者与分类信息</div>
    </div>
    <button type="button" aria-label="收藏文章">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M6 4h12v16l-6-4-6 4z" />
      </svg>
    </button>
  </article>
</body>
</html>
```

## 10. 易错点

| 误区 | 原因与正确做法 |
| --- | --- |
| 只写一个品牌字体 | 字体缺失时会由浏览器任意回退；应提供覆盖目标语言的完整字体栈 |
| `font-display: swap` 能避免布局跳动 | 它只控制显示策略，字体到达后仍可能改变字宽；选择近似回退并验证 |
| `line-height: 28px` 对所有标题都安全 | 固定长度会原样继承；优先使用无单位数，让子元素按字号计算 |
| `text-overflow` 可以省略多行 | 它只作用于单行文本溢出；多行使用 line-clamp 并检查目标浏览器 |
| 给所有中文加大字距更精致 | 汉字有自身结构，正字距容易松散；通常保留默认，仅微调标题 |
| 设置 `direction: rtl` 就完成 RTL | 还需语言、逻辑属性、图标与内容镜像；两者解决的问题不同 |
| 图标字体一定比 SVG 快 | 取决于字符子集、图标数量和缓存；图标字体也可能阻塞并产生回退方框 |
| 截断后内容不可访问 | 截断通常只影响绘制，DOM 文本仍完整；权限与隐藏必须另行处理 |

## 11. DevTools 与验证方法

1. **Network 面板**：过滤 Font，确认只请求所需字体、字重与语言子集，检查缓存与失败状态。
2. **Computed 面板**：查看最终 `font-family`、`font-size`、`line-height`、`letter-spacing`，确认相对单位如何解析。
3. **Rendering → Render fonts**：部分浏览器可高亮字体渲染状态，辅助判断自定义字体是否已经使用。
4. **Elements 面板**：检查省略元素是否仍有完整文本；键盘 Tab 到链接和按钮，确认焦点没有被截断。
5. **限制网络并刷新**：分别观察 `swap`、`fallback`、`optional` 下的首屏和字体替换过程。
6. **改变视口与系统字号**：验证 200% 缩放、窄屏、长标题和无空格文本；不要只测设计稿宽度。
7. **切换语言与方向**：至少测试中文、英文长词和阿拉伯语或希伯来语样本，检查逻辑边距、标点和数字。

## 关联示例

- [排版实验室](../../examples/visual/typography-lab.html)：字体度量、`text-wrap`、截断、竖排与逻辑属性。
- [多列与形状环绕](../../examples/visual/shape-multicol.html)：观察长文本的多栏阅读与浮动形状避让。

## 12. 练习

1. 为同一个标题分别设置 `px`、`rem`、`em` 字号，在 Computed 中记录计算结果，再改变根字号验证差异。
2. 搭建含中文、英文和数字的字体栈，禁用网络后观察回退；为价格列表添加等宽数字。
3. 对比 `text-wrap: wrap`、`balance`、`pretty` 在同一容器中的换行，找出各自最合适的元素类型。
4. 实现单行与三行截断组件，补充“展开全文”交互，并说明为什么截断不能替代内容权限控制。
5. 将一组左、右、上、下物理属性改写为逻辑属性，切换 `horizontal-tb` 与 `vertical-rl`，画出实际方向映射。

> 上一篇：[盒模型与尺寸](../01-foundations/04-box-model.md)。文字的行盒最终仍要回到盒模型与尺寸计算。
>
> 下一篇：[颜色、背景与边框](06-color-background-border.md)。掌握文字之后，再建立颜色与视觉层次的判断标准。
