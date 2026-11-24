# 02 · 选择器与伪类

> 学习目标：用准确而低耦合的选择器找到元素，并掌握结构、状态和表单相关伪类。

## 1. 选择器的本质

选择器是一组匹配条件。浏览器把规则与 DOM 元素匹配，命中的声明才有机会参与层叠计算。

```css
/* 标签 */
p { }

/* 类 */
.card { }

/* ID */
#main-navigation { }

/* 属性 */
a[href^="https"] { }
```

## 2. 基础选择器

| 类型 | 示例 | 用途 | 建议 |
| --- | --- | --- | --- |
| 通用 | `*` | 所有元素 | 初始化时慎用，避免影响范围过大 |
| 标签 | `section` | 同类语义元素 | 适合全局基线，组件内尽量收敛 |
| 类 | `.button` | 可复用组件与状态 | 默认首选 |
| ID | `#app` | 页面唯一锚点 | 样式优先级高，通常不用于组件 |
| 属性 | `[aria-expanded="true"]` | 按属性或值匹配 | 表达状态与数据特征 |

```html
<button class="button" type="button" aria-expanded="false">
  展开详情
</button>
```

```css
.button[aria-expanded="true"] {
  background: #dff2b7;
}
```

## 3. 组合器：描述元素关系

```text
.container
├── .title
├── .content
│   ├── p
│   └── strong
└── .footer
```

| 组合器 | 示例 | 含义 |
| --- | --- | --- |
| 后代 | `.container p` | 任意深度的后代 p |
| 直接子 | `.container > p` | 直接子 p |
| 相邻兄弟 | `h2 + p` | 紧接 h2 后的第一个 p |
| 后续兄弟 | `h2 ~ p` | h2 后的所有同级 p |

```css
.card > .card__title { }
.card__title + .card__description { }
```

子组合器能减少样式泄漏，但不要为了“永远只用 `>`”而牺牲语义和可维护性。

## 4. 选择器列表

多个选择器共享声明时，使用逗号分隔：

```css
:where(h1, h2, h3, h4, h5, h6) {
  text-wrap: balance;
}
```

注意：下面两种写法不一样。

```css
.a,
.b { color: red; }

.a > .b { color: red; }
```

## 5. 伪类：表达状态与结构

### 用户交互状态

```css
a:link { color: #275d8c; }
a:visited { color: #6f4f91; }
a:hover { text-decoration-thickness: 0.15em; }
a:active { transform: translateY(1px); }

.button:focus-visible {
  outline: 3px solid #8262d7;
  outline-offset: 3px;
}
```

触摸设备上 `:hover` 可能“粘住”，因此关键信息不能只在 hover 时出现。

### 表单状态

```css
input:disabled { opacity: 0.6; }
input:checked + label { font-weight: 700; }
input:invalid:not(:placeholder-shown) { border-color: #c84732; }
input:user-invalid { border-color: #c84732; }
```

`:user-invalid` 比 `:invalid` 更适合表达“用户已经尝试提交后的错误”，可避免页面刚加载就把所有空必填项标红。

### 结构伪类

```css
li:first-child { }
li:last-child { }
li:nth-child(2n) { background: #f0ede5; }
li:nth-child(3) { }
li:nth-last-child(2) { }
p:only-child { }
```

`nth-child` 从 1 开始计数，`2n` 表示偶数项。注意它按所有兄弟元素计数，而不是只数同类元素。

### 功能伪类与空状态

```css
:root { color-scheme: light dark; }
:where(:fullscreen) { background: white; }
.card:empty { display: none; }
```

### 目标与当前状态

```css
section:target { scroll-margin-top: 6rem; }
```

## 6. 伪元素：生成内容或局部盒子

```css
p::first-line { font-variant-caps: small-caps; }
p::selection { background: #c8f35c; color: #24261f; }

.notice::before {
  content: "提示";
  margin-right: 0.5rem;
  font-weight: 700;
}

.input::placeholder { color: #8b8e83; }
```

历史写法 `:before`、`:after` 仍被兼容，新代码统一写 `::before`、`::after`。

## 7. `:is()`、`:where()` 与 `:has()`

```css
/* :is() 取参数中优先级最高的选择器 */
:is(h1, h2, .title):hover { color: #3d601c; }

/* :where() 的优先级始终为 0 */
:where(.card, .panel) > :where(h2, h3) {
  margin-block-start: 0;
}

/* :has() 根据后代或兄弟状态选择父级 */
.card:has(> img) { padding-block-start: 0; }
.field:has(input:invalid) label { color: #a53d2b; }
```

```text
.card
  └── img 存在 ──▶ .card:has(> img) 命中
```

`:has()` 很强大，但复杂表达式会增加匹配和审查成本，应优先选择最直接的 DOM 状态类。

## 8. 优先级

优先级按四组计数比较（逐位比较，前一位分出胜负后不再看后面）：

```text
(行内样式, ID 数量, 类/属性/伪类数量, 标签/伪元素数量)
```

| 选择器 | 优先级简写 |
| --- | --- |
| `p` | `(0,0,0,1)` |
| `.card` | `(0,0,1,0)` |
| `.card p` | `(0,0,1,1)` |
| `#app .card` | `(0,1,1,0)` |
| `style="..."` | `(1,0,0,0)` |
| `!important` | 不参与计数，属于重要性层叠 |

```css
#title { color: red; }
.card #title { color: blue; }
```

后者 ID 与类都更多，所以是蓝色。**优先级不是十进制数字**：`(0,1,0,0)` 高于任意多个类组成的 `(0,0,99,99)`。

`:where()` 不增加优先级；`:is()`、`:not()`、`:has()` 取参数选择器中的最高优先级；伪元素增加第三组计数。

## 9. 控制优先级的实用策略

```css
/* 默认按钮：低优先级 */
.button {
  border: 1px solid currentColor;
  background: transparent;
}

/* 状态：用属性表达，避免双重类名不断升级 */
.button[aria-pressed="true"] {
  background: #24261f;
  color: #fbfaf6;
}
```

推荐顺序：

1. 保持选择器短，通常 1～2 层足够。
2. 用组件类划分边界，而不是靠标签选择器到处覆盖。
3. 状态与结构分开：`.button` 管基础外观，`.is-active` 或 `[aria-pressed]` 管状态。
4. 避免 `!important`；工具类覆盖或第三方样式冲突时再评估。

## 10. 性能与可维护性

现代浏览器对选择器匹配做了大量优化，不必为了微秒级性能把代码写得难以理解。真正重要的是：

- 避免过深后代选择器。
- 避免依赖 DOM 顺序但语义上并非顺序关系的选择器。
- 避免为纯视觉结构引入无意义的 ID。
- 不要在状态变化时增删复杂后代类，优先切换根元素状态类。

## 关联示例

- [选择器实验台](../../examples/foundations/selectors-playground.html)：组合器、结构伪类、`:is()`、`:where()`、`:has()` 与 `:user-invalid`。
- [层叠、层与主题](../../examples/foundations/cascade-layers-theme.html)：把选择器结果放入完整层叠流程中观察。

## 11. 练习

1. 写一个只选中 `.card` 直接子标题的选择器。
2. 给列表第 3、6、9 项设置背景。
3. 用 `:has()` 让包含错误提示的表单项显示红色边框。
4. 分别用 `.card p` 和 `.card > p` 测试后代与直接子元素的差别。
5. 用 DevTools 查看 `:where()` 与 `:is()` 命中时的优先级差异。

> 下一篇：[层叠、继承与 CSS 变量](03-cascade-inheritance.md)。
