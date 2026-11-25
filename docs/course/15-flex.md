# 15 · 一维空间怎么分

> **前置**：会用第 05 篇的盒子尺寸计算，尤其是 `min-width: auto` 如何撑破 flex 子项；知道第 04 篇的"指定值 / 计算值"区别。
>
> 上一篇：[状态的变化](14-animation.md) ｜ [本阶段目录](README.md)

## 1. 本章目标

- 给定容器宽度、gap、每项 basis 与 grow 系数，能按四步算出每项最终像素，误差为 0。
- 能解释 `flex: 2` 与 `flex-grow: 2` 为什么结果不同，并说出两者展开后的 basis 分别是什么。
- 能区分主轴与交叉轴，判断 `justify-content`、`align-items`、`align-content` 各自管哪一轴、何时生效。
- 能诊断长 URL 把 flex 子项撑破的原因，并用 `min-width: 0` 配合换行策略修复。

**为什么现在学这个**：第 05 篇算出单个盒子占多大，但一排盒子怎么分摊容器宽度还没解决。Flex 是"一维空间分配"：basis → 剩余空间 → 系数分配 → min-size 拦截。第 16 篇的 Grid 会把同一套思路搬到二维。

## 2. 新增模型

三张卡片，第一张写 `flex: 2`，另两张写 `flex: 1`：

```css
.row { display: flex; gap: 16px; width: 600px; }
.row > :first-child { flex: 2; }
.row > :nth-child(n+2) { flex: 1; }
```

你以为宽度是 2:1:1，实际量出来第一张往往没到两倍。原因藏在简写里：`flex: 2` 展开是 `2 1 0%`，`flex: 1` 是 `1 1 0%`，basis 都是 0，按 2:1:1 分没问题；但如果你写的是 `flex-grow: 2`，basis 仍是 `auto`——每项先按内容占好位置，再分配剩下的空间，结果自然不是 2:1:1。

**模型：Flex 不是"自动排列"，而是先给每项一个基准尺寸，算出剩余空间，再按系数分配，最后被最小尺寸拦截。对齐只是分配之后的附加动作。**

![Flex 的空间分配四步](figures/15-flex.svg)

*图 15-1 · Flex 的空间分配四步*

上图先分清两条轴：主轴决定空间往哪个方向流，交叉轴决定对齐方向。下图用数字走一遍：容器 600px，三项 basis 各 100px 共 300px，两处 gap 共 32px，剩余 `600 − 300 − 32 = 268px`；按 grow 2:1:1 分成 `134 / 67 / 67`，最终三项为 `234 / 167 / 167px`。最后一步的 min-size 是很多"算对了却不对"的原因。

**这张图的一句话结论：最终宽度 = basis + 分到的剩余空间，而"剩余"是扣掉所有 basis 与 gap 之后才有的。**

术语落地：

- **主轴**：`flex-direction` 指定的方向，空间沿它分配；`row` 时是水平方向。
- **交叉轴**：永远与主轴垂直，负责对齐而非分配。
- **basis**：分配开始前每项在主轴上的尺寸，由 `flex-basis` 决定。
- **剩余空间**：容器主轴尺寸减去所有 basis 与 gap 后剩下的部分，是 grow 真正分配的对象。

## 3. 可运行的 demo

先预测第一项的像素，再带着"剩余空间从哪来"读四步规则。

[打开 demo：拖动容器宽度，看每一项实际分到多少](../../examples/minimal/15-flex-space.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/15-flex-space.html" title="拖动容器宽度，看每一项实际分到多少" loading="lazy"></iframe>

> **先预测**：容器 600px、gap 16px、三项 basis 各 100px、grow 为 2:1:1 时，第一项最终多少 px？
>
> **验证**：打开 demo 把容器拖到 600px，用页面显示的实测宽度核对——答案是 234px，demo 同时列出 basis 合计、剩余空间与每项的增量。

demo 会把每项实测像素和计算式一起显示。拖动滑块时重点观察：剩余空间怎么变、每项的增量比例是否保持 2:1:1、什么时候 min-size 开始拦截。

## 4. 原理与规则

### 4.1 定方向：主轴与交叉轴

`flex-direction: row` 时主轴是水平方向，`column` 时主轴是垂直方向；交叉轴永远与主轴垂直。`justify-content` 只管主轴，`align-items` 只管交叉轴——记混了就会调错属性。

一个常见误区是给单行 Flex 写 `align-content`：它只在换行产生多行后才起作用。单行要垂直居中就用 `align-items`，多行要整体分布才用 `align-content`。

**失效条件**：`flex-direction: column` 时所有"宽高"角色互换——主轴尺寸是高度，`flex-basis` 管的是高度，`min-width: auto` 换成 `min-height: auto`；按 `row` 的直觉写会调错轴。

### 4.2 定基准：flex-basis 优先于 width

`flex-basis` 是**分配开始前**每项在主轴上的尺寸。在 `row` 方向它优先于 `width`；`auto` 表示先看 `width`，再看内容尺寸。

```css
.item { flex: 1 1 100px; }  /* basis = 100px */
```

三个常用简写必须记住展开式：`flex: 1` 等价于 `1 1 0%`，`flex: none` 等价于 `0 0 auto`，`flex: auto` 等价于 `1 1 auto`。写简写时把 basis 想清楚，比背口诀有用：`flex: 1` 让每项从同一起点分配，`flex-grow: 1` 则让每项先按内容占位再分剩余，两者结果不同。

**失效条件**：`flex-basis: auto` 且未设 `width` 时，basis 取内容尺寸，内容越长起点越大，最终比例不会按 grow 走；`box-sizing: border-box` 下 `width` 含 padding 与 border，与 basis 换算时要保持同一把尺子（第 05 篇）。

### 4.3 算剩余，按系数分

计算有严格顺序：

```text
剩余空间 = 容器主轴尺寸 − 所有 basis 之和 − 所有 gap
```

拿图里的数字走一遍：容器 600px，两项 gap 共 32px，三个 basis 各 100px 共 300px，剩余 `600 − 32 − 300 = 268px`。grow 为 2:1:1，按四份分：`134 / 67 / 67`，最终每项 `100 + 134 = 234px`、`100 + 67 = 167px`、`100 + 67 = 167px`。

空间不足时 `flex-shrink` 按"系数 × basis"加权收缩，不是简单按系数平分——items 基准越大，承担的收缩越多。收缩后的尺寸可以算成 `basis − 短缺 × (系数 × basis) ÷ Σ(系数 × basis)`；`flex-shrink: 0` 的项完全不参与收缩。

**失效条件**：当 shrink 系数全为 0 时空间不足会直接溢出容器；`min-size` 不为 0 时，按系数算出的收缩量可能把某项压到下限之下，那一项会停在 min-size 而让其他项承担更多（4.4）。

### 4.4 被最小尺寸拦截

Flex 子项默认 `min-width: auto`（`column` 方向是 `min-height: auto`），意思是"别比我内容的最小尺寸还窄"。长 URL、长单词会卡在这一步，让前面的计算全部失效：

```css
.row > .url {
  min-width: 0;             /* 允许收缩到内容最小尺寸以下 */
  overflow-wrap: anywhere;  /* 再给文本一个可断行的出路 */
}
```

**为什么不是默认就让它收缩？** 因为默认行为优先保护内容不被裁掉；你需要主动声明"这里允许截断"。`min-width: 0` 只解除下限，文本能否断行还要靠 `overflow-wrap` 或 `overflow: hidden` 配合，否则内容仍可能溢出到项外。

**失效条件**：只加 `min-width: 0` 而不给文本断行出路时，长串仍会溢出容器；`column` 方向要写 `min-height: 0` 而不是 `min-width: 0`，写错轴等于没改。

## 5. 常见坑

**坑 1：`flex: 1` 与 `flex-grow: 1` 结果不一样**

- **原因**：前者 basis 是 0，后者 basis 是 auto；起点不同，分到的剩余空间自然不同。
- **确认**：在 DevTools 的 Flexbox 面板看每项的 `flex-basis`，0 与 auto 一眼可辨。
- **修法**：要等分就写 `flex: 1` 或 `flex: 1 1 0`；要保留内容宽度再分配就明确写 `flex-grow` 并接受结果。

**坑 2：设了 `width` 却被压扁，"固定宽度"失效**

- **原因**：basis 为 0 或 auto 时，`width` 只是起点，最终尺寸由剩余空间分配决定。
- **确认**：看 Computed 里的实际宽度与声明的 `width` 是否一致。
- **修法**：要固定就写 `flex: none`（`0 0 auto`）；需要下限就用 `flex: 0 0 100px` 或 `min-width`。

**坑 3：含长 URL 的卡片明显更宽，容器被撑破**

- **原因**：`min-width: auto` 解析为内容最小尺寸，把下限顶高，`flex` 压不下去。
- **确认**：给子项临时加 `outline`，看它是否被内容撑开而非按份额分配。
- **修法**：子项加 `min-width: 0`，文本配 `overflow-wrap: anywhere`；代价是内容可能被截断。

**坑 4：给单行 Flex 写 `align-content`，垂直居中不生效**

- **原因**：`align-content` 只在换行产生多行后分配行间空间，单行时没有多行可分配。
- **确认**：看 Computed 里 `align-content` 虽然生效，但元素位置没变。
- **修法**：单行用 `align-items: center`；确实需要多行分布时先设 `flex-wrap: wrap`。

## 6. 练习

1. **基础**：三个子项 basis 均为 0，grow 为 1:2:3，容器 600px、无 gap。
   验收：三项为 100 / 200 / 300px，总和 600px。

2. **基础**：把上题改成 basis 各 100px、grow 为 1:2:3，容器 600px、无 gap。
   验收：先各扣 100px，剩余 300px 按 1:2:3 分得 50 / 100 / 150，总计 150 / 200 / 250px。

3. **进阶**：容器 600px、gap 16px、三项 basis 各 100px、grow 为 2:1:1。
   验收：剩余 `600 − 32 − 300 = 268px`，三项为 234 / 167 / 167px，与 demo 实测一致。

4. **进阶**：一个很长的 URL 子项设 `flex: 1 1 0`，容器缩到 300px，先观察溢出再加 `min-width: 0` 与 `overflow-wrap: anywhere`。
   验收：加之前 URL 撑破容器（`scrollWidth > clientWidth`）；加之后子项收缩、文本断行，溢出消失。

5. **进阶**：同一组三项分别用 `flex: 1` 与 `flex-grow: 1`，内容宽度各不相同。
   验收：`flex: 1` 下三项等宽；`flex-grow: 1` 下三项不等宽，且 DevTools 显示后者的 basis 为 auto。

6. **挑战**：`flex-direction: column`、容器高 400px、三项 `flex-basis: 80px`、grow 为 1:1:2、无 gap。
   验收：剩余 `400 − 240 = 160px`，按 1:1:2 分得 40 / 40 / 80，三项高 120 / 120 / 160px；若某项是长单词且未设 `min-height: 0`，它会顶高下限导致分配失效。

> 下一篇：[二维空间怎么画](16-grid.md)
