# 27 · 让浏览器替你算

> 一句话模型：锚点定位、滚动驱动动画、视图过渡都没有发明新画面，它们只是把原本 JS 每帧算坐标、算进度、算快照的活交还浏览器；用它们的前提是"基础状态独立可用 + 能力检测 + 明确回退"。

## 先看一个现象

给一个按钮加跟随提示框，传统写法是这样：

```js
function place() {
  const r = button.getBoundingClientRect();
  tip.style.top = `${r.bottom + 8}px`;
  tip.style.left = `${r.left}px`;
}
addEventListener('scroll', place);
addEventListener('resize', place);
```

你以为这只是"几行定位代码"；实际每次滚动都触发布局读取加样式写入，正好撞上第 25 篇说的强制同步布局。类似的事还在别处重演：阅读进度条靠 `scrollTop / (scrollHeight - clientHeight)` 算比例；卡片揭示靠 `IntersectionObserver` 加类；页面切换靠手写 FLIP 记录前后位置再倒推变换。

你以为是四个互不相干的效果，其实是同一个问题：**谁在每一帧做计算**。新平台把这几件事交给了浏览器——你只声明关系，进度和快照由引擎算。

## 先建立直觉

![把时间轴的驱动源换掉](figures/27-modern-features.svg)

*图 27-1 · 把时间轴的驱动源换掉*

图上两条时间轴共享同一组 `@keyframes`。上面那条是传统动画：横轴是墙钟时间，从 0 走到 duration，进度匀速增加；下面那条是 `animation-timeline: scroll()`：横轴换成滚动位置，从容器顶部走到底部，进度由当前滚动量决定。两条轴之间有一条虚线箭头，标注"换掉驱动源，不换动画代码"。读者应当看出：卡片还是那段淡入，只是"什么时候算哪一帧"改由滚动说了算——停手就停，往回滚就倒放。

图里最关键的一条：**动画代码没变，变的只是进度从哪来**。锚点定位和视图过渡是同一招的变体：前者把坐标计算交给引擎，后者把快照交给引擎。

## 机制拆成四步

### 1. 锚点定位：把"跟着谁"写进 CSS

三个角色：被跟随的元素用 `anchor-name: --tip-anchor` 命名；浮层以 `position-anchor` 指向该名字，并且必须是 `absolute` 或 `fixed` 定位；再用 `position-area` 或 `anchor()` 真正摆放它。

```css
.tip {
  position: absolute;                  /* 基础定位，先写 */
  inset-block-start: calc(100% + 0.5rem);
}
@supports (anchor-name: --tip-anchor) {
  .tip {
    position: fixed;
    inset: auto;
    position-anchor: --tip-anchor;
    position-area: bottom span-right;
    margin-block-start: 0.5rem;
    position-try-fallbacks: flip-block, flip-inline;
  }
}
```

**为什么它能替掉那段 JS？** 按钮和浮层的几何关系被声明出来，浏览器在布局/合成时直接算，不再需要每帧读 `getBoundingClientRect()`。`anchor()` 返回锚点某条边对应的长度并可带兜底值；`@position-try --name { … }` 可封装一组候选位置，再由 `position-try-fallbacks` 按序尝试——按钮贴到视口边缘时翻到另一侧，是浏览器试出来的，不是你写的分支。

`anchor()` 取的是位置，`anchor-size()` 取的是尺寸——想让下拉与触发按钮等宽，写 `inline-size: anchor-size(width, 12rem)` 即可。**为什么尺寸也要纳入关联？** 过去这只能在 JS 里读 `offsetWidth` 再写回去，同样会在滚动时触发同步布局；交给引擎后，按钮尺寸一变浮层跟着变。

回退不能只靠 `anchor()` 的兜底值：它只是"函数无法解析时使用"的值，不是一套布局。基础 `position: absolute` 写在前面、增强包在 `@supports` 里；锚点名在一屏内要唯一，否则浮层可能绑到错误的元素。候选位置也不是无限重排引擎，浮层本身太大时仍放不下。

### 2. 滚动驱动动画：把时钟换成滚动进度

```css
.progress__bar {
  animation: grow linear both;          /* 简写先写 */
  animation-timeline: scroll(root block);
}
.reveal {
  animation: fade-up linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

`scroll()` 取滚动容器的位置（适合进度条），`view()` 取元素进入、离开 scrollport 的过程（适合揭示卡片），`animation-range` 把动画限制在某个阶段。**为什么"停手就停"不用额外写？** 因为进度来自滚动位置而不是时间，滚动一动进度才动；反向滚动自然倒放。这正好替掉 `scroll` 事件加 rAF 那套手算。

局部滚动容器还可以命名时间轴：

```css
.gallery { overflow-x: auto; scroll-timeline: --gallery x; }
.gallery__bar { animation: grow linear both; animation-timeline: --gallery; }
```

**为什么要命名？** `scroll(root block)` 只能指根滚动容器；横向画廊这类局部容器要先起名，进度条才知道该读谁的位置。命名时间轴与 `animation-range` 属于子特性，检测时不能只看 `animation-timeline` 这一个属性名。

没它时你要监听滚动、读 `scrollTop`、算比例、再写 `transform`；有它时只写上面几行。回退原则是：**基础状态必须完整可见**——先让进度条可见、卡片不透明，再用 `@supports (animation-timeline: view())` 把动画叠上去；不支持时删掉整段动画，内容不消失。若进度是关键功能，不支持时用 JS 兜底，而不是留一根静态满条误导用户。`animation` 简写会重置时间轴与范围，所以简写在先、时间轴在后。

### 3. 视图过渡：用快照桥接 DOM 变化

```js
if ('startViewTransition' in document) {
  document.startViewTransition(() => { title.textContent = '新标题'; });
} else {
  title.textContent = '新标题';        // 基础路径：内容立即更新
}
```

API 会捕获旧快照、执行 `update()`、捕获新状态，再用一组 `::view-transition-*` 伪元素播放过渡；`view-transition-name` 给需要共享位置的元素起唯一名字。伪元素树大致是 `::view-transition` → `::view-transition-group(root)` → `::view-transition-image-pair(root)`，下面再分 `::view-transition-old` 与 `::view-transition-new`。**为什么分成 old 和 new？** old 是静态旧快照、new 是新视图区域，两者交叠播放才形成"桥"；共享元素则各自多出一组同名伪元素。

**为什么它比 FLIP 省心？** FLIP 要你自己读 First、Last 两组几何再倒推变换；视图过渡直接拿两张快照做桥接，DOM 结构变了也能连起来。JS 只决定"什么时候变"，动画交给 CSS。

回退有两层：`"startViewTransition" in document` 为假时直接调用 `update()`，内容照常更新；开启减弱动画偏好时也应跳过动画而非硬播。同名元素必须唯一，否则 `ready` 会被拒绝、过渡被跳过——所以别把 `view-transition-name` 写死在列表的每一项上。跨文档导航还要双方页面都 opt-in，支持范围比这个 API 更窄。

### 4. 共同的边界：检测、回退，以及一条指针

| 特性 | 把什么交给了浏览器 | 检测入口 | 不支持时 |
| --- | --- | --- | --- |
| 锚点定位 | 浮层相对锚点的坐标与翻转 | `@supports (anchor-name: --a)` | 保留 `position: absolute` 基础定位 |
| 滚动驱动动画 | 每帧的进度值 | `@supports (animation-timeline: view())` | 基础状态可见，进度关键时用 JS |
| 视图过渡 | 前后两帧快照与插值 | `"startViewTransition" in document` | 直接执行 DOM 更新 |

**为什么必须逐个检测？** 这三者都有多个子特性：`position-area`、`@position-try`、`scroll()` / `view()`、`animation-range`、跨文档导航都可能处于不同支持阶段。`@supports` 与 `CSS.supports()` 只验证语法被接受，不保证行为完整；最终仍要在最小页面里看一次真实效果。想在更底层把绘制或布局也开放给 JS，是 Houdini 的方向，这里只留一个指针，不展开清单。

`prefers-reduced-motion` 对这三者同样适用：锚点浮层可以取消位移、滚动动画直接呈现终态、视图过渡把时长压到极短——减少的是运动，不是功能。

## 动手验证

[打开 demo：关掉原生能力，看谁还在算](../../examples/minimal/27-modern-features.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/27-modern-features.html" title="关掉原生能力，看谁还在算" loading="lazy"></iframe>

> **先预测**：一个跟随按钮的提示框，关掉锚点定位后它会掉回哪里？一个由滚动驱动的进度条，关掉时间轴后是保持可见还是消失？一个视图过渡，删掉 `startViewTransition` 后内容还会不会更新？写下来再揭晓。
>
> **验证**：打开 demo 调节参数，用页面显示的实时读数核对你的预测。

验证：打开 demo，用下拉在「锚点 / 滚动时间轴 / 视图过渡」之间选一个能力，再用「禁用原生能力」开关切到回退路径。状态栏显示检测结果、当前生效的 CSS 片段和内容可见性，用来核对你的预测。

demo 一次只看一个能力，两个参数。重点不是记住属性名，而是每次切换都能回答：**关掉之后，内容是否仍然可读、任务是否仍然可完成？** 只要答案是"是"，这项增强就接对了位置。

## 容易误判的地方

- **"`anchor()` 的兜底值就是降级方案"** → 它只是函数无法解析时的值；基础定位必须独立写在前面，`@position-try` 也解决不了浮层根本放不下的情况。
- **"不支持滚动动画就让元素保持 `opacity: 0`"** → 内容会直接消失；基础状态必须完整可见，动画是叠加层。
- **"视图过渡只写 CSS 就能触发"** → 同文档需要 `document.startViewTransition()`，跨文档还要双方 opt-in；同名元素重复时过渡会被跳过。

## 自己再做一次

1. 写一个跟随按钮的提示框：先用 `getBoundingClientRect()` 加 rAF 跟随，再用 `anchor-name` / `position-anchor` / `position-area` 重写。**预期结果**：滚动时两者都跟随，但原生版在 Performance 里没有每帧的 Layout 段；按钮滚到视口底部时，`position-try-fallbacks: flip-block` 让提示框翻到上方。
2. 给长页面加 `animation-timeline: scroll(root block)` 的进度条，基础状态写 `transform: scaleX(1)`，动画包进 `@supports`。**预期结果**：支持时进度随滚动从 0 到 1，停手即停；不支持时进度条保持可见的满格，内容不消失——若进度是关键信息，改用 JS 兜底，不留静态满格。
3. 用 `document.startViewTransition(() => { title.textContent = '新标题' })` 切换标题，并给标题加 `view-transition-name: demo-title`。**预期结果**：支持时旧标题淡出、新标题淡入且位置连续；把调用改成直接赋值时内容仍立即更新；给两个元素起同一个名字时过渡被跳过、内容直接切换。

> 下一篇：[打印样式](28-print.md)
