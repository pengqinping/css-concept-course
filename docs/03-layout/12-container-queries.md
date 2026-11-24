# 12 · 容器查询与自适应布局

> 学习目标：让组件根据“自己拿到了多少空间”改变布局，而不是根据设备屏幕宽度猜测；理解查询容器、尺寸包含、样式查询与容器单位的边界，并能设计可复用、可降级的组件。

## 1. 从“页面响应式”到“组件响应式”

媒体查询回答的是“视口有多大”。但同一个卡片可能出现在 360px 宽的手机正文里，也可能出现在 1200px 宽桌面的三列网格里。如果卡片只监听视口，它在桌面的小列里仍然可能太窄，在手机的大图区域里又可能浪费空间。

```text
媒体查询：视口宽度 ───────────────▶ 页面级布局
                                    │
                                    ├─▶ 导航从纵向变横向
                                    └─▶ 主区域从一列变两列

容器查询：组件可用宽度 ───────────▶ 组件内部布局
                                    │
                                    ├─▶ 卡片图片从上方移到左侧
                                    └─▶ 按钮组从换行变同行
```

因此，容器查询不是媒体查询的替代品，而是把响应式判断下沉到真正需要改变布局的边界。一个常见策略是：

- 用媒体查询控制页面外壳、全局导航和主要内容列数。
- 用容器查询控制卡片、工具条、侧栏内容等可复用组件。
- 用内在尺寸、Flex/Grid 的自动换行处理不确定空间，最后才添加少量断点。

## 2. 建立查询容器

给元素设置 `container-type`，它就成为一个“查询容器”。尺寸查询由它的**后代元素**触发；查询尺寸来自容器的内容盒，而不是边框盒或视口。

```css
.card-region {
  container-type: inline-size;
  container-name: card;
}
```

也可以使用简写：

```css
.card-region {
  container: card / inline-size;
}
```

`container` 的简写顺序是“名称 / 类型”。名称可以省略，类型不能省略；更复杂的多名称写法见后文。

### 2.1 最小示例

下面的卡片会自动占满外层区域。拖动外层区域右下角的调整手柄，组件会在约 `36rem` 处由纵向布局切换为横向布局。外层区域变窄时，桌面视口并不需要变化。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>容器查询卡片</title>
  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      padding: 2rem 1rem;
      color: #18332b;
      background: #eef4f0;
      font: 1rem/1.6 system-ui, sans-serif;
    }

    .card-region {
      inline-size: min(100%, 52rem);
      min-inline-size: 18rem;
      margin-inline: auto;
      resize: horizontal;
      overflow: auto;
      container: card / inline-size;
    }

    .product-card {
      display: grid;
      gap: 1.25rem;
      padding: 1.25rem;
      border: 1px solid #b7cbc1;
      border-radius: 1rem;
      background: #fff;
      box-shadow: 0 0.75rem 2rem rgb(24 51 43 / 8%);
    }

    .product-card__media {
      display: grid;
      min-block-size: 10rem;
      place-items: center;
      border-radius: 0.75rem;
      color: #fff;
      background: #256d5b;
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: 0.08em;
    }

    .product-card__eyebrow {
      margin: 0 0 0.25rem;
      color: #41685b;
      font-size: 0.875rem;
    }

    .product-card__title { margin: 0; font-size: 1.5rem; }
    .product-card__description { margin: 0.75rem 0 1rem; color: #4e625b; }
    .product-card__actions { display: flex; flex-wrap: wrap; gap: 0.75rem; }

    .button {
      min-block-size: 2.75rem;
      padding: 0.5rem 1rem;
      border: 1px solid #256d5b;
      border-radius: 0.5rem;
      color: #256d5b;
      background: #fff;
      font: inherit;
      cursor: pointer;
    }

    .button--primary { color: #fff; background: #256d5b; }

    @container card (inline-size >= 36rem) {
      .product-card {
        grid-template-columns: minmax(12rem, 0.8fr) minmax(0, 1.2fr);
        align-items: center;
        padding: 1.5rem;
      }

      .product-card__media { min-block-size: 14rem; }
    }
  </style>
</head>
<body>
  <div class="card-region" aria-label="可调整宽度的卡片区域">
    <article class="product-card">
      <div class="product-card__media" aria-hidden="true">CSS</div>
      <div>
        <p class="product-card__eyebrow">组件化布局</p>
        <h1 class="product-card__title">一张不依赖屏幕宽度的卡片</h1>
        <p class="product-card__description">
          拖动外层区域，观察卡片如何根据自身可用宽度重排。
        </p>
        <div class="product-card__actions">
          <button class="button button--primary" type="button">开始学习</button>
          <button class="button" type="button">查看示例</button>
        </div>
      </div>
    </article>
  </div>
</body>
</html>
```

这个例子里有两个关键点：

1. 查询容器是 `.card-region`，不是卡片本身。卡片不能查询自己的尺寸。
2. 基础布局先写成可用的纵向 Grid；容器查询只负责在空间足够时重排。不支持容器查询的浏览器仍然得到完整、可读的卡片。

## 3. 查询语法：尺寸、名称与逻辑组合

### 3.1 尺寸查询

```css
@container (inline-size > 40rem) {
  .component { /* ... */ }
}

@container card (min-width: 50rem) {
  .component { /* ... */ }
}

@container card (width >= 50rem) {
  .component { /* ... */ }
}
```

前两种写法和第三种在常见场景下含义相近，但现代范围语法更直观。范围语法没有“等于”运算符：

| 条件 | 含义 |
| --- | --- |
| `(inline-size >= 36rem)` | 内联尺寸至少为 `36rem` |
| `(inline-size > 36rem)` | 内联尺寸严格大于 `36rem` |
| `(inline-size < 36rem)` | 内联尺寸严格小于 `36rem` |
| `(inline-size <= 36rem)` | 内联尺寸至多为 `36rem` |
| `(28rem <= inline-size < 44rem)` | 范围查询，左闭右开 |

`min-width`/`max-width` 这类传统媒体查询语法也可以用于容器查询。工程中最好统一选择一种风格，避免同一项目混用后难以审阅。

### 3.2 物理尺寸与逻辑尺寸

| 查询特性 | 判断对象 | 使用建议 |
| --- | --- | --- |
| `width` / `height` | 物理宽度 / 高度 | 代码直观，但书写模式变化时需要额外考虑 |
| `inline-size` / `block-size` | 书写模式的内联 / 块尺寸 | 适合作为组件断点的默认选择 |
| `aspect-ratio` | 容器内容盒的宽高比 | 只对同时具有两个尺寸查询能力的容器有意义 |
| `orientation` | 容器的横向或纵向 | 需要 `container-type: size` 才能可靠使用 |

在拉丁文横排页面里，`inline-size` 通常就是宽度；切换为竖排书写后，它就可能是高度。组件如果本来就使用逻辑属性，断点也应优先使用逻辑尺寸。

### 3.3 命名容器与组合条件

```css
.container {
  container: sidebar layout / inline-size;
}

@container sidebar (inline-size >= 20rem) {
  .sidebar__label { display: inline; }
}

@container layout (inline-size >= 60rem) and (block-size >= 30rem) {
  .workspace { /* ... */ }
}
```

一个容器可以声明多个名称，用空格分隔。`@container sidebar (...)` 会寻找最近且名称匹配的合格祖先容器。

还需要注意：

- 查询从后代向上查找，不能查询自身。
- 未命名查询选择最近一个满足条件的合格祖先容器。
- 命名查询找不到对应容器时条件不成立，不会随意改查另一个无名容器。
- `and` 表示同时满足，`,` 表示“或”，`not` 用于否定整个条件。

```css
@container card (inline-size >= 30rem),
@container wide-card (inline-size >= 50rem) {
  .card__meta { display: flex; }
}

@container not (inline-size < 24rem) {
  .toolbar { justify-content: space-between; }
}
```

## 4. 容器查询单位

容器单位让后代不必重复声明断点，也能按容器的可用空间缩放字号、间距或图像尺寸。

| 单位 | 相对基准 | 常见用途 |
| --- | --- | --- |
| `cqw` | 查询容器内容盒宽度的 `1%` | 标题字号、横向间距 |
| `cqh` | 查询容器内容盒高度的 `1%` | 需要高度参与的比例 |
| `cqi` | 查询容器内联尺寸的 `1%` | 逻辑布局中的通用缩放 |
| `cqb` | 查询容器块尺寸的 `1%` | 块方向尺寸或视觉比例 |
| `cqmin` | `cqi` 与 `cqb` 中较小者 | 同时受宽高约束的图形 |
| `cqmax` | `cqi` 与 `cqb` 中较大者 | 强调较长边的视觉元素 |

这些单位按查询容器的**内容盒**解析。`100cqi` 是容器的整个内联尺寸，`50cqi` 是其中一半。

```css
.card {
  padding: clamp(1rem, 4cqi, 2rem);
}

.card__title {
  font-size: clamp(1.25rem, 2rem + 2cqi, 2.5rem);
}

.card__ratio-box {
  inline-size: min(60cqi, 18rem);
  aspect-ratio: 16 / 9;
}
```

如果不存在能提供对应轴尺寸的查询容器，容器单位会回退到小视口单位：`cqw` 类似 `svw`，`cqh` 类似 `svh`，`cqi`/`cqb` 分别回退到小视口的内联/块尺寸。因此，没有容器时单位不一定会失效，但得到的可能是基于视口的结果。

**不要因为单位“有兜底”就忽略容器边界。** 一个没有声明容器的组件突然使用 `cqi`，其实际基准可能来自很远的外层容器，导致同一个类在不同页面表现不同。

## 5. 四种 `container-type`

| 值 | 建立什么能力 | 主要约束 |
| --- | --- | --- |
| `normal` | 默认值，不建立查询容器 | 等价于不声明；可用于显式重置 |
| `inline-size` | 只对内联轴施加尺寸包含，可查询内联尺寸 | 最常用；不会固定块轴高度 |
| `size` | 对内联轴和块轴都施加尺寸包含，可查询两个轴 | 元素在相应轴上不能再由内容决定尺寸 |
| `style` | 建立样式查询容器 | 不能用于尺寸查询；只提供样式 containment |

### 5.1 为什么 `inline-size` 最常用

`inline-size` 会让容器在该轴上的尺寸独立于后代内容，避免“内容改变尺寸，尺寸又触发查询，查询再改变内容”的循环。块轴仍然可以由内容撑开，因此适合卡片、侧栏等自然高度组件。

`size` 则要求两个轴都有确定的尺寸。若写成下面这样，容器高度会被包含为零，后代也就无法获得预期高度：

```css
/* 反例：高度没有外部来源，尺寸包含会使内容盒高度塌陷 */
.panel {
  container-type: size;
}
```

需要高度查询时，应让高度来自明确的父级布局：

```css
.panel-slot {
  display: grid;
  grid-template-rows: minmax(0, 1fr);
  min-block-size: 20rem;
}

.panel-slot > .panel {
  container-type: size;
  min-block-size: 0;
}
```

### 5.2 样式查询基础

样式查询可以根据容器的自定义属性值改变后代样式。它不是通用的“选择父元素的任意 CSS 属性”机制。

```css
.notice {
  --notice-tone: neutral;
  container: notice / style;
}

@container notice style(--notice-tone: warning) {
  .notice__icon { background: #8a4b00; }
}

@container notice style(--notice-tone: success) {
  .notice__icon { background: #1f6b45; }
}
```

在容器上切换变量即可：

```css
.notice[data-tone="warning"] { --notice-tone: warning; }
.notice[data-tone="success"] { --notice-tone: success; }
```

样式查询有几个容易误解的边界：

- 它主要查询已计算的自定义属性值，不能直接写 `style(display: grid)` 这类普通属性查询。
- 自定义属性必须能到达后代；被重置或覆盖后，查询结果也会变化。
- 查询发生在容器上，样式应用在匹配查询的后代上，不能利用它直接重排容器自身。
- 样式查询的浏览器支持与尺寸查询并不完全相同，应采用可降级设计并检查目标环境。

## 6. 容器查询与媒体查询的分工

| 问题 | 更适合的机制 | 原因 |
| --- | --- | --- |
| 页面从一列变两列 | 媒体查询 | 变化来自视口和整体阅读区域 |
| 全局导航折叠 | 媒体查询 | 导航与页面外壳共享可用空间 |
| 卡片在窄列中纵向排列 | 容器查询 | 同一张卡片可能出现在不同页面位置 |
| 组件字号随自身宽度缩放 | 容器单位 | 缩放基准应是组件，而非设备 |
| 用户偏好、打印、设备能力 | 媒体查询 | 它们不是容器尺寸信息 |
| 内容刚好放不下 | 先 Flex/Grid 内在布局 | 不应为每个像素制造断点 |

两者可以嵌套使用，媒体查询负责页面骨架，容器查询负责局部适应。但不要机械地复制两套相同断点，否则组件会同时受视口和局部空间影响，问题更难复现。

## 7. 导航与侧栏完整示例

下面示例中，页面外壳在视口足够宽时变成两列；侧栏内部则根据自己实际分到的宽度，把纵向导航切换为横向导航。把侧栏移到其他页面时，它仍能保持相同规则。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>页面与组件协同响应</title>
  <style>
    * { box-sizing: border-box; }

    :root {
      font-family: system-ui, sans-serif;
      color: #202a35;
      background: #f4f6f8;
    }

    body { margin: 0; }

    .site-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 1rem clamp(1rem, 4vw, 2.5rem);
      color: #fff;
      background: #243b53;
    }

    .brand { font-size: 1.25rem; font-weight: 750; }
    .global-nav { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; }
    .global-nav a { color: inherit; text-decoration-thickness: 0.1em; }

    .page-shell {
      display: grid;
      gap: 1.5rem;
      max-inline-size: 78rem;
      margin-inline: auto;
      padding: 1.5rem clamp(1rem, 4vw, 2.5rem);
    }

    .sidebar {
      align-self: start;
      padding: 1rem;
      border: 1px solid #cbd5df;
      border-radius: 0.75rem;
      background: #fff;
      container: sidebar / inline-size;
    }

    .sidebar__title { margin: 0 0 0.75rem; font-size: 1rem; }

    .side-nav {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .side-nav a {
      display: block;
      min-block-size: 2.75rem;
      padding: 0.65rem 0.8rem;
      border-radius: 0.4rem;
      color: #243b53;
      text-decoration: none;
    }

    .side-nav a:hover { background: #e9eff5; }

    .content {
      min-inline-size: 0;
      padding: clamp(1rem, 3vw, 2rem);
      border: 1px solid #cbd5df;
      border-radius: 0.75rem;
      background: #fff;
    }

    .content h1 { margin-block-start: 0; }
    .content p { max-inline-size: 65ch; }

    @media (width >= 52rem) {
      .page-shell {
        grid-template-columns: minmax(14rem, 18rem) minmax(0, 1fr);
        align-items: start;
      }
    }

    @container sidebar (inline-size >= 30rem) {
      .sidebar__title { margin-block-end: 1rem; }
      .side-nav { flex-wrap: nowrap; }
      .side-nav li { flex: 1 1 auto; }
      .side-nav a { text-align: center; }
    }

    @media (hover: hover) and (pointer: fine) {
      .side-nav a { transition: background-color 150ms ease; }
    }

    @media (prefers-reduced-motion: reduce) {
      .side-nav a { transition: none; }
    }

    @media print {
      .site-header, .sidebar { display: none; }
      .page-shell { display: block; padding: 0; }
      .content { border: 0; }
    }
  </style>
</head>
<body>
  <header class="site-header">
    <div class="brand">CSS 手记</div>
    <nav class="global-nav" aria-label="全局导航">
      <a href="#guide">指南</a>
      <a href="#examples">示例</a>
      <a href="#about">关于</a>
    </nav>
  </header>

  <div class="page-shell">
    <aside class="sidebar">
      <h2 class="sidebar__title">本章导航</h2>
      <nav aria-label="章节导航">
        <ul class="side-nav">
          <li><a href="#container">查询容器</a></li>
          <li><a href="#units">容器单位</a></li>
          <li><a href="#style">样式查询</a></li>
        </ul>
      </nav>
    </aside>

    <main class="content" id="guide">
      <h1>页面布局与组件布局各司其职</h1>
      <p>
        媒体查询根据视口决定页面骨架；侧栏根据自己分到的空间决定内部导航形态。
      </p>
      <p id="container">当视口变窄时，侧栏会回到内容上方并恢复纵向空间。</p>
      <p id="units">组件被放入更窄的列时，也不需要媒体查询来“救场”。</p>
      <p id="style">语义、状态和布局应该分别建模，再通过清晰的边界组合。</p>
    </main>
  </div>
</body>
</html>
```

## 8. 兼容性与渐进增强

尺寸容器查询和容器查询单位在现代主流浏览器中已经广泛可用，但对于仍需支持旧版浏览器的项目，应把“基础可用”放在查询之前，而不是把整个组件包进查询。

推荐顺序：

1. 先写默认布局，让内容在任意宽度下都能自然阅读。
2. 使用 Flex/Grid 的换行、`minmax()`、`auto-fit` 处理大部分变化。
3. 添加容器查询，只优化需要明确重排的状态。
4. 对确实依赖容器查询的高级交互，再用 `@supports` 提供替代方案。

```css
.card {
  display: grid;
  gap: 1rem;
}

@supports (container-type: inline-size) {
  .card-region { container-type: inline-size; }
}

@container (inline-size >= 36rem) {
  .card { grid-template-columns: 12rem minmax(0, 1fr); }
}
```

不支持 `@container` 的浏览器会忽略该规则块，前面的基础布局仍然生效。不要只写高级版本，再指望浏览器自动补出合理布局。

还应注意：容器查询单位没有容器时会按小视口回退，所以升级不像“突然不生效”那么明显。测试时要确认它实际引用了预期容器。

## 9. 性能注意事项

容器查询本身不是性能问题，不合理的尺寸依赖和失效范围才是。

- **避免在同一个组件上建立大量嵌套查询。** 每层都可能扩大样式失效范围；优先在最稳定的布局边界建立容器。
- **不要动画容器的尺寸来“演示查询”。** 宽度不断变化可能反复触发布局与查询求值。拖动或窗口缩放时也要观察 Performance 面板。
- **不要把 `container-type` 本身做成动画属性。** 切换包含模式可能引起突发布局。
- **尺寸包含会改变内在尺寸贡献。** 如果容器位于 Grid/Flex 自动轨道中，确认轨道不会因此被压扁或异常扩张。
- **谨慎在自定义属性变化时触发样式查询。** 它适合主题、密度等低频状态，不适合每帧变化的数值。
- **避免查询后把容器尺寸重新绑定到后代内容。** 浏览器能处理合法场景，但这种依赖难以推理，也容易产生循环式布局问题。

## 10. 易错点

| 易错点 | 原因与正确做法 |
| --- | --- |
| 在卡片自身上写查询，希望改变卡片布局 | 查询由后代触发；应在卡片外层放查询容器，或查询内部子区域 |
| 给所有元素都加 `container-type: size` | 会把自然高度压成零；默认使用 `inline-size`，两轴尺寸都来自外部时才用 `size` |
| 用视口断点描述组件状态 | 同一组件可能出现在不同宽度区域；断点应基于组件内容何时拥挤 |
| 认为 `cqw` 永远等于视口宽度 | 它优先相对查询容器；无容器时才回退到小视口 |
| 查询宽度时忘记 padding/border | 尺寸查询使用内容盒；调整 `box-sizing` 不会把边框盒当作查询尺寸 |
| 样式查询直接判断 `color`、`display` | 常见实现只支持自定义属性；不要假设可以查询任意声明 |
| 为每个可能尺寸增加断点 | 过度碎片化；先让 Flex/Grid 自然适应，再处理真正的布局冲突 |
| 升级后仍保留两套冲突的媒体查询 | 页面级与组件级规则可能互相覆盖；明确每一层负责什么 |

## 11. 验证与 DevTools

1. **确认查询命中。** 在 Styles 面板中查看 `@container` 规则是否变灰，展开后确认当前条件和容器名称。
2. **检查容器来源。** 选中后代元素，查看是哪一个祖先提供了 `container-type`；临时修改其宽度，观察后代是否按预期重排。
3. **核对内容盒。** 使用 Layout/Box Model 面板确认查询宽度不包含 padding 与 border。
4. **检查命名匹配。** 临时改名或增加同名嵌套容器，验证命中的是最近且名称匹配的祖先。
5. **验证单位基准。** 在 Computed 中查看 `padding`、`font-size` 等最终值，或用 `CSS.registerProperty` 调试自定义数值，不要只根据源码猜测。
6. **模拟降级。** 暂时禁用 `container-type` 与 `@container` 规则，确认基础布局仍完整。
7. **观察性能。** 连续拖动容器宽度，在 Performance 面板中记录布局、样式计算耗时；如果出现长任务，先减少查询层数和动画尺寸。

## 关联示例

- [容器查询卡片](../../examples/container-query-card.html)：同一组件在窄侧栏与宽主栏中的布局变化。
- [流式单位与函数](../../examples/responsive/fluid-units.html)：把 `cqi` / `cqw` 与 `clamp()` 组合成组件内流式尺度。

## 12. 练习

1. 把一个已有卡片从媒体查询迁移到容器查询，并分别放入手机单列、桌面三列和弹窗三种宽度，验证布局只取决于可用空间。
2. 用 `container-type: inline-size` 与 `cqi` 实现一个自动缩放的头像区，限制最小、最大字号，并检查没有查询容器时的回退结果。
3. 为通知组件增加 `--notice-tone` 与样式查询；用 `neutral`、`warning`、`success` 三种状态验证样式隔离。
4. 找出一个被 `container-type: size` 压扁高度的组件，改为由 Grid 提供明确高度，或降级为只查询内联尺寸。
5. 给同一组件写基础版和容器查询增强版，在旧浏览器模拟或禁用规则后检查内容是否仍然可读、可操作。

> 上一篇：[Grid 网格布局](11-grid.md)。下一篇：[响应式设计](../04-responsive/13-responsive-design.md)。
