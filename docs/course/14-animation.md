# 14 · 状态的变化

> 一句话模型：元素的"变化"不是属性自己动了，而是浏览器在两个计算值之间补出中间帧——`transition` 靠事件给出前后两个状态，`animation` 靠 `@keyframes` 写出整条时间轴；补出的值在层叠里占着固定席位，不是任何声明都盖得住。

## 先看一个现象

一段文字配一个循环动画，颜色本该在深灰和琥珀之间来回变：

```css
.box { color: #23291e; animation: recolor 2s infinite alternate; }
@keyframes recolor { to { color: #c47f17; } }
```

给 `.box` 补一句 `color: #23291e !important`，动画突然"坏了"，文字恒定深灰。可 `!important` 不是号称最强吗？

再看另一边：

```css
.box { background: #f7f8f4; transition: background-color 300ms linear; }
.box.dark { background: #23291e !important; }
```

切换 `.dark` 的 300ms 里，你看到的是一层层插值出来的灰，而不是那条 `!important` 声明的深灰——过渡结束后才稳定在深灰。

你以为：加 `!important` 就一定能压住"动起来"的效果。实际：动画和过渡都不是普通声明，它们在层叠里有自己的席位，一个在重要声明之下，一个在所有重要声明之上。

## 先建立直觉

![状态变化的时间轴与层叠席位](figures/14-animation.svg)

*图 14-1 · 状态变化的时间轴与层叠席位*

图上半是一条 transition 时间轴：事件发生时，浏览器已经算出变化前的计算值 A，变化后得到 B，在 duration 内用 timing-function 把"时间进度"映射成"值进度"，补出一串中间值；delay 只是让元素先停在 A。图下半是层叠席位：过渡值最高，重要声明居中，动画值夹在普通作者声明和重要声明之间。看图时只问一句：当前这一帧的值，来自静态声明，还是插值？

这张图的关键不是记住动画属性，而是接受一件事：**插值产生的值也是参与层叠的值**，只是它的位置由机制规定，不能靠书写顺序挪动。

## 机制拆成四步

### 1. 先有两帧，才谈插值

"插值"就是浏览器在两个值之间算出中间值。过渡需要同时满足三个条件：

- 属性在两端都是**可插值类型**：长度、数值、颜色、`transform` 之类可以；`display: none` 到 `block`、结构差异大的关键字传统上不行。
- 有一个**触发事件**让计算值从 A 变成 B，比如 `:hover`、类名切换、媒体查询命中。
- `transition-duration` 大于 `0s`，且属性被列进 `transition-property`。

```css
.button {
  transition: background-color 180ms ease-out; /* 写在基础状态 */
}
.button:hover { background-color: #315b24; }
```

**为什么 transition 要写在基础状态，而不是只写在 `:hover` 里？** 因为鼠标移出时也要从 B 回到 A，那时命中的是基础规则。写在基础状态，进入和离开共用同一组参数；只写在 hover 里，离开往往瞬间跳回。

页面首次加载时元素直接以某状态出现、或元素处于 `display: none`，都没有"变化前的已计算样式"，通常不会触发过渡。**`@starting-style` 就是给"首次出现"补一个起点**，让刚显示的弹层也有可插值的第一帧。

### 2. `@keyframes` 自己写出时间轴

动画不需要事件。它把一段时间切成若干关键帧，浏览器在帧与帧之间插值：

```css
.dot { animation: pulse 900ms ease-in-out infinite; }
@keyframes pulse {
  0%   { opacity: 0.55; scale: 0.98; }
  50%  { opacity: 1;    scale: 1.02; }
  100% { opacity: 0.55; scale: 0.98; }
}
```

未写出的 `0%` / `100%` 会用元素在"没有这条动画时"的计算值，也就是 underlying style。**为什么这点重要？** 它意味着动画的起点不一定是 `0`，而可能是你平时写的那条样式。

`animation-fill-mode` 决定时间轴之外的两帧：

| 取值 | 延迟期间 | 结束后 |
| --- | --- | --- |
| `none` | 用元素本身的值 | 用元素本身的值 |
| `backwards` | 用第一帧 | 用元素本身的值 |
| `forwards` | 用元素本身的值 | 保留最后一帧 |
| `both` | 用第一帧 | 保留最后一帧 |

**为什么不能把 `forwards` 理解成"永久固定最终值"？** 它只在动画仍然应用时保留结果；一旦移除动画或元素被隐藏，样式会回到 underlying value。最终状态要长期存在，应该写进基础样式，而不是靠填充模式。

滚动进度条这类"进度由滚动位置决定"的动画，换的不是时钟而是时间轴，属于另一套机制，见[第 27 篇](27-modern-features.md)。

### 3. 插值的值在层叠里的位置

这里只借用[第 03 篇](03-cascade.md)的结论，不重复整张表：从低到高大致是"普通作者声明 → CSS 动画 → 作者 `!important` → … → CSS 过渡"。

于是开头的现象有了统一解释：

- 动画值高于普通作者声明，所以能盖掉 `.box { color: #23291e }`，把文字染成琥珀。
- 作者 `!important` 高于动画值，所以补上 `!important` 后动画被压住，文字恒定深灰。
- 过渡值高于**所有**重要声明，所以那条 `background: #23291e !important` 在过渡期间压不住插值出来的中间灰。

**为什么过渡被排到最高？** 它表达的是用户对"当前这一帧"的即时期望；动画则只是样式来源之一，用户用重要声明表达的辅助需求理应能盖过它。理解了席位，判断"为什么不动"就多了一个固定动作：先看这一帧的值来自静态声明还是插值。

### 4. 是否应该动，也是机制的一部分

`prefers-reduced-motion` 是用户偏好，不是设备性能检测。尊重它不等于把所有时长改成 `0.01ms`——大幅位移和缩放仍可能引起不适。正确做法是关掉装饰运动、把反馈运动改为即时切换、让状态揭示直接呈现最终结果，同时保留状态反馈本身。

```css
@media (prefers-reduced-motion: reduce) {
  .dot { animation: none; }
  .button { transition-duration: 0.01ms; }
}
```

## 动手验证

[打开 demo：把 duration 调到 0，看插值怎么消失](../../examples/minimal/14-animation.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/14-animation.html" title="把 duration 调到 0，看插值怎么消失" loading="lazy"></iframe>

> **先预测**：一个方块从浅色过渡到深色，`transition-duration` 为 300ms 时中途出现灰；把它拖到 0s 再切换，方块会渐变还是瞬间跳变？写下答案再揭晓。
>
> **验证**：打开 demo 调节参数，用页面显示的实时读数核对你的预测。

验证：打开 demo，拖动 duration 滑块（0–600ms），点开关切换状态，对照状态文本里显示的当前计算值和过渡进度。重点看 duration 为 0 时中间帧是否还存在。

## 容易误判的地方

- **"可动画的属性都值得动画"** → `width`、`height` 每帧可能触发布局；能用 `transform` / `opacity` 表达同样视觉变化时优先用它们。
- **"`animation-delay: -1s` 是提前结束"** → 负延迟让动画立刻从迭代中对应位置开始播放，总时长不变。
- **"reduce 模式下功能也要慢慢演完"** → 减少的是运动，不是功能；直接呈现最终状态同样可用。

## 自己再做一次

1. `.box { background: #fff; transition: background-color 300ms linear; }`，`.box.on { background: #000; }`。切换 `.on` 后第 150ms 读取计算值。**预期结果：约 `rgb(128, 128, 128)`**，线性插值在中点取黑白中点，而不是黑色。
2. `@keyframes fade { from { opacity: 0 } to { opacity: 1 } }`，`.el { animation: fade 400ms both; animation-delay: 200ms; }`。**预期结果：延迟的 200ms 内 `opacity` 为 0**（`both` 提供 backwards）；把 `both` 去掉则延迟期间显示元素原值 1。
3. `.el { color: red; animation: recolor 1s infinite; }`，关键帧把颜色设为 blue，再加一条 `.el { color: red !important; }`。**预期结果：加之前动画期间显示蓝色（动画压过普通声明），加之后始终红色（作者 `!important` 压过动画）；两条都不影响过渡席位最高的结论。**

> 下一篇：[一维空间怎么分](15-flex.md)
