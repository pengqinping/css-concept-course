# 09 · 定位与层叠

> 学习目标：理解包含块、偏移属性、sticky 的约束与 z-index 的层级规则，避免“加了 z-index 却不生效”。

## 1. position 的四种基础行为

| 值 | 是否脱离普通流 | 定位参照 |
| --- | --- | --- |
| `static` | 否 | top/right/bottom/left 不生效 |
| `relative` | 否 | 自身原位置 |
| `absolute` | 是 | 最近定位祖先的 padding 盒 |
| `fixed` | 是 | 视口或特定变换祖先 |
| `sticky` | 否 | 正常流位置 + 滚动阈值 |

```css
.rel { position: relative; top: 10px; left: 20px; }
.abs { position: absolute; inset-block-start: 0; inset-inline-end: 0; }
.fixed { position: fixed; inset-block-end: 1rem; inset-inline-end: 1rem; }
```

## 2. relative：移动但不腾位

```html
<div class="box">普通位置</div>
<div class="box moved">移动后</div>
```

```css
.moved {
  position: relative;
  top: 12px;
}
```

视觉上下移 12px，但原位置仍被保留，兄弟元素不会补位。

相对定位还常用于：

- 为绝对定位子元素提供包含块。
- 建立层叠上下文（配合 z-index）。
- 微调图标或装饰元素位置。

## 3. absolute：相对包含块定位

```html
<div class="card">
  <span class="badge">推荐</span>
  <p>卡片内容</p>
</div>
```

```css
.card {
  position: relative;
  padding: 1.25rem;
  border-radius: 0.75rem;
  background: #fbfaf6;
}

.badge {
  position: absolute;
  inset-block-start: 0;
  inset-inline-end: 0;
  padding: 0.25rem 0.5rem;
  background: #c8f35c;
  border-end-end-radius: 0.75rem;
}
```

```text
card 的 padding 盒
┌──────────────────────┐
│               badge  │
│                      │
│ 卡片内容             │
└──────────────────────┘
```

### 定位祖先

只要 position 不是 static，就可能成为包含块，不要求一定是 relative。transform、filter、contain 等属性也可能让元素成为绝对定位后代的包含块。

### inset 简写

```css
.tooltip {
  inset: auto 0 0; /* top right bottom left */
}
```

当 left 与 right 同时设置、width 为 auto 时，元素会拉伸；同时指定 width 和 left/right 时，某些书写模式下 over-constrained，优先级规则会决定忽略哪一边。通常只指定一个方向。

### 负 inset 与溢出

`inset-inline-end: -0.5rem` 可以让元素局部越出容器，但要防止造成页面横向滚动。

## 4. fixed：视口定位

```css
.header {
  position: fixed;
  inset-block-start: 0;
  inset-inline: 0;
  z-index: 100;
}
```

fixed 元素脱离文档流，需要给页面内容预留空间，或给 body 添加对应 padding。

**注意**：祖先元素设置 `transform`、`perspective`、`filter` 或 `will-change: transform` 时，fixed 可能相对于该祖先定位，而不是视口。这是弹层、滚动头部错位的常见原因。

## 5. sticky：滚动到阈值后吸顶

```html
<nav class="toc">章节目录</nav>
<main>正文</main>
```

```css
.toc {
  position: sticky;
  inset-block-start: 1rem;
  align-self: start; /* Flex/Grid 中防止被拉伸 */
}
```

sticky 同时受以下因素约束：

1. 父容器必须有足够滚动空间。
2. 父容器不能有 `overflow: hidden/auto/scroll` 等裁剪/滚动容器，否则吸顶可能失效。
3. 元素不能超出父容器边界。
4. 块级布局中，父级高度通常需要明确或由内容撑开。

```text
┌ parent ──────────────────┐
│ normal                   │
│ ┌ sticky ──────────────┐ │ ← 到 top 后吸顶
│ │ 保持可见             │ │
│ └──────────────────────┘ │
│ remaining content        │
└──────────────────────────┘
```

## 6. 层叠上下文

层叠上下文是一个独立的绘制与层叠单位。常见创建条件：

- 根元素。
- position 为 relative/absolute 且 z-index 不是 auto。
- position 为 fixed/sticky。
- Flex/Grid 子项且 z-index 不是 auto。
- opacity 小于 1。
- transform、filter、perspective、clip-path、mask 等特定值。
- isolation: isolate。
- 某些 will-change 与 contain 值。

```css
.card {
  position: relative;
  isolation: isolate;
}

.card::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background: #f0ebfa;
}
```

`isolation: isolate` 让伪元素留在卡片内部层叠，不会跑到页面背景之后。

## 7. z-index 的规则

```css
.modal { position: fixed; z-index: 1000; }
.toast { position: fixed; z-index: 1100; }
```

- z-index 对定位元素以及 Flex/Grid 子项最有效。
- 数值越大越靠上，但不跨父级层叠上下文任意比较。
- 父级 z-index 为 1 时，其内部 z-index 为 999 的子元素，仍可能低于外部 z-index 为 2 的兄弟。

```text
A 上下文 z-index: 1
└── A 子元素 z-index: 9999

B 上下文 z-index: 2   ← B 整个上下文仍高于 A
```

### 层叠顺序简化

同一上下文内通常按以下顺序绘制：

```text
背景/边框
→ 负 z-index 层叠上下文
→ 普通流块
→ 浮动
→ 行内内容
→ z-index: 0 / auto 定位元素
→ 正 z-index 层叠上下文
```

## 8. opacity、visibility 与 pointer-events

```css
.fade-out {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}
```

- `opacity: 0` 仍占据布局，也仍可能接收点击。
- `visibility: hidden` 不占视觉空间但保留布局，子元素可用 visibility: visible 重新显示。
- `display: none` 不生成盒子，不能直接过渡。
- `pointer-events: none` 阻止命中，但不影响可访问性树或键盘焦点。

弹层关闭时常用 `hidden` 属性配合 CSS；不要在可聚焦内容仅视觉隐藏时使用 `display:none` 以外的“伪隐藏”而不处理焦点。

## 9. 完整浮层示例

```html
<div class="card">
  <img src="cover.jpg" alt="封面" />
  <button class="favorite" type="button" aria-label="收藏">☆</button>
  <div class="card__body">内容</div>
</div>
```

```css
.card {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border-radius: 1rem;
  background: white;
}

.card img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }

.favorite {
  position: absolute;
  inset-block-start: 0.75rem;
  inset-inline-end: 0.75rem;
  z-index: 1;
  width: 2.5rem;
  height: 2.5rem;
  border: 0;
  border-radius: 50%;
  background: rgb(255 255 255 / 90%);
  cursor: pointer;
}
```

## 10. 常见问题

| 症状 | 原因 |
| --- | --- |
| z-index 很大仍被遮挡 | 父级层叠上下文低于其他上下文 |
| fixed 跟随祖先滚动 | 祖先建立了 transform 等包含块 |
| sticky 不吸顶 | 祖先 overflow、父级高度不足或被拉伸 |
| absolute 跑到页面角落 | 没有定位祖先，或祖先不是预期元素 |
| 父级高度塌陷 | 子元素全部脱离普通流 |
| opacity 动画结束后元素仍挡住点击 | 只改了 opacity |

## 关联示例

- [定位与层叠上下文](../../examples/layout/positioning-stacking.html)：四种定位、sticky 阈值、包含块、`z-index` 与 `isolation`。

## 11. 练习

1. 用 relative 微调图标，并说明为什么兄弟元素不会移动。
2. 制作一个相对卡片定位的角标，验证父级 padding 对包含块的影响。
3. 实现 sticky 侧边目录，并用 DevTools 找出 overflow 导致失效的情况。
4. 创建两个层叠上下文，验证“子元素 z-index 再大也无法越过父级上下文”。
5. 修复一个 fixed 弹层因 transform 父级而错位的问题。

> 下一篇：[Flexbox 弹性布局](10-flexbox.md)。
