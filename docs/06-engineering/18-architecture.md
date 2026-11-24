# 18 · CSS 架构与工程化

> 学习目标：用命名、组件边界、设计令牌和层叠层控制 CSS 的影响范围，理解预处理器、PostCSS、CSS Modules、工具类和 CSS-in-JS 各自解决的问题，并掌握低风险重构与评审方法。

## 1. 架构的目标：让影响可预测

CSS 很容易从几行局部规则长成全局耦合网络。架构不是为了增加目录和概念，而是为了让开发者能回答三个问题：

1. 这条规则会影响哪些元素？
2. 同一条规则为什么能覆盖另一条？
3. 修改一个组件时，会不会破坏看起来无关的页面？

```text
设计令牌 ──▶ 基础样式 ──▶ 布局原语 ──▶ 业务组件 ──▶ 页面组合
    │            │             │             │
    │            │             │             └─ 只通过公开类名/变量交互
    │            │             └─ 决定元素放在哪里，不侵入内部结构
    │            └─ 语义默认值、排版、焦点、全局盒模型
    └─ 颜色、字体、间距、圆角、动效等可复用决策

第三方样式 ──▶ 独立层 + 作用域边界 + 明确重置范围
```

好的架构允许复用，但不鼓励通过复制选择器“复用”；允许覆盖，但不依赖覆盖顺序碰运气；允许主题，但不让每个组件各自发明一套颜色。

## 2. 命名方法：思路比缩写重要

### 2.1 BEM：块、元素、修饰符

BEM 把组件拆成稳定边界：

```css
.card { /* block：组件 */ }
.card__title { /* element：组件内部角色 */ }
.card--featured { /* modifier：组件变体 */ }
.card__actions { /* element */ }
```

```html
<article class="card card--featured">
  <h2 class="card__title">标题</h2>
  <div class="card__actions">...</div>
</article>
```

优点：

- 从类名就能看出归属，降低全局冲突概率。
- 修饰符适合表达 `featured`、`compact`、`danger` 等离散变体。
- 对多人协作和大型代码库较友好。

代价：

- 类名较长，HTML 噪声增加。
- 状态和工具类如果全部 BEM 化，会产生大量重复。
- 层级过深仍会写出 `.card__list__item__icon`，应重新判断组件边界。

状态可以使用数据属性或明确的 `is-*`/`has-*` 类，但项目应只选一种主要约定：

```css
.card[data-state="loading"] { opacity: 0.6; }
```

### 2.2 OOCSS：结构与外观分离

OOCSS 强调把可复用的结构模式与皮肤分开。例如：

```css
.media-object {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 1rem;
  align-items: start;
}

.media-object--bordered {
  padding: 1rem;
  border: 1px solid currentColor;
}
```

这种思路适合按钮、媒体对象、布局原语，但不意味着把每个视觉差异都拆成一个类。若两个组件只是颜色相同，共享一个皮肤类可能比共享整个结构更合适。

### 2.3 SMACSS：按职责分类

SMACSS 把样式分为 Base、Layout、Module、State、Theme 等类别：

| 类别 | 示例 | 约束 |
| --- | --- | --- |
| Base | `body`、`a`、标题默认值 | 只包含低层语义默认值 |
| Layout | `.page-shell`、`.sidebar-region` | 决定组件放在哪里 |
| Module | `.card`、`.dialog` | 一个可复用组件边界 |
| State | `[aria-expanded="true"]` | 描述状态，不复制整套组件样式 |
| Theme | 颜色、阴影、字体令牌 | 只改变设计令牌，不重写布局 |

实际项目不必严格采用某套方法论。更常见的是：BEM 或简单作用域命名负责组件内部，SMACSS 思路负责目录职责，工具类负责少量通用决策，设计令牌负责主题。

## 3. 组件边界：谁有权修改谁

### 3.1 布局所有者和内容所有者分开

```css
/* 布局层：只决定位置和空间分配 */
.search-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: minmax(0, 1fr) auto;
}

/* 组件层：只决定自身内部表现 */
.search-box { padding: 0.75rem; }
.search-box__input { min-inline-size: 0; }
```

父级不应该为了修正一个标题，深入选择 `.card > div > div > h3`。如果布局层必须修改组件内部，通常意味着：

- 组件缺少合理变体；
- 尺寸约束应由容器查询解决；
- 内容结构不应承担布局职责；
- 组件边界拆分错了。

### 3.2 公开接口尽量少

组件的公开接口可以包括：

- 根类名；
- 少量修饰符；
- 设计令牌，如 `--card-accent`；
- 数据属性表达的状态；
- 必要时通过 `::part()` 暴露的 Web Component 部分。

内部类名可以被构建工具重命名，但不应被外部页面随意选择。使用 `:where()` 可以降低选择器特异性，让组件默认样式更容易被覆盖；它不是作用域隔离，也不会自动防止外部命中。

```css
:where(.button) {
  min-block-size: 2.75rem;
  padding-inline: 1rem;
  border-radius: 0.5rem;
}

:where(.button--primary) {
  color: #fff;
  background: #245d4d;
}
```

低特异性必须配合清晰的层和变体，否则会变成“谁都覆盖不了/覆盖太容易”的混乱。

## 4. 设计令牌：把数值变成决策

令牌不是“把所有值换成变量”。它应表达稳定、可复用、可主题化的设计决策。

### 4.1 三层令牌

```css
:root {
  /* 原始令牌：具体值 */
  --green-700: #245d4d;
  --green-100: #e6f0ec;
  --gray-900: #202a33;
  --gray-100: #f3f5f6;
  --space-100: 0.5rem;
  --space-200: 0.75rem;
  --space-300: 1rem;
  --space-400: 1.5rem;

  /* 语义令牌：表达用途 */
  --color-action: var(--green-700);
  --color-action-subtle: var(--green-100);
  --color-text: var(--gray-900);
  --color-surface: var(--gray-100);
  --space-inline: var(--space-300);
  --space-stack: var(--space-400);

  /* 组件令牌：只暴露可调接口 */
  --card-accent: var(--color-action);
  --card-padding: var(--space-inline);
}
```

组件优先消费语义令牌，而不是直接依赖 `--green-700`。主题切换时只替换语义值：

```css
[data-theme="dark"] {
  color-scheme: dark;
  --color-action: #8fd0b8;
  --color-action-subtle: #17372d;
  --color-text: #edf3f0;
  --color-surface: #111c18;
}
```

### 4.2 令牌设计原则

- 名称描述用途，不绑定某个页面或组件实例。
- 原始令牌可以较多，语义令牌应克制。
- 不为一次性的像素调整建立全局令牌。
- 颜色令牌要同时考虑正常、悬停、焦点、禁用和强制颜色模式。
- 如果设计与前端共享 JSON，应明确生成流程和单一数据源，避免手写两份后漂移。
- CSS 自定义属性是运行时值；Sass 变量是编译时值，两者职责不同。

## 5. `@layer`：显式管理层叠顺序

当样式来源增多，选择器优先级和文件导入顺序会形成隐式竞争。层叠层把顺序变成可声明的架构。

```css
@layer reset, tokens, base, layout, components, vendor, utilities, overrides;
```

这条语句定义层的顺序。普通声明中，后面的层优先于前面的层；同一层内仍按来源、重要性和特异性等规则竞争。

### 5.1 普通声明与重要声明

- 未分层普通样式优先于所有分层普通样式。
- 分层普通样式中，后声明的层优先。
- 未分层 `!important` 优先于分层 `!important`。
- 分层 `!important` 的顺序与普通声明相反：较早的层优先。

```css
@layer reset, components, utilities;

@layer reset {
  [hidden] { display: none !important; }
}

@layer utilities {
  .u-flex { display: flex !important; }
}
```

这里 reset 的 `!important` 会压过 utilities 的 `!important`，因为重要样式遵循相反的层顺序。`!important` 很容易跨越预期边界，除非确有必要，否则应优先调整层顺序或拆分规则。

### 5.2 第三方样式放入独立层

```css
@import url("./vendor/widget.css") layer(vendor);
```

`@import` 必须位于允许的位置，并注意构建工具是否支持保留层信息。导入后，组件库的普通规则就位于 `vendor` 层，不再因为“未分层”而压过你的组件层。

`revert-layer` 可以放弃当前层对该声明的参与，让前一层接管；它不是“清除所有第三方影响”的万能键。

## 6. Sass、Less 与 PostCSS：职责不同

| 工具 | 主要职责 | 不应承担的职责 |
| --- | --- | --- |
| Sass | 编译期变量、mixins、函数、模块、循环和嵌套 | 不能根据用户运行时主题动态改变编译结果 |
| Less | 类似 Sass 的编译期组织能力，适合既有 Less 技术栈 | 不应与原生 CSS 变量混为一谈 |
| PostCSS | 解析和转换 CSS 插件链，如自动前缀、语法降级、lint | 本身不是一套完整的预处理器 |
| 原生 CSS | 自定义属性、原生嵌套、层、容器查询、逻辑属性 | 不负责项目级抽象和构建调度 |

### 6.1 Sass 与 Less

Sass 现代项目通常使用模块系统：

```scss
@use "tokens" as tokens;

.card {
  padding: tokens.$space-300;
  color: tokens.$color-text;

  &__title {
    font-size: tokens.$font-size-lg;
  }
}
```

编译期变量有利于静态优化和复用计算，但无法在 `data-theme` 改变时切换值。运行时主题应使用 CSS 自定义属性。

Less 的变量、mixin 和嵌套能力与 Sass 类似，但模块生态和语法不同。已有 Less 项目不必为了统一而重写；新项目应基于团队熟悉度、插件和构建集成选择，而不是只看功能清单。

### 6.2 PostCSS

PostCSS 把 CSS 解析成 AST，让插件执行转换。常见用途：

- `autoprefixer`：按目标浏览器补充需要的前缀。
- `postcss-preset-env`：把选定的现代特性转换为目标环境可用的 CSS。
- 排序、lint、自定义属性回退、CSS 嵌套转换等。

PostCSS 不会自动修复语义错误、布局缺陷或缺少的降级方案。启用“未来语法”时也要评估输出体积和调试成本，不应把所有实验特性都降到最低浏览器。

## 7. CSS Modules、工具类与 CSS-in-JS

### 7.1 CSS Modules

```css
/* Card.module.css */
.card { padding: 1rem; }
.card__title { margin: 0; }
.card--accent { border-color: #245d4d; }
```

构建工具会把局部类名编译成带哈希的名称：

```html
<article class="Card_card__a1b2c Card_card--accent__d3e4f">
  <h2 class="Card_card__title__g5h6i">标题</h2>
</article>
```

它适合 React、Vue 等组件化构建流程，默认无需运行时。常用能力：

- `:global(...)`：明确声明全局选择器。
- `composes`：组合局部类。
- `:local(...)`：显式声明局部作用域。
- 动画名和关键帧：需要关注是否被局部化以及第三方引用方式。

CSS Modules 隔离的是类名选择器，不会自动隔离：

- 继承的全局字体和颜色；
- 全局 `::backdrop`、`html`、`body` 规则；
- 自定义属性；
- 未局部化的 keyframes；
- 通过 `:global` 逃逸的选择器。

### 7.2 Utility CSS

工具类把少量设计决策编码为可组合类：

```html
<div class="flex items-center gap-300 p-400">
  <span class="text-muted">内容</span>
</div>
```

优点：

- 减少为每个小差异创建新组件类的成本。
- 约束在令牌内，容易保持一致性。
- 样式靠近模板，局部变化直观。

代价：

- HTML 变长，业务语义隐藏在类名组合中。
- 响应式和状态工具类过多时，类名顺序难以审阅。
- 设计变体可能通过堆类实现，导致同一个组件出现几十种不可识别组合。

合理策略是：布局与间距使用受限工具类，复杂组件保留语义类，业务状态不发明工具类。

### 7.3 CSS-in-JS

CSS-in-JS 把样式与组件代码放在一起，便于动态生成和传递变量：

```jsx
<div style={{ "--card-accent": accent }}>
  <Card />
</div>
```

选择时至少区分：

- **运行时 CSS-in-JS**：浏览器中插入样式，支持动态值，但需考虑运行时开销、SSR 水合、缓存和 CSP nonce。
- **编译时/零运行时方案**：构建时提取静态 CSS，运行时成本低，但动态能力受工具限制。
- **作用域与层叠**：插入顺序、选择器优先级和第三方样式仍可能冲突；作用域化不等于完全隔离。

如果应用是服务端渲染、内容站或需要严格 CSP，零运行时 CSS 往往更简单；如果高度动态主题与组件逻辑紧密耦合，CSS-in-JS 也有价值。不要把它当成解决所有架构问题的手段。

## 8. 第三方样式隔离

第三方组件可能自带按钮、标题、盒模型和全局 reset。隔离应优先缩小影响范围，而不是全站重写。

### 8.1 分层、作用域与包含

```css
@import url("./vendor/widget.css") layer(vendor);

@layer components {
  .embed { container: embed / inline-size; }
}

@layer vendor {
  .embed__button {
    min-block-size: 2.75rem;
    font: inherit;
  }
}
```

其他手段：

- 使用唯一前缀，如 `.vendor-widget__button`，避免选择器碰撞。
- `contain: layout style` 可以限制布局和样式计算等方面的部分影响，但不会隔离继承或所有全局规则。
- `isolation: isolate` 建立独立层叠上下文，不负责盒模型或字体隔离。
- Shadow DOM 对样式和 DOM 有较强隔离，但会改变焦点、表单、主题和全局样式穿透方式。
- iframe 隔离最彻底，适合广告、地图、第三方编辑器，但通信和布局成本更高。

### 8.2 `all: initial` / `all: unset` 的代价

在容器上使用 `all: initial` 看起来能“清空一切”，但也会清掉继承的字体、颜色等，可能让按钮、输入框和焦点样式不可用。`all` 不负责清除所有自定义属性，也不等于建立组件作用域。

如果使用，应逐项恢复需要的继承和交互状态，并验证键盘、高对比度和表单控件。

### 完整示例 1：令牌、层与 BEM 组件

保存为 `architecture.html`。代码演示令牌分层、布局与组件分工、低特异性组件样式和明确的变体接口。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CSS 架构示例</title>
  <style>
    @layer reset, tokens, base, layout, components, utilities, overrides;

    @layer reset {
      *, *::before, *::after { box-sizing: border-box; }
    }

    @layer tokens {
      :root {
        --green-700: #245d4d;
        --green-100: #e6f0ec;
        --gray-900: #202a33;
        --gray-600: #5a6872;
        --gray-100: #f3f5f6;
        --space-300: 1rem;
        --space-400: 1.5rem;
        --color-action: var(--green-700);
        --color-text: var(--gray-900);
        --color-surface: var(--gray-100);
      }
    }

    @layer base {
      body {
        margin: 0;
        font: 1rem/1.6 system-ui, sans-serif;
        color: var(--color-text);
        background: var(--color-surface);
      }

      :focus-visible {
        outline: 3px solid #0b63ce;
        outline-offset: 3px;
      }
    }

    @layer layout {
      .page-shell {
        inline-size: min(calc(100% - 2rem), 58rem);
        margin-inline: auto;
        padding-block: var(--space-400);
      }

      .panel-layout {
        display: grid;
        gap: var(--space-300);
        grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
      }
    }

    @layer components {
      :where(.button) {
        min-block-size: 2.75rem;
        padding: 0.5rem 1rem;
        border: 1px solid var(--color-action);
        border-radius: 0.5rem;
        color: var(--color-action);
        background: #fff;
        font: inherit;
        cursor: pointer;
      }

      :where(.button--primary) {
        color: #fff;
        background: var(--color-action);
      }

      .button[aria-pressed="true"] {
        box-shadow: inset 0 0 0 2px #fff;
      }

      .panel {
        min-inline-size: 0;
        padding: var(--space-400);
        border: 1px solid #c9d2d7;
        border-radius: 0.75rem;
        background: #fff;
      }

      .panel__eyebrow {
        margin: 0 0 0.25rem;
        color: var(--gray-600);
        font-size: 0.875rem;
      }

      .panel__title { margin: 0 0 0.75rem; font-size: 1.5rem; }
      .panel__body { margin: 0; }

      .panel__actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-block-start: var(--space-400);
      }

      .panel--accent { border-block-start: 0.25rem solid var(--color-action); }
    }

    @layer utilities {
      .u-flow > * + * { margin-block-start: 0.75rem; }
    }
  </style>
</head>
<body>
  <main class="page-shell">
    <h1>把顺序、边界和令牌写进架构</h1>
    <div class="panel-layout">
      <article class="panel">
        <p class="panel__eyebrow">标准面板</p>
        <h2 class="panel__title">组件拥有内部结构</h2>
        <div class="panel__body u-flow">
          <p>外部布局只决定面板放在哪里。</p>
          <p>内部类名表达角色，不暴露深层 DOM 路径。</p>
        </div>
        <div class="panel__actions">
          <button class="button button--primary" type="button">主要操作</button>
          <button class="button" type="button" aria-pressed="false">收藏</button>
        </div>
      </article>

      <article class="panel panel--accent">
        <p class="panel__eyebrow">强调变体</p>
        <h2 class="panel__title">修饰符只改变差异</h2>
        <p class="panel__body">变体不复制整份组件规则，只覆盖需要变化的令牌或少量属性。</p>
      </article>
    </div>
  </main>
</body>
</html>
```

### 完整示例 2：主题与第三方组件边界

保存为 `third-party.html`。组件通过语义令牌换肤，第三方区域使用独立层、前缀和窄范围重置。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>主题与第三方隔离</title>
  <style>
    @layer reset, base, components, vendor, utilities, overrides;

    @layer reset {
      *, *::before, *::after { box-sizing: border-box; }
    }

    @layer base {
      :root {
        color-scheme: light;
        --color-page: #f3f5f6;
        --color-surface: #fff;
        --color-text: #202a33;
        --color-muted: #5a6872;
        --color-border: #c9d2d7;
        --color-action: #245d4d;
      }

      [data-theme="dark"] {
        color-scheme: dark;
        --color-page: #111c18;
        --color-surface: #1b2a25;
        --color-text: #edf3f0;
        --color-muted: #b8c8c1;
        --color-border: #496158;
        --color-action: #8fd0b8;
      }

      body {
        margin: 0;
        font: 1rem/1.6 system-ui, sans-serif;
        color: var(--color-text);
        background: var(--color-page);
      }

      :focus-visible { outline: 3px solid #76b7ff; outline-offset: 3px; }
    }

    @layer components {
      .app-shell {
        inline-size: min(calc(100% - 2rem), 48rem);
        margin-inline: auto;
        padding-block: 2rem;
      }

      .app-card {
        padding: 1.5rem;
        border: 1px solid var(--color-border);
        border-radius: 0.75rem;
        background: var(--color-surface);
      }

      .app-card h1 { margin-block-start: 0; }
      .app-card p { color: var(--color-muted); }
    }

    @layer vendor {
      .vendor-widget {
        margin-block-start: 1.5rem;
        padding: 1rem;
        border: 1px dashed var(--color-border);
        border-radius: 0.75rem;
        background: var(--color-surface);
        contain: layout style;
        isolation: isolate;
      }

      .vendor-widget,
      .vendor-widget * { box-sizing: border-box; }

      .vendor-widget__title {
        margin: 0 0 0.75rem;
        color: var(--color-text);
        font: inherit;
      }

      .vendor-widget__button {
        min-block-size: 2.75rem;
        padding: 0.5rem 1rem;
        border: 1px solid var(--color-action);
        border-radius: 0.4rem;
        color: var(--color-action);
        background: transparent;
        font: inherit;
      }

      .vendor-widget__button:hover { background: color-mix(in srgb, var(--color-action) 12%, transparent); }
    }
  </style>
</head>
<body data-theme="light">
  <main class="app-shell">
    <section class="app-card">
      <h1>主题只改变令牌</h1>
      <p>切换 body 的 data-theme，布局和组件结构不需要重写。</p>

      <section class="vendor-widget" aria-label="第三方组件区域">
        <h2 class="vendor-widget__title">隔离的第三方区域</h2>
        <button class="vendor-widget__button" type="button">组件按钮</button>
      </section>
    </section>
  </main>
</body>
</html>
```

这个示例使用 `color-mix()` 生成轻微悬停背景；目标环境不支持时，按钮仍有完整的边框和文本状态。真实项目中，应把第三方 CSS 导入 `vendor` 层，并继续检查其全局选择器。

## 9. 代码组织

可以采用职责分层并按组件就近组织，目录名不必完全照搬某套方法论：

```text
styles/
  tokens/           # 原始令牌、语义令牌、主题
  base/             # 语义默认值、盒模型、基础排版、焦点
  primitives/       # button、field、visually-hidden 等低层原语
  layout/           # shell、stack、cluster、grid-region
  components/       # 业务组件，尽量与模板就近
  features/         # 跨页面的大型功能样式
  utilities/        # 少量受控工具类
  vendor/           # 第三方样式或覆盖层
  main.css          # 明确的层顺序与导入入口
```

组织原则：

- 入口文件显式声明 `@layer` 顺序，避免依赖文件系统排序。
- 一个组件可以有多个样式文件，但只能有一个清晰的公开接口。
- 按依赖方向引用，不从底层原语反向引用业务组件。
- 删除未被引用的样式，保留“将来可能用到”的文件会让架构腐化。
- 构建产物应关注体积与关键 CSS，不要把“按需”当作默认事实。

## 10. 低风险重构步骤

1. **建立现状基线。** 保存关键页面截图、浏览器矩阵和交互清单；先有可回退分支。
2. **绘制影响图。** 搜索类名、选择器、`!important`、全局标签选择器和第三方入口。
3. **先稳定令牌。** 把高频颜色、间距和字体映射为语义变量，但暂不大改布局。
4. **声明层顺序。** 建立 reset、base、layout、components、vendor、utilities 等层，把样式移入对应层。
5. **缩小作用域。** 用 BEM、CSS Modules 或组件根类收窄选择器，逐项删除深层后代选择器。
6. **提取原语和重复模式。** 只在差异明确、复用超过两处时抽象，避免提前设计。
7. **统一状态接口。** 用 `aria-*`、数据属性或有限状态类替代多个视觉类同时表示状态。
8. **清理与验证。** 删除死代码，比较截图、键盘流程、主题、响应式和构建体积。
9. **分批提交。** 令牌、层、组件拆分、删除旧样式应可独立回退，避免一次性大爆炸。

## 11. 评审清单

### 边界与命名

- 是否能从类名或模块名判断它属于哪个组件？
- 是否有父组件深入修改子组件内部结构？
- 选择器是否依赖偶然的 DOM 层级？
- 修饰符是否只覆盖真实差异，而不是复制组件？
- 状态是否由 `aria-*`、数据属性或明确状态类表达？

### 令牌与主题

- 颜色、间距和字号是否使用语义令牌？
- 是否存在大量一次性全局变量？
- 深色主题、高对比度、强制颜色模式是否可读？
- 运行时主题是否使用 CSS 自定义属性，而不是编译期变量？

### 层叠与工具链

- `@layer` 顺序是否显式声明？
- 是否有未分层第三方样式压过应用层？
- `!important` 是否有明确理由和局部范围？
- Sass/Less 变量与 CSS 变量职责是否混淆？
- PostCSS 目标浏览器是否与真实支持策略一致？

### 质量与交付

- 是否验证键盘焦点、缩放、窄屏和 RTL？
- 是否有无意义的死代码、重复声明和超大选择器？
- 构建后 CSS 体积、缓存和加载顺序是否可接受？
- 是否检查了第三方组件的继承、焦点和表单行为？

## 12. 易错点

| 易错点 | 原因与正确做法 |
| --- | --- |
| 把 BEM 当成层级越深越好 | BEM 应表达组件边界，过深说明结构需要重新拆分 |
| 每个像素都建立全局令牌 | 令牌应表达复用决策，不是替代所有字面量 |
| `@layer` 只写声明，不规定顺序 | 层顺序仍由首次出现决定；在入口集中声明 |
| 认为未分层样式最“干净” | 未分层普通样式会压过所有分层普通样式 |
| 混用 Sass 变量和 CSS 变量但职责不清 | 编译期计算用 Sass，运行时主题用 CSS 自定义属性 |
| CSS Modules 能隔离所有样式 | 它主要隔离类名；继承、全局规则和自定义属性仍可能泄漏 |
| CSS-in-JS 自动解决层叠问题 | 插入顺序、优先级、SSR 和 CSP 仍需管理 |
| 对第三方组件使用全站 reset | 影响范围失控；分层、前缀化并做窄范围恢复 |
| 重构时只比较桌面截图 | 会漏掉焦点、缩放、主题、打印和响应式问题 |

## 13. 验证与 DevTools

1. **查看层叠来源。** Styles 面板可显示规则属于哪个 `@layer`；确认未预期覆盖来自哪一层。
2. **搜索全局影响。** 在构建产物中搜索通用类名、标签选择器、`!important` 和 `:root`，找出高影响规则。
3. **检查作用域。** 使用 Coverage 面板查看未使用 CSS，再结合源码搜索确认不是动态加载后才删除。
4. **验证令牌链。** 临时切换 `data-theme`，在 Computed 中追踪颜色最终来自哪个语义令牌和原始令牌。
5. **对比生产构建。** 类名哈希、CSS 压缩、嵌套转换和 CSS Modules 只在构建后才会完全暴露。
6. **检查网络与缓存。** 确认第三方 CSS 是否阻塞渲染、是否重复打包、是否能被缓存。
7. **进行回归测试。** 至少覆盖键盘焦点、主题切换、320px 窄屏、200% 文本放大和打印样式。

## 关联示例

- [Web Components 样式边界](../../examples/engineering/webcomponents.html)：`:host`、`::slotted()`、`::part()` 和自定义属性穿透。
- [层叠、层与主题](../../examples/foundations/cascade-layers-theme.html)：用 `@layer` 管理重置、组件与工具类顺序。
- [补充属性与专题](../07-reference/27-additional-properties.md)：Shadow DOM 的样式入口与边界。

## 14. 练习

1. 为一个已有组件重命名为 BEM，把布局规则移到外层，并用一个修饰符实现紧凑变体。
2. 建立原始、语义、组件三层令牌，将组件中的硬编码颜色替换为语义令牌，再增加深色主题。
3. 用 `@layer` 整理 reset、base、components、vendor、utilities，故意制造冲突并解释最终胜出的原因。
4. 将同一组件分别用普通 CSS、CSS Modules 和零运行时方案实现，比较作用域、构建产物和运行时成本。
5. 对一个第三方组件做隔离：导入到 `vendor` 层，缩小重置范围，并验证焦点、表单和深色主题没有被破坏。

> 上一篇：[渲染性能与调试](../05-advanced/17-performance-debugging.md)。下一篇：[兼容性、无障碍与测试](19-compatibility-accessibility.md)。
