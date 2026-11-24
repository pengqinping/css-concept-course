# 21 · 常见布局方案

> 每个方案都给出 HTML、CSS 和适用边界。复制后根据内容、字体、语言和设计系统调整，不要当成无需思考的模板。

## 1. 水平垂直居中

### Flex：适合已知尺寸或任意内容

```html
<div class="center">
  <div class="center__box">居中内容</div>
</div>
```

```css
.center {
  min-height: 20rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.center__box { padding: 1rem 1.5rem; }
```

### Grid：最简洁

```css
.center {
  min-height: 20rem;
  display: grid;
  place-items: center;
}
```

### absolute + transform：适合浮层内部

```css
.center { position: relative; }
.center__box {
  position: absolute;
  inset-block-start: 50%;
  inset-inline-start: 50%;
  transform: translate(-50%, -50%);
}
```

边界：transform 方案不参与流，父级需要明确尺寸；内容可能溢出。

## 2. 两端对齐工具栏

```html
<div class="toolbar">
  <strong>标题</strong>
  <div class="toolbar__actions">
    <button>取消</button>
    <button>保存</button>
  </div>
</div>
```

```css
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.toolbar__actions { display: flex; gap: 0.5rem; }
```

更复杂的导航可用自动 margin 将一组操作推到右侧：

```css
.toolbar__actions { margin-inline-start: auto; }
```

## 3. 圣杯布局

```html
<div class="layout">
  <header class="layout__header">页头</header>
  <aside class="layout__aside">侧栏</aside>
  <main class="layout__main">主内容</main>
  <footer class="layout__footer">页脚</footer>
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

边界：DOM 顺序应尽量与主要阅读顺序一致，视觉重排不要制造焦点错乱。

## 4. 自动响应式卡片墙

```html
<div class="cards">
  <article class="card">卡片 A</article>
  <article class="card">卡片 B</article>
  <article class="card">卡片 C</article>
</div>
```

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  gap: 1.25rem;
}

.card {
  min-width: 0;
  padding: 1.25rem;
  border: 1px solid #d7d3c8;
  border-radius: 0.75rem;
  background: #fbfaf6;
}
```

边界：项目较多时 auto-fit 会保持较宽卡片；若希望空轨道占位，使用 auto-fill。

## 5. 等高卡片与对齐页脚

```css
.card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card__body { flex: 1; }
.card__footer { margin-block-start: auto; }
```

多张卡片需要图片、标题、正文、页脚跨行对齐时，使用 Grid + subgrid：

```css
.cards { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.card {
  display: grid;
  grid-row: span 4;
  grid-template-rows: subgrid;
  gap: 0.75rem;
}
```

## 6. 响应式导航

```html
<header class="nav">
  <a class="nav__brand" href="/">站点</a>
  <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="nav-menu">菜单</button>
  <nav class="nav__menu" id="nav-menu">
    <a href="/">首页</a>
    <a href="/docs">文档</a>
    <a href="/about">关于</a>
  </nav>
</header>
```

```css
.nav {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.nav__menu { display: flex; gap: 1rem; margin-inline-start: auto; }
.nav__toggle { display: none; }

@media (max-width: 40rem) {
  .nav { flex-wrap: wrap; }
  .nav__toggle { display: inline-flex; margin-inline-start: auto; }
  .nav__menu {
    display: none;
    flex-basis: 100%;
    flex-direction: column;
    margin-inline-start: 0;
  }
  .nav__toggle[aria-expanded="true"] + .nav__menu { display: flex; }
}
```

边界：折叠菜单需要 JavaScript 更新 `aria-expanded`；打开时考虑焦点管理、点击外部关闭和 Escape。

## 7. 粘性页头 + 锚点偏移

```css
.header {
  position: sticky;
  inset-block-start: 0;
  z-index: 100;
  background: rgb(255 255 255 / 92%);
  backdrop-filter: blur(12px);
}

section { scroll-margin-block-start: 5rem; }
```

边界：sticky 祖先 overflow 会限制吸顶；固定页头应预留占位。

## 8. 媒体对象

```html
<div class="media">
  <img class="media__avatar" src="avatar.jpg" alt="" />
  <div class="media__body">
    <h2>标题</h2>
    <p>说明文字</p>
  </div>
</div>
```

```css
.media {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.media__avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  object-fit: cover;
  flex: none;
}

.media__body { min-width: 0; }
```

## 9. 表单两列布局

```html
<form class="form">
  <label>姓名<input name="name" autocomplete="name" /></label>
  <label>邮箱<input name="email" type="email" autocomplete="email" /></label>
  <label class="form__full">留言<textarea name="message"></textarea></label>
  <button class="form__full" type="submit">提交</button>
</form>
```

```css
.form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.form label { display: grid; gap: 0.35rem; }
.form input,
.form textarea { width: 100%; }
.form__full { grid-column: 1 / -1; }

@media (max-width: 36rem) {
  .form { grid-template-columns: 1fr; }
}
```

边界：错误提示、说明文字和必填标记都应有明确语义与关联。

## 10. 固定比例缩略图

```html
<div class="thumb">
  <img src="photo.jpg" alt="示例照片" />
</div>
```

```css
.thumb {
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border-radius: 0.75rem;
  background: #e9e4d7;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

## 11. 单行省略

```css
.truncate {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
```

要求宽度受到约束；在 Flex/Grid 中通常配合 `min-width: 0`。

## 12. 多行省略

```css
.clamp {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  overflow: hidden;
}
```

边界：行数截断会隐藏内容，不适合关键正文；浏览器支持以 `line-clamp` 标准化进度为准。

## 13. 左右固定、中间滚动区域

```html
<div class="panes">
  <aside class="panes__side">目录</aside>
  <main class="panes__main">内容</main>
</div>
```

```css
.panes { display: flex; min-height: 0; }
.panes__side { flex: 0 0 16rem; overflow-y: auto; }
.panes__main { flex: 1; min-width: 0; overflow-y: auto; }
```

父容器需要明确高度或 Flex/Grid 的 min-height: 0 链，否则可能一起撑长而不是内部滚动。

## 14. 徽章与状态点

```html
<span class="badge">新功能</span>
```

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: #e6f4c9;
  color: #3d601c;
  font-size: 0.75rem;
  line-height: 1.4;
}
```

状态不能只靠颜色表达，应同时提供文字或可访问名称。

## 15. 无障碍视觉隐藏

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}
```

用于给图标按钮补充屏幕阅读器文本。不要用此方法隐藏实际可聚焦元素。

## 16. 弹层遮罩

```html
<div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal__panel">
    <h2 id="modal-title">标题</h2>
    <p>内容</p>
  </div>
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
  border-radius: 1rem;
  background: white;
}
```

边界：CSS 只负责视觉，还需处理焦点陷阱、关闭按钮、Escape、背景滚动锁定和打开前焦点恢复。

## 17. 组件查询卡片

```css
.card-wrapper { container-type: inline-size; }

@container (min-width: 32rem) {
  .card {
    display: grid;
    grid-template-columns: 10rem minmax(0, 1fr);
    gap: 1.25rem;
  }
}
```

同一个卡片放入主栏或侧栏时，可以根据自身可用宽度改变布局，而不是猜测当前设备尺寸。

## 18. 调试模板

当布局不符合预期时，临时添加：

```css
.debug,
.debug * {
  outline: 1px solid rgb(239 118 95 / 65%);
}

.debug {
  background-image:
    linear-gradient(rgb(200 243 92 / 15%) 1px, transparent 1px),
    linear-gradient(90deg, rgb(200 243 92 / 15%) 1px, transparent 1px);
  background-size: 8px 8px;
}
```

只用于本地排查，不要提交到生产样式。

> 练习这些方案的变体与答案见 [练习与参考答案](22-exercises.md)。
