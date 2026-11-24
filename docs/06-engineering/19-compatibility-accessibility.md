# 19 · 兼容性、无障碍与测试

> 学习目标：用渐进增强和真实目标环境管理 CSS 兼容性，正确使用 `@supports`、Baseline、caniuse 与 Autoprefixer，并让语义、焦点、对比度、缩放、动画偏好、强制颜色、触控和 RTL 成为样式设计的一部分。

## 1. 兼容性不是“让旧浏览器一模一样”

兼容性目标是：**在支持范围内，内容可用、任务可完成、信息不丢失。** 不要求圆角、阴影、布局细节在每个环境完全一致。

```text
核心内容与任务
    │
    ├─▶ 所有目标环境：语义、可读文本、基本布局、可操作控件
    ├─▶ 支持增强特性：Grid、容器查询、逻辑属性、现代颜色
    └─▶ 用户偏好：减弱动画、更多对比度、强制颜色、深色主题
```

渐进增强先保证基础版本成立，再叠加增强。与之相对的“优雅降级”通常从完整现代版本出发逐步削减，两者可以结合，但新项目更适合先写基础可用状态。

## 2. 基线支持与信息来源

### 2.1 Baseline

Web Platform Baseline 用浏览器集合中的共同支持情况帮助判断一项特性是否足够成熟。可以把它当作“能否默认使用”的参考，而不是项目支持策略本身。

判断时仍要区分：

- 基础语法是否支持；
- 是否只有部分实现；
- 浏览器是否修复了关键布局 bug；
- 目标用户是否使用旧版本、WebView 或企业环境；
- 辅助技术和其他浏览器功能是否配套。

容器查询、容器单位等能力在现代核心浏览器中已广泛可用，但样式查询、某些逻辑属性组合或新颜色函数仍应逐项核对。不要把“大多数浏览器支持”理解为“所有目标环境都支持”。

### 2.2 caniuse、MDN BCD 与真实数据

| 来源 | 适合回答 | 局限 |
| --- | --- | --- |
| caniuse | 特性覆盖范围、部分支持、已知问题 | 聚合数据，不代表你的用户 |
| MDN BCD | 具体浏览器版本和兼容性细节 | 需要结合项目支持范围 |
| 官方规范与发布说明 | 语法、实现意图、新版本变化 | 不一定反映线上用户环境 |
| 分析数据、日志、设备统计 | 用户实际使用什么 | 可能缺少辅助技术和边缘设备信息 |

使用 caniuse 时重点看 notes、partial support 和 issue 链接。一个属性“支持”了，不代表容器查询中的等价写法、选择器语法或边界行为也支持。

## 3. 渐进增强与 `@supports`

### 3.1 基础规则在前，增强规则在后

```css
.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.cards > * {
  flex: 1 1 18rem;
  min-inline-size: 0;
}

@supports (display: grid) {
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  }
}
```

不支持 Grid 的浏览器使用 Flex 版本；支持 Grid 的浏览器获得更合适的轨道分配。两条路径都不依赖 JavaScript。

### 3.2 常见检测形式

```css
@supports (display: grid) { /* 属性与值 */ }
@supports selector(:focus-visible) { /* 选择器 */ }
@supports (container-type: inline-size) { /* 容器能力 */ }
@supports not (display: grid) { /* 否定条件 */ }
@supports ((display: grid) and (container-type: inline-size)) { /* 组合条件 */ }
```

检测的是“浏览器是否接受这个语法”，不是“实现是否完全正确”。某些旧实现可能返回 `true`，但仍有布局缺陷，因此需要行为测试。

### 3.3 JavaScript 特性检测

```js
if (CSS.supports("container-type", "inline-size")) {
  document.documentElement.classList.add("has-container-queries");
}

if (CSS.supports("selector(:focus-visible)")) {
  console.log("当前环境识别 :focus-visible");
}
```

纯布局增强应优先使用 CSS 的 `@supports`，避免依赖脚本执行。需要脚本控制交互时，再使用 `CSS.supports()`，并确保无脚本时核心内容仍可访问。

### 3.4 回退的边界

```css
.button {
  padding: 0.75rem;
  padding: max(0.75rem, env(safe-area-inset-top));
}
```

前一条声明是基础值，后一条在不支持 `max()`/`env()` 时会被忽略。回退应保持功能，而不是把按钮变成不可点击或文本被裁切。

## 4. Autoprefixer 与构建目标

Autoprefixer 根据 Can I Use 数据补充需要的前缀，不负责实现缺失功能：

```js
// postcss.config.js（示例，需在项目中实际安装）
export default {
  plugins: {
    autoprefixer: {}
  }
};
```

浏览器目标通常由 Browserslist 配置：

```text
> 0.5%
last 2 versions
Firefox ESR
not dead
```

注意事项：

- 目标配置应来自真实用户和产品支持承诺，不追求支持所有历史版本。
- `not dead` 等动态查询会随数据库变化，构建结果可能改变，发布策略要明确。
- Autoprefixer 不能补出缺少的 Grid、容器查询、`:has()` 或逻辑属性回退。
- 它也不会修复旧浏览器缺少 Flex/Grid gap 的行为，必要时仍需显式 fallback。
- 不要无依据手写大量前缀，也不要关闭构建检查后假设“现代浏览器都一样”。

## 5. 浏览器测试矩阵

测试矩阵应按风险分层，而不是追求穷举。

| 层级 | 环境 | 重点 |
| --- | --- | --- |
| P0 | 团队主推的 Windows/macOS Chrome、Edge、Firefox、Safari | 日常功能、构建产物、视觉回归 |
| P0 | iOS Safari 真机、Android Chrome 真机 | 视口、软键盘、触控、安全区、动态高度 |
| P1 | 上一版核心浏览器 | 实际回退、`@supports`、字体和布局差异 |
| P1 | Windows 高对比度/强制颜色、系统减弱动画 | 用户偏好和系统颜色 |
| P1 | 键盘-only、屏幕阅读器代表组合 | 焦点顺序、名称、状态、隐藏内容 |
| P2 | 企业 WebView、旧版 Android、特殊输入设备 | 产品承诺范围内的特殊环境 |

每条测试记录应包含浏览器版本、操作系统、设备、视口、DPR、复现步骤和截图/录屏。桌面 DevTools 可以模拟很多条件，但不能替代真实触摸、软键盘和安全区测试。

## 6. 语义与键盘焦点

### 6.1 CSS 不能修复错误语义

```html
<!-- 反例：看起来像按钮，但没有按钮语义 -->
<div class="button" onclick="save()">保存</div>

<!-- 正确：原生按钮自带键盘、焦点和状态语义 -->
<button class="button" type="button">保存</button>
```

优先使用原生 `button`、`a`、`input`、`select` 和 `details`。链接用于导航，按钮用于执行动作；不要用 `href="#"` 伪装按钮。若必须自定义控件，需要完整实现键盘交互、ARIA 状态和焦点管理，CSS 只负责外观。

### 6.2 永远保留可见焦点

```css
.button:focus {
  outline: 3px solid #0b63ce;
  outline-offset: 3px;
}

/* 支持 focus-visible 时，鼠标操作可以减少干扰，键盘焦点仍清晰 */
@supports selector(:focus-visible) {
  .button:focus:not(:focus-visible) { outline: none; }
  .button:focus-visible { outline: 3px solid #0b63ce; outline-offset: 3px; }
}
```

不要在尚未提供替代焦点样式时写 `outline: none`。阴影也可以形成焦点环，但在强制颜色模式中可能被系统移除，因此应优先使用 `outline`。

其他常见问题：

- 父容器 `overflow: hidden` 裁掉焦点环。
- 用 `opacity: 0` 隐藏可聚焦元素，但键盘仍能聚焦到不可见目标。
- DOM 顺序与视觉顺序不一致，焦点移动方向令人困惑。
- 删除元素或弹窗关闭后没有合理返回焦点，这是 JavaScript 焦点管理问题，但常与 CSS 可见性一起出现。

## 7. 颜色对比度

WCAG 2.2 AA 的常用对比度要求：

| 内容 | 最低对比度 |
| --- | --- |
| 普通文本 | 4.5:1 |
| 大号文本：至少 24px 常规，或约 18.66px 粗体 | 3:1 |
| 识别控件、状态、重要图形所必需的视觉信息 | 3:1，并考虑与相邻颜色的关系 |
| 纯装饰、禁用控件、Logo 等 | 有特定豁免，不应随意扩大解释 |

仅靠肉眼很难稳定判断。使用 DevTools 颜色选择器、对比度工具或 axe 检查实际前景、背景和透明叠加后的结果。

```css
.muted {
  color: #4f635c; /* 需要与真实背景一起验证 */
}

.button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
```

`opacity` 会同时改变文本和背景的有效对比度，不能只检查变量色值。不要只靠颜色表达错误、选中或必填状态，还应结合文字、图标、边框或 ARIA。

## 8. 缩放、重排与文字间距

### 8.1 文本缩放与浏览器缩放

WCAG 要求文本能在不使用辅助技术的情况下放大到 200% 而不丢失内容或功能。桌面浏览器 400% 缩放时，内容应能在约 320 CSS 像素宽度下重排，避免出现不必要二维滚动。

```css
.page {
  inline-size: 100%;
  max-inline-size: 70rem;
  margin-inline: auto;
}

.card {
  min-inline-size: 0;
  overflow-wrap: anywhere;
}
```

避免：

- 用固定高度裁切正文；
- 把关键按钮放在只有鼠标悬停才能到达的位置；
- 用 `transform: scale()` 模拟响应式布局；
- 禁止页面缩放；
- 用 `white-space: nowrap` 锁定长标题。

### 8.2 文字间距覆盖测试

WCAG 1.4.12 要求用户覆盖以下文字间距时不丢失内容：

- 行高不少于字号的 1.5 倍；
- 段后间距不少于字号的 2 倍；
- 字间距不少于 0.12 倍字号；
- 词间距不少于 0.16 倍字号。

可用临时测试样式验证：

```css
/* 仅用于测试，不要写进正式主题 */
* {
  line-height: 1.5 !important;
  letter-spacing: 0.12em !important;
  word-spacing: 0.16em !important;
}

p { margin-block-end: 2em !important; }
```

如果按钮、导航或卡片文字被裁切，通常是固定高度、`overflow: hidden` 或过度紧凑的行高导致的。

## 9. 减弱动画、更多对比度与强制颜色

### 9.1 `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }

  .spinner { animation: none; }

  .card {
    transition-duration: 0.01ms;
    animation-iteration-count: 1;
  }
}
```

目标是减少非必要运动，而不是让交互状态消失。加载指示器可以换成静态文字或进度条；视差、自动播放和大幅位移动画应优先关闭。不要只依赖 `transition: none`，还要检查 JavaScript 驱动的滚动和动画。

### 9.2 `prefers-contrast`

```css
@media (prefers-contrast: more) {
  .card { border-color: currentColor; }
  .muted { color: inherit; }
}
```

`prefers-contrast: more` 与系统强制颜色不是一回事。它表达用户希望增加对比度，具体值可能包括 `more`、`less` 或 `custom`。

### 9.3 `forced-colors`

Windows 高对比度等模式会启用 `forced-colors: active`。浏览器可能用系统颜色替换作者颜色，并忽略背景图片和阴影。

```css
@media (forced-colors: active) {
  .card {
    border: 1px solid CanvasText;
    background: Canvas;
    color: CanvasText;
  }

  .button--primary {
    border: 1px solid ButtonText;
    color: ButtonText;
    background: ButtonFace;
  }

  .icon { forced-color-adjust: auto; }
}
```

使用 `Canvas`、`CanvasText`、`ButtonFace`、`ButtonText`、`LinkText`、`Highlight` 等系统颜色，通常比写死品牌色更可靠。只有确实需要保留复杂图形语义时，才局部使用 `forced-color-adjust: none`，并验证所有状态仍可辨认。

## 10. 触摸目标

```css
.icon-button {
  display: inline-grid;
  min-inline-size: 2.75rem;
  min-block-size: 2.75rem;
  place-items: center;
}
```

WCAG 2.2 AA 的 2.5.8 要求目标至少 24×24 CSS 像素，并允许通过间距或特定例外满足；2.5.5 AAA 建议 44×44 CSS 像素。实际产品常把约 44px 作为舒适触控尺寸，但不应机械放大数据表格中的每个密集控件。

需要检查：

- 相邻目标不会重叠或被误触；
- 图标的可点击区域不只有图形本身；
- 输入框、下拉框和复选框的可操作区域足够大；
- 悬停内容不能是触屏获得关键信息的唯一途径；
- 安全区和软键盘不会遮挡主要操作。

## 11. RTL 与逻辑属性

从右到左布局不应通过整套镜像样式实现。优先使用逻辑属性：

```css
.callout {
  margin-inline: 1rem;
  padding-inline-start: 1rem;
  border-inline-start: 0.25rem solid currentColor;
  text-align: start;
}

.dialog {
  inset-inline: 1rem;
}
```

测试时切换 `<html dir="rtl">` 或局部 `dir="rtl"`，检查：

- 导航、面包屑、步骤条和前后按钮方向是否合理；
- 箭头、进度、勾选等方向图标是否需要翻转；
- Logo、照片、媒体控制按钮和数学表达式不应盲目镜像；
- `translateX()`、`left`/`right`、背景定位等物理值是否需要调整；
- 数字、日期、货币和代码片段是否符合语言习惯；
- 文本截断方向与省略号位置是否自然。

只翻转真正表达方向的图标，不要对整个组件使用 `scaleX(-1)`，否则文字也会镜像。

## 12. 视觉隐藏与可访问名称

视觉隐藏用于屏幕阅读器可读、视觉上不可见的内容，例如输入框补充说明：

```css
.visually-hidden {
  position: absolute;
  inline-size: 1px;
  block-size: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}
```

不要使用 `display: none` 或 `visibility: hidden` 隐藏需要被屏幕阅读器读取的内容，它们通常会把元素从可访问性树中移除。

“跳到主要内容”链接则应在键盘聚焦时显示：

```css
.skip-link {
  position: fixed;
  inset-block-start: 0.75rem;
  inset-inline-start: 0.75rem;
  z-index: 1000;
  padding: 0.75rem 1rem;
  transform: translateY(-200%);
}

.skip-link:focus { transform: translateY(0); }
```

隐藏可聚焦元素时要特别小心。若元素仍可通过 Tab 到达，但屏幕上完全不可见，就会形成“焦点消失”。

## 13. 完整示例

### 完整示例 1：可访问的交互组件

保存为 `accessible-ui.html`。使用 Tab 键遍历页面，再在系统或 DevTools 中切换减弱动画、强制颜色和增加对比度。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>可访问的交互组件</title>
  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      font: 1rem/1.6 system-ui, sans-serif;
      color: #18332b;
      background: #f3f7f5;
    }

    .skip-link {
      position: fixed;
      inset-block-start: 0.75rem;
      inset-inline-start: 0.75rem;
      z-index: 1000;
      padding: 0.75rem 1rem;
      color: #fff;
      background: #123d31;
      transform: translateY(-200%);
    }

    .skip-link:focus { transform: translateY(0); }

    .site-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 1rem clamp(1rem, 4vw, 2.5rem);
      color: #fff;
      background: #123d31;
    }

    .site-nav { display: flex; flex-wrap: wrap; gap: 1rem; }
    .site-nav a { color: inherit; text-underline-offset: 0.2em; }

    main {
      inline-size: min(calc(100% - 2rem), 44rem);
      margin-inline: auto;
      padding-block: 2rem;
    }

    .card {
      padding: clamp(1rem, 4vw, 1.75rem);
      border: 1px solid #9db8ad;
      border-radius: 0.75rem;
      background: #fff;
    }

    .card h1 { margin-block-start: 0; }
    .muted { color: #4f635c; }

    .field { display: grid; gap: 0.4rem; margin-block-start: 1.5rem; }
    .field input {
      min-block-size: 2.75rem;
      padding: 0.6rem 0.75rem;
      border: 1px solid #56776b;
      border-radius: 0.4rem;
      color: inherit;
      background: #fff;
      font: inherit;
    }

    .actions { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-block-start: 1.25rem; }

    .button {
      min-inline-size: 2.75rem;
      min-block-size: 2.75rem;
      padding: 0.6rem 1.1rem;
      border: 1px solid #245d4d;
      border-radius: 0.4rem;
      color: #245d4d;
      background: #fff;
      font: inherit;
      cursor: pointer;
    }

    .button--primary { color: #fff; background: #245d4d; }

    :focus-visible {
      outline: 3px solid #0b63ce;
      outline-offset: 3px;
    }

    .status {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-block-start: 1.25rem;
      padding: 0.75rem;
      border-inline-start: 0.25rem solid #245d4d;
      background: #e6f0ec;
    }

    .spinner {
      inline-size: 1.25rem;
      block-size: 1.25rem;
      border: 0.2rem solid #9db8ad;
      border-block-start-color: #245d4d;
      border-radius: 50%;
      animation: spin 800ms linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    html { scroll-behavior: smooth; }

    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      .spinner { animation: none; border-block-start-color: inherit; }
    }

    @media (prefers-contrast: more) {
      .card, .field input, .button { border-width: 2px; border-color: currentColor; }
      .muted { color: inherit; }
    }

    @media (forced-colors: active) {
      .card, .field input { border-color: CanvasText; background: Canvas; color: CanvasText; }
      .button { color: ButtonText; background: ButtonFace; border-color: ButtonText; }
      .button--primary { color: HighlightText; background: Highlight; border-color: HighlightText; }
      .status { border-color: CanvasText; background: Canvas; color: CanvasText; }
      .spinner { display: none; }
    }
  </style>
</head>
<body>
  <a class="skip-link" href="#main">跳到主要内容</a>
  <header class="site-header">
    <strong>可访问组件</strong>
    <nav class="site-nav" aria-label="主导航">
      <a href="#main">内容</a>
      <a href="#help">帮助</a>
    </nav>
  </header>

  <main id="main" tabindex="-1">
    <section class="card" aria-labelledby="page-title">
      <h1 id="page-title">保存阅读偏好</h1>
      <p class="muted">焦点、对比度和触控目标都属于组件契约。</p>

      <div class="field">
        <label for="display-name">显示名称</label>
        <input id="display-name" name="display-name" autocomplete="nickname" aria-describedby="name-help" />
        <span class="muted" id="name-help">此名称会显示在你的公开资料中。</span>
      </div>

      <div class="actions">
        <button class="button button--primary" type="button">保存</button>
        <button class="button" type="button">取消</button>
      </div>

      <p class="status" role="status">
        <span class="spinner" aria-hidden="true"></span>
        <span>正在检查设置，请稍候。</span>
      </p>
    </section>
  </main>
</body>
</html>
```

### 完整示例 2：渐进增强、视觉隐藏与 RTL

保存为 `enhancement-rtl.html`。基础布局是 Flex，支持 Grid 时增强为自动轨道；右侧区域使用逻辑属性和局部 RTL。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>渐进增强与 RTL</title>
  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      font: 1rem/1.6 system-ui, sans-serif;
      color: #22313f;
      background: #f5f7fa;
    }

    main {
      inline-size: min(calc(100% - 2rem), 52rem);
      margin-inline: auto;
      padding-block: 2rem;
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }

    .toolbar__item {
      flex: 1 1 12rem;
      min-inline-size: 0;
      padding: 1rem;
      border: 1px solid #b8c6d0;
      border-radius: 0.5rem;
      background: #fff;
    }

    @supports (display: grid) {
      .toolbar {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(min(100%, 12rem), 1fr));
      }
    }

    .callout {
      margin-block-start: 1.5rem;
      padding: 1rem;
      padding-inline-start: 1.25rem;
      border: 1px solid #b8c6d0;
      border-inline-start: 0.35rem solid #2c6474;
      border-radius: 0.5rem;
      background: #fff;
      text-align: start;
    }

    .callout h2 { margin-block-start: 0; }

    .next-link {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      min-block-size: 2.75rem;
      margin-block-start: 0.75rem;
      color: #175267;
      font-weight: 700;
    }

    .directional-icon { display: inline-block; }

    [dir="rtl"] .directional-icon { transform: scaleX(-1); }

    .search-field { display: grid; gap: 0.4rem; margin-block-start: 1.5rem; }
    .search-field input {
      min-block-size: 2.75rem;
      padding: 0.6rem 0.75rem;
      border: 1px solid #718896;
      border-radius: 0.4rem;
      font: inherit;
    }

    .visually-hidden {
      position: absolute;
      inline-size: 1px;
      block-size: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
      clip-path: inset(50%);
      white-space: nowrap;
      border: 0;
    }

    :focus-visible { outline: 3px solid #0b63ce; outline-offset: 3px; }

    @media (forced-colors: active) {
      .toolbar__item, .callout, .search-field input { border-color: CanvasText; background: Canvas; color: CanvasText; }
    }
  </style>
</head>
<body>
  <main>
    <h1>基础可用，再逐步增强</h1>

    <section class="toolbar" aria-label="工具区域">
      <div class="toolbar__item"><strong>Flex 回退</strong><p>基础布局允许换行。</p></div>
      <div class="toolbar__item"><strong>Grid 增强</strong><p>支持时使用自动轨道。</p></div>
      <div class="toolbar__item"><strong>逻辑属性</strong><p>布局方向跟随书写模式。</p></div>
    </section>

    <div class="search-field">
      <label for="search">搜索文档</label>
      <input id="search" type="search" aria-describedby="search-help" />
      <span class="visually-hidden" id="search-help">输入关键词后按回车开始搜索。</span>
    </div>

    <section class="callout" dir="rtl" lang="ar">
      <h2>محتوى من اليمين إلى اليسار</h2>
      <p>تتغير الهوامش واتجاه النص تلقائيًا باستخدام الخصائص المنطقية.</p>
      <a class="next-link" href="#next">
        التالي
        <span class="directional-icon" aria-hidden="true">→</span>
      </a>
    </section>

    <p id="next">中文内容仍保持从左到右，局部 dir 不会改变整个页面。</p>
  </main>
</body>
</html>
```

## 14. 易错点

| 易错点 | 原因与正确做法 |
| --- | --- |
| 把“支持”当成“行为完全一致” | 检查 caniuse notes、浏览器 bug 和实际布局；`@supports` 只检测语法 |
| 先写高级样式，再补旧浏览器 | 基础版本可能长期不可用；先保证内容与任务成立 |
| 认为 Autoprefixer 能补齐所有兼容性 | 它只加前缀，不实现 Grid、容器查询或逻辑属性回退 |
| 删除 `outline` 但不提供替代焦点 | 键盘用户无法定位；保留清晰焦点，必要时使用 `focus-visible` |
| 用 `div` 模拟按钮 | 缺少键盘和语义；优先原生元素 |
| 只检查品牌色对比度 | 透明背景、禁用态、悬停态和系统颜色都可能改变最终对比度 |
| 用固定高度解决重排 | 放大文字后内容被裁切；让容器随内容增长 |
| 减弱动画时直接隐藏所有状态 | 可能让加载和进度无法理解；用静态替代或缩短非必要运动 |
| 强制颜色模式仍保留背景图片和阴影 | 这些效果可能被忽略，边框与文字应独立表达边界 |
| RTL 时镜像整个组件 | 文字、Logo 和媒体控件也会被翻转；只翻转方向性图标 |
| 用 `display: none` 做屏幕阅读器文本 | 内容会离开可访问性树；使用视觉隐藏类 |
| 只做桌面截图回归 | 漏掉键盘、缩放、触控、用户偏好和真实移动环境 |

## 15. 验证与 DevTools

1. **键盘遍历。** 从地址栏后按 Tab，确认焦点顺序合理、焦点环可见、没有不可见的可聚焦元素；用 Shift+Tab 反向检查。
2. **可访问性树。** Elements → Accessibility 检查名称、角色、状态和隐藏内容；确认视觉隐藏文本可读、装饰图标被忽略。
3. **自动扫描。** Lighthouse 和 axe 可发现部分语义、名称、对比度和目标尺寸问题，但不能替代人工键盘与屏幕阅读器测试。
4. **对比度。** 使用颜色选择器检查真实背景上的文本与 UI 边界；不要只测十六进制变量。
5. **缩放与重排。** 浏览器放大到 200%，桌面再测 400%/约 320 CSS 像素宽；检查横向滚动和裁切。
6. **文字间距。** 临时注入 WCAG 1.4.12 的覆盖值，观察按钮、导航和卡片是否丢失内容。
7. **模拟用户偏好。** Rendering 面板可模拟 reduced motion、forced colors 等；同时验证真实系统设置。
8. **检查降级。** 禁用高级声明或在旧版浏览器打开，确认 `@supports` 前后都有可用布局。
9. **RTL 与语言。** 切换 `dir` 和 `lang`，检查逻辑属性、图标方向、省略号和可访问名称。
10. **真机测试。** 验证触控目标、安全区、软键盘、横竖屏和动态视口，不只依赖桌面模拟。

## 16. 测试清单

### 内容与语义

- 页面标题、语言、地标和标题层级正确。
- 按钮和链接有准确名称与正确角色。
- 表单标签、错误提示、必填状态和帮助文本可访问。
- 装饰性内容不会干扰屏幕阅读器。

### 键盘与焦点

- 所有交互可仅用键盘完成。
- 焦点可见，不被固定头部、弹层或容器裁切。
- 焦点顺序与视觉、DOM 顺序一致。
- 弹层、抽屉和菜单的状态与焦点管理符合预期。

### 视觉与缩放

- 文本、控件边界和状态达到所需对比度。
- 200% 文本放大和桌面 400% 重排不丢失内容。
- 文字间距覆盖不导致截断。
- 减弱动画、更多对比度、深色主题和强制颜色均可读。

### 输入与国际化

- 触控目标不过小，相邻目标不重叠。
- 不依赖悬停提供关键信息。
- RTL 布局、图标、截断和焦点方向正确。
- 安全区和软键盘不遮挡主要操作。

### 兼容与交付

- 支持矩阵中的 P0/P1 环境通过核心任务。
- `@supports`、Autoprefixer 和 Browserslist 与支持策略一致。
- 无 JavaScript 时核心内容和主要导航仍可用。
- 自动扫描问题已人工复核，关键缺陷有回归用例。

## 关联示例

- [媒体特性与用户偏好](../../examples/responsive/media-preference.html)：查看浏览器当前匹配的深色、对比度、指针和减弱动态条件。
- [表单状态实验台](../../examples/forms/form-states.html)：焦点、校验、`accent-color` 与键盘状态。
- [补充属性与专题](../07-reference/27-additional-properties.md)：`prefers-reduced-transparency`、`dynamic-range`、`scripting` 与输入交互属性。

## 17. 练习

1. 为一个卡片列表添加 Flex 回退和 Grid 增强，分别禁用高级规则，验证内容顺序和可操作性不变。
2. 使用 Tab 键审查一个页面，找出所有删除焦点轮廓、焦点被裁切或焦点顺序混乱的位置。
3. 用对比度工具检查正常、悬停、禁用和强制颜色状态，修正只靠颜色表达的信息。
4. 将一个固定左右属性的组件改为逻辑属性，切换到 RTL，并只翻转必要的方向图标。
5. 建立一份包含桌面、iOS、Android、键盘、屏幕阅读器和系统偏好的浏览器测试矩阵，记录每条用例的复现步骤。

> 上一篇：[CSS 架构与工程化](18-architecture.md)。下一篇：[属性速查表](../07-reference/20-cheatsheet.md)。
