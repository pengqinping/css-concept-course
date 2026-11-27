# 02 · 选择器：精准选中元素

> **前置**：[01 · 样式怎么生效](01-how-css-works.md)——知道一条规则由选择器和声明块组成。
>
> 上一篇：[01](01-how-css-works.md) ｜ 下一篇：[谁说了算：层叠与继承](03-cascade-inheritance.md) ｜ [教程总览](README.md)

```css
#main .list > li:nth-child(2) { color: crimson; }
```

一行选择器里混了五种武器：id、类、子组合器、位置伪类。它们按什么规则组合？为什么它能精确命中"main 里 list 的第二个 li"？这章把选择器体系完整过一遍：**基本选择器（含属性匹配）、组合器、伪类全景、伪元素**，最后把优先级算法和现代嵌套语法讲透。

## 基本选择器：五种，外加属性匹配的六种姿势

| 选择器 | 写法 | 什么时候用 |
| --- | --- | --- |
| 类 | `.card` | **默认选择**，可复用、可组合 |
| 标签 | `p`、`input` | 元素级默认样式（reset、排版基线） |
| id | `#header` | 几乎不用：优先级太高，难覆盖 |
| 通配 | `*` | 全局重置（如 `box-sizing`） |
| 属性 | `[type="email"]` | 靠属性区分的元素（表单控件最典型） |

属性选择器不只是"有没有"，它有完整的一套匹配模式：

| 模式 | 含义 | 例子 |
| --- | --- | --- |
| `[attr]` | 存在即命中 | `[disabled]` |
| `[attr="v"]` | 完全相等 | `[type="email"]` |
| `[attr^="v"]` | 以 v 开头 | `[href^="https"]` |
| `[attr$="v"]` | 以 v 结尾 | `[href$=".pdf"]`（给 PDF 链接加图标） |
| `[attr*="v"]` | 包含 v | `[class*="btn"]`（慎用：太宽） |
| `[attr~="v"]` | 空格分隔的词之一 | `[class~="active"]` 等价 `.active` |

另有两个修饰符：`i` 忽略大小写（`[type="EMAIL" i]`），`s` 强制区分。

一条经验不变：**日常写类，元素级写标签，id 基本不写**。id 的优先级是 id 级的，想覆盖它就得再掏 id 或 `!important`。

## 组合器：表达元素之间的关系

```css
ul li        { }   /* 后代：ul 里面所有层级的 li */
ul > li      { }   /* 子代：只选 ul 的直接子级 li */
h2 + p       { }   /* 相邻：紧跟在 h2 后面的第一个 p */
h2 ~ p       { }   /* 同级之后：h2 后面所有同层 p */
```

组合器选的是**关系**。写组件样式时优先用子代 `>`——后代空格会把"别人塞进来的嵌套"也选中，这是样式互相污染的常见来源。`+` 的典型用法是"标题后第一段缩进"、"label 后面的输入框"这类"位置跟随"关系。

## 伪类全景：按状态、按位置、按关系

伪类（单冒号）命中**已有元素**的某种状态或位置。数量多，按用途分四组记：

| 组 | 代表 | 说明 |
| --- | --- | --- |
| 交互状态 | `:hover` `:focus` `:active` | 鼠标、键盘交互 |
| 表单状态 | `:checked` `:disabled` `:valid` `:invalid` `:required` | 表单篇展开 |
| 位置 | `:first-child` `:last-child` `:nth-child()` `:empty` | 结构位置 |
| 链接与语言 | `:link` `:visited` `:lang()` | `:visited` 受隐私限制，能改的样式极少 |

### :nth-child 的公式语法 an+b

`:nth-child()` 不只是数字，它接受一个线性公式 `an + b`：

| 写法 | 命中 | 用途 |
| --- | --- | --- |
| `:nth-child(odd)` / `even` | 第 1,3,5… / 2,4,6… | 隔行变色 |
| `:nth-child(3n)` | 第 3,6,9… | 每三个一组 |
| `:nth-child(-n+3)` | 第 1,2,3 | **前三个**（最常用 trick） |
| `:nth-child(n+4)` | 第 4 起所有 | 除前三个外 |

**`:nth-child` 与 `:nth-of-type` 的经典坑**：`:nth-child(2)` 数的是**所有兄弟**（不分标签），`:nth-of-type(2)` 数的是**同标签**兄弟。容器里"两个 div + 三个 p"时，`p:nth-child(2)` 命中的可能是那个 div（它恰好排第 2）——想要"第 2 个 p"，得用 `:nth-of-type(2)` 或保证容器结构纯净。

### 关系伪类四兄弟：:not / :is / :where / :has

```css
li:not(.skip)                    { }   /* 排除 */
:is(h1, h2, h3) .title           { }   /* 任一命中；写法合并 */
:where(article, section) p       { }   /* 同 is，但优先级恒为 0 */
.card:has(img)                   { }   /* 含 img 的 .card——"父选择器" */
li:has(> a.badge)                { }   /* 直接子级带徽章的 li */
```

- **`:is()` 和 `:where()` 唯一区别是优先级**：`:is()` 取括号里**最高**的优先级；`:where()` 恒为 0。这让 `:where` 成为重置样式的理想工具——重置永远输给任何具体样式，天然不添乱。
- **`:has()` 是 2023 年落地的里程碑**：以前 CSS 只能从父找子，`:has()` 终于允许"看孩子选爸爸"。表单联动、卡片含图加样式、后面有兄弟就调整间距，全都不用 JS。
- `:is()` 里只能写简单选择器（不能写 `div p` 这种带组合器的），要表达关系放进 `:has()`。

### :focus 三兄弟，别混

`:focus` 聚焦就命中；`:focus-visible` **只在"应该显示焦点环"时命中**（键盘 Tab 导航命中，鼠标点击通常不命中）；`:focus-within` 自己或**后代**聚焦就命中。自定义焦点样式用 `:focus-visible`（体验最好），做"输入框组高亮"用 `:focus-within`。

## 伪元素：造出原本不存在的盒子

伪元素（双冒号）**生成一个新盒子**或命中元素内部的小部件：

- **`::before` / `::after`**：必须配 `content`（`content: ""` 也行），默认是行内盒。装饰箭头、分隔线、遮罩层全靠它们——**装饰不进 HTML**。`content` 还有进阶玩法：
  ```css
  a[href^="http"]::after { content: " (" attr(href) ")"; }  /* 打印版：显示链接地址 */
  h2::before { content: "§" counter(section) " "; }         /* 自动编号 */
  ```
- **部件类**：`::placeholder`（输入框占位文字）、`::selection`（选中文字）、`::marker`（列表符号）、`::first-letter` / `::first-line`（首字下沉、首行）。
- 配合第 04 篇的盒模型，`::before/::after` 是纯 CSS 绘图的基础积木。

## 优先级算法与现代嵌套

优先级四元组 **(行内, id, 类/伪类/属性, 标签/伪元素)** 逐位比较：

| 选择器 | 行内 | id | 类 | 标签 | 权重 |
| --- | --- | --- | --- | --- | --- |
| `p` | 0 | 0 | 0 | 1 | (0,0,0,1) |
| `.card p` | 0 | 0 | 1 | 1 | (0,0,1,1) |
| `#main .card` | 0 | 1 | 1 | 0 | (0,1,1,0) |

几条精确规则：通配 `*` 和组合器（`>`、`+`、空格）**不计数**；`:where()` 恒为 0；`:is()` / `:not()` / `:has()` 取括号内**最高**项的优先级；`!important` 不在这个表里——它换到层叠的"来源与重要性"档位去比（第 03 篇）。

**原生嵌套**（2023 年标准化）让选择器可以像 Sass 一样写，`&` 代表父选择器：

```css
.card {
  padding: 1rem;
  & h2  { color: crimson; }      /* .card h2 */
  & > p { margin: 0; }           /* .card > p */
  &:hover { background: #f6f7f3; }  /* .card:hover */
  @media (min-width: 60em) { padding: 2rem; }  /* 嵌套里也能写 at-rule */
}
```

注意：嵌套只解决**书写组织**，不改变任何优先级和层叠行为，也不会限制样式的影响范围（高级篇 `@scope` 章对比三者）。

引擎层面还有个值得知道的细节：选择器**从右往左**匹配——`ul > li:nth-child(2)` 先找出所有"是第二个孩子"的 li，再向左验证祖先。最右侧的复合选择器决定了规则的大概命中范围，这也是"别用通配开头的超长选择器"的性能理由。

## 动手验证

[打开实验台：组合选择器，实时看命中了谁](../../examples/foundations/selectors-playground.html)

<iframe class="demo-frame" src="/css-concept-course/examples/foundations/selectors-playground.html" title="选择器实验台" loading="lazy"></iframe>

[打开 demo：最小选择器练习](../../examples/minimal/02-selectors.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/02-selectors.html" title="选择器练习" loading="lazy"></iframe>

实验台里拼 `:nth-child(-n+3)` 和 `:nth-of-type(2)`，观察两者在"混合标签"容器里的差别；再写一个 `:has()`，看父元素怎么被孩子的状态选中。

## 本章要点

- 属性选择器有完整匹配模式（`^=` `$=` `*=` `~=`），配 `i` 忽略大小写。
- `:nth-child()` 是 `an+b` 公式：`-n+3` 选前三个，`n+4` 选第四个起；数兄弟用 child，数同标签用 of-type。
- `:is()` 取最高优先级，`:where()` 恒为 0 适合做重置，`:has()` 让 CSS 第一次"看孩子选爸爸"。
- 焦点样式用 `:focus-visible`，输入框组联动用 `:focus-within`。
- `::before/::after` 造盒子，`content` 能引用 `attr()` 和 `counter()`；装饰不进 HTML。
- 原生嵌套用 `&`，只改书写不改层叠行为。

下一篇 [03 · 谁说了算：层叠与继承](03-cascade-inheritance.md)：两条规则真的打起来时，完整的裁决流程是什么；哪些属性又会从父元素传下来。
