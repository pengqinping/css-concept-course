# 附录 C · 练习与参考答案

本附录服务于 [课程总览](README.md)。

> 按正文 01–30 篇顺序排列，每篇 1–2 题，最后 5 题为跨篇综合。先写下自己的预测，再展开答案；答案只是可行解之一，不是唯一模板。

### 01–05 · 基础与盒模型

**01-1 · 计算值不等于占位宽度**：任务：给 `.box { width: 200px; padding: 20px }`，在 Styles 与 Computed 面板各读一次 `width`。验收：两处都是 `200px`，padding 不改变计算值。

<details><summary>参考答案</summary>
两处都是 `200px`。padding 属于盒模型阶段，改变的是占位宽度，不是 `width` 的计算值；占位宽度按 `box-sizing` 另算。

</details>

**02-1 · 两种序号选择器**：任务：混排 `li` 与 `div` 的列表，分别用 `li:nth-child(2n)` 和 `li:nth-of-type(2n)` 上色。验收：两者着色项不同。

<details><summary>参考答案</summary>
`nth-child` 把所有兄弟一起计数，`nth-of-type` 只数同类型的 `li`，所以被染色的项不一样。

</details>

**03-1 · 未分层胜出**：任务：`reset` 层、`components` 层、未分层各写一条命中同一 `p` 的普通声明。验收：未分层那条生效，即使写在最前面。

<details><summary>参考答案</summary>
普通声明中未分层样式强于所有分层样式，层顺序按声明先后比较，书写位置在更后面的关卡。

</details>

**03-2 · 重要性反转层序**：任务：给第 1 题 `reset` 层的规则加 `!important`。验收：它反超未分层规则。

<details><summary>参考答案</summary>
重要声明反转层顺序：先声明的层更强，未分层反而最弱。所以 `reset` 层的 `!important` 胜出。

</details>

**04-1 · initial 与 revert**：任务：对比 `color: initial` 与 `color: revert` 分别用在 `p` 和 `<a>` 上的显示。验收：`p` 两者都黑；`<a>` 的 `initial` 黑、`revert` 链接蓝。

<details><summary>参考答案</summary>
`initial` 取规范初始值（`canvastext`），`revert` 退回浏览器默认样式——`<a>` 的 UA 样式设了蓝色，所以两者在链接上分叉。

</details>

**05-1 · 两种 box-sizing**：任务：`.b { width: 300px; padding: 20px; border: 5px solid }`，切换 `content-box` 与 `border-box`。验收：前者占位 `350px`，后者占位 `300px` 且内容宽 `250px`。

<details><summary>参考答案</summary>
`content-box` 下 300 + 40 + 10 = 350px；`border-box` 下 `width` 涵盖 padding 与 border，内容被压到 250px，占位仍是 300px。

</details>

**05-2 · margin 不折叠的场景**：任务：上下两个 div 分别 `margin-bottom: 30px`、`margin-top: 20px`，量间距后再套一个 `display: flex` 父容器。验收：普通流间距 `30px`，flex 中间距 `50px`。

<details><summary>参考答案</summary>
普通流中相邻垂直 margin 折叠取较大值 30px；flex 子项之间不折叠，直接相加成 50px。

</details>

### 06–10 · 包含块、BFC、层叠与视觉

**06-1 · 参照盒换了人**：任务：父元素 content 宽 300px、padding 10px，子 `position: static; width: 50%`；再改父为 `relative`、子为 `absolute`。验收：子宽从 150px 变成 160px。

<details><summary>参考答案</summary>
static 时百分比参照父级 content box（300px）；absolute 时参照 padding box（300 + 10×2 = 320px），所以是 160px。父元素位置没变，参照盒变了。

</details>

**07-1 · 两种隔离方式**：任务：父无 padding，子 `margin-top: 40px`；分别给父加 `padding-top: 1px` 和 `display: flow-root`。验收：两种做法下父元素都不再被推下，40px 变成内部空白。

<details><summary>参考答案</summary>
padding 隔断了相邻 margin 的折叠条件；`flow-root` 建立 BFC，把折叠关在盒子内部。两者都不是"清掉 margin"，而是改变折叠发生在哪一侧。

</details>

**08-1 · 家族牌位**：任务：A 设 `position: relative; z-index: 1`，内含 `z-index: 9999` 的子；兄弟 B 设 `relative; z-index: 2`，内含 `z-index: 0` 的子。验收：B 的子盖住 A 的子。

<details><summary>参考答案</summary>
先比较两个层叠上下文的层级（1 vs 2），再比家族内部；子元素的 9999 逃不出 A 这个家族。

</details>

**09-1 · 行高的继承差异**：任务：`.box { font-size: 16px; line-height: 1.5 }` 内有 `h3 { font-size: 24px }`；再把 `line-height` 改成 `24px`。验收：前者 h3 行高 36px，后者 24px 且两行重叠。

<details><summary>参考答案</summary>
无单位 `1.5` 按各自字号计算，24 × 1.5 = 36px；带单位的 `24px` 是计算值直接继承，h3 字号也是 24px，于是行高等于字号，两行贴在一起。

</details>

**10-1 · 半透明叠色降低对比度**：任务：算 `#3f6b2a` 在白底的对比度，再把它与白各占 50% 混合后重算。验收：约 6.3:1 达标；混合后约 2.2:1 不达标。

<details><summary>参考答案</summary>
把深色文字向白色混合 50% 会大幅抬高亮度，对比度从约 6.3:1 掉到约 2.2:1，说明"看起来淡一点"的代价是可读性。

</details>

### 11–15 · 表面、溢出、变形与一维布局

**11-1 · 两种阴影**：任务：给透明底星形 SVG 分别加 `box-shadow` 和 `filter: drop-shadow`。验收：前者得到矩形阴影，后者得到星形轮廓阴影。

<details><summary>参考答案</summary>
`box-shadow` 按元素矩形盒投影，`drop-shadow` 按 alpha 轮廓投影；换成不透明矩形后两者结果一致。

</details>

**12-1 · 三种隐藏**：任务：同一按钮分别用 `display: none`、`visibility: hidden`、`opacity: 0` 隐藏，检查占位与 Tab。验收：`none` 失占位且跳过；`hidden` 保留占位、通常不可 Tab；`opacity: 0` 保留占位、仍可 Tab 且拦截点击。

<details><summary>参考答案</summary>
三者分别作用在布局、可见性、绘制阶段；只有 `display: none` 把盒子从布局树移除，`opacity: 0` 的元素依然在命中测试的范围内。

</details>

**13-1 · 变换顺序**：任务：写 `rotate(30deg) translateX(100px)` 与反序，记录元素中心落点。验收：约 `(86.6px, 50px)` 与 `(100px, 0)`。

<details><summary>参考答案</summary>
变换从右往左作用：前者先平移 100px，再把平移向量旋转 30°；后者先旋转再平移，平移向量不跟着转。

</details>

**14-1 · 过渡中点**：任务：`.box { transition: background-color 300ms linear }`，切换 `.on` 后第 150ms 读计算值。验收：约 `rgb(128, 128, 128)`。

<details><summary>参考答案</summary>
线性插值在中点取黑白的中值，不是立刻跳到黑色；读的是过渡席位的当前值，来源优先级最高。

</details>

**15-1 · basis 为零的等分**：任务：三个子项 basis 均为 0、grow 为 1:2:3，容器 600px、无 gap。验收：100 / 200 / 300px。

<details><summary>参考答案</summary>
先按 basis 各扣 0，剩余 600px 按 1:2:3 分配，得到 100/200/300px。这是"等分/按比例分"最可预测的前提。

</details>

**15-2 · 长 URL 撑破容器**：任务：长 URL 子项设 `flex: 1 1 0`，容器缩到 300px，先观察溢出再加 `min-width: 0`。验收：加之前溢出，加之后子项收缩并按换行策略截断。

<details><summary>参考答案</summary>
Flex 子项的默认最小尺寸是 min-content，长 URL 把下限顶住了；`min-width: 0` 解除这个下限后，收缩才能继续。

</details>

### 16–20 · 网格、容器、单位、响应式与表单

**16-1 · 先扣再分**：任务：容器 900px，模板 `200px 1fr 2fr`，gap 20px，轨道最小尺寸为 0。验收：三列 200 / 220 / 440px。

<details><summary>参考答案</summary>
先扣固定列 200px 与两个 gap 共 40px，剩下 660px 按 1:2 分，得到 220px 与 440px；总和 200 + 220 + 440 + 40 = 900px，与容器宽度自洽。

</details>

**16-2 · 1fr 的下限**：任务：`repeat(3, 1fr)` 中一列放不换行的长单词，再改成 `repeat(3, minmax(0, 1fr))`。验收：先某一列明显变宽，后恢复等宽。

<details><summary>参考答案</summary>
`1fr` 等价于 `minmax(auto, 1fr)`，下限由内容撑出；写成 `minmax(0, 1fr)` 后下限归零，三列重新等宽，长内容只能换行或溢出。

</details>

**17-1 · 组件自己的断点**：任务：260px 侧栏与 700px 主区放同一张卡片，用 `@container (min-width: 420px)` 让它横排。验收：主区横排、侧栏竖排，两者视口相同。

<details><summary>参考答案</summary>
容器查询读的是查询容器的可用宽度，不是视口宽度；同一个组件被放进不同宽度的槽位，就能各自重排。

</details>

**18-1 · em 与 rem**：任务：根字号 16px，父 `font-size: 1.25em`（20px），子分别设 `1.25em` 与 `1.25rem`。验收：25px 与 20px。

<details><summary>参考答案</summary>
`em` 相对当前元素的父级字号，20 × 1.25 = 25px；`rem` 永远相对根字号，16 × 1.25 = 20px。

</details>

**18-2 · 百分比 padding**：任务：宽 400px 的包含块，子元素 `padding: 10% 5%`。验收：上下各 40px、左右各 20px。

<details><summary>参考答案</summary>
垂直方向的百分比 padding 也参照包含块的**宽度**，所以四个值都按 400px 算：上下 40px、左右 20px。

</details>

**19-1 · 移动优先断点**：任务：两列卡片从 1000px 拖窄，把断点设在 46rem。验收：≥736px 两列、<736px 单列，720px 时已单列；不支持媒体查询时基础单列仍成立。

<details><summary>参考答案</summary>
基础样式写单列，用 `min-width` 查询向上加两列，这样不支持媒体查询的环境退回单列也不会坏掉。

</details>

**20-1 · 表单状态**：任务：`required` 邮箱框不填时看 `:invalid` 与 `:user-invalid`；再用 Tab 和鼠标分别聚焦按钮看 `:focus-visible`。验收：初始 `:invalid` 命中而 `:user-invalid` 不命中；Tab 命中、鼠标通常不命中。

<details><summary>参考答案</summary>
`:user-invalid` 要等用户交互后才命中，避免一进页面就报错；`:focus-visible` 按输入方式决定是否显示焦点环。

</details>

### 21–25 · 表格、弹层、架构、无障碍与渲染

**21-1 · 表头关联**：任务：写三列订单表，含 `caption`、`thead` 的 `th scope="col"` 和 `tbody` 每行的 `th scope="row"`。验收：读金额单元格时能听到列头"金额"。

<details><summary>参考答案</summary>
`scope` 建立单元格与表头的语义关联，屏幕阅读器才能读出"金额，某行"；`caption` 提供整表标题。

</details>

**22-1 · 模态与非模态**：任务：同一 `<dialog>` 分别用 `showModal()` 和 `open` 属性打开。验收：前者背景不可 Tab、Escape 可关、`:modal` 命中；后者背景仍可操作、`:modal` 不命中。

<details><summary>参考答案</summary>
只有 `showModal()` 把对话框放进 top layer 并让背景 inert；`open` 属性只是显示它，不产生模态行为。

</details>

**23-1 · 令牌集中**：任务：把三处硬编码的 `#245d4d` 改成 `var(--color-action)`，并在 `[data-theme="dark"]` 里换值。验收：三处同时变色，组件布局完全不动。

<details><summary>参考答案</summary>
变量把设计决策集中到一处；换主题只改令牌定义，组件选择器与布局规则都不用碰。

</details>

**24-1 · 语义元素自带行为**：任务：把 `<div class="button" onclick="save()">保存</div>` 改成 `<button class="button" type="button">保存</button>`，只用键盘操作。验收：Tab 可聚焦、回车与空格都能触发、焦点环可见。

<details><summary>参考答案</summary>
原生按钮自带可聚焦、键盘激活与焦点语义，不需要额外 JS；div 只是画得像按钮，行为全靠补。

</details>

**25-1 · 只走合成的属性**：任务：120px 宽的块分别用 `width: 300px` 和 `transform: scaleX(2.5)` 做 1 秒动画，看 Performance。验收：终点都是 300px，但前者有 Layout 段、后者没有。

<details><summary>参考答案</summary>
`width` 改动落在布局阶段，要重算再重绘；`transform` 落在合成阶段，不触发布局与绘制。

</details>

**25-2 · 强制同步布局**：任务：循环里交替执行 `box.style.width = '300px'` 与读 `box.offsetWidth` 各 50 次，再把读移出循环。验收：前者约 50 个 Layout 段，后者约 1 个。

<details><summary>参考答案</summary>
写入后立刻读取几何属性会强制浏览器同步完成布局；把读集中到写之前或之后，Layout 就只发生一次。

</details>

### 26–30 · 作用域、新平台、打印、混合与组件边界

**26-1 · scope 不阻断继承**：任务：写 `@scope (.card) to (figure) { p { color: red } }`，并在 `figure` 内放一个带自身 `font-family` 的段落。验收：`figure` 内的 `p` 不变红，但继承来的 `font-family` 仍生效。

<details><summary>参考答案</summary>
`@scope` 只限制"哪些元素被这条规则命中"，不改变继承链；被排除的元素仍从祖先继承未被覆盖的属性。

</details>

**27-1 · @supports 兜底**：任务：给滚动进度条写 `animation-timeline: scroll(root block)`，基础状态写 `transform: scaleX(1)`，动画包进 `@supports`。验收：支持时进度随滚动 0→1；不支持时进度条保持满格可见。

<details><summary>参考答案</summary>
`@supports` 把新特性关在条件里，基础样式在不支持的环境仍然完整；若进度是关键信息，应改用 JS 兜底而不是留静态满格。

</details>

**28-1 · 打印样式**：任务：给带导航、深色背景的报告写 `@media print`，隐藏导航、白底黑字、用 `::after` 展开链接地址。验收：预览无导航与深色背景；`http` 链接后多出 `(地址)`，页内锚点不追加。

<details><summary>参考答案</summary>
打印媒体是独立样式层，要把屏幕上的装饰与交互线索换成纸上可读的信息；用属性选择器匹配 `href^="http"` 即可只展开外部链接。

</details>

**29-1 · 形状绕行**：任务：圆形图片浮动后只写 `border-radius: 50%`，再补 `shape-outside: circle(50%)` 与 `shape-margin: 1rem`。验收：先按矩形绕行，后沿圆边绕行且间距变大。

<details><summary>参考答案</summary>
`border-radius` 只改变视觉裁剪，浮动区仍是矩形；`shape-outside` 才改变文字的绕行路径，`shape-margin` 控制文字与路径的距离。

</details>

**30-1 · 组件边界**：任务：Shadow DOM 卡片内按钮写 `part="action"` 和 `color: var(--accent, #172033)`；页面写 `.card button { color: red }`、`--accent: #3f6b2a` 与 `::part(action) { border-color: gold }`。验收：按钮文字是绿色、边框是金色；删掉 `part` 后边框不再变金。

<details><summary>参考答案</summary>
自定义属性可以穿透 Shadow 边界，普通选择器被挡在外面；`::part()` 只在组件显式暴露 part 名之后才能命中。

</details>

### 跨篇综合题

**C-1 · 层与令牌一起用（03/04/23）**：任务：建立 `@layer reset, components, utilities`，用变量做主题令牌，在 `reset` 层写 `h2 { color: red }`、在 `components` 层写 `.card__title { color: blue }`。验收：标题为蓝；删掉组件规则后变红；改一处令牌即可换主题。

<details><summary>参考答案</summary>
层顺序把"谁覆盖谁"显式化，组件层后于 reset 层所以胜出；令牌把主题差异收敛到变量定义，布局不受影响。

</details>

**C-2 · 等分与溢出联调（05/15/16/25）**：任务：300px 容器里三个 `flex: 1` 子项含长 URL，先观察溢出，再用 `min-width: 0` 配合 `overflow-wrap: anywhere` 修复，并检查 Performance 无额外 Layout。验收：三项等宽、页面无横向滚动。

<details><summary>参考答案</summary>
min-content 下限撑破等分，`min-width: 0` 解除下限，`overflow-wrap: anywhere` 给长串提供断点；全程只改样式，不触发逐帧布局。

</details>

**C-3 · 弹层错位溯源（06/08/13/22）**：任务：用 `fixed` 居中的弹层在祖先加了 `transform: translateX(0)` 后只覆盖祖先区域；改为挂到 `body` 或换原生 `<dialog>`。验收：弹层覆盖整个视口，焦点与 Escape 正常。

<details><summary>参考答案</summary>
`transform` 祖先给 `fixed` 换掉了包含块，所以 inset 参照祖先而非视口；挂到 body 或进入 top layer 都能绕开这个包含块。

</details>

**C-4 · 响应式组合拳（17/18/19/24）**：任务：同一卡片在侧栏与主区用容器查询重排，标题用 `clamp()` 配合 `cqi`，并支持 `prefers-reduced-motion` 与键盘焦点。验收：视口不变时两处布局不同；标题随容器连续变化；减弱动画下直接显示终态且焦点环可见。

<details><summary>参考答案</summary>
视口查询管页面骨架，容器查询管组件内部，`cqi` 让字号跟着容器走；减弱动画与焦点样式属于交付门槛，不是附加项。

</details>

**C-5 · 一份文档的两种介质（01/12/25/28/24）**：任务：给长文档写打印样式，隐藏导航、重复表头、避免行被拆开、页码从第二页开始，并在屏幕版检查 Computed 与焦点。验收：每页有表头、无行被切、首页无页码；屏幕版焦点环仍可见。

<details><summary>参考答案</summary>
`@media print` 与 `@page` 只描述纸张这一介质，屏幕版保持不变；用 Computed 验证计算值，用 `:focus-visible` 确认可访问性没被打印规则污染。

</details>

> 下一份附录：[附录 D · 常见问题速查](appendix-d-pitfalls.md)
