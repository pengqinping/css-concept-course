# 05 · 元素到底占多大

> 一句话模型：一个盒子由 content / padding / border / margin 四层叠成；`box-sizing` 不改变任何尺寸，只改变 `width` 描述的是哪一层——**content-box 描述内容层，border-box 描述"内容 + 内边距 + 边框"那一层**。

## 先看一个现象

```css
.box {
  width: 300px;
  padding: 20px;
  border: 5px solid #b8860b;
}
```

你以为拿尺子量是 `300px`，实际是 `350px`——`padding` 和 `border` 各自左右各来一份，悄悄加了 `40 + 10 = 50px`。

改成 `box-sizing: border-box` 再量，变成了 `300px`。但这时真正放内容的地盘只剩 `250px`。你以为少的是边角，实际少的是整块内容宽度。

再加上 `margin: 20px`，横向总占空间分别是 `390px` 和 `340px`——`margin` 又加了 `40px`，但这次它不属于盒子自身。

还有一种更隐蔽的溢出：三列等宽的 flex 容器里，只要某一列塞进一长串不换行的文字，它就不会等宽，而是把整个容器撑出去。这跟 padding/border 无关，是另一个默认在作怪（第 4 步会揭晓）。

## 先建立直觉

:::figure 05-box-model|四层盒剖面与两种 box-sizing 对照
左半边是从内到外的剖面：content（放内容）、padding（内容与边框之间的缓冲）、border（边框本身）、margin（盒子之外、用来推开别人的透明间距）。右半边用同一组数字 `width:300px; padding:20px; border:5px` 并排画两个盒子：content-box 下内容层是 `300px`、总宽 `350px`；border-box 下总宽锁在 `300px`、内容层被挤到 `250px`。对照着看，两种模式只是"300 标在哪一层"不同。
:::

一句话抓住这张图：**`box-sizing` 换的不是盒子，是尺子的起点。**

## 机制拆成四步

### 1. 四层各管什么，margin 为什么在盒外

从里到外：

- **content**：装文字和子元素的地方，`width`/`height` 默认描述它。
- **padding**：内容与边框之间的缓冲，会被背景填充，透明但占位。
- **border**：边框本身，占据实实在在的宽度。
- **margin**：盒子之外的透明间距，不填充背景、不能放内容，作用是"我和别人之间留多远"。

为什么 margin 必须在盒外？因为它表达的是**关系**而不是**自身**：两块内容之间的呼吸，属于它们之间的空隙，不属于任何一块。把它算进盒子，就等于把"关系"塞进了"物体"，布局和折叠都会乱套（第 3 步会看到后果）。

所以 `width` 再怎么算，都只在前三层里打转；margin 另算。

一个验证技巧：默认 `background-clip: border-box`，背景会铺到边框外沿，但绝不会铺进 margin。打开背景色就能一眼看出盒子到哪为止、哪一段是 margin。

### 2. box-sizing 换的是 width 描述哪一层

固定用开头那组数字：`width: 300px; padding: 20px; border: 5px`（左右各一份），两种模式放在一起对照：

| 量的是什么 | content-box（默认） | border-box |
| --- | --- | --- |
| `width: 300px` 描述的是 | 内容层 = `300px` | 内容 + padding + border = `300px` |
| 内容实际宽 | `300px` | `300 - 2×20 - 2×5 = 250px` |
| 盒子实际占位（不含 margin） | `300 + 40 + 10 = 350px` | `300px` |
| 加上左右 `margin: 20px` 后 | `350 + 40 = 390px` | `300 + 40 = 340px` |

数字是同一组，只有 `300px` 标在哪一层变了。这就是为什么两种模式看起来"换数字"——其实换的是参考点。

为什么要有两种？`content-box` 是历史默认，padding 和 border 会在你声明的宽度上"额外加价"，算栅格时容易溢出；`border-box` 让"我声明多宽就占多宽"，把 padding 和 border 从外面挪到里面消化，更适合按列算尺寸。所以很多项目会把 `*, *::before, *::after { box-sizing: border-box }` 设为全局默认。

注意 border-box 不是"内容宽也是 300px"——恰恰相反，内容宽被 padding 和 border 吃掉了。

### 3. 垂直 margin 折叠：相邻兄弟取较大值

看两个上下相邻的块：

```css
.a { margin-bottom: 30px; }
.b { margin-top: 20px; }
```

它们的间距是 `30px`，不是 `50px`——两个垂直 margin 相遇时会**折叠**成一个，取较大的那个。max(30, 20) = 30。

为什么会折叠？因为垂直 margin 表达的是"两段内容之间要呼吸"，两个相邻的呼吸叠在一起会浪费空间。浏览器把它理解成"这一段间距至少要有多少"，于是取最大值而不是相加。这正好呼应第 1 步：margin 是关系，不是实体，所以它可以重叠。

边界要说清：折叠只发生在**垂直方向**、**正常流的块级盒之间**。水平 margin 从不折叠；flex 或 grid 子项之间的 margin 也不折叠——它们各有各的布局规则。父子之间的垂直 margin 也会折叠，那是第 06 篇"格式化上下文"要处理的事。

### 4. min-width: auto 让 flex/grid 子项撑破容器

普通块级元素的 `min-width` 初始值是 `auto`，但浏览器把它当 `0` 用——所以你能把块压到很窄。flex 和 grid 的子项不一样：它们的 `auto` 会解析成**基于内容的最小尺寸**，也就是内容再挤也不能小于的宽度（比如一个不换行的长单词、一张固定宽的图片）。

```css
.row  { display: flex; width: 300px; }
.item { flex: 1; }  /* 内容是一串不换行的长文本 */
```

你以为三项均分，实际长文本那项把容器撑破了，出现横向溢出。原因是 `min-width: auto` 挡住了收缩：`flex: 1` 想把它压到 100px，内容说"我最少要 200px"，auto 选了后者。

为什么浏览器默认这样？因为把内容压到看不清比溢出更糟——这是保护性默认。要让它按你的意愿收缩，得显式解除保护：

```css
.item { flex: 1; min-width: 0; }
```

`min-width: 0` 把"内容最小尺寸"改成 `0`，子项就能真正均分了；代价是内容可能被截断或溢出，需要配合 `overflow` 或省略号处理。

grid 子项踩的是同一个坑：`grid-template-columns: repeat(3, 1fr)` 遇到长内容时，那一列会突破 `1fr` 的均分。解法写成 `repeat(3, minmax(0, 1fr))`，本质也是把最小尺寸从 `auto` 改成 `0`。

## 动手验证

:::demo 05-box-model|调 padding 和 border，实时算占位宽度
先预测：`width: 300px` 固定，把 padding 从 `0` 调到 `20px`、border 从 `0` 调到 `5px`，content-box 与 border-box 下的"内容宽"和"占位宽"分别变成多少？先把两组数字写下来。
验证：打开 demo，拖动 padding 和 border 两个滑块，页面显示当前生效的 CSS 和实时读数——content-box 占位 = `300 + 2×padding + 2×border`，border-box 内容 = `300 - 2×padding - 2×border`。对照你写下的数字核对。
:::

demo 的重点不是背公式，而是建立一个动作：**看到 `width`，先问一句"这是描述哪一层"，再决定要不要加 padding 和 border。** 如果调滑块时 border-box 那栏的"占位宽"始终是 `300px`，说明你已经抓住了关键；变的只是里面的内容宽。

## 容易误判的地方

- **"`width: 300px` 就是占 300px 宽"** → 只在 `border-box` 下成立；默认 `content-box` 下还要加 padding 和 border，本例是 `350px`。margin 无论哪种模式都要另加。
- **"`box-sizing: border-box` 让内容宽也是 300px"** → 反过来：总宽锁在 `300px`，内容被 padding 和 border 吃掉，本例只剩 `250px`。
- **"`flex: 1` 一定等宽"** → 不一定。`min-width: auto` 会阻止子项收缩到内容最小尺寸以下，长内容会撑破均分；要加 `min-width: 0`。

## 自己再做一次

1. 写 `.b { width: 300px; padding: 20px; border: 5px solid; }`，先用默认 `content-box`，再改 `border-box`。**预期结果：默认下 `getBoundingClientRect().width` 为 `350px`；改成 border-box 后为 `300px`，且内容宽为 `250px`。**
2. 写两个相邻 div：上 `margin-bottom: 30px`、下 `margin-top: 20px`，量两者间距；再给它们套 `display: flex` 的父容器。**预期结果：正常流下间距 `30px`；放进 flex 容器后间距变成 `50px`（flex 子项间 margin 不折叠）。**
3. 写 `display: flex; width: 300px` 的容器，里面三个各含长不换行文本的 `flex: 1` 子项。**预期结果：子项宽度不均、容器溢出；给子项加 `min-width: 0` 后预期结果：三项各约 `100px`，恢复均分。**

> 下一篇：[百分比是谁的百分比](06-containing-block.md)
