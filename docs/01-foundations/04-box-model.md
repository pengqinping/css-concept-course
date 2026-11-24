# 04 · 盒模型与尺寸

> 学习目标：准确计算元素占位，理解包含块、百分比、内在尺寸与溢出，建立布局测量的共同语言。

## 1. 盒模型结构

```text
┌────────────── margin 外边距 ──────────────┐
│ ┌──────────── border 边框 ────────────┐ │
│ │ ┌────────── padding 内边距 ───────┐ │ │
│ │ │ ┌──────── content 内容 ───────┐ │ │ │
│ │ │ │                             │ │ │ │
│ │ │ └─────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────┘ │ │
│ └─────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

- **content**：文字、图片、子元素等内容区域。
- **padding**：内容与边框之间的空间。
- **border**：边框，占据实际空间。
- **margin**：盒子外部空间，不参与背景绘制。

```css
.card {
  width: 300px;
  padding: 20px;
  border: 2px solid #24261f;
  margin: 24px;
}
```

## 2. `box-sizing`

### `content-box`

`width` 与 `height` 只描述内容区域。

```text
实际宽度 = width + padding-left + padding-right
         + border-left + border-right
         = 300 + 40 + 4 = 344px
```

### `border-box`

`width` 与 `height` 包含 padding 与 border。以上面 `padding: 20px`、`border: 2px` 为例，若 `width: 300px`：

```text
实际宽度 = 300px（padding 与 border 已在其中）
实际内容宽度 = 300 - 40 - 4 = 256px
```

反过来，若希望**内容宽度**为 300px，则 `border-box` 下应写 `width: 344px`。`box-sizing` 不会把 `300px` 自动解释成 `344px`。

注意：**margin 永远不包含在 width 中**。上面的元素无论使用哪种 box-sizing，外部占位宽度都是 `344 + 48 = 392px`。

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}
```

这是项目初始化中最常见的规则之一。需要保持第三方组件或 SVG 的特定尺寸语义时，再局部覆盖。

## 3. 最小尺寸与内容溢出

```css
.card {
  width: 200px;
  min-width: 0;
  min-height: 0;
}
```

Flex/Grid 子项默认有一个自动最小尺寸，长单词或不可压缩内容可能把轨道撑开。

```css
.card {
  min-width: 0;       /* 允许 Flex/Grid 子项收缩 */
  overflow-wrap: anywhere;
}
```

`min-width: auto` 在普通块布局中通常计算为 0；在 Flex/Grid 项目上可能表现为内容最小尺寸。遇到“明明设置了宽度却还是溢出”，优先检查这一点。

## 4. 最大尺寸与媒体

```css
img,
video {
  max-width: 100%;
  height: auto;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  flex: none;
}
```

`max-width: 100%` 让替换元素不超过容器，但它的百分比仍相对于包含块。`height: auto` 用于保持宽高比。若要固定比例并裁剪，可使用 `aspect-ratio` 与 `object-fit`。

## 5. 宽高属性速查

| 属性 | 含义 |
| --- | --- |
| `width` / `height` | 内容尺寸或边框盒尺寸，取决于 box-sizing |
| `min-width` / `min-height` | 最小尺寸限制 |
| `max-width` / `max-height` | 最大尺寸限制 |
| `inline-size` / `block-size` | 按书写模式描述的逻辑尺寸 |
| `aspect-ratio` | 首选宽高比 |
| `box-sizing` | 解释 width/height 的盒模型 |

### 逻辑属性

```css
.card {
  margin-inline: auto;
  padding-block: 1rem;
  border-inline-start: 3px solid #3d601c;
}
```

`inline` 是文字排列方向，`block` 是块堆叠方向。中文横排时大致对应水平与垂直；从右到左或竖排时，逻辑属性更可靠。

## 6. 宽高同时设置与 aspect-ratio

```css
.thumbnail {
  aspect-ratio: 16 / 9;
  background: #e9e4d7;
}
```

只设置 `aspect-ratio` 且另一个维度为 `auto` 时，浏览器根据内容与可用尺寸计算比例。

```css
.thumbnail {
  width: 100%;
  aspect-ratio: 16 / 9;
}
```

如果内容超出，盒子仍可能被内容撑高。需要裁剪时：

```css
.thumbnail {
  overflow: hidden;
}
```

`aspect-ratio: auto 16 / 9` 表示有内在比例时优先内在比例，否则使用 16/9。

## 7. 包含块：百分比的参照物

包含块是元素尺寸和位置解析的参照。普通流子元素的包含块通常是最近块容器的内容盒；绝对定位元素的包含块通常是最近定位祖先的 padding 盒。

```html
<div class="parent">
  <div class="child"></div>
</div>
```

```css
.parent {
  position: relative;
  width: 400px;
  padding: 20px;
  border: 2px solid;
}

.child {
  position: absolute;
  width: 50%;
  height: 50%;
}
```

子元素百分比基于最近定位祖先的 padding 盒。若父元素没有定位，则继续向上寻找，可能最终相对于初始包含块（通常是视口）。

```text
.parent padding box = 400 + 2×20 = 440px
.child width = 50% × 440px = 220px
```

普通流的 `.child` 若宽度为 50%，则参照父元素 content box：

```text
child width = 50% × 400px = 200px
```

## 8. margin 折叠

普通文档流中，相邻块级元素的垂直 margin 可能合并：

```text
A margin-bottom: 30px
B margin-top: 20px
实际间距：30px，而不是 50px
```

正 margin 取最大值；负值参与计算：

- `30px + 20px` → `30px`
- `30px + (-10px)` → `20px`
- `-20px + (-10px)` → `-20px`

不会发生垂直 margin 折叠的常见场景：

- Flex/Grid 项目之间。
- 元素建立了 BFC 且其 margin 与外部隔离时。
- 容器有 border、padding 或明确高度，导致父子 margin 不再能穿过。
- 绝对定位、浮动元素。

```css
.stack > * + * {
  margin-block-start: 1rem;
}
```

用相邻兄弟规则统一间距，通常比每个元素单独 margin 更稳定。

## 9. padding、border 与背景

默认情况下，背景延伸到 border-box，`background-clip: padding-box` 可让背景不覆盖边框：

```css
.card {
  border: 8px solid rgb(36 38 31 / 20%);
  background: #c8f35c;
  background-clip: padding-box;
}
```

`overflow: hidden` 会裁剪 padding box 之外的内容，但边框本身仍可显示。圆角与背景的关系由 `background-clip` 控制。

## 10. 尺寸计算示例

```html
<div class="card">
  <img src="photo.jpg" alt="示例图片" />
  <h2>标题</h2>
  <p>说明文字</p>
</div>
```

```css
.card {
  box-sizing: border-box;
  width: min(100%, 24rem);
  padding: clamp(1rem, 4vw, 1.5rem);
  border: 1px solid #d7d3c8;
}
```

分析：

1. `width: min(100%, 24rem)` 让卡片不宽于容器，也不超过 24rem。
2. `box-sizing: border-box` 让 padding、border 都包含在最大宽度内。
3. `clamp()` 根据视口缩放内边距，同时设置上下限。
4. 图片若没有设置规则，可能溢出；需要媒体约束。

## 11. 用 DevTools 验证

把鼠标悬停在 Elements 面板的元素上，页面会显示盒模型覆盖层。注意区分：

- 页面覆盖层的颜色可能由 DevTools 设置决定。
- 显示的 content 尺寸不等于元素外部占位。
- margin 折叠时，两个元素的 margin 区域可能显示为重叠。
- `transform` 会改变视觉尺寸，但布局盒尺寸不一定改变。

## 关联示例

- [盒模型与 margin 折叠](../../examples/foundations/box-model-margin.html)：对比 `box-sizing`、负 margin、百分比和 BFC 隔离效果。

## 12. 练习

1. 写一个 `width: 300px`、`padding: 20px`、`border: 5px` 的元素，分别计算两种 box-sizing 下的实际宽度。
2. 用 Flex 创建一个包含长单词的子项，先观察溢出，再用 `min-width: 0` 修复。
3. 制作一个 16:9 的响应式图片容器，要求图片填满且不变形。
4. 解释普通流子元素和绝对定位子元素的 50% 宽度为何可能不同。
5. 实现一组垂直间距统一为 16px 的卡片，不依赖每个卡片单独 margin。

> 下一篇：[排版与字体](../02-visual/05-typography.md)。
