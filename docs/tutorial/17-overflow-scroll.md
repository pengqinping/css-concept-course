# 17 · overflow 与滚动

> **前置**：[04](04-box-model.md)——盒模型；[08](08-display-flow.md)——隐藏三式；[09](09-position.md)——定位参照。
>
> 上一篇：[16](16-pseudo-elements.md) ｜ 下一篇：[层叠上下文](18-stacking-context.md) ｜ [教程总览](README.md)

```css
.panel { height: 200px; overflow: hidden; }
```

一行 `overflow: hidden` 裁掉溢出，也**悄悄把盒子变成滚动容器性质的盒子**。这一章讲全：overflow 五值语义、裁剪的作用边界（absolute 怎么"逃"出裁剪）、滚动条的工程问题、scroll-snap 与滚动穿透治理。

## overflow 五值，重点是 clip

| 值 | 行为 | 连带影响 |
| --- | --- | --- |
| `visible`（默认） | 溢出画到盒外 | 无 |
| `hidden` | 裁掉；**JS 仍可 scrollTo 滚到** | 成为滚动容器 + 独立格式化上下文 |
| `scroll` | 保留滚动条（内容不满也占位） | 滚动容器 |
| `auto` | 需要时才出滚动条 | 滚动容器 |
| **`clip`** | 裁掉，**彻底不可滚、无滚动器开销** | **不是滚动容器**（配 `overflow-clip-margin` 留缓冲） |

`hidden` 与 `clip` 的本质差别：hidden 的内容"理论上可达"（JS/键盘可滚），clip 永久不可达且开销最低。**"只裁不滚"的现代答案是 `overflow: clip`**。

## 裁剪的边界：为什么 overflow 管不住 absolute

裁剪不是"画个框框罩住所有后代"，它沿着**包含块链**传递——这是大量"裁不住"事故的根源：

- 普通后代：被裁。
- **absolute/fixed 后代，其包含块是裁剪元素的祖先**（例如裁剪层不是定位元素）→ **逃出裁剪**，从框上飞出去。
- 想裁住一切：让裁剪元素自己当包含块（加 `position: relative`），或用 `clip` + `contain: paint`，或 `filter`/`transform` 顺手创建边界（有副作用，第 18/21 篇）。

## 滚动条的工程问题

- **滚动条占宽导致布局跳动**：内容从"不满一屏"变"超一屏"时滚动条突然出现，横向抖一下。现代解法 **`scrollbar-gutter: stable`**——预先保留滚动条槽位，内容变化不再挤布局。
- **隐藏滚动条但保留滚动**：`scrollbar-width: none`（标准）或 `::-webkit-scrollbar { display: none }`（Chromium/Safari）——横向滑动卡片列的标配；**给键盘/读屏留可达性**（内容必须仍可通过键盘滚动）。
- **给滚动条上色**：`scrollbar-color`（Firefox/标准）与 `::-webkit-scrollbar-thumb`（Webkit）。

## 滚动吸附：scroll-snap 三件套

```css
.carousel { overflow-x: auto; scroll-snap-type: x mandatory;
            scroll-padding-inline: 1rem; }
.carousel .slide { scroll-snap-align: start; scroll-margin-inline: 1rem; }
```

`mandatory` 强吸附（松手必吸，适合分页）、`proximity` 近了才吸（适合列表）。`scroll-padding` 在容器侧、`scroll-margin` 在项目侧——**fixed 导航遮挡锚点、锚点贴死页顶**的修复也是这对属性（对 `:target` 生效）。平滑滚动 `scroll-behavior: smooth`（包一层动效偏好媒体查询）。

## 滚动穿透与 sticky 的滚动容器语义

- **弹层滚到底后带动背景滚**：弹层容器 `overscroll-behavior: contain` 截断滚动链（`none` 连回弹也禁）——移动端弹窗标配。
- **sticky 失效的滚动容器解释**：sticky 钉在"**最近的滚动容器**"上。中间某祖先 `overflow: hidden` 虽然从不滚动，但它**就是一个滚动容器**——sticky 被它截胡，看起来"失灵"（第 09 篇问题 2 的机制层答案）。纯裁剪需求改用 `clip`，就不抢 sticky 的归属。

## 常见问题

**问题 1：下拉菜单/悬浮角标被父容器裁掉一半**
- **原因**：父容器 `overflow: hidden`，而菜单是 absolute 子元素且父容器不是它的包含块——按包含块链它本该逃逸，但如果父容器同时是参照（relative）就会被裁死。
- **修法**：裁剪层与参照层拆开（外层裁剪、内层 relative 参照）；或改 `overflow: clip` + `overflow-clip-margin` 给溢出留缓冲。

**问题 2：内容变多时页面横向抖一下**
- **原因**：滚动条突然出现挤压内容区。
- **修法**：滚动容器 `scrollbar-gutter: stable`；整页场景在 `html` 上设。

**问题 3：sticky 表头/侧栏不吸顶**
- **原因**：机制见上——被中间层 hidden 的"不滚滚动容器"截胡；或父元素没有滚动行程。
- **修法**：中间层 hidden 改 `clip`；确认 sticky 元素父级有可滚高度。

**问题 4：`overflow-x: auto` 写完，y 方向内容也被裁**
- **原因**：规范规定一个方向非 visible/clip 时，另一方向的 `visible` 自动变 `auto`——"横滚纵露"单盒不成立。
- **修法**：拆两层：外层裁剪/露头，内层滚动。

**问题 5：弹层滚动穿透**
- **修法**：弹层 `overscroll-behavior: contain`；iOS 兼容不足时叠加"打开时锁 `body` overflow"的传统方案。

## 动手验证

[打开实验台：scroll-snap 吸附节奏实测](../../examples/layout/scroll-snap.html)

<iframe class="demo-frame" src="/css-concept-course/examples/layout/scroll-snap.html" title="scroll-snap 实验" loading="lazy"></iframe>

[打开 demo：overflow 各值对照](../../examples/minimal/12-display-overflow.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/12-display-overflow.html" title="overflow 实验" loading="lazy"></iframe>

snap 实验台切 mandatory/proximity、调 scroll-padding；overflow demo 里试 `clip` 与 `hidden` 的"能否被滚到"差别，再给盒内放 absolute 子元素复现"逃逸"。

## 本章要点

- `hidden` 可被 JS 滚到、`clip` 彻底不可滚且最便宜；"只裁不滚"用 clip。
- 裁剪沿**包含块链**传递——absolute 逃逸的条件与治理（relative/clip/contain）。
- `scrollbar-gutter: stable` 防布局跳动；隐藏滚动条仍保键盘可达。
- snap：容器 type + 项目 align + 两侧 padding/margin；锚点遮挡同样修在 margin/padding。
- sticky 的归属是"最近滚动容器"——中间层 hidden 会截胡；弹层穿透 `overscroll-behavior: contain`。

下一篇 [18 · 层叠上下文](18-stacking-context.md)：z-index: 9999 为什么还被盖住。
