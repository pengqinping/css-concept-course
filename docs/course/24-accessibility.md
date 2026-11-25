# 24 · 页面是给谁用的

> 一句话模型：可访问性先问"语义对不对、键盘走不走得通"，再问"好不好看"；CSS 的职责是让焦点与状态始终可见、尊重用户的系统偏好与能力边界，并用 `@supports` 逐层增强，而不是猜浏览器。

## 先看一个现象

```css
.button { outline: none; color: #b9b9b9; }
.menu { display: none; }
.card:hover .menu { display: block; }
.spinner { animation: spin 800ms linear infinite; }
```

你以为这只是"把按钮做清爽、把菜单收起来"：鼠标用户点得动，页面看着也干净。实际：键盘用户 Tab 到按钮时看不到焦点，低视力用户读不动那行浅灰字，触屏用户永远打不开只在 `:hover` 出现的菜单，前庭敏感用户被旋转图标转得头晕，开了高对比度模式的用户看到按钮和背景合成同一种颜色。

这不是五个互不相干的 bug，而是同一个问题：**样式只照顾了"鼠标 + 正常视觉 + 默认系统 + 新版浏览器"这一条路径**。可访问性就是把这条路径之外的用户也接回来，而顺序不能反——先保证语义与键盘能完成任务，再来谈视觉。

## 先建立直觉

:::figure 24-accessibility|可访问性是一叠自下而上的依赖层
图里是一个四层台阶，从下到上依次是：语义与键盘（原生元素、地标、Tab 顺序）→ 可见的焦点与对比度 → 用户偏好（减弱动画、强制颜色）→ 能力增强（`@supports` 分层）。箭头向上表示"上一层只有在下一层成立时才有意义"。读者应当看出：最底下一层塌了，上面装饰得再漂亮也没人用得了；而最上一层永远是可拆的，拆掉后下面几层仍然可用。
:::

图里最关键的一条：**下面三层是底线，最上面一层才是增强**。把焦点环删掉却去调圆角，等于把地基拆了来装修屋顶。

## 机制拆成四步

### 1. 语义与键盘先成立，CSS 才登场

可访问性树里"这是个按钮、这是主导航、现在展开着"这些信息，来自 HTML 的标签与属性，不是来自 CSS 画得像不像。用 `<button>` 而不是 `<div onclick>`，用 `<nav>` / `<main>` / `<header>` 这些地标（landmark，即"导航区、主内容区"这类语义分区）而不是一排 `<div class="nav">`；链接用于导航，按钮用于执行动作。

**为什么 CSS 排不上这个班？** 屏幕阅读器和键盘只认语义与焦点顺序，不认 `border-radius`。一个画得再像按钮的 `div`，Tab 键会直接跳过它。地标也一样：给 `<div>` 补 `role="navigation"` 勉强能用，但不如直接写 `<nav>` 稳。

键盘顺序跟着 **DOM 顺序**走，不跟视觉位置走。用 `order`、`grid-area`、绝对定位把视觉重排之后，Tab 仍按 DOM 走，焦点会在页面上"乱跳"。所以视觉重排时要么同步 DOM 顺序，要么别把顺序改得面目全非。

键盘用户还需要一条绕过重复导航的路，这就是"跳到主要内容"链接：

```css
.skip-link { position: fixed; transform: translateY(-200%); }
.skip-link:focus { transform: translateY(0); }
```

**为什么平时藏起来、聚焦时才出现？** 它要跳过的是页头和导航，所以键盘用户按第一下 Tab 时它必须出现；对鼠标用户它又不能常驻占位置。注意它靠 `:focus` 显示而不是靠 `:hover`——后者对键盘用户等于不存在。

### 2. 焦点与对比度：CSS 真正要扛的两件事

不要写 `outline: none`。`:focus-visible` 不是为了取消焦点，而是为了**区分由谁来显示焦点环**：

```css
:focus { outline: 3px solid #0b63ce; outline-offset: 3px; }
@supports selector(:focus-visible) {
  .button:focus:not(:focus-visible) { outline: none; }
}
```

基础的 `:focus` 规则写在 `@supports` 外面，它在所有环境都有效；支持 `:focus-visible` 的环境里，鼠标点击不再显示环，键盘 Tab 仍由基础规则显示。**为什么不能把 `outline: none` 写在外面？** 那样在不支持该选择器的环境里，焦点就被彻底删掉了——增强只能用来"减掉鼠标的环"，不能用来"拿走键盘的环"。

对比度的数值门槛第 10 篇已经算过，这里不重复表，只补一条推理：**门槛要按"最终合成后的颜色"算，不是按你写下的色值算**。`opacity: 0.6` 的禁用态、半透明遮罩、悬停时的插值、渐变上最不利的那一小段底色，都会改变最终对比度。而且不要用颜色单独表达错误、选中或必填——配上文字、图标或 ARIA 状态，颜色丢了信息还在。

焦点环本身也会被 CSS 吃掉：父级 `overflow: hidden` 会把 `outline-offset` 挪出边界的那几像素裁掉；用 `opacity: 0` 藏起来的控件仍可被 Tab 聚焦，于是焦点走到一个看不见的目标上。这两处都不是"焦点样式不够粗"，而是**焦点存在但看不见**，调试时要按"键盘走到哪一步看不见了"定位，而不是去加粗边框。

### 3. 用户偏好是输入，不是装饰

`prefers-reduced-motion` 和 `forced-colors` 表达的是用户环境，不是"给我一个特效开关"：

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .spinner { animation: none; }
}

@media (forced-colors: active) {
  .button {
    border: 1px solid ButtonText;
    color: ButtonText;
    background: ButtonFace;
  }
}
```

减少动态要关掉的是**非必要运动**，不是把所有状态一起抹掉：加载指示器换成静态文字或进度条，反馈仍在，只是不转了。**为什么强制颜色下要改用系统色？** 该模式会用 `Canvas`、`CanvasText`、`ButtonFace`、`ButtonText` 等系统色覆盖作者颜色，并忽略背景图和阴影。用 `box-shadow` 画的焦点环在这里可能整圈消失，所以焦点优先用 `outline`；边框与文字也要能独立表达边界，不能只靠背景色区分状态。

### 4. 能力差异靠特性检测，不靠浏览器名字

渐进增强的顺序永远是"基础可用在前，增强在后"：

```css
.cards { display: flex; flex-wrap: wrap; gap: 1rem; }
@supports (display: grid) {
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  }
}
```

Flex 版本在所有目标环境都成立，Grid 版本只给认识它的浏览器。**为什么要检测特性而不是检测浏览器？** 浏览器版本回答不了"这条语法到底支不支持"：同一个版本的 WebView 可能落后好几个版本，新版本也可能只在部分语法上完整实现。`@supports` 问的是"你认不认这条声明"，`CSS.supports()` 是同一件事的 JS 版本；两者问的都不是"你是哪个浏览器、哪个版本"。

需要脚本控制交互时，用同一套推理的 JS 版本，并保证无脚本时核心内容仍可用：

```js
if (CSS.supports('selector(:focus-visible)')) {
  document.documentElement.classList.add('has-focus-visible');
}
```

**为什么加类名而不直接改样式？** 类名只是给 CSS 多一个可判定的条件，最终样式仍写在 stylesheet 里，视觉样式不会散落到 JS 中；没有脚本执行时，基础规则照常成立。

但要清醒：`@supports` 只证明**语法被解析**，不证明行为完整。所以增强永远写成"叠加上去"，基础状态独立成立；绝不能把取消焦点、隐藏内容、固定高度这类动作放进增强分支。

## 动手验证

:::demo 24-accessibility|删掉 outline 之后，谁还能完成任务
先预测：一个按钮同时删掉 `outline`、把菜单改成只在 `:hover` 出现、给文字加 `opacity: 0.6`。只用键盘、不碰鼠标，你还能"看到焦点"和"打开菜单"吗？把答案写下来再揭晓。
验证：打开 demo，先用 Tab 走一遍，再切换「减弱动画」「强制颜色」两个开关。状态栏显示当前匹配的用户偏好、焦点是否可见、以及每项检查通过还是失败，用来核对预测。
:::

demo 只暴露两个开关，对应"用户偏好"这一层。交付前把同一页再走三遍，这三遍比任何自动扫描都管用：

1. **键盘走一遍**：地址栏后按 Tab，确认焦点顺序合理、焦点环始终可见、没有 Tab 得到却看不见的元素；Shift+Tab 反向再走一次。
2. **缩放 200%**：文字与按钮不裁切、不重叠，页面不出现不必要的横向滚动。
3. **强制颜色**：开启系统的高对比度/强制颜色模式，确认边界与状态仍可辨，背景图和阴影消失后信息不丢。

## 容易误判的地方

- **"`outline: none` 只是去掉丑边框"** → 没提供替代焦点样式时，它等于让键盘用户失去定位；替代方案要写在基础规则里，`focus-visible` 只负责区分显示时机。
- **"对比度是审美偏好，调顺眼就行"** → 它是"能否被读到"的底线；叠加 `opacity`、悬停插值、系统覆盖色之后要重新测，且不能只靠颜色表意。
- **"`@supports` 返回真就万事大吉"** → 它只检测语法，不保证行为完整；增强必须是叠加，基础状态必须独立可用。

## 自己再做一次

1. 把 `<div class="button" onclick="save()">保存</div>` 改成 `<button class="button" type="button">保存</button>`，只用键盘操作。**预期结果**：Tab 能聚焦、回车与空格都能触发、焦点环可见，全程不需要额外 JS。
2. 写 `:focus { outline: 3px solid #0b63ce }`，再用 `@supports selector(:focus-visible)` 包住 `.button:focus:not(:focus-visible) { outline: none }`。**预期结果**：支持该选择器时，鼠标点击不显示环、键盘 Tab 显示 3px 环；在不支持的环境里，鼠标和键盘都仍按基础 `:focus` 规则显示环。
3. 写 `padding: 0.75rem;` 紧跟 `padding: max(0.75rem, env(safe-area-inset-top));`，再开启强制颜色。**预期结果**：不支持 `max()` / `env()` 时第一条仍然生效；强制颜色下背景图与阴影被忽略，但用系统色写的边框与文字仍可辨认。

> 下一篇：[变化如何发生](25-rendering.md)
