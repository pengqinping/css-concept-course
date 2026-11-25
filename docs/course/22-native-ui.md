# 22 · 原生弹层

> 一句话模型：浏览器已经给了三种"弹层"——展开、模态、浮层——它们进的是 top layer，键盘与焦点也由浏览器管；用 `div` 加 `z-index` 重造，等于把这些能力全丢掉。

## 先看一个现象

```html
<div class="modal" style="display: block">
  <p>确认删除？</p>
</div>
```

```css
.modal { position: fixed; inset: 0; z-index: 99999; }
```

你以为 `z-index: 99999` 能盖住一切，实际它可能被某个祖先的层叠上下文困住——`z-index` 只在自己的上下文里比大小。背景照样能 Tab 到、能点击，Escape 也没反应；父容器若有 `overflow: hidden`，它还会被裁掉。你造了一个"看起来像弹窗"的 `div`，但模态最要紧的三件事——背景不可交互、焦点圈定、Escape 关闭——一件都没有。

## 先建立直觉

![top layer 与常规文档层的剖面](figures/22-native-ui.svg)

*图 22-1 · top layer 与常规文档层的剖面*

图是一个竖直剖面：下方大块是常规文档层，里面画着若干层叠上下文和 `overflow: hidden` 的裁剪框；上方一条窄带是 top layer，放着模态 `dialog` 和 popover。箭头从"触发"指向"元素被提升到 top layer"。图上标明两条规则：top layer 绘制在所有常规内容之上，且不受祖先 `overflow` 裁剪；但元素自身的尺寸与定位仍按原本的包含块计算。

记住这条剖面：**"盖得住"靠的是层级，不是数值大小**。top layer 是浏览器单独开的一层，`z-index` 再大也到不了那里。

## 机制拆成四步

### 1. 三种原生能力，各解一种问题

`details/summary` 是零 JS 的 disclosure（折叠展开）：点 `summary` 展开内容，状态、键盘和读屏都由浏览器负责。`details[open]` 是原生状态，不要再维护一套 `is-open` 类。`summary` 前面的小三角由浏览器绘制，可以用 `::marker` 改颜色；别为了换图标把 `summary` 换成 `div`，那会连键盘操作一起丢掉。

`<dialog>` 面向模态任务：调 `showModal()` 后背景变成 inert、焦点被圈进对话框、Escape 可关闭、关闭后焦点回到原触发元素——这些都是浏览器做的。只用 `open` 属性打开的是非模态对话框，没有这些能力。

`popover` 属性面向轻量浮层：`popovertarget` 不写 JS 就能开关，脚本则用 `showPopover()` / `hidePopover()`。它默认**不是模态**：背景仍可交互，也不圈定焦点；`auto` 类型支持 light dismiss（点外部或 Escape 关闭），`manual` 类型不会。

| 场景 | 选谁 | 理由 |
| --- | --- | --- |
| 可折叠的问答、说明 | `details/summary` | 零 JS，状态与键盘由浏览器管 |
| 必须完成或取消的任务（确认、编辑） | `dialog.showModal()` | 背景 inert、焦点圈定、Escape |
| 非阻塞的提示、菜单、气泡 | `popover` | 轻量、light dismiss、不打断页面 |

一个 popover 连脚本都不用：

```html
<button type="button" popovertarget="help">帮助</button>
<div id="help" popover>这里是填写说明。</div>
```

`manual` 类型的 popover 不会因点外部而关闭，需要再放一个带 `popovertargetaction="hide"` 的按钮，或由脚本调 `hidePopover()`。选 `auto` 还是 `manual`，取决于"点外部就关掉是否安全"。

**为什么不能三选一通用？** 它们的能力是正交的：disclosure 不阻塞，modal 阻塞且要管焦点，popover 不阻塞但要浮在上方并轻关闭。用 modal 做 FAQ 会逼用户先关掉它；用 popover 做删除确认，用户还能点背景里的其他按钮，任务就不完整了。

### 2. top layer 不是"很大的 z-index"

被提升的元素绘制在所有常规内容之上，也不再被祖先的 `overflow: hidden` 裁剪——这是层级规则，不是 `z-index` 的数值。

```css
dialog::backdrop { background: rgb(16 24 40 / 55%); }
[popover]::backdrop { background: rgb(16 24 40 / 12%); }
```

`::backdrop` 只在元素进入 top layer 后才有，是背景遮罩的样式入口。给它加深色遮罩**不会**让 popover 变成模态：背景是否 inert，由打开方式决定。

在常规文档层里，祖先的 `transform` 会新建层叠上下文，把内部的 `z-index: 9999` 关在里面；top layer 位于所有常规上下文之上，所以不必再盘点祖先有没有 `transform` 或 `overflow`。

判断一个浮层是不是模态，别看它有没有遮罩，看它有没有让背景 inert。

**为什么"逃出 overflow"不等于"逃出布局"？** top layer 改的是绘制层级与裁剪关系，元素自身的尺寸、定位和包含块仍按 CSS 正常计算。该写的 `position: fixed`、`inset`、`max-block-size` 一个都不能省。

### 3. 打开状态用原生选择器表达

```css
details[open] summary { font-weight: 700; }
dialog:modal { border: 1px solid #c9d2d7; }
[popover]:popover-open { animation: pop-in 140ms ease-out; }
@media (prefers-reduced-motion: reduce) {
  [popover]:popover-open { animation: none; }
}
```

`details[open]`、`dialog:modal`、`[popover]:popover-open` 分别对应三种原生状态。注意 `dialog[open]` 包含非模态对话框，单凭 `[open]` 判断不出是否模态，要用 `:modal`。

键盘验收其实只有两件事：Tab 能不能进到该进的地方，Escape 能不能按预期退出。

**为什么要用原生状态而不是自己加类？** 自己加的类会和浏览器状态脱节：用户按了 Escape、点了背景，浏览器已经关掉弹层，你的类还留在 DOM 上，样式就卡在"打开"态。这些伪类都是只读的——CSS 能读取它们改变外观，但写伪类不会把元素变成模态。

### 4. CSS 只管外观，行为交给浏览器

CSS 负责位置、尺寸、背景、边框、遮罩、动画和状态视觉变化；浏览器负责焦点、键盘、light dismiss、背景隔离与打开关闭 API。

```js
const dialog = document.querySelector("#confirm");
dialog.showModal(); // 而不是 dialog.setAttribute("open", "")
```

用 `showModal()` 打开的对话框关闭时，浏览器会把焦点还给打开前获得焦点的元素；所以触发按钮最好留在 DOM 里，而不是打开后把它删掉。

**为什么这层分工不能糊弄？** 焦点圈定、Escape、焦点恢复都挂在 `showModal()` 带来的模态语义上。用 `div` 或只加 `open` 属性，CSS 画得再像也没有这些行为；确有复杂需求时再用少量 JS 补足，而不是从零重造。

## 动手验证

[打开 demo：三种弹层逐个开，看焦点和背景怎么变](../../examples/minimal/22-native-ui.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/22-native-ui.html" title="三种弹层逐个开，看焦点和背景怎么变" loading="lazy"></iframe>

> **先预测**：打开模态 `dialog` 后，Tab 会不会跑到背景里的按钮？打开 popover 后呢？分别按 Escape，谁会关闭？写下答案再揭晓。
>
> **验证**：打开 demo 调节参数，用页面显示的实时读数核对你的预测。

验证：打开 demo，依次触发三种弹层，用 Tab 和 Escape 操作，核对状态文本显示的"是否模态 / 背景是否 inert / 关闭方式"。再调背景遮罩开关，确认给 popover 加深遮罩后它依然不是模态。

## 容易误判的地方

- **"`z-index: 99999` 等于 top layer"** → top layer 是独立层级，`z-index` 再大也出不了祖先的层叠上下文与 `overflow` 裁剪。
- **"给 popover 加 `::backdrop` 就是模态"** → 遮罩只是样式；背景 inert 与焦点圈定由 `showModal()` 决定，popover 默认没有。
- **"`dialog[open]` 就是模态"** → `[open]` 包含非模态；模态要认 `:modal`，打开要用 `showModal()`。

## 自己再做一次

1. 写三个 `<details>` 组成的 FAQ，其中第一个默认带 `open`。**预期结果：不用任何 JS，点 `summary` 能展开/收起；Tab 能聚焦 `summary`，Enter/Space 能切换；第一个初始就是展开态。**
2. 写一个 `<dialog>`，分别用 `showModal()` 和 `open` 属性打开。**预期结果：`showModal()` 下背景无法 Tab 到、Escape 可关闭、`:modal` 命中；`open` 属性下背景仍能操作、`:modal` 不命中。**
3. 写一个 `<div popover>`，把它所在的触发按钮放在一个 `overflow: hidden; height: 60px` 的容器里，再用 `popovertarget` 打开。**预期结果：弹层显示在容器之外、不被裁掉；点外部或按 Escape 可关闭（`auto` 类型）；手动加 `::backdrop` 后背景依旧可交互。**

> 下一篇：[样式架构与设计令牌](23-architecture.md)
