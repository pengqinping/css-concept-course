# 附录 B · 常见布局配方

本附录服务于 [课程总览](README.md)。

> 每个配方都是最小可运行骨架：用途 → 代码 → 为什么 → 变体与坑 → 详见第 NN 篇。按内容、字体与语言调整，不要当成免思考的模板；机制解释回正文对应篇章看。

## 空间分配

### 1. 水平垂直居中

用途：把一个尺寸未知的子元素放到父容器正中。

```html
<div class="stage"><div class="box">内容</div></div>
```

```css
.stage { min-height: 20rem; display: grid; place-items: center; }
.box { padding: 1rem 1.5rem; }
```

为什么这样写：`place-items: center` 一次设好两个轴的对齐，单个项目不需要知道自己多大；`min-height` 给父容器一个可供居中的空间。

变体与坑：浮层内部可用 `absolute` + `inset-block-start: 50%` + `translate(-50%, -50%)`，但它脱离普通流，父级必须给出明确尺寸，内容过长时会溢出。

详见[第 16 篇](16-grid.md)。

### 2. 等分栏

用途：把容器等宽切成若干列，内容再长也不破坏均分。

```html
<div class="cols"><div>A</div><div>B</div><div>C</div></div>
```

```css
.cols {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}
```

为什么这样写：`1fr` 先扣掉 gap 再分剩余空间；`minmax(0, …)` 把轨道的最小尺寸约束清零，否则一个不换行的长单词会把某一列撑宽。

变体与坑：Flex 的 `flex: 1` 也能等分，但在内容差异大时更容易受 min-content 影响；要比例就写 `2fr 1fr`。纯居中不成立时先检查容器有没有确定宽度。

详见[第 16 篇](16-grid.md)。

### 3. 卡片网格

用途：按容器宽度自动决定列数，窄屏自然减列而不出横向滚动。

```html
<div class="cards"><article class="card">A</article><article class="card">B</article></div>
```

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  gap: 1.25rem;
}
.card { min-width: 0; padding: 1.25rem; }
```

为什么这样写：`min(100%, 18rem)` 保证单列不会宽过容器，`auto-fit` 在轨道空出来时让现有卡片拉伸填满剩下的空间。

变体与坑：`auto-fill` 会保留空轨道、卡片保持较窄宽度，适合固定栅格感。卡片要等高时让卡片自身 `display: flex; flex-direction: column`，页脚用 `margin-block-start: auto` 推到底。

详见[第 16 篇](16-grid.md)。

### 4. 圣杯 / 侧边栏骨架

用途：页头、侧栏、主区、页脚的经典页面骨架，窄屏把侧栏移到主内容之后。

```html
<div class="layout">
  <header class="layout__header">页头</header><aside class="layout__aside">侧栏</aside>
  <main class="layout__main">主内容</main><footer class="layout__footer">页脚</footer>
</div>
```

```css
.layout {
  min-height: 100dvh;
  display: grid;
  grid-template-columns: 16rem minmax(0, 1fr);
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "aside main"
    "footer footer";
}
.layout__header { grid-area: header; }
.layout__aside { grid-area: aside; }
.layout__main { grid-area: main; min-width: 0; }
.layout__footer { grid-area: footer; }

@media (max-width: 48rem) {
  .layout {
    grid-template-columns: 1fr;
    grid-template-areas: "header" "main" "aside" "footer";
  }
}
```

为什么这样写：命名区域让"哪块放在哪"一眼可读；`minmax(0, 1fr)` 加主区的 `min-width: 0` 一起防止长代码块撑破页面。

变体与坑：DOM 顺序尽量跟随阅读顺序，别只靠 `grid-area` 重排导致焦点错乱。断点里改的是区域排列而不是只改列宽；侧栏内容很多时要单独给滚动容器。

详见[第 16 篇](16-grid.md)。

### 5. 粘性页脚

用途：内容不足一屏时页脚贴在底部，内容变长时页脚正常往下走。

```html
<div class="page"><header>页头</header><main>内容</main><footer>页脚</footer></div>
```

```css
.page {
  min-height: 100dvh;
  display: grid;
  grid-template-rows: auto 1fr auto;
}
```

为什么这样写：中间行的 `1fr` 吃掉剩余高度，把页脚推到底；用 `dvh` 而不是 `vh`，避免移动端地址栏伸缩时底部被遮住。

变体与坑：写成固定 `height` 而不是 `min-height`，内容一变长就会溢出。若中间区域要自己滚动，给那一行补 `min-height: 0`，否则滚动链断不掉。

详见[第 16 篇](16-grid.md)。

## 内容与媒体

### 6. 宽高比媒体

用途：给图片或视频预留固定比例的位置，加载前后不跳版。

```html
<div class="media"><img src="photo.jpg" alt="示例" /></div>
```

```css
.media { aspect-ratio: 16 / 9; overflow: hidden; }
.media > img { width: 100%; height: 100%; object-fit: cover; }
```

为什么这样写：`aspect-ratio` 只规定盒子的首选比例，`object-fit` 单独规定内容如何填满它；一个管容器，一个管内容，职责不重叠。

变体与坑：内容本身可能反过来撑破比例，所以要配合 `overflow` 或给子项 `min-height: 0`。要完整保留画面就换 `object-fit: contain`，代价是留边。

详见[第 12 篇](12-display-overflow.md)。

### 7. 文本截断

用途：超长文本在单行或多行后用省略号收尾。

```html
<p class="truncate">很长很长的一段文件名……</p>
<p class="clamp">很长很长的一段摘要……</p>
```

```css
.truncate {
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.clamp {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  overflow: hidden;
}
```

为什么这样写：省略号只在"宽度受限 + 不换行 + 溢出隐藏"同时成立时才出现；多行版借 `-webkit-box` 的行向布局才能按行数截断。

变体与坑：Flex/Grid 子项的默认 `min-width: auto` 会让截断失效，必须先归零。截断会隐藏内容，关键文字别用；长 URL 想保留全部信息就换 `overflow-wrap: anywhere` 让它断行。

详见[第 09 篇](09-typography.md)。

### 8. 滚动吸附

用途：横向图集或整屏区块滚动时，自动对齐到每个项目的起点。

```html
<div class="gallery"><div class="gallery__item">1</div><div class="gallery__item">2</div></div>
```

```css
.gallery {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
}
.gallery__item { flex: 0 0 80%; scroll-snap-align: start; }
```

为什么这样写：容器用 `scroll-snap-type` 声明"按哪个轴、是否强制吸附"，项目用 `scroll-snap-align` 声明"吸附到自己的哪条边"，两边缺一不可。

变体与坑：祖先的 `overflow` 会吞掉吸附效果；有粘性页头时给滚动容器加 `scroll-padding-inline-start`。平滑滚动记得给 `prefers-reduced-motion` 留降级。

详见[第 27 篇](27-modern-features.md)。

## 导航与浮层

### 9. 导航工具栏

用途：左侧标题、右侧操作组的工具栏，窄屏时操作组换行或折成菜单。

```html
<div class="toolbar">
  <strong>标题</strong><div class="toolbar__actions"><button>取消</button><button>保存</button></div>
</div>
```

```css
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.toolbar__actions { display: flex; gap: 0.5rem; margin-inline-start: auto; }
```

为什么这样写：`space-between` 把两组推到两端，而 `margin-inline-start: auto` 保证即使只剩一组，它也会贴到右侧。

变体与坑：折叠菜单需要 JS 同步 `aria-expanded`，并处理焦点、点击外部关闭和 Escape。别用 `order` 改视觉顺序却让 Tab 顺序与画面对不上。

详见[第 15 篇](15-flex.md)。

### 10. 弹层遮罩

用途：视口居中的模态面板，带遮罩且内容过长时面板内部滚动。

```html
<div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal__panel"><h2 id="modal-title">标题</h2><p>内容</p></div>
</div>
```

```css
.modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgb(20 22 18 / 55%);
}
.modal__panel {
  width: min(100%, 32rem);
  max-height: calc(100dvh - 2rem);
  overflow-y: auto;
  padding: 1.5rem;
}
```

为什么这样写：`fixed` + `inset: 0` 撑满视口，`grid` 负责居中，`min()` 让面板在窄屏自动收窄；`max-height` 把滚动留在面板内部，遮罩本身不动。

变体与坑：祖先若有 `transform` 会改变 `fixed` 的包含块，弹层应挂到 `body` 下（层叠原理见[第 08 篇](08-stacking-context.md)）。CSS 只负责视觉，焦点陷阱、Escape、背景滚动锁定与关闭后焦点恢复仍要用 JS 或原生 `<dialog>` 处理。

详见[第 22 篇](22-native-ui.md)。

> 下一份附录：[附录 C · 练习与参考答案](appendix-c-exercises.md)
