# 29 · 分栏、绕行与叠色，各管一层

> 一句话模型：多列改的是内容流如何分配，形状改的是行盒避让的区域，混合改的是颜色合成的边界，遮罩与裁剪决定哪些像素留下——四件事作用于四个不同对象，认错对象就白写。

## 先看一个现象

同一段带图片的排版：你给图片写了 `border-radius: 50%`，图片变圆了，旁边的文字却还按矩形留白；你把卡片标题设成 `mix-blend-mode: multiply`，标题在深色页面上一会儿发灰、一会儿看不见；你想给图片做渐隐边缘，写了 `clip-path: linear-gradient(...)`，浏览器直接忽略。

你以为这些都在"改外观"；实际它们管的不是同一个东西：图片轮廓、文字避让区、颜色合成组、像素可见集合，是四层不同的对象。用错属性，不是效果弱，是根本没作用在你以为的地方。

## 先建立直觉

:::figure 29-shapes-mix|混合隔离剖面：颜色在哪一层合成
图说明：一张剖面图——最外是页面背景，卡片根部标 `isolation: isolate`，画成一道边界；边界内依次是卡片背景、设置了 `mix-blend-mode: multiply` 的图片、卡片文字。箭头显示图片只与边界内的卡片背景混合，边界外的页面背景被挡住；只有去掉 `isolation`，图片才会把页面背景当作 backdrop 卷进来。读者应当看出：`mix-blend-mode` 决定算法，`isolation` 决定算法的作用范围。
:::

图要记住的一句话：`isolation: isolate` 自己不混色，它只画一条线，决定混色发生在哪一组里。

## 机制拆成四步

### 1. 多列是把内容倒进栏里，Grid 是把项目摆进格子

```css
.article {
  columns: 18rem 3;         /* 理想栏宽 18rem，最多 3 栏 */
  column-gap: 2rem;
  column-rule: 1px solid #d8d3c5;
}
.article > h2 { column-span: all; }  /* 标题跨全部栏，不能写 span 2 */
```

`column-count` 是上限，`column-width` 是算法输入，实际栏数由容器宽度算出来。**为什么这不是 Grid？** 多列里内容是一条连续的流：先填满第一栏再进第二栏，浏览器自动平衡栏高，DOM 顺序不变；Grid 是你显式把每个项目放进命名的行和列。要"卡片各自对齐"就选 Grid，要"一段长文自动分栏"才选多列。

| 你要做的事 | 选谁 | 判断依据 |
| --- | --- | --- |
| 一段长文均匀分栏、栏高自动平衡 | 多列 | 内容是连续流，断点由浏览器决定 |
| 每个卡片占据指定行与列 | Grid | 位置是你显式指定的 |
| 标题横跨所有栏 | 多列 + `column-span: all` | 仍留在同一条内容流里 |

栏线画在 `column-gap` 之内，不额外吃宽度；`break-inside: avoid` 在多列里同样能减少引文被栏边界切开。窄屏时把 `column-count` 当上限，让宽度自己降栏，必要时回到单栏——别把 3 写死后让每行只剩几个字。

`column-fill` 默认 `balance`，自动高度下各栏高度接近；只有容器高度固定时 `auto` 才会明显地按顺序填满第一栏再下一栏。把它当成"控制阅读顺序"的开关是误解——DOM 顺序始终不变，变的只是内容在哪一栏结束。

### 2. shape-outside 改的是文字的避让区，不是图片轮廓

```css
.portrait {
  float: left;
  inline-size: 12rem;
  aspect-ratio: 1;
  border-radius: 50%;                   /* 画成圆的 */
  shape-outside: circle(50% at 50% 50%); /* 文字按圆绕开 */
  shape-margin: 0.75rem;                /* 避让区外再留一圈 */
}
```

普通浮动让行盒避开元素的矩形外框，所以圆形图片周围仍是方角留白。`shape-outside` 在浮动元素之外重新定义避让区，行盒沿这个形状排列。

**为什么必须写 `float`？** `shape-outside` 作用于浮动元素；没有浮动就没有需要绕开的区域，属性写了也不会让文字回流。它也**不裁剪元素本身**——想让图片真的变圆，要靠 `border-radius` 或 `clip-path`，两者用同一几何才对齐。图片轮廓来自带 alpha 的 PNG 时，可用 `shape-outside: url(...)` 配 `shape-image-threshold: 0.3`（alpha 大于或等于阈值的像素算进形状）；阈值只对带透明信息的图片有意义，完全不透明的图不会被"抠"出形状。

`shape-image-threshold` 默认 0，此时带 alpha 的图所有像素（包括全透明像素）都算进形状，得到完整矩形；调到 1 只保留完全不透明像素，复杂边缘可能出现锯齿。`shape-margin` 是避让区外侧的额外留白，不是元素的 `margin`，也不负责清除浮动——收尾仍要靠容器的 `display: flow-root` 或 clearfix。

### 3. 混合先找边界，再谈模式

```css
.card {
  isolation: isolate;   /* 画一条混合边界 */
  background: #fffdf7;
}
.card > img {
  mix-blend-mode: multiply; /* 与本组内的背景混合 */
}
.texture {
  background-image:
    linear-gradient(#3f6b2a55, transparent),
    url("./grain.png");
  background-blend-mode: multiply, multiply; /* 只混自己的背景层 */
}
```

`mix-blend-mode` 把元素像素与它背后的画面混合；`background-blend-mode` 只混同一个元素的背景层与背景色，不碰后代。`isolation: isolate` 自身不混色，它创建层叠上下文和隔离组，让组内元素不再与组外的页面背景混合。

**为什么去掉 isolation 后颜色会"随页面变"？** 没有边界时，元素的 backdrop 一直向上找到页面背景；把卡片放进深色区块就换了一个 backdrop。加上隔离组，外部只看到合成后的结果，卡片内部视觉稳定。

```text
无隔离：  页面背景 + 卡片背景 + 图片(乘) + 文字  ← 混色一直找到页面
有隔离：  页面背景 | [卡片背景 + 图片(乘) + 文字] ← 外部只看到合成结果
```

注意 `opacity < 1`、`filter`、`transform` 也会建立层叠上下文，可能意外切断混合；`z-index` 只管绘制先后，不定义混合边界。标题和正文保持默认的 `normal`，别跟着一起混。

### 4. mask 看 alpha，clip-path 看几何

```css
/* 硬边：几何裁剪 */
.geo { clip-path: inset(0 40% 0 0); }
/* 软边：alpha 遮罩 */
.fade { mask-image: linear-gradient(90deg, #000 60%, transparent); }
```

`clip-path` 用几何路径判定内外：路径外的像素被丢弃，边缘是硬切，而且被裁掉的区域不再接收点击——它真的改变了元素的命中区域。`mask` 用遮罩图或渐变的 alpha 调制可见度：alpha 为 0 的像素透明、0.5 的像素半透明，因此能做渐隐；被遮住的区域仍可接收点击。

**为什么不能互换？** 你要"从右往左淡出"就需要连续的 alpha，`clip-path` 只有边界内外两种状态；你要"精确切掉左侧 40%、并让该处点击穿透"就该用 `clip-path`，`mask` 不会改变命中测试。两者都可和 `shape-outside` 同时出现，但记住：遮罩与裁剪管的是元素被看见的部分，`shape-outside` 管的是文字绕行的部分。

`mask` 默认按 alpha 读遮罩；`mask-mode: luminance` 改按亮度读，白色保留、黑色透明，适合复用灰度图。写成简写 `mask` 时还会带上 `mask-size` / `mask-position` / `mask-repeat`，它们决定遮罩图怎么铺到元素上——这部分和 `background-*` 的铺贴逻辑相近。

## 动手验证

:::demo 29-shapes-mix|切换 isolation，看图片跟谁混色
先预测：图片设了 `mix-blend-mode: multiply`，卡片背景米色、页面背景深绿。关闭卡片上的 `isolation: isolate` 后，图片颜色会变吗？把模式从 `multiply` 换成 `screen` 呢？先写下答案。
验证：用开关切换隔离，用下拉选混合模式（normal / multiply / screen）。状态文本显示当前生效的 CSS、混合组边界（卡片 / 页面）与图片的合成结果描述；核对"边界变了才换 backdrop，模式变了才换算法"。
:::

## 容易误判的地方

- **"`columns: 3` 就是每栏 1/3 宽"** → 栏宽与栏数都是输入，实际栏数由容器宽度算出；窄屏应让它自己降栏。
- **"`shape-outside` 会把图片裁成那个形状"** → 它只改文字避让区；视觉轮廓要靠 `border-radius` / `clip-path` 同步。
- **"`mask` 和 `clip-path` 都能做渐隐"** → 只有 `mask` 读 alpha 能做软边；`clip-path` 是几何硬切，还会改变命中区域。

## 自己再做一次

1. 容器 1200px、`columns: 18rem 3`、`column-gap: 2rem`（根字号 16px），给 `h2` 加 `column-span: all`。**预期结果：1200px 下 3 栏（3×18rem + 2×2rem = 928px，放得下）；容器缩到 800px 变 2 栏，400px 变 1 栏；标题横跨全部栏，正文 DOM 顺序不变。**
2. 圆形图片只写 `border-radius: 50%`，让它浮动后观察文字，再补 `shape-outside: circle(50%)` 和 `shape-margin: 1rem`。**预期结果：只有 `border-radius` 时文字仍按矩形绕行；补上 `shape-outside` 后文字沿圆边走；`shape-margin` 让文字与圆边距离增加，而图片轮廓本身没被裁剪。**
3. 对同一张图分别应用 `clip-path: inset(0 40%)`、`mask-image: linear-gradient(90deg, #000 60%, transparent)`。**预期结果：前者在 60% 处出现硬边、被裁区域点击穿透到下层；后者从 60% 到 100% 渐变透明、被遮区域仍能点中图片。**

> 下一篇：[交互状态与组件边界](30-component-boundary.md)
