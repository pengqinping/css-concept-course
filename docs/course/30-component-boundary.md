# 30 · 状态何时成立，样式到哪里为止

> 一句话模型：交互状态是一条有先后的时序，输入能力决定哪些状态成立；组件边界则是一道有闸门的墙——普通选择器过不去，`:host`、`::part()` 和 CSS 变量只能按约定的通道穿过。

## 先看一个现象

你给按钮写了悬停变色，用手机点开却发现颜色"粘"在按钮上不消失；你给页面写了 `button { color: red }`，想顺手改一个第三方卡片组件里的按钮，页面其余按钮都红了，组件里那个纹丝不动；你又把 `:focus-visible` 的焦点环加在页面全局，组件内部的输入框还是没有焦点环。

你以为这些都是"样式没生效"；实际是两件事：状态在错误的时间被触发，或者样式撞到了一堵墙。判断错原因，就会在错误的地方加大选择器优先级——而那两件事都不靠优先级解决。

## 先建立直觉

:::figure 30-component-boundary|Shadow DOM 边界：哪条线能过去
图说明：一道竖墙把左侧页面文档与右侧影子树分开，墙上的自定义元素宿主 `:host` 是关口。左边三条箭头被墙挡回：`.card button`、页面全局 `button`、页面里的 `:focus-visible`。右边三条带标签的箭头穿过关口：CSS 变量沿继承链进入、`:host` 从内部描述宿主、`::part()` 只命中组件显式标了 `part` 的节点。图上注明：跨树的普通声明由外层胜出，`!important` 则反过来。
:::

图要记住的一句话：边界不是"全封闭"，而是"只有列出的通道能过"。想改组件内部，要么改它公开的令牌和 Part，要么别越过边界。

## 机制拆成四步

### 1. 四个状态是一条时序，优先级却相同

```css
.btn:hover         { background: #2d4d1d; }
.btn:focus-visible { outline: 3px solid #3157d5; outline-offset: 3px; }
.btn:active        { background: #17340f; transform: translateY(1px); }
.btn:disabled      { background: #e5e7eb; color: #9aa2ad; cursor: not-allowed; }
```

时序是：鼠标移入先 `:hover`，按下时 `:active`，键盘 Tab 到位时 `:focus-visible`，控件被禁用后 `:disabled`。四者都是伪类，优先级同为 `(0,0,1,0)`；同时命中时由**书写顺序**决定谁生效，所以最"不可逆"的 `:disabled` 放最后——禁用按钮仍可能被 `:hover` 命中，不能让悬停色盖掉禁用态。

**为什么不写 `:focus`？** `:focus` 在鼠标点击后也会匹配，容易给每一处点击都加一圈焦点环；`:focus-visible` 由浏览器判断何时该显示焦点提示，通常是键盘或辅助技术操作时。需要"内部有焦点时高亮宿主"，在影子树写 `:host(:focus-within)`，而不是指望页面全局规则钻进去。

| 状态 | 何时成立 | 触屏上的表现 |
| --- | --- | --- |
| `:hover` | 指针停在元素上 | 可能点后粘住，不承载关键信息 |
| `:active` | 按压/激活期间 | 短暂成立，适合即时反馈 |
| `:focus-visible` | 浏览器判断需要可见焦点时 | 键盘与辅助技术触发，与指针无关 |
| `:disabled` | HTML 有 `disabled` 属性 | 不可聚焦、不参与提交，与输入方式无关 |

### 2. 输入能力决定哪些状态能成立

```css
@media (hover: hover) and (pointer: fine) {
  .btn:hover { background: #2d4d1d; transform: translateY(-2px); }
}
@media (any-pointer: coarse) {
  .btn { min-block-size: 3rem; }
}
```

`:hover` 是伪类，`(hover: hover)` 是能力查询，两者不是一回事（呼应第 19 篇）。触屏主输入报告 `hover: none`、`pointer: coarse`：点按后 `:hover` 可能粘住，但它不该承载唯一的功能或信息；`:active` 在按压期间短暂成立，适合做即时反馈；`:focus-visible` 与 `:disabled` 跟输入方式无关，前者由键盘交互触发，后者由 HTML 的 `disabled` 属性决定。

**为什么要把悬停规则包进查询？** 混合设备很常见——触屏笔记本同时报告鼠标与触控。只关心主输入时用 `hover`/`pointer`，"只要有任一触控输入"时用 `any-hover`/`any-pointer`。把关键操作藏在悬停里，触屏用户就够不到；悬停位移只是增强，还要配 `prefers-reduced-motion`。

`@media (any-hover: hover)` 只问"有没有任意一个输入能悬停"，混合设备可能同时命中它和 `hover: none`。写样式时先想清楚"这条规则是给主输入的增强，还是给任何输入的兜底"，再选 `pointer` 或 `any-pointer`；把触控目标放大这类通用改进写在查询外，所有环境都得到。

### 3. Shadow DOM 把样式切成两个域

影子树内部的样式表与外部文档互不穿透：页面里写 `.card button { color: red }` 选不中影子树里的按钮；反过来，组件内部的类名也不会漏到页面。能跨越边界的只有几条明确通道：

| 通道 | 写在哪 | 能改什么 | 边界 |
| --- | --- | --- | --- |
| 宿主选择器 | 页面 | 自定义元素本身的尺寸、布局、主题令牌 | 选不中内部节点 |
| `:host` | 影子树 | 宿主的默认样式 | 只在组件自己内部生效 |
| `::slotted()` | 影子树 | 被 `<slot>` 分发的直接节点 | 不穿透到节点的深层后代 |
| `::part()` | 页面 | 内部显式标了 `part` 的节点 | 没标 `part` 的结构不可选 |
| CSS 变量 | 两侧 | 用 `--token` 传颜色、间距等设计值 | 内部必须用 `var()` 消费 |

```css
/* 页面文档：能改宿主，改不了内部 */
demo-card { --accent: #3f6b2a; width: 20rem; }
demo-card::part(action) { border-color: gold; }
demo-card button { color: red; }   /* 无效：内部按钮在影子树里 */

/* 影子树内部：自己决定内部结构 */
:host { color: var(--accent, #172033); }
.action { padding: 0.5rem 1rem; }   /* 外部类名选不中它 */
```

**为什么跨树的普通声明外层赢？** 层叠比较时，来自外层文档的普通声明胜过影子树内部的 `:host` 声明，与选择器优先级无关；`!important` 时顺序反转，内部赢。所以别靠在 `:host` 里堆高优先级来抵抗页面样式——把允许外部改的项设计成令牌或 Part，才是稳定的契约。Part 名属于对外接口，改了名外部规则会直接失效。

### 4. :host 与 all 决定组件的起跑线

```css
:host {
  all: initial;              /* 切断从页面继承来的排版 */
  display: inline-block;     /* all 之后必须自己补回布局 */
  font: 500 1rem/1.5 var(--font-ui, system-ui);
  color: var(--accent, #172033);
}
```

`all` 把几乎所有属性一次性重置：`all: initial` 设为各属性的初始值，`all: unset` 让继承属性继承、非继承属性回到初始，`all: revert` 退到用户代理样式；`direction`、`unicode-bidi` 和自定义属性不在重置范围内。

**为什么组件需要它？** 组件可能被放进任何页面，页面的全局 `font`、`line-height`、`color` 会通过继承渗进来，让同一个组件在不同站点长得不一样。在 `:host` 里用 `all: initial` 把起跑线归零，再显式补回需要的布局与字体；注意 `display` 的初始值是 `inline`，不补回 `inline-block` 组件就退回行内盒，宽高设置不再生效。若想沿用页面字体，就显式写 `font: inherit`。

`::part()` 与变量都是"受限穿透"：`::part(action)` 只能命中内部写了 `part="action"` 的节点；变量能沿继承链进入影子树，但只有内部写了 `var(--accent)` 才起作用，而且 `var()` 的回退只在变量**缺失**时使用——外部传了非法颜色，回退不会救它。把组件样式的影响范围收进边界，靠的就是这种"只开放少数入口"的推理。

如果要对外公开一个令牌，最好用 `@property` 注册它的语法与初始值：`--accent` 被注册为 `<color>` 后，外部传进来的非法值会在赋值时被丢弃，而不是等到 `var(--accent)` 使用处才让整条声明失效。令牌是接口，接口要写清类型、默认值和允许范围。

## 动手验证

:::demo 30-component-boundary|两道开关，看谁改得动影子树里的按钮
先预测：页面写 `button { color: red }`，影子树内部按钮会变红吗？给内部按钮加上 `part="action"` 并在页面写 `::part(action) { color: green }`，它会不会变绿？先写下答案。
验证：用开关切换"页面全局 button 规则"与"组件暴露 action part"，状态文本显示当前生效 CSS、内部按钮的计算颜色与命中的通道（被挡住 / `::part()`）。核对普通选择器被挡、只有公开 Part 能改内部这两件事。
:::

## 容易误判的地方

- **"`:focus-visible` 等于 `:focus`"** → 前者只在需要可见焦点提示时匹配，鼠标点击通常不触发；组件内部焦点要在影子树里写样式，或用 `:host(:focus-within)`。
- **"触屏上 `:hover` 不存在"** → 它可能粘住；关键是别把功能只放在悬停里，并用 `(hover: hover) and (pointer: fine)` 限定增强。
- **"提高 `:host` 选择器优先级就能盖过页面"** → 跨影子树比较时普通声明由外层胜出；该开放的是令牌与 Part，不是优先级。

## 自己再做一次

1. 同一按钮按 `:hover`、`:focus-visible`、`:active`、`:disabled` 顺序写四种背景色（优先级相同）。**预期结果：鼠标悬停未按显示 hover 色；按下瞬间 active 色覆盖 hover；Tab 聚焦显示焦点环、背景为 focus-visible 色；加 `disabled` 后即使鼠标悬停也保持 disabled 色。**
2. 把第 1 题的悬停规则包进 `@media (hover: hover) and (pointer: fine)`，用触屏模拟（`hover: none`、`pointer: coarse`）打开。**预期结果：触屏模拟下悬停变色消失；键盘 `:focus-visible` 与 `disabled` 样式仍成立；点击时只有短暂的 `:active` 反馈。**
3. 用 Shadow DOM 封装一张卡片，内部按钮写 `part="action"` 和 `color: var(--accent, #172033)`。页面写 `.card button { color: red }`、`--accent: #3f6b2a` 与 `::part(action) { border-color: gold }`。**预期结果：内部按钮文字是绿色（变量穿透），不是红色（普通选择器被挡）；边框变金色（`::part()` 命中）；删掉 `part` 属性后金色边框消失。**

> 回到 [课程总览](README.md)，或查阅 [属性速查表](appendix-a-cheatsheet.md)。
