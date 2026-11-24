# 27 · 补充属性与专题：多列、形状、混合、交互与组件边界

> 学习目标：补齐多列、形状、混合、图像回退、输入交互、表单状态、SVG 与彩色字体、用户偏好媒体查询，以及 Shadow DOM 样式边界。这些主题横跨布局、绘制、状态与组件封装；使用前先判断属性作用于哪个盒、哪层像素或哪个上下文，再写可回退的最小实现。

本章采用同一条增强路径：**先保证 HTML 语义和基础样式，再增加新特性，最后验证窄屏、键盘、打印与不支持环境**。`@supports` 只能证明某个声明可以解析，不能证明分页、字体调色板、混合边界等运行行为完全一致。

## 1. 多列布局：先设计阅读顺序，再决定栏数

### 1.1 多列是内容流，不是 Grid

多列容器把连续内容排入若干栏：先沿第一栏向下排列，再进入下一栏。它适合长篇文章、说明文字和杂志式排版，不适合把每个卡片当作独立项目精确对齐。内容在 DOM 中仍是一个连续序列，浏览器负责分栏与平衡栏高。

| 属性 | 作用 | 容易误解的地方 |
| --- | --- | --- |
| `column-count` | 指定期望栏数，取正整数或 `auto` | 栏数仍受可用宽度和栏宽约束，不保证一定得到指定栏数 |
| `column-width` | 指定理想栏宽，取长度或 `auto` | 它是算法输入，不是每栏固定宽度 |
| `columns` | 同时设置栏宽与栏数的简写 | 两个值都写时，浏览器同时兼顾，而不是后者简单覆盖前者 |
| `column-gap` | 设置栏间距 | 与 `gap` 不是同一个属性；栏线绘制在间隙中，不额外占宽 |
| `column-rule` | 设置栏线宽度、样式、颜色 | `column-rule-style: none` 或宽度为 `0` 时不显示 |
| `column-span` | 取 `none` 或 `all`，让块级元素跨栏 | 只能跨全部栏，不能写 `span 2` |
| `column-fill` | 取 `balance` 或 `auto`，控制填栏方式 | 自动高度下通常平衡；固定高度下 `auto` 才会明显按顺序填满 |

`columns` 中栏宽与栏数的顺序可以交换，例如 `columns: 18rem 3` 与 `columns: 3 18rem` 等价。更稳妥的阅读策略是给 `column-width` 一个接近正文舒适行宽的值，把 `column-count` 作为上限，再由容器宽度决定实际栏数。

### 1.2 最小示例：响应式长文

```css
.article {
  columns: 18rem 3;
  column-gap: clamp(1.25rem, 4vw, 2.5rem);
  column-rule: 1px solid #d8d3c5;
  column-fill: balance;
  line-height: 1.75;
}

.article > h2 {
  column-span: all;
  break-after: avoid;
}

.article > h3 {
  break-after: avoid;
}

.article > blockquote,
.article > figure {
  break-inside: avoid;
}

@media (max-width: 44rem) {
  .article {
    columns: 1;
    column-rule: 0;
  }
}
```

这里没有把栏数写死成 `3` 后不再处理窄屏，而是让 `18rem` 的栏宽参与计算；空间不足时浏览器可以减少栏数，最窄时显式回到单栏。跨栏标题用 `column-span: all`，正文仍保持连续阅读顺序。

### 1.3 分页与可读性：换栏不等于换页

**多列布局只处理元素内容框内的分栏，不负责纸张分页。** 打印时还会受到 `@page` 页面尺寸、页边距、`break-before` / `break-after` / `break-inside` 以及 `orphans` / `widows` 的影响。

```css
@media print {
  @page {
    size: A4;
    margin: 18mm 16mm;
  }

  .article {
    columns: 2;
    column-gap: 8mm;
    column-rule: 0;
    font-size: 10.5pt;
  }

  .article > h2,
  .article > h3 {
    break-after: avoid;
  }

  .article p {
    orphans: 3;
    widows: 3;
  }

  .article > figure,
  .article > table {
    break-inside: avoid;
  }
}
```

打印建议：

- 正式文档优先单栏；双栏能减少长行，但栏内宽度也会显著变窄。
- `break-inside: avoid` 是请求，不是绝对保证。图片、表格或代码块高于一页时仍可能被拆分。
- `column-span: all` 会打断分栏流；跨栏元素前后的分页行为要用打印预览验证。
- 多列容器内部的外边距折叠、浮动、固定定位与分页组合比普通文档流复杂，尽量不要在同一个长文里叠加过多特殊布局。
- 代码和表格通常不适合塞进窄栏。代码需要横向滚动或换行，表格需要稳定列宽，可回到单栏或使用独立布局容器。
- 视觉栏序不能改变 DOM 顺序。读屏、查找、复制和键盘阅读仍依赖源文档结构。

### 1.4 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 手机上每行只有几个字 | 栏数或最小栏宽不适合窄屏 | 用 `column-width` 参与计算，并设置单栏断点 |
| 指定 `3` 栏却得到 `2` 栏 | 宽度不足以容纳三栏及间距 | 检查实际栏数、栏宽与容器内容盒 |
| 标题只占一栏 | 没有设置 `column-span: all` | 给需要跨栏的块级标题显式设置 |
| 内容高度固定后只填满第一栏 | 使用了 `column-fill: auto` 或高度约束不同 | 按顺序填充需求选择 `auto`，否则优先 `balance` |
| 引文被拆到两栏 | 缺少 fragmentation 约束 | 对短引文、图注使用 `break-inside: avoid` |
| 打印时出现很窄的残栏 | 页面可用宽度、栏距或跨栏元素共同影响 | 打印改单栏或更宽栏宽，并实测 `@page` |
| 栏线看起来占空间 | 把栏线误认为额外间距 | 栏线绘制在 `column-gap` 内，不另加宽度 |

**对应示例**：[多栏与文字环绕实验室](../../examples/visual/shape-multicol.html)可调整栏数、栏宽、栏距、栏线、跨栏标题和栏高平衡；[打印布局示例](../../examples/engineering/print-layout.html)用于对照 `@page`、强制分页、孤行寡行和跨页表格。两者要分别验证“栏”和“页”，不能相互替代。

## 2. 浮动与形状环绕：只改变文字避让区域

### 2.1 先浮动，再定义外部形状

普通浮动让行盒避开元素的 margin box，因此圆形图片周围仍会按矩形留白。`shape-outside` 在浮动元素之外建立一个新的排除区域，行盒沿这个形状排列。

| 属性 | 作用对象 | 不会做什么 |
| --- | --- | --- |
| `float` | 浮动元素本身 | 不会自动裁剪图片，也不会创建任意 exclusion |
| `shape-outside` | 浮动元素外部的环绕区域 | 不改变元素自身的绘制、背景或边框 |
| `shape-margin` | `shape-outside` 形状外侧 | 不是元素 `margin`，不能替代清除浮动 |
| `shape-image-threshold` | 带透明通道的形状图片 | 不影响几何形状、`clip-path` 或元素透明度 |

视觉轮廓与文字轮廓通常要分开声明：`border-radius` / `clip-path` 负责“画成什么”，`shape-outside` 负责“文字避开什么”。两者使用相同几何函数时看起来才一致。

### 2.2 几何形状与图片阈值

```css
.portrait {
  float: left;
  inline-size: clamp(8rem, 28vw, 14rem);
  aspect-ratio: 1;
  margin-block: 0.25rem 0.75rem;
  margin-inline-end: 1.5rem;
  border-radius: 50%;
  shape-outside: circle(50% at 50% 50%);
  shape-margin: 1rem;
}

.leaf-cutout {
  float: left;
  inline-size: 12rem;
  shape-outside: url("./leaf-mask.png");
  shape-image-threshold: 0.2;
  shape-margin: 0.75rem;
}

.prose::after {
  content: "";
  display: block;
  clear: both;
}
```

`shape-image-threshold` 取 `0` 到 `1` 的数值。对于带 alpha 通道的图片，alpha **大于或等于**阈值的像素构成形状，其余像素成为可让文字穿过的区域。默认值为 `0`，此时所有像素（包括全透明像素）都满足阈值，通常得到完整矩形；提高阈值才会逐步排除半透明或透明区域。阈值设为 `1` 时只保留完全不透明像素，复杂边缘可能出现锯齿。完全不透明的图片没有透明区域，阈值不会“抠出”内部内容。

### 2.3 选择正确的环绕方式

| 需求 | 首选 | 原因 |
| --- | --- | --- |
| 普通图片左右留白 | `float` + `margin` | 最简单，文字避开矩形外框 |
| 圆形、椭圆形或多边形环绕 | `float` + 基本形状 `shape-outside` | 不需要额外图片资源 |
| 人物、叶片等透明轮廓 | `shape-outside: url(...)` + 阈值 | 按图片 alpha 生成排除区域 |
| 同时裁剪显示轮廓 | `clip-path` + 相同的 `shape-outside` | 一个管绘制，一个管环绕 |
| 两侧同时环绕、复杂杂志拼版 | 评估 Grid、定位或专业排版方案 | 标准浮动与 `shape-outside` 不提供完整双栏 exclusion 模型 |

### 2.4 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 属性写了但文字不回流 | 元素没有浮动，或 `shape-outside: none` | 先确认 `float` 和计算值 |
| 文字沿圆形走，图片仍是方块 | 只设置了 `shape-outside` | 用 `clip-path` 或 `border-radius` 同步视觉轮廓 |
| 图片加载后形状消失 | URL 失效、跨域限制或格式不支持 | 检查网络、CORS 与图片 alpha；提供几何形状或 `none` 回退 |
| 阈值变化没有效果 | 图片完全不透明，或形状不是图片 | 阈值只对带透明信息的 `shape-outside` 图片有意义 |
| 后续内容被浮动带上来了 | 没有清除浮动 | 容器 `display: flow-root` 或 clearfix；`shape-margin` 不负责收尾 |
| 浮动图形在窄屏挤占正文 | 图形宽度与行宽比例失衡 | 缩小图形、取消浮动或改为单列图文结构 |
| 绝对定位文字也跟着弯曲 | 误以为形状影响所有定位内容 | 环绕只影响相关行盒，定位元素需单独安排 |

装饰性肖像应使用 `aria-hidden="true"`，有信息含义的图片仍需可访问名称。形状只改变排版，不应改变正文顺序。

**对应示例**：[多栏与文字环绕实验室](../../examples/visual/shape-multicol.html)可切换矩形、圆形、多边形，并开关浮动、调整 `shape-margin`，适合观察“文字避让区域”和“元素绘制区域”的差别。

## 3. 混合模式与隔离：先确定混合边界

### 3.1 两种混合模式作用在不同层

`mix-blend-mode` 把元素渲染出的像素与其背后的画面混合；`background-blend-mode` 只混合同一个元素自己的背景层，不混合后代内容。`isolation: isolate` 创建独立的层叠与混合边界，使内部元素不再与边界外的背景混合。

| 属性 | 混合对象 | 典型用途 |
| --- | --- | --- |
| `mix-blend-mode` | 元素内容与元素背后的 backdrop | 插画叠色、图片纹理、双色图形 |
| `background-blend-mode` | 元素的多个背景层，以及背景色 | 渐变叠纹理、照片调色、材质背景 |
| `isolation: isolate` | 不直接混合像素，而是建立隔离组 | 防止组件混合到页面背景，限定混合范围 |

`isolation` 不是 `contain`，不会自动裁剪内容、改变尺寸或建立 BFC；它也不等于 `overflow: hidden`。`opacity` 小于 `1`、`filter`、`transform` 等也可能创建层叠上下文，从而意外切断混合。

### 3.2 最小示例：把混合限制在组件内

```css
.hero-media {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background: #e8eedf;
}

.hero-media > img {
  inline-size: 100%;
  block-size: 100%;
  object-fit: cover;
  mix-blend-mode: multiply;
}

.texture-card {
  color: #172033;
  background-color: #f4f1e9;
  background-image:
    linear-gradient(135deg, rgb(63 107 42 / 18%), transparent 60%),
    url("./paper-grain.png");
  background-blend-mode: soft-light, multiply;
}
```

第一层背景位于最上方，第二层位于下方。`background-blend-mode` 列表与背景层顺序对应；写全比依赖列表重复更容易维护。背景色会参与最后一层背景的合成，但 `background-color` 不是额外的一张背景图片。

如果希望混合只发生在图片区域，可以把 `isolation: isolate` 放在图片包装层；如果希望整个卡片与页面背景混合，就不要在卡片根部创建隔离组。前者更容易保证标题、按钮和说明文字可读。

### 3.3 混合上下文如何影响结果

```text
没有隔离：
页面背景 + 卡片背景 + 混合图片 + 卡片文字
                         ↑ 元素可能与更外层的页面背景混合

卡片 isolation: isolate：
页面背景 | [卡片背景 + 混合图片 + 卡片文字]
           ↑ 混合在卡片组内完成，外部只看到最终合成结果
```

`z-index` 解决绘制顺序，不自动定义混合边界。一个子元素设置了很大的 `z-index`，仍可能只在祖先的隔离组内部有效。

### 3.4 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 图片设置了混合模式却看不出变化 | 背景透明，或 backdrop 在隔离组外 | 检查父级背景、层叠上下文与隔离边界 |
| 加上 `opacity` 后混合突然失效 | `opacity` 创建了新的层叠上下文 | 把透明度移到专门图层，或重新设计隔离位置 |
| 卡片正文也被混合 | `mix-blend-mode` 作用于包含文字的整个元素 | 只混合图片或单独装饰层，正文保持 `normal` |
| 多层背景颜色不对 | 背景顺序与模式列表没有对应 | 从最上层开始逐层核对，第一层在最上面 |
| 去掉 `isolation` 后组件颜色随页面变化 | 混合泄露到外层背景 | 在组件边界使用 `isolation: isolate` |
| 打印或强制颜色下效果消失 | 浏览器改变颜色合成或禁用视觉效果 | 提供不依赖混合的纯色、边框和文字状态 |
| 提高 `z-index` 仍无法修复 | 祖先隔离组或层叠上下文限制了比较范围 | 调整组边界，而不是继续增大数值 |

混合效果是增强，不应成为唯一的信息表达。例如错误不能只靠红色混合叠加表示，还需要文字、图标或语义属性。

**对应示例**：[色彩混合与明暗主题](../../examples/visual/color-blend-theme.html)可切换 `mix-blend-mode` 和 `isolation`，观察混合边界变化；[背景、边框与滤镜](../../examples/visual/background-border-filter.html)可调整多层背景与 `background-blend-mode`。

## 4. `image-set()` 与 `border-image`：用声明顺序做回退

### 4.1 `image-set()` 选择资源，不负责艺术指导

`image-set()` 允许浏览器在多个 CSS 图片候选中选择支持的格式与合适分辨率。它常用于背景和装饰边框。与 HTML `srcset` 的 `w` 描述符不同，`image-set()` 使用 `1x`、`2x` 等分辨率描述符，不能表达“窄屏显示裁切图、宽屏显示全景图”这类艺术指导。

```css
.hero {
  background-image: url("./hero-1x.jpg"); /* 第一层回退 */
  background-image: image-set(
    "./hero-1x.avif" type("image/avif") 1x,
    "./hero-2x.avif" type("image/avif") 2x,
    "./hero-1x.webp" type("image/webp") 1x,
    "./hero-2x.webp" type("image/webp") 2x,
    "./hero-1x.jpg" 1x,
    "./hero-2x.jpg" 2x
  );
  background-position: center;
  background-size: cover;
}
```

浏览器会忽略不支持的 `type()` 候选，再根据显示能力选择分辨率。旧浏览器若不支持 `image-set()`，第二条声明无效，第一条 `url()` 仍然生效。浏览器可能为候选资源进行预取或选择，不能把“最终只用一张图”当作必然的网络行为。

### 4.2 `border-image` 先保留普通边框，再增强

`border-image` 把图片或渐变切分后绘制到边框区域。它不遵循 `border-radius` 的圆角裁剪，因此适合直角装饰框，不适合直接替代所有圆角边框。

```css
.frame {
  border: 8px solid #3f6b2a; /* 图片边框不可用时的回退 */
  border-radius: 4px; /* 只会在回退边框上看出来 */

  border-image-source: url("./frame.png");
  border-image-source: image-set(
    "./frame-1x.avif" type("image/avif") 1x,
    "./frame-2x.avif" type("image/avif") 2x,
    "./frame-1x.webp" type("image/webp") 1x,
    "./frame-2x.webp" type("image/webp") 2x,
    "./frame-1x.png" 1x,
    "./frame-2x.png" 2x
  );

  border-image-slice: 20;
  border-image-width: 8px;
  border-image-repeat: round;
}
```

- `border-image-slice`：从源图切出四边、四角和中间区域。无单位数值在栅格图中通常表示像素，在矢量图中使用用户坐标。
- `border-image-width`：控制边框图片绘制宽度，不自动等于 `border-width`。
- `border-image-repeat`：`stretch` 拉伸、`repeat` 重复、`round` 取整后重复，避免半块图案。
- `fill` 关键字用于把切出的中间区域绘制到内容盒；不需要填充时不要加。
- `border` 仍决定元素几何尺寸。即使图片边框绘制失败或未加载，也要保留合理的普通边框与内容间距。

### 4.3 选择正确的图片机制

| 需求 | 首选 | 限制 |
| --- | --- | --- |
| 内容图片按视口宽度选择资源 | `<img srcset sizes>` | 需要 HTML 与布局宽度信息 |
| 同一内容在不同构图间切换 | `<picture>` + `media` | 用于艺术指导，不是格式回退 |
| CSS 背景按 DPR / 格式选择 | `image-set()` | 分辨率描述符，不能表达复杂布局条件 |
| 渐变或切图装饰边框 | `border-image` | 不受 `border-radius` 裁剪，复杂响应式行为需实测 |
| 圆角边框、状态边框 | 普通 `border` + `box-shadow` / 背景 | 更易维护，也能参与焦点与主题状态 |

### 4.4 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 旧浏览器背景完全消失 | 只写了一条 `image-set()` | 在前面保留普通 `url()` 声明 |
| AVIF 不支持时没有回退 | 候选中没有通用格式，或 `type()` 写错 | 同时提供 WebP/PNG/JPEG 等回退并核对 MIME |
| 高 DPR 屏幕图片模糊 | 只提供 `1x` 资源 | 提供 `2x` 候选，并检查实际选择的 URL |
| 窄屏裁切不符合设计 | 把 `image-set()` 当成 `sizes` 使用 | 改用 `<picture>` 或不同媒体查询的背景 |
| 图片边框被圆角切掉或显示为方角 | `border-image` 不遵循 `border-radius` | 装饰框保持直角，或改用普通边框与遮罩 |
| 边框图片被拉长变形 | `border-image-slice` / `repeat` 设置不当 | 明确切角尺寸并尝试 `round` |
| 图片加载失败后内容贴边 | 没有普通边框与内边距回退 | 先写完整 `border` 和 `padding`，再增加图片边框 |

旧版 WebKit 可能使用带前缀的 `image-set` 语法，前缀版对格式与描述符的支持并不完全一致。应由构建工具按目标浏览器生成，不要凭记忆同时堆叠标准版和前缀版。

**对应示例**：[背景、边框与滤镜](../../examples/visual/background-border-filter.html)演示了 `border-image` 的长属性、渐变切图、重复方式以及多层背景混合；可在此基础上用网络面板禁用 AVIF/WebP 验证本文的回退顺序。

## 5. 选择、光标、制表符、文字缩放与触控

### 5.1 这些属性解决的是不同问题

| 属性 | 控制范围 | 不能替代 |
| --- | --- | --- |
| `user-select` | 用户能否用鼠标或触摸选择文本 | 复制保护、权限控制、内容加密 |
| `caret-color` | 可编辑控件中文本插入光标的颜色 | 选区颜色、焦点轮廓、错误状态 |
| `tab-size` | 保留空白时制表符的显示宽度 | HTML 源码缩进排版或 `white-space` 设置 |
| `text-size-adjust` | 移动浏览器对文字自动放大的策略 | 响应式字号、页面缩放、无障碍设置 |
| `touch-action` | 浏览器如何处理触摸滚动与缩放手势 | 点击目标尺寸、键盘操作、事件绑定 |
| `-webkit-tap-highlight-color` | WebKit/Blink 移动端的点击高亮 | `:active` 反馈、`:focus-visible` 焦点环 |

### 5.2 最小示例：保留操作能力，只调整反馈

```css
.prose {
  user-select: text;
  -webkit-user-select: text;
}

.no-select-label {
  user-select: none;
  -webkit-user-select: none;
}

input,
textarea {
  caret-color: #3157d5;
}

pre,
code {
  tab-size: 2;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

html {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

.carousel {
  touch-action: pan-y pinch-zoom;
}

.action-button {
  min-block-size: 2.75rem;
  -webkit-tap-highlight-color: transparent;
}

.action-button:active {
  transform: translateY(1px);
}

.action-button:focus-visible {
  outline: 3px solid #3157d5;
  outline-offset: 3px;
}
```

`tab-size: 2` 表示两个空格字符的 advance width，也可以写长度。它只在制表符实际保留时有效；普通 HTML 会把连续空白折叠，因此不能只靠 `tab-size` 排版源码。

`text-size-adjust: 100%` 表示不进行额外的文字自动放大，并不禁止用户缩放页面。规范中的 `none` 与 `100%` 等价，但不同浏览器历史上的支持并不一致；本文使用百分比写法，并在 iOS 上保留必要的 `-webkit-` 声明。不要用它掩盖错误的字号、视口或布局设计。

`touch-action: pan-y pinch-zoom` 允许浏览器处理纵向滚动和双指缩放，把横向手势留给组件；`manipulation` 允许平移和缩放但禁用双击缩放；`none` 会阻止这些浏览器手势，包括用户主动缩放，通常不应放在页面根元素上。

`touch-action` 还受到祖先直到滚动容器的影响。自定义横向轮播时，应把它放在实际滚动容器上，同时保留垂直滚动与缩放手势。`pointer-events: none` 是另一套命中测试机制，不能替代 `touch-action`。

### 5.3 点击高亮与可见反馈

隐藏系统点击高亮的前提是已经有清晰的按压反馈和键盘焦点。仅写 `-webkit-tap-highlight-color: transparent` 会让移动端按钮“点了看起来没反应”。

```css
@media (prefers-reduced-motion: no-preference) {
  .action-button {
    transition: transform 120ms ease, background-color 120ms ease;
  }
}
```

`-webkit-tap-highlight-color` 不是标准属性，在 Firefox 等浏览器中会被忽略，因此不能承载唯一的状态表达。

### 5.4 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 禁止选择后内容仍能被复制 | 把 CSS 当成 DRM | 接受用户可复制，改用服务端权限与法律措施 |
| 光标颜色改了但焦点看不见 | 只设置了 `caret-color` | 单独保留 `:focus-visible` 轮廓 |
| 制表符宽度没有变化 | 空白被折叠或元素不渲染制表符 | 设置合适的 `white-space`，检查实际字符 |
| 手机文字大小不一致 | 浏览器自动文字放大与固定字号共同作用 | 先修正视口和流式字号，再考虑 `text-size-adjust` |
| 横向轮播无法纵向滚动 | `touch-action` 在祖先上被过度限制 | 检查滚动容器及祖先链，保留 `pan-y` |
| 页面无法双指缩放 | 根元素或滚动容器使用了 `touch-action: none` | 移除全局禁用，明确允许 `pinch-zoom` |
| 移动端按钮没有按下反馈 | 点击高亮被隐藏，但没有 `:active` | 增加轻微位移、背景变化或其他即时反馈 |
| Firefox 中高亮设置无效 | 使用了非标准 WebKit 属性 | 以 `:active` 和焦点样式作为跨浏览器反馈 |

选择限制应局部使用。长文章、错误信息、代码和可复制内容不应因为视觉设计被设为 `user-select: none`；辅助技术、翻译工具和用户工作流都可能依赖文本选择。

**对应示例**：[媒体特性与用户偏好](../../examples/responsive/media-preference.html)演示了 `hover` / `pointer` 与触控目标尺寸；[字体与文字排版实验室](../../examples/visual/typography-lab.html)可用于对照字体、换行与文本可读性。`touch-action` 和点击高亮需在真实触控设备上验证，桌面模拟不能完整代替。

## 6. 表单状态：让选择器表达正确时机

### 6.1 HTML 决定状态，CSS 决定呈现

`:required`、`:default`、`:in-range`、`:read-only` 等伪类读取控件状态，不会替控件添加语义。`required`、`min`、`max`、`checked`、`readonly` 等仍要写在 HTML 中；`:indeterminate` 通常由 JavaScript 设置；服务端校验结果则要通过 `aria-invalid` 和可见文案表达。

| 选择器 | 匹配含义 | 常见误区 |
| --- | --- | --- |
| `:indeterminate` | 部分选中等不确定状态，如 JS 设置的复选框、未选择的 radio 组、不确定的 progress | CSS 不能仅靠一条规则把复选框设为部分选中 |
| `:default` | HTML 中的默认选中项，如带 `checked` / `selected` 的选项 | 不是“当前选中项”；重置表单可观察差异 |
| `:required` | 应用了 `required` 约束且该约束适用的控件 | 不代表已经报错，也不等于 `aria-required` |
| `:optional` | 可应用 `required` 但没有该属性的控件 | 不是所有元素都适用，也不是“服务器可省略” |
| `:in-range` | 有范围限制且当前值没有越界 | 没有 `min` / `max` 等限制时通常两者都不匹配 |
| `:out-of-range` | 当前值低于下限或高于上限 | 不等于所有 `:invalid`，步长不匹配是另一类问题 |
| `:read-only` | 用户不可编辑，包括 readonly、disabled 及天然不可编辑元素 | 不是 `[readonly]` 属性的完全同义词 |
| `:read-write` | 用户可编辑，如普通输入框、textarea、可编辑区 | 不代表值一定通过校验 |
| `:user-invalid` | 用户已经交互后仍不满足约束的控件 | 不覆盖服务端错误，也不能代替 `aria-invalid` |

### 6.2 最小示例：区分中性约束与用户错误

```css
.field input,
.field select,
.field textarea {
  border: 1px solid #9aa2ad;
  background: #fff;
  color: #172033;
}

.field input:required,
.field select:required,
.field textarea:required {
  border-color: #8a6d1d; /* 必填提示，不是错误色 */
}

.field input:optional,
.field select:optional,
.field textarea:optional {
  border-color: #9aa2ad;
}

.field input:default {
  box-shadow: 0 0 0 2px rgb(49 87 213 / 16%);
}

/* 仅在自定义 checkbox 外观时生效；原生控件通常交给 accent-color */
.choice input[type="checkbox"]:indeterminate {
  border-color: #3f6b2a;
  background: #3f6b2a;
}

.field input:in-range {
  border-color: #16805a;
}

.field input:out-of-range {
  border-color: #a15c00;
  background: #fff8e8;
}

.field input:read-only {
  color: #4b5563;
  background: #f3f4f6;
}

.field input:read-write {
  caret-color: #3157d5;
}

@supports selector(:user-invalid) {
  .field input:user-invalid {
    border-color: #b42318;
    box-shadow: 0 0 0 3px rgb(180 35 24 / 12%);
  }
}

.field [aria-invalid="true"] {
  border-color: #b42318;
}
```

`:required` 的样式只是辅助提示。表单仍应有持久可见的 label、必填说明和错误原因；不要试图在 `<input>` 的 `::after` 中生成“必填星号”，替换元素的伪元素能力并不稳定。只有颜色变化也不足以表达状态。

### 6.3 `:invalid` 与 `:user-invalid` 的时机差异

```html
<input id="email" name="email" type="email" required />
<label for="email">邮箱</label>
<p id="email-error" aria-live="polite"></p>
```

- 页面刚加载时，空 `required` 邮箱已经可能匹配 `:invalid`。
- 使用 `:invalid` 直接画红色边框，会在用户尚未操作时就显示错误。
- `:user-invalid` 会延迟到用户实际提交或交互之后，但仍由浏览器的用户交互判定驱动。
- 应用自己确认的失焦校验、服务端错误或跨字段错误，应同步设置 `aria-invalid="true"`，并用 `aria-describedby` 关联错误文案。

需要精确控制时机时，使用 `novalidate` 接管校验流程，或在不改变原生语义的前提下补充 JS；不要为了颜色而删除 `required`、`min`、`max` 等约束。

### 6.4 `:default`、`:indeterminate` 与重置

`<input type="radio" checked>` 在用户改选另一项后仍匹配 `:default`，因为默认值来自 HTML，而不是当前 `checked` 状态。表单重置会恢复默认项。

复选框的 `indeterminate` 是独立属性，可以与 `checked` 同时存在；视觉上通常显示为短横线。用户操作该复选框时，浏览器会清除不确定状态。只写 CSS 不能让一个分组复选框自动知道子项选中数量，仍需 JavaScript 同步。

### 6.5 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 页面一打开所有必填项变红 | 直接使用 `:invalid` | 使用 `:user-invalid`，或由应用确认后加 `aria-invalid` |
| 重置后“默认项”样式跑到当前项 | 混淆 `:default` 与 `:checked` | 默认项看 HTML，当前项看 `:checked` |
| 部分选中复选框没有样式 | 只设置了 `:checked` | 同时设计 `:indeterminate`，并由 JS 设置属性 |
| 自定义复选框没有不确定外观 | 原生绘制忽略了作者背景 | 使用 `appearance: none` 后补齐 checked、indeterminate、焦点、禁用状态 |
| `:in-range` / `:out-of-range` 不生效 | 控件没有范围限制或类型不支持 | 检查类型、`min`、`max` 与计算值 |
| `div` 也匹配 `:read-only` | 该伪类表示不可编辑，不只表示 readonly 属性 | 只针对需要的控件或输入类型选择 |
| 只读与禁用外观混淆 | 两者行为不同 | readonly 可聚焦、选择和提交；disabled 通常不可聚焦且不参与提交 |
| 服务端错误没有 CSS 状态 | 只依赖原生约束伪类 | 显式设置 `aria-invalid` 并显示错误文本 |
| 校验状态只靠颜色 | 对比度或色觉差异下不可辨 | 增加图标、文案、边框样式和焦点反馈 |

**对应示例**：[表单状态实验室](../../examples/forms/form-states.html)覆盖 `:indeterminate`、`:default`、`:user-invalid`、重置与原生校验；[选择器练习场](../../examples/foundations/selectors-playground.html)可对比 `:invalid` 与 `:user-invalid` 的出现时机。

## 7. SVG 与彩色字体：颜色、坐标和调色板是三套机制

### 7.1 `currentColor` 与 `fill` / `stroke`

`currentColor` 取使用它的元素当前计算后的 `color`。把 `color` 本身设为 `currentColor` 会形成循环，没有实际意义。SVG 的 `fill` 默认通常为黑色，`stroke` 默认通常为 `none`；线性图标常需要显式关闭填充并设置描边。

```css
.icon {
  inline-size: 1.25em;
  block-size: 1.25em;
  color: var(--icon-color, #3157d5);
}

.icon path {
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.brand-mark {
  inline-size: min(100%, 18rem);
  block-size: auto;
  aspect-ratio: 2 / 1;
  color: #3f6b2a;
}

.brand-mark path {
  fill: none;
  stroke: currentColor;
  stroke-width: 4;
}
```

```html
<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
  <path d="m5 12 4 4L19 6" />
</svg>

<svg class="brand-mark" viewBox="0 0 240 120" preserveAspectRatio="xMidYMid meet"
     role="img" aria-labelledby="brand-title">
  <title id="brand-title">山野观察标志</title>
  <path d="M20 100 80 30l60 70 40-50 40 50" />
</svg>
```

SVG presentation attribute 的优先级低于作者 CSS 规则。若路径自身写了 `fill="black"`，仅在外层 SVG 上写 `fill: none` 可能被路径属性覆盖。需要时直接选中路径或把对应属性写在路径上。

### 7.2 `viewBox` 与 `preserveAspectRatio`

`viewBox="min-x min-y width height"` 建立 SVG 用户坐标系，决定图形如何映射到 SVG 视口。它不是 CSS 宽高，也不自动保证元素在页面上有合适尺寸；仍要用 CSS 或 HTML 属性设置显示宽高。

`preserveAspectRatio` 控制缩放与对齐：

| 值 | 行为 | 适用场景 |
| --- | --- | --- |
| `xMidYMid meet` | 等比缩放并居中，完整容纳 viewBox | 默认图标、标志，允许留白 |
| `xMidYMid slice` | 等比缩放并居中，填满视口，可能裁切 | 全屏 SVG 背景、封面图形 |
| `none` | 分别缩放两个轴，不保持比例 | 已知需要非等比拉伸的图案 |
| `xMinYMin meet` 等 | 改变对齐位置，同时保持比例 | 裁切或留白需要固定方向 |

`meet` 类似 `object-fit: contain`，`slice` 类似 `cover`。切换这两种值可能让边缘图形被裁掉，应检查描边是否也被 viewBox 边界裁切；必要时在 viewBox 内预留安全空间，而不是无限制地使用 `overflow: visible`。

### 7.3 `@font-palette-values`：为彩色字体定义命名调色板

COLR 彩色字体的字形颜色来自字体附带的调色板，普通 `color` 不一定能重绘这些颜色。`@font-palette-values` 定义命名调色板，`font-palette` 把它应用到元素。

```css
@font-face {
  font-family: "Demo Color";
  src: url("./demo-color.woff2") format("woff2");
  font-display: swap;
}

@font-palette-values --BrandPalette {
  font-family: "Demo Color";
  base-palette: 1; /* 0 起始，具体索引由字体的 CPAL 表决定 */
  override-colors:
    0 #fffdf7,
    1 #3f6b2a,
    2 #d49a3a;
}

.brand-wordmark {
  font-family: "Demo Color", system-ui, sans-serif;
  font-palette: --BrandPalette;
  color: #172033; /* 普通回退字体的文字颜色 */
}
```

- 字体必须实际包含可用的彩色字形和调色板；普通字体不会因此变成彩色字体。
- `base-palette` 选择字体内置调色板，`override-colors` 按字体定义的颜色索引覆盖。索引不是设计令牌编号，不能凭感觉写。
- 浏览器不支持时，相关规则会被忽略，字体可能使用默认调色板或回退为普通字体。默认状态也要保证对比度。
- 颜色索引和字体文件版本绑定。升级字体后应重新检查所有覆盖色，避免某个索引在新版中换了含义。
- 调色板是字体能力，不是任意 SVG 路径着色，也不等于 `currentColor`。

### 7.4 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 图标颜色不跟随按钮 | SVG 内部硬编码颜色，或 CSS 没有命中路径 | 用 `currentColor`，检查 presentation attribute 与 CSS 优先级 |
| `color: currentColor` 后颜色异常 | 自引用形成循环 | 给 `color` 一个实际颜色，只在 fill/stroke/border 等属性中使用关键字 |
| 图标被压扁或出现空白 | `viewBox` 比例与 CSS 尺寸不一致 | 保持宽高比，并明确 `preserveAspectRatio` |
| `slice` 模式裁掉重要图形 | 填满视口时发生裁切 | 使用 `meet`、调整 viewBox 安全区或单独移动装饰层 |
| 描边在边缘消失 | 描边超出 viewBox 后被裁切 | 在 viewBox 内留出描边空间 |
| 彩色字体没有主题色 | 字体没有调色板、索引错误或浏览器不支持 | 检查字体文档与 CPAL 表，保留默认回退 |
| 回退字体颜色不可读 | 只设计了彩色字形，没有普通文本颜色 | 同时设置 `color`、字重、字号和回退字体 |
| 图标被读屏重复朗读 | 装饰图标没有隐藏或语义图标没有名称 | 装饰图用 `aria-hidden`，有意义图标提供 title / `aria-label` |

**对应示例**：[色彩混合与明暗主题](../../examples/visual/color-blend-theme.html)演示了 `currentColor` 图标、边框与状态色联动；[字体与文字排版实验室](../../examples/visual/typography-lab.html)用于验证字体栈、字号与回退度量。彩色字体调色板依赖具体字体文件，应另外检查字体本身的 CPAL 表。

## 8. 用户偏好媒体查询：基础体验与增强体验分开

### 8.1 三个显示/脚本查询与两个输入能力查询

| 查询 | 值 | 应响应的差异 |
| --- | --- | --- |
| `prefers-reduced-transparency` | `no-preference` / `reduce` | 用户希望减少半透明、模糊与重叠层 |
| `dynamic-range` | `standard` / `high` | 显示能力可支持更高动态范围内容 |
| `scripting` | `none` / `initial-only` / `enabled` | 文档当前是否允许脚本运行 |
| `hover` | `none` / `hover` | 主输入设备能否稳定悬停 |
| `pointer` | `none` / `coarse` / `fine` | 主输入设备的指针精度 |

这些查询描述能力或偏好，不是设备型号。`no-preference` 是默认值，不能理解为“桌面”；`standard` 是安全基线，不能把高动态范围内容当作唯一可读版本。

### 8.2 减少透明度：同时处理背景与模糊

```css
.panel {
  color: #172033;
  background: rgb(255 253 247 / 88%);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
}

@media (prefers-reduced-transparency: reduce) {
  .panel {
    background: #fffdf7;
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
    box-shadow: 0 1px 0 #d8d3c5;
  }
}
```

不要只降低半透明面板的透明度，却保留背后的复杂动画或模糊。减少透明度偏好也不要求删除所有图片透明度、遮罩或动画；重点是降低视觉叠加和内容辨认难度。

### 8.3 动态范围与脚本能力

```css
.hero {
  background-image: url("./hero-sdr.avif");
}

@media (dynamic-range: high) {
  .hero {
    background-image: url("./hero-hdr.avif");
  }
}

@media (scripting: none) {
  .script-enhancement {
    display: none;
  }
}
```

`dynamic-range: high` 不保证浏览器一定会把图片显示为 HDR，具体还取决于图片格式、色彩空间、视频动态范围能力和浏览器实现。正文、按钮和状态仍应在 SDR 下清晰可读，不应为了 HDR 效果提高饱和度或降低对比度。

`scripting: initial-only` 表示脚本在文档解析期间可用，但之后不可用；`enabled` 表示文档运行期间可用。它不能检测某个脚本是否报错、是否被 CSP 拦截或网络请求是否失败。重要内容和基础操作必须存在于 HTML，脚本增强失败时也要尽量可用。

```html
<noscript>
  <p>当前环境未启用脚本，仍可阅读正文；需要提交的表单请使用页面提供的联系方式。</p>
</noscript>
```

`<noscript>` 与媒体查询可以互补：前者直接面向未启用脚本的环境，后者可避免在解析阶段显示只有脚本才能初始化的装饰。

### 8.4 `hover` 与 `pointer`：不要只依赖悬停

```css
.action-button {
  min-inline-size: 2.75rem;
  min-block-size: 2.75rem;
}

@media (hover: hover) and (pointer: fine) {
  .action-button:hover {
    background: #2d4d1d;
    transform: translateY(-2px);
  }
}

@media (any-pointer: coarse) {
  .action-button {
    min-block-size: 3rem;
  }
}
```

- `:hover` 是伪类，`@media (hover: hover)` 是能力查询，两者不能混写。
- 触屏上的 `:hover` 可能粘住。关键操作、说明和错误不能只在 hover 时出现，应同时支持 focus、点击和键盘。
- 混合设备的主输入可能是鼠标，但仍连接触屏。需要照顾任何触控输入时，可使用 `any-pointer: coarse`；只关心主输入时使用 `pointer`。
- `pointer: coarse` 不等于“手机”，也不等于屏幕窄。布局仍应由实际容器与视口条件决定。
- 悬停位移只是增强，需要配合 `prefers-reduced-motion` 和清晰的按压、焦点状态。

### 8.5 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 减少透明度后面板仍叠在复杂背景上 | 只改了 opacity，没有移除模糊或更换背景 | 使用不透明背景并移除 backdrop-filter |
| 不支持查询的浏览器样式全丢 | 基础样式写在媒体查询内 | 把默认样式放在查询外，只写覆盖规则 |
| HDR 图片让文字难以阅读 | 用高动态范围效果承载关键信息 | SDR 基线保证可读，HDR 只增强装饰或媒体 |
| 未启用脚本时内容消失 | 用媒体查询隐藏了核心内容 | 核心内容写在 HTML 中，提供 `<noscript>` |
| 脚本报错但 CSS 认为可用 | `scripting: enabled` 不代表脚本成功执行 | 应用需在初始化成功后添加状态类 |
| 手机上菜单只能悬停打开 | 关键交互绑定在 `:hover` | 使用按钮、`details`、popover 或点击状态，并支持键盘 |
| 触屏笔记本只有鼠标尺寸 | 只看主 `pointer` | 用 `any-pointer: coarse` 增强触控目标 |
| 减少透明度被误解为减少所有动画 | 把不同偏好查询混为一谈 | 透明度、动态效果、对比度分别处理 |

**对应示例**：[媒体特性与用户偏好](../../examples/responsive/media-preference.html)演示了 `hover`、`pointer`、深色模式、增强对比度、强制颜色与减少动态效果；`prefers-reduced-transparency`、`dynamic-range` 和 `scripting` 应按本文查询在目标浏览器中另行验证。

## 9. Shadow DOM：封装结构，不封装继承与协作

### 9.1 样式边界的三条通道

Shadow DOM 把内部结构放进影子树。页面中的普通选择器不能直接选中影子树内部元素，但仍可通过五条明确通道协作：

| 通道 | 写法位置 | 能做什么 | 边界 |
| --- | --- | --- | --- |
| 宿主样式 | 页面文档 | 设置自定义元素本身的布局、主题和状态 | 不能因此选中内部节点 |
| `:host` | 影子树样式表 | 从组件内部设置宿主默认样式 | 不是任意页面容器的选择器 |
| `::slotted()` | 影子树样式表 | 设置被 `<slot>` 分发的 light DOM 节点 | 只匹配直接分发节点，不穿透深层后代 |
| `::part()` | 页面文档 | 修改影子树中显式 `part` 暴露的部分 | 没有 `part` 的内部结构不可选 |
| 自定义属性 | 两侧都可以 | 用 `--token` 传递颜色、间距、圆角等设计值 | 继承的是变量，不是任意 CSS 规则 |

### 9.2 最小示例：令牌、插槽与 Part API

影子树内部 CSS：

```css
:host {
  display: block;
  color: var(--card-accent, #172033);
  font: inherit;
}

:host([variant="compact"]) {
  --card-space: 0.75rem;
}

.surface {
  padding: var(--card-space, 1.25rem);
  border: 1px solid currentColor;
  border-radius: var(--card-radius, 1rem);
  background: #fffdf7;
}

::slotted(h3) {
  margin: 0;
  font-size: 1.25rem;
}

::slotted([slot="tag"]) {
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--card-accent, #3f6b2a) 12%, transparent);
  font-size: 0.8rem;
}
```

页面文档 CSS：

```css
demo-card {
  --card-accent: #3f6b2a;
  --card-radius: 1rem;
}

demo-card::part(surface) {
  border-color: var(--card-accent, #3f6b2a);
}

demo-card::part(action) {
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
```

使用结构与影子树内部标记：

```html
<demo-card variant="compact" style="--card-accent: #b9633f">
  <h3 slot="title">森林来信</h3>
  <span slot="tag">每月一期</span>
  <p>正文仍属于页面 light DOM，可通过普通页面样式设置。</p>
</demo-card>

<!-- 影子树内部：part 是对外公开的样式 API -->
<article class="surface" part="surface">
  <header>
    <slot name="title"></slot>
    <slot name="tag"></slot>
  </header>
  <slot></slot>
  <button type="button" part="action">保存偏好</button>
</article>
```

`part` 属性可以包含多个空格分隔的名称，组件内部也可以用 `exportparts` 转发嵌套组件的 Part。无论采用哪种方式，Part 名称都属于公开 API；改名会让外部 `::part()` 规则失效。

### 9.3 自定义属性为什么能穿透

CSS 自定义属性默认继承。页面在宿主或祖先上设置 `--card-accent` 后，影子树内部的 `var(--card-accent)` 可以取得该值；组件也可以在 `:host` 中给出默认值。

```css
demo-card {
  --card-accent: #3f6b2a;
}

/* 影子树内部 */
.surface {
  border-color: var(--card-accent, #172033);
}
```

`var()` 的回退只在自定义属性**缺失**时使用。如果外部把 `--card-accent` 设成非法颜色，回退不会自动修复这个值；声明会在使用处变得无效。因此公开令牌应说明类型、默认值和允许范围，必要时用 `@property` 注册。

普通非继承属性如 `background`、`border`、`padding` 不会因为自定义属性机制自动进入影子树。页面仍可用宿主选择器设置 `demo-card` 自身的这些属性，但不能用 `.surface` 之类的内部类名选中影子树节点。

### 9.4 层叠顺序与 `!important` 的反转

对于来自不同影子树的普通声明，外层文档的声明会胜过内部 `:host` 声明，**与选择器优先级无关**；对于 `!important` 声明，顺序反转，内部影子树优先。因此页面里的 `demo-card { color: red; }` 可以覆盖 `:host { color: black; }`，仅提高 `:host` 的选择器优先级通常不是解决办法。

`::slotted()` 也不是完全私有：被分发的节点仍属于 light DOM，页面可以继续用普通选择器设置它们。跨影子树比较普通声明时，同样要意识到外层规则的影响。

### 9.5 常见坑与排查

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| 页面类名无法修改组件内部 | 普通选择器不穿透 Shadow DOM | 使用自定义属性、`:host` 状态、`::part()` 或公开槽位 |
| `::slotted(.title)` 没有命中 | 分发的是另一个节点，或后代层级不同 | `::slotted()` 只针对直接分发的节点，检查 `slot` 分配 |
| 试图用 `::slotted(h3 span)` 选择深层节点 | 该伪元素不接受后代组合器 | 在 light DOM 上用普通选择器，或重新设计插槽结构 |
| `::part()` 完全无效 | 内部节点没有 `part`，或名称不匹配 | 检查影子树标记和公开 API 文档 |
| 外部样式覆盖了 `:host` | 跨影子树的普通声明由外层胜出 | 把可覆盖项设计成令牌或公开状态，不要依赖优先级对抗 |
| 内部 `!important` 无法被页面覆盖 | important 在跨树比较中方向反转 | 避免在组件内部对公开样式入口使用 `!important` |
| 令牌有值却没有效果 | 内部没有 `var()`，或值在错误元素上设置 | 检查继承链、使用位置和是否被局部覆盖 |
| 设置了令牌但样式无效 | 令牌值非法，`var()` 回退不会处理非法值 | 校验令牌，必要时使用 `@property` |
| 内部控件没有焦点环 | 页面全局 `:focus-visible` 不进入影子树 | 在影子树内部写焦点样式，或用 `:host(:focus-within)` 表达宿主焦点 |
| 内部事件在页面监听不到 | 事件没有 `composed: true`，或被 retarget | 组件显式派发可组合事件，并约定事件契约 |

Shadow DOM 是封装边界，不是安全边界，也不等同于 `contain`。它不能阻止恶意代码读取已暴露的信息；它解决的是样式与 DOM 查询的隔离。设计组件时应把“内部实现”和“外部契约”分开：内部类名可重构，属性、槽位、Part、令牌和事件需要保持稳定。

**对应示例**：[Web Components 与 Shadow DOM](../../examples/engineering/webcomponents.html)演示了 `:host`、`:host([variant])`、`::slotted()`、`::part()`、自定义属性、组合事件和表单关联，可直接对照组件边界契约。

## 10. 属性选择决策表

| 需求 | 首选方案 | 不要误用为 | 必须验证 |
| --- | --- | --- | --- |
| 长文自动分栏 | `columns` + 合理的 `column-width` | Grid 项目布局或纸张分页 | 窄屏栏宽、跨栏标题、打印分页 |
| 文章打印分页 | `@page` + `break-*` + `orphans` / `widows` | `column-count` 或滚动吸附 | 打印预览、跨页表格、超长元素 |
| 圆形或多边形文字环绕 | `float` + `shape-outside` + `shape-margin` | 裁剪元素自身 | 浮动清除、视觉轮廓、窄屏退让 |
| 透明图片轮廓环绕 | `shape-outside: url()` + `shape-image-threshold` | 对所有图片都自动抠图 | URL、CORS、alpha、阈值边缘 |
| 元素与背景叠色 | `mix-blend-mode` + 边界 `isolation` | 修改 DOM 或提高 `z-index` | 隔离组、文字可读性、强制颜色 |
| 多层背景互相混合 | `background-blend-mode` | 混合整个元素及其后代 | 背景层顺序、背景色、打印回退 |
| CSS 背景格式与 DPR 回退 | 普通 `url()` 后接 `image-set()` | `srcset sizes` 或 `<picture>` | 禁用格式、网络选择、2x 清晰度 |
| 装饰性切图边框 | 普通 `border` 回退 + `border-image` | 圆角边框 | 切角、重复、加载失败、圆角限制 |
| 禁止局部文本选择 | 小范围 `user-select: none` | 内容保护或权限系统 | 复制、翻译、辅助技术 |
| 代码制表符宽度 | `tab-size` + 合适的 `white-space` | HTML 源码自动格式化 | 折叠空白、长行换行 |
| 自定义横向手势 | 滚动容器 `touch-action: pan-y pinch-zoom` | 全局禁用手势 | 纵向滚动、双指缩放、混合设备 |
| 移动端点击反馈 | `:active` + `:focus-visible`，按需隐藏点击高亮 | 只隐藏高亮 | 真机按压、键盘焦点、减少动态 |
| 原生约束的用户错误 | `:user-invalid` + 可见错误 + `aria-invalid` | 页面初始的 `:invalid` 红框 | 提交前、提交后、重置、服务端错误 |
| 默认项与部分选中 | `:default` / `:indeterminate` | 当前 `:checked` 或纯 CSS 分组状态 | HTML 默认值、JS 属性、表单重置 |
| 数值范围与可编辑性 | `:in-range` / `:out-of-range`、`:read-only` / `:read-write` | 通用 `:valid` / `:invalid` | 类型、范围限制、readonly 与 disabled 差异 |
| 图标跟随主题色 | `currentColor` + `fill` / `stroke` | 在 SVG 内重复硬编码颜色 | CSS 优先级、深色模式、强制颜色 |
| SVG 自适应缩放 | `viewBox` + CSS 尺寸 + `preserveAspectRatio` | 仅设置 `width="100%"` | `meet` 留白、`slice` 裁切、描边安全区 |
| 彩色字体主题 | `@font-palette-values` + `font-palette` | 用普通 `color` 任意重绘字形 | 字体 CPAL 表、索引、回退对比度 |
| 减少透明视觉效果 | `prefers-reduced-transparency: reduce` | 删除所有图片透明度 | 不透明背景、去模糊、文字对比度 |
| HDR 媒体增强 | `dynamic-range: high` | 让关键信息只在高动态范围可读 | SDR 回退、色彩管理、实际显示能力 |
| 鼠标悬停增强 | `@media (hover: hover) and (pointer: fine)` | 只在 hover 中提供关键功能 | 触屏粘滞、键盘、`any-pointer` |
| 脚本不可用环境 | HTML 基础内容 + `<noscript>`，必要时 `scripting` | 检测脚本是否成功运行 | 核心内容、初始化失败、CSP |
| Web Component 主题与局部样式 | 自定义属性 + `:host` / `::slotted()` / `::part()` | 用全局类名穿透影子树 | 令牌类型、Part 契约、焦点、事件组合 |

选择时可以按顺序问四个问题：

1. **这是结构、状态还是绘制？** 结构优先改 HTML / 布局，状态优先保留原生语义，绘制才考虑混合、形状与图片边框。
2. **它作用于内容、元素、背景层还是组件边界？** 选错作用面是“属性没生效”的最常见原因。
3. **不支持时是否仍可读、可操作？** 把基础样式放在查询外，新特性只覆盖增强部分。
4. **验证的是计算值还是最终行为？** 分页、字体、混合、触控和 Shadow DOM 必须在目标环境中观察最终结果。

## 11. 练习

1. **响应式多列文章**：用 `columns: 18rem 3` 排版一篇长文，在 320px、768px 和 1200px 宽度下检查每行字数、栏数与跨栏标题；打印为 PDF，确认标题、图注和段落没有在页边界被无意义拆开。
2. **多列打印对照**：同一篇文章分别使用单栏、双栏和 `column-span: all`，比较 `@page`、`break-inside`、`orphans` / `widows` 的实际结果，记录哪种组合在你的目标浏览器中最稳定。
3. **形状环绕诊断**：分别设置 `shape-outside: none`、`circle()` 和透明图片 URL。用 `clip-path` 同步视觉轮廓，再调整 `shape-image-threshold`，解释阈值变化是否影响边缘以及为什么。
4. **混合边界实验**：给一个包含图片和标题的卡片添加 `mix-blend-mode`，切换祖先的 `isolation`、`opacity` 和 `filter`。找出混合开始或停止的位置，并保证标题在打印与强制颜色下仍可读。
5. **图片与边框回退**：为背景和边框各写一组 AVIF、WebP、通用格式候选。在 DevTools 中禁用格式或阻断图片请求，确认普通 `url()`、普通 `border` 和内容间距仍构成完整回退。
6. **触控交互**：实现一个横向滑动卡片轨道，使用 `touch-action` 允许纵向滚动和双指缩放；在触屏与触控笔记本上验证，并确保每个卡片都能通过键盘聚焦，按压反馈不依赖系统点击高亮。
7. **表单状态矩阵**：制作包含必填邮箱、可选输入、数值范围、只读字段、默认 radio 和分组复选框的表单。验证页面初始不误报错误、提交后显示错误、重置恢复 `:default`、部分选中显示 `:indeterminate`，并补齐错误文案与 `aria-invalid`。
8. **SVG 与字体主题**：制作一个可切换深浅主题的 SVG 图标，对比 `meet`、`slice`、`none` 的缩放结果；若有彩色字体资源，定义命名调色板并检查默认调色板、覆盖色和普通字体回退。
9. **偏好媒体查询**：模拟减少透明度、高动态范围、无脚本、无悬停和粗指针，逐项记录页面变化。确保任何偏好下核心内容都可见，关键操作不依赖悬停，SDR 与有脚本环境也不是残缺版本。
10. **组件边界契约**：用 Shadow DOM 封装一张卡片，让页面全局类名无法修改内部结构，但自定义属性、插槽和 `::part()` 可以工作。再添加一个内部 focusable 控件，验证焦点样式与可组合事件。

> 返回 [文档首页](../README.md)，术语速查见 [GLOSSARY](../GLOSSARY.md)。
