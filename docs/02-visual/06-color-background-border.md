# 06 · 颜色、背景与边框

> 学习目标：能根据显示与无障碍需求选择颜色空间，正确组合渐变与多层背景，区分背景、边框、轮廓、阴影和滤镜的职责，并理解裁剪与遮罩为什么“看起来相似但用途不同”。

## 1. 从像素到视觉层次

CSS 中的颜色最终要转换成显示设备能呈现的信号。背景、边框、阴影和滤镜看起来都是“上色”，但发生在不同阶段：

```text
内容与背景色
     │
     ├─▶ 背景图片：多层渐变或图像，上层覆盖下层
     │
     ├─▶ 边框：参与盒模型尺寸，围绕 padding box 绘制
     │
     ├─▶ 阴影：按盒模型或几何形状向外扩散，不占布局
     │
     └─▶ filter / clip-path / mask：整体变换或遮住已有绘制结果
```

建立视觉层次时，先决定语义颜色和对比度，再决定背景材质，最后用边框、阴影或滤镜辅助。不要依赖“加一层很重的阴影”掩盖错误的层级关系；过多阴影会让组件看起来像漂浮在彼此之上，也会增加绘制成本。

## 2. 现代颜色语法

### 2.1 Hex 与 `rgb()`

Hex 适合固定品牌色和设计令牌：

```css
:root {
  --brand: #3f6b2a;          /* #RGB / #RRGGBB */
  --brand-soft: #3f6b2a33;  /* #RRGGBBAA，最后两位是 alpha */
}
```

当需要动态透明度时，现代空格语法更清晰：

```css
.callout {
  color: rgb(36 42 30 / 92%);
  background-color: rgb(240 245 232 / 70%);
  border-color: rgb(63 107 42 / 35%);
}
```

也可以使用 `rgb(63 107 42 / 0.35)`。旧逗号语法 `rgba(63, 107, 42, 0.35)` 仍然有效，但不要在同一个项目中随意混用。

Alpha 表示“与背景混合的程度”：`0` 完全透明，`1` 完全不透明。透明不等于白色，也不等于 `visibility: hidden`；透明元素仍会拦截鼠标事件、参与布局，并可能被辅助技术读取。

### 2.2 `hsl()`：用直觉描述颜色

```css
hsl(105 36% 35%);       /* 色相 105，饱和度 36%，亮度 35% */
hsl(105 36% 35% / 20%);
```

- **色相 H**：色环上的角度，`0deg` 通常为红色，`120deg` 为绿色，`240deg` 为蓝色；无单位数也表示为度。
- **饱和度 S**：0% 为灰色，100% 为色相纯度上限。
- **亮度 L**：0% 为黑，100% 为白；50% 并不一定是最鲜艳的颜色。

HSL 便于生成同一色相的不同明度，但它的“亮度”与人眼感知并不完全一致。例如不同色相在相同 HSL  lightness 下，实际对比度可能相差很大。因此不能只凭 HSL 数值宣称无障碍达标。

### 2.3 `oklch()`：更接近感知的颜色调整

```css
:root {
  --brand: oklch(45% 0.12 142);
  --brand-hover: oklch(40% 0.13 142);
  --brand-subtle: oklch(95% 0.025 142);
}
```

OKLCH 的三个轴是：

- **L 感知亮度**：0–100% 或 0–1；0 为黑，1 为白。
- **C 色度**：近似色彩鲜艳程度，0 为无彩色；数值没有统一的“最大 1”限制，取决于色相和显示器色域。
- **H 色相角**：0–360 的循环角度，不直接对应 RGB 色相。

OKLCH 的优势是调整亮度时较少出现“变灰”或刺眼变化，适合从一个种子色生成状态色、表面色与边框色。代价是它不是 sRGB：部分颜色超出常见色域，浏览器会进行色域映射，不同实现和屏幕可能产生差异。品牌色上线前仍需在实际背景上验证。

### 2.4 更宽色域与其他颜色函数

- `hwb()`：用色相、白度、黑度描述颜色，适合快速混合到黑或白。
- `lab()` / `lch()`：分别以 Lab 和极坐标表示 CIELAB 颜色空间。
- `color(display-p3 0.2 0.5 0.3)`：可表达 P3 等宽色域颜色，常用于支持 HDR 或广色域的现代设备。

使用新颜色函数时采用渐进增强：

```css
.swatch { background: #3f6b2a; } /* 回退 */
.swatch { background: oklch(45% 0.12 142); }
```

不支持第二条声明的浏览器会忽略它并保留第一条。不要因为“现代浏览器都支持”就忽略项目实际的最低版本，也不要让只支持旧语法的工具链错误地删除回退。

### 2.5 `color-mix()`：在颜色空间里混合

```css
.button {
  --accent: #3f6b2a;
  background: var(--accent);
  border-color: color-mix(in srgb, var(--accent), black 20%);
}

.button:hover {
  background: color-mix(in oklch, var(--accent), white 12%);
}

.callout {
  border-color: color-mix(in srgb, currentColor 30%, transparent);
}
```

语法是 `color-mix(in <颜色空间>, <颜色> [<百分比>], <颜色>)`。只写一个百分比时，另一个百分比自动补足。省略两个百分比时通常各占一半。`transparent` 也是合法颜色；在部分插值空间中混合透明色可能得到意外结果，因此建议显式指定 `in srgb` 或 `in oklch`。

对于 HSL、HWB、LCH、OKLCH 等极坐标颜色空间，可以进一步指定色相插值方式：

```css
background: color-mix(in oklch shorter hue, #e53935, #2962ff);
```

`shorter hue` 走较短色相路径，`longer hue` 走较长路径，`increasing hue` 与 `decreasing hue` 指定方向。两个互补色混合时，路径选择会决定结果偏向哪一段色环。

`color-mix()` 是计算阶段的功能，不会自动检查对比度。混合 50% 黑通常能加深，但最终文字是否满足 4.5:1，必须根据实际结果验证。

### 2.6 `currentColor`：让颜色跟随语义

```css
.icon-button {
  color: #3f6b2a;
  border: 2px solid currentColor;
  background: color-mix(in srgb, currentColor 10%, white);
}

.icon-button svg { stroke: currentColor; }
```

`currentColor` 通常在使用时取该元素最终生效的 `color`。它让边框、图标、装饰线和局部背景共享同一颜色令牌，比重复写色值更容易响应主题与状态变化。它不是“永远继承父元素颜色”；元素自己的 `color` 声明会改变解析结果。

注意：把 `color` 自身设置为 `currentColor` 没有意义，因为它没有可用的非循环颜色来源。对伪元素使用 `currentColor` 时，伪元素可以继承或拥有自己的 `color`，要检查实际计算值。

## 3. 对比度、主题与 `color-scheme`

### 3.1 对比度是关系，不是颜色属性

对比度由前景色与背景色共同决定。同一个文字颜色放在白底与浅绿底上，结果可能完全不同。WCAG 常用参考值：

- 普通正文至少 **4.5:1**。
- 大号文本至少 **3:1**。大号通常指至少 24px 常规字重，或至少约 18.66px 粗体。
- 关键控件边界、图标与焦点指示通常需要 **3:1**，具体要求还取决于控件状态与相邻颜色。
- 关闭、禁用、占位等内容仍有各自标准；不能把“看起来淡”当作可读性达标。

```css
:root {
  color-scheme: light dark;
  --text: #20241b;
  --surface: #fffdf8;
  --brand: #3f6b2a;
  --border: color-mix(in srgb, var(--text) 18%, transparent);
}

@media (prefers-color-scheme: dark) {
  :root {
    --text: #eef2e9;
    --surface: #181c16;
    --brand: #a9ce8c;
    --border: color-mix(in srgb, var(--text) 24%, transparent);
  }
}
```

在浅色与深色两套令牌中分别验证对比度，不要只在浅色主题把品牌色调亮、深色主题继续沿用同一数值。半透明边框叠在图片或渐变上时，还要验证最亮与最暗的背景区域。

### 3.2 `color-scheme` 控制什么

```css
:root { color-scheme: light dark; }
```

它告诉浏览器页面支持哪些主题，让用户代理选择相应的表单控件、滚动条、画布和系统颜色。`light`、`dark`、`only light`、`only dark` 也可以使用；`only` 表示强制该主题，不允许用户代理自行选择另一种。

`color-scheme` 本身不会把作者定义的背景和文字变成深色。没有显式颜色的 `input`、`button` 可能变化，而写死 `color: black; background: white` 的卡片不会变化。真正的深色主题仍需完整令牌。

使用 CSS `light-dark()` 可以减少媒体查询：

```css
:root {
  color-scheme: light dark;
  --surface: light-dark(#fffdf8, #181c16);
  --text: light-dark(#20241b, #eef2e9);
}
```

它依据元素使用的 `color-scheme` 选择值，适合配色，不应承载所有布局主题逻辑。还要考虑 `forced-colors`：Windows 高对比度模式可能覆盖自定义颜色，应保留清晰的边界和系统颜色回退。

## 4. 渐变：方向、形状与色标

### 4.1 线性渐变

```css
.linear {
  background-image: linear-gradient(135deg, #eef3e7 0%, #3f6b2a 100%);
}
```

`135deg` 表示渐变线的方向：`0deg` 向上，`90deg` 向右，`180deg` 向下。第一个和最后一个色标通常由浏览器延伸到渐变线两端，但实际可见区域的渐变长度取决于几何形状，不能简单认为角度就是某条屏幕对角线。

可以添加多个色标与硬边界：

```css
.stripes {
  background-image: linear-gradient(
    to right,
    #3f6b2a 0 25%,
    #a9ce8c 25% 50%,
    #eef3e7 50% 75%,
    #fffdf8 75% 100%
  );
}
```

色标位置必须非递减。`red 20%, blue 10%` 会被修正为两者都在 20%，形成硬停止，而不是浏览器报错或自动交换。`repeating-linear-gradient()` 按渐变线长度重复，适合规则条纹；颜色空间和色标间隔决定周期。

### 4.2 径向渐变

```css
.radial {
  background-image: radial-gradient(
    circle farthest-corner at 20% 20%,
    #fff 0%,
    #3f6b2a 70%
  );
}
```

`circle` 的半径唯一；`ellipse` 有横纵两个半径。尺寸关键字包括：

- `closest-side`：到最近一条边的距离。
- `farthest-side`：到最远一条边的距离。
- `closest-corner`：到最近顶点的距离。
- `farthest-corner`：到最远顶点的距离。

只写形状时，浏览器使用默认尺寸；只写尺寸时，默认是椭圆。`at` 后的位置决定圆心或椭圆中心。利用径向渐变可以制作光晕、聚焦背景和半透明遮罩，但大面积高饱和光晕容易降低文字对比度。

### 4.3 锥形渐变

```css
.conic {
  background: conic-gradient(from 45deg at 50% 50%, #3f6b2a, #a9ce8c, #3f6b2a);
}
```

`conic-gradient()` 围绕中心点排列颜色，常用于饼图、色环和装饰性放射纹理。`from` 定义起始角度，`at` 定义中心点。它默认从中心向外平滑扩展色标，颜色相同的相邻扇区不会形成清晰边界；需要明确边界时使用双位置色标或遮罩。

### 4.4 渐变尺寸与插值质量

颜色可以在指定空间内插值：

```css
background: linear-gradient(in oklch, #f4f8ef, #3f6b2a);
```

默认 sRGB 插值在两种色相差异较大的颜色之间可能经过低饱和的灰色区域；OKLCH 插值通常更自然。但“更自然”不等于自动符合品牌规范或对比度要求。渐变上的文字需要在最不利位置测量，必要时叠加半透明底板或缩短渐变范围。

## 5. 背景属性：图像、盒子与滚动

### 5.1 一个元素可以有多层背景

```css
.hero {
  background-image:
    linear-gradient(rgb(0 0 0 / 35%), rgb(0 0 0 / 35%)),
    url("/images/hero.webp");
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}
```

**第一层在最上面，最后一层在最下面。** 多层的定位、尺寸和重复也按逗号一一对应。数量不足时，浏览器会重复对应的值列表；数量多于图像时，多余值不生效。背景颜色只能画在所有背景层之下，不能为某一层单独设置 CSS `background-color`。

### 5.2 `background-size`

- 单个 `auto`：保持图像固有比例；渐变没有固有尺寸时行为与图像不同。
- `cover`：放大到完全覆盖背景定位区域，可能裁掉边缘。
- `contain`：缩小到完整放进背景定位区域，可能留下空白。
- 两个长度：分别指定宽、高，可能改变比例。
- 一个长度：指定宽度，高度按比例计算；渐变等无固有比例图像则高度为 `auto`。

`cover` 不是“永远合适”。人物照片使用 cover 时，焦点可能被裁掉；重要区域应配合 `background-position`，复杂场景可结合 `<img>` 与 `object-position` 或提供多个尺寸版本。

### 5.3 背景定位的进阶语法

```css
.hero {
  background-position: right 1rem bottom 2rem;
}
```

四值语法是“边名 + 偏移量”：元素距离右边缘 1rem、距离下边缘 2rem。混用边名和百分比时，偏移的参照不同，建议固定使用一种直观表达。负值可以让图像移出盒子，但溢出是否可见还取决于裁剪与祖先的 overflow。

`background-repeat` 除了 `repeat`、`no-repeat`、`repeat-x`、`repeat-y`，还有：

- `space`：在图像之间分配空间，不裁切首尾图像。
- `round`：缩放图像以填满区域，避免边缘被裁掉。

纹理图案必须检查缩放后的接缝；高 DPI 屏幕上细线渐变可能产生摩尔纹。装饰纹理应足够简单，并提供纯色回退。

### 5.4 `origin`、`clip` 与 `attachment`

```css
.panel {
  background-origin: padding-box; /* 定位与 background-size 的参照区域 */
  background-clip: padding-box;   /* 背景实际绘制到哪个盒子 */
  background-attachment: scroll;  /* 随页面或元素内容滚动 */
}
```

- `border-box`、`padding-box`、`content-box` 分别以边框、内边距、内容盒为参照。
- `background-clip: text` 将背景裁剪到文字字形；通常需要把文字设为透明。
- `background-clip` 不改变元素自己的 `overflow`，也不等于 `clip-path`。
- `background-attachment: local` 让背景随元素内容滚动，适合可滚动面板。
- `fixed` 将背景相对视口定位，但移动端支持与性能历来不稳定，慎用。

```text
默认绘制区域（background-clip: border-box）
┌─ border ─────────────────────┐
│ ┌─ padding ────────────────┐ │
│ │ ┌─ content ────────────┐ │ │
│ │ │ 文字/子元素            │ │ │
│ │ └──────────────────────┘ │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

默认背景会延伸到边框下方，但会被半透明边框透出来；将 clip 改为 padding-box 后，边框区域不再绘制该背景。

### 5.5 `background` 简写

```css
.button {
  background: #eef3e7 no-repeat center / contain;
}
```

简写可以包含颜色、图像、位置、尺寸、重复、附着、origin 与 clip。它会重置所有未写出的背景长属性，包括把 `background-image` 设为 `none`。因此不要在后来的状态样式中用简写只改颜色，否则可能意外删除基础渐变或纹理。组件基础样式建议写长属性，局部状态只覆盖真正变化的属性。

## 6. 边框、轮廓、圆角与阴影

### 6.1 `border` 与 `outline` 的职责不同

```css
.input {
  border: 1px solid #9aa292;
  outline: 2px solid transparent; /* 为状态变化预留空间 */
}

.input:focus-visible {
  border-color: #3f6b2a;
  outline-color: #3f6b2a;
  outline-offset: 2px;
}
```

| 特性 | `border` | `outline` |
| --- | --- | --- |
| 布局 | 占据盒模型空间 | 通常不占布局空间 |
| 形状 | 受 `border-radius` 影响 | 现代浏览器通常跟随圆角；旧环境需验证 |
| 每边 | 可分别设置四边 | 传统上是围绕元素的连续轮廓 |
| 主要用途 | 分隔、结构、控件边界 | 焦点、高亮、调试 |
| 裁剪 | 受 overflow、clip-path 等影响 | 通常绘制在元素外部，但不保证永不被裁 |

`outline: none` 不能单独作为焦点样式。使用 `:focus-visible` 提供清晰轮廓，并确保轮廓与相邻背景有足够对比度。`outline-offset` 可以是负值，但不要把焦点环藏在 overflow 容器中。

边框使用 `border-width`、`border-style`、`border-color` 共同决定可见性。`border: 0` 会把样式设为 none；即使写宽度也不会出现默认实线。逻辑边框如 `border-inline-start` 能随书写模式变化，适合列表、引用和输入框分隔线。

### 6.2 圆角不是“统一像素”

```css
.card { border-radius: 1rem; }
.avatar { border-radius: 50%; }
.notch { border-radius: 1rem 1rem 0 0; }
```

`border-radius` 可接受一至四个值，按左上、右上、右下、左下排列。斜杠可分别定义水平与垂直半径，形成椭圆角：

```css
.leaf { border-radius: 2rem 0.5rem 2rem 0.5rem / 0.5rem 2rem; }
```

百分比分别参照对应盒子的宽和高。大圆角会自动缩小，避免相邻半径重叠。圆角只影响背景、边框和溢出裁剪等部分绘制，不会自动裁掉子元素的内容；裁切子元素需要 `overflow: hidden` 或 `clip-path`。

### 6.3 `box-shadow`：几何阴影

```css
.card {
  box-shadow:
    0 1px 2px rgb(20 30 15 / 12%),
    0 12px 24px -8px rgb(20 30 15 / 18%);
}

.inset {
  box-shadow: inset 0 2px 4px rgb(20 30 15 / 15%);
}
```

语法为 `inset? x-offset y-offset blur-radius spread-radius color`。模糊半径越大越柔和，扩散半径正数扩大阴影、负数缩小。多个阴影用逗号分隔，先写的在上层。

阴影不占布局空间，因此不会自动为相邻元素预留空间。溢出可能被祖先的 overflow 裁剪，也可能与 clip-path 产生意外组合。大面积模糊阴影绘制成本较高，动画中优先只改变 transform 或 opacity，而不是每帧重算阴影。

### 6.4 `filter` 与 `backdrop-filter`

`filter` 会处理元素及其内容形成的渲染结果：

```css
.photo {
  filter: blur(2px) saturate(1.1) contrast(1.05);
}

.photo:hover { filter: none; }
```

常用函数包括 `blur()`、`brightness()`、`contrast()`、`grayscale()`、`sepia()`、`hue-rotate()`、`invert()`、`opacity()`、`saturate()` 和 `drop-shadow()`。

- `drop-shadow()` 根据 alpha 轮廓产生阴影，适合不规则图标；`box-shadow` 始终基于盒子的矩形或圆角几何。
- `filter` 不等于背景滤镜。`backdrop-filter` 处理元素后方的内容，常用于毛玻璃，需要背景半透明才能看出效果。
- 非 `none` 的 filter 通常创建层叠上下文和包含块，可能改变 fixed/absolute 后代的参照。
- 模糊会采样周围像素，可能造成边缘透明或半透明发暗；大半径滤镜成本更高。
- 对比度滤镜不能修复页面所有文字对比度，它可能同时改变前景与背景。

## 7. 裁剪与遮罩基础

### 7.1 `clip-path`：用几何区域裁掉外部

```css
.avatar {
  width: 8rem;
  aspect-ratio: 1;
  clip-path: circle(50% at 50% 50%);
}

.badge {
  clip-path: polygon(0 0, 100% 0, 100% 75%, 50% 100%, 0 75%);
}
```

支持 `inset()`、`circle()`、`ellipse()`、`polygon()`、`path()`，以及组合函数。`clip-path: inset(1rem round 1rem)` 可以同时实现内缩和圆角。函数中的百分比通常参照 reference box，可使用 `border-box`、`padding-box`、`content-box` 等关键字。

`clip-path` 不改变布局，被裁掉的区域不再参与命中测试，也不可见。与 `overflow: hidden` 相比，它不创建滚动容器，也不能用来滚动查看被裁内容。对可聚焦元素裁剪时，要确保焦点没有被裁掉。

### 7.2 `mask`：用图像透明度或亮度控制可见性

```css
.fade-image {
  mask-image: linear-gradient(to bottom, black, transparent);
  mask-size: 100% 100%;
  mask-repeat: no-repeat;
}

.icon {
  background: currentColor;
  mask: url("/icons/check.svg") center / contain no-repeat;
}
```

`mask-image` 接受与背景图像类似的渐变和图像。默认 `mask-mode: match-source`：图像使用 alpha，渐变等匹配源也通常使用 alpha。`mask-mode: luminance` 则用亮度作为遮罩值，白色不透明、黑色透明。也可以分别设置 `mask-type`。

多个遮罩层用逗号组合，并可通过 `mask-composite` 控制相加、相减、相交或排除。与背景一样，层顺序与默认值容易混淆，应先实现单层再增加组合。Safari 的部分版本仍需要 `-webkit-mask-*` 前缀，应按最低目标版本验证，而不是假设所有新特性完全一致。

| 方法 | 最适合 | 不会做的事 |
| --- | --- | --- |
| `overflow: hidden` | 裁剪溢出盒、形成滚动容器 | 任意几何形状 |
| `clip-path` | 圆形、多边形、路径裁剪 | 为裁掉的内容提供滚动查看 |
| `mask-image` | 渐隐、镂空、复杂透明度混合 | 改变元素布局尺寸 |
| `border-radius` | 圆润盒子和背景 | 自动裁掉所有子元素 |

## 8. 完整示例一：自适应主题卡片

保存为 `color-card.html`。切换系统深浅色，并检查按钮文字、边框与卡片表面的对比度。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>主题颜色卡片</title>
  <style>
    :root {
      color-scheme: light dark;
      --brand: oklch(45% 0.12 142);
      --brand-ink: #ffffff;
      --text: light-dark(#20241b, #eef2e9);
      --muted: light-dark(#5c6455, #b6c0ad);
      --surface: light-dark(#fffdf8, #181c16);
      --soft: light-dark(#eef3e7, #252d21);
      --border: light-dark(#c8d0bf, #4b5843);
      --shadow: light-dark(rgb(20 30 15 / 12%), rgb(0 0 0 / 35%));
    }

    * { box-sizing: border-box; }

    body {
      min-block-size: 100vh;
      display: grid;
      place-items: center;
      margin: 0;
      padding: 1.5rem;
      color: var(--text);
      background:
        radial-gradient(circle at 15% 15%, color-mix(in srgb, var(--brand) 15%, transparent), transparent 45%),
        var(--surface);
      font-family: system-ui, "PingFang SC", "Microsoft YaHei", sans-serif;
    }

    .card {
      inline-size: min(100%, 26rem);
      padding: 1.75rem;
      border: 1px solid var(--border);
      border-radius: 1.25rem;
      background: var(--surface);
      box-shadow: 0 1.5rem 3rem -1.5rem var(--shadow);
    }

    .eyebrow {
      color: var(--brand);
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    h1 { margin-block: 0.5rem 0.75rem; font-size: 1.75rem; line-height: 1.2; }
    p { color: var(--muted); line-height: 1.7; }

    .preview {
      block-size: 8rem;
      margin-block: 1.5rem;
      border: 1px solid color-mix(in srgb, var(--brand) 35%, var(--surface));
      border-radius: 0.875rem;
      background:
        linear-gradient(120deg, color-mix(in oklch, var(--brand), white 15%), var(--brand));
    }

    button {
      padding: 0.75rem 1rem;
      border: 1px solid color-mix(in srgb, var(--brand), black 15%);
      border-radius: 0.625rem;
      color: var(--brand-ink);
      background: var(--brand);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    button:hover { background: color-mix(in oklch, var(--brand), black 12%); }
    button:focus-visible { outline: 3px solid var(--brand); outline-offset: 3px; }

    .note {
      margin-block-start: 1rem;
      padding: 0.75rem;
      border-inline-start: 0.25rem solid currentColor;
      color: var(--muted);
      background: var(--soft);
      font-size: 0.875rem;
    }
  </style>
</head>
<body>
  <main class="card">
    <span class="eyebrow">Design token</span>
    <h1>用语义颜色建立主题</h1>
    <p>品牌色用于强调，表面色承载内容，边框只提供必要分隔。每个状态都单独验证对比度。</p>
    <div class="preview" aria-hidden="true"></div>
    <button type="button">应用主题</button>
    <p class="note">提示：在 DevTools 中模拟 dark、light 和强制颜色模式，检查控件与焦点环。</p>
  </main>
</body>
</html>
```

## 9. 完整示例二：多层背景、渐变文字与遮罩

保存为 `background-lab.html`。这个示例不依赖图片资源，适合观察层叠顺序、裁剪和滤镜效果。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>背景与遮罩实验</title>
  <style>
    :root { font-family: system-ui, "PingFang SC", sans-serif; color: #1f281a; }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 2rem 1rem; background: #f3f1e9; }
    main { max-inline-size: 48rem; margin-inline: auto; }
    h1 { text-wrap: balance; }

    .panel {
      display: grid;
      place-items: center;
      min-block-size: 12rem;
      margin-block: 1rem;
      border: 10px solid rgb(63 107 42 / 25%);
      border-radius: 1.5rem;
      background-color: #dce8d2;
      background-image:
        linear-gradient(45deg, rgb(255 255 255 / 22%) 25%, transparent 25% 75%, rgb(255 255 255 / 22%) 75%),
        linear-gradient(135deg, #dce8d2, #3f6b2a);
      background-size: 2rem 2rem, 100% 100%;
      background-position: 0 0, center;
      background-origin: padding-box;
      background-clip: padding-box;
      box-shadow: 0 1rem 2rem -1rem rgb(20 30 15 / 35%);
      overflow: hidden;
    }

    .gradient-text {
      margin: 0;
      padding: 1rem;
      color: transparent;
      background: linear-gradient(in oklch, #dce8d2 10%, #1f3d12 90%);
      background-clip: text;
      font-size: clamp(2rem, 8vw, 4rem);
      font-weight: 800;
      letter-spacing: -0.04em;
      -webkit-background-clip: text;
    }

    .fade {
      position: relative;
      min-block-size: 10rem;
      margin-block-start: 2rem;
      border-radius: 1rem;
      background: repeating-conic-gradient(#3f6b2a 0 15deg, #a9ce8c 15deg 30deg);
      mask-image: linear-gradient(to bottom, black 20%, transparent 100%);
      -webkit-mask-image: linear-gradient(to bottom, black 20%, transparent 100%);
    }

    .fade p {
      position: absolute;
      inset-inline: 1rem;
      inset-block-start: 1rem;
      margin: 0;
      color: white;
      font-weight: 700;
      text-shadow: 0 1px 3px rgb(0 0 0 / 60%);
    }

    @media (prefers-reduced-motion: no-preference) {
      .panel { transition: box-shadow 200ms ease, translate 200ms ease; }
      .panel:hover { translate: 0 -0.25rem; box-shadow: 0 1.5rem 2.5rem -1rem rgb(20 30 15 / 45%); }
    }
  </style>
</head>
<body>
  <main>
    <h1>背景、渐变与遮罩实验</h1>
    <section class="panel">
      <p class="gradient-text">CSS VISUAL</p>
    </section>
    <section class="fade">
      <p>下方使用亮度与透明渐变遮罩渐隐，内容仍然存在。</p>
    </section>
  </main>
</body>
</html>
```

## 10. 易错点

| 误区 | 原因与正确做法 |
| --- | --- |
| 相同 OKLCH 亮度就一定有相同对比度 | 色相、色域映射和背景都会影响结果；用实际颜色测量 |
| `color-scheme: dark` 会自动变暗 | 它主要影响用户代理绘制；作者颜色仍需令牌切换 |
| 多层背景第一层在最底层 | 第一层在最上层；背景颜色位于所有层之下 |
| `background-size: cover` 永不裁图 | 它会按比例放大直到覆盖，焦点区域可能被裁掉 |
| 用 `outline: none` 去掉默认焦点 | 会移除键盘定位反馈；应提供清晰且高对比度的替代焦点样式 |
| 阴影会影响元素尺寸 | 阴影不占布局；相邻元素不会自动避让 |
| `filter` 与 `box-shadow` 可以互换 | 前者处理渲染结果，后者按盒模型几何生成阴影；不规则轮廓用 drop-shadow |
| `mask` 只是另一种圆角 | 遮罩使用图像 alpha 或亮度，能表达渐隐与复杂组合 |
| 背景简写只覆盖指定部分 | 简写会重置所有背景长属性；局部修改优先写长属性 |

## 11. DevTools 与验证方法

1. **Computed 面板**：查看颜色是否被转换为 `color(srgb ...)`、OKLCH 或其他表示，确认色域映射后的结果。
2. **颜色选择器**：检查 alpha、色域和对比度信息；把文字与真实背景一起测量，而不是只看色值。
3. **Elements → Styles**：逐个禁用背景层，验证哪一层造成纹理、遮挡或接缝。
4. **Rendering 面板**：开启绘制闪烁或图层边界，观察大面积阴影与滤镜是否带来额外绘制。
5. **设备模拟**：测试高 DPI、广色域屏幕（若可用）、200% 缩放和深浅色偏好。
6. **强制颜色模式**：检查边框、图标和焦点环是否仍能区分；不要只依赖背景色传递含义。
7. **Network 面板**：确认背景图片的格式、尺寸和缓存；不要在移动端用超大原图承担装饰纹理。
8. **可访问性检查**：同时验证文字、控件状态、焦点、错误提示与图标，不把自动检查分数当作完整审计。

## 关联示例

- [颜色、混合与主题](../../examples/visual/color-blend-theme.html)：OKLCH、`color-mix()`、`currentColor`、混合模式与隔离。
- [背景、边框与滤镜](../../examples/visual/background-border-filter.html)：多层背景、`border-image`、阴影与 `backdrop-filter`。
- [裁剪、遮罩与阴影](../../examples/visual/filters-masks-clip.html)：`clip-path`、`mask-*` 与 `box-shadow` / `drop-shadow()` 对比。
- [补充属性与专题](../07-reference/27-additional-properties.md)：混合模式、`image-set()`、SVG 与彩色字体的延伸说明。

## 12. 练习

1. 用一个 OKLCH 种子色生成品牌色、悬停色、柔和背景和边框色，并用工具验证正文与按钮的对比度。
2. 制作同时包含条纹、径向光晕和纯色回退的多层背景，调换层顺序并记录视觉变化。
3. 对比 `box-shadow` 与 `drop-shadow()` 在圆角矩形和不规则 SVG 上的效果，说明为何轮廓不同。
4. 分别用 `overflow`、`clip-path`、`mask-image` 实现渐隐卡片，比较滚动、命中测试与焦点行为。
5. 实现深浅两套主题，检查原生表单控件、滚动条、渐变文字和强制颜色模式下的回退。

> 上一篇：[排版与字体](05-typography.md)。颜色与背景必须结合文字大小、字重和实际底色判断。
>
> 下一篇：[视觉格式与溢出](07-formatting-overflow.md)。理解 display、overflow 与层叠上下文，才能控制视觉结果的边界。
