# 13 · 视觉变形

> **前置**：会用第 05 篇的布局盒与 `offsetWidth` 区分"声明尺寸"和"实测尺寸"；知道第 06 篇的包含块与第 08 篇的层叠上下文各是什么。
>
> 上一篇：[看见与看不见](12-display-overflow.md) ｜ [本阶段目录](README.md)

## 1. 本章目标

- 给定 `transform` 后的元素，能说出哪些量不变（布局盒、`offsetWidth`、兄弟位置），哪些量变（视觉位置、命中区域、后代参照、层叠归属）。
- 能按"从右往左"算出 `rotate(30deg) translateX(100px)` 与 `translateX(100px) rotate(30deg)` 的落点差异（约 86.6/50 与 100/0）。
- 能解释为什么 `translate(50%)` 参照元素自身而不是父容器，以及 `transform-origin` 改变的是轨迹还是终点尺寸。
- 能判断非 `none` 的 transform（含 `scale(1)`）为什么会给 fixed 后代充当包含块并创建层叠上下文。

**为什么现在学这个**：第 12 篇拆开了"隐藏"的四个环节；这一篇要拆开"移动"的两个世界——视觉上位置变了，布局上没变。不分清这一点，fixed 弹层错位和 `z-index` 失效会反复出现。

## 2. 新增模型

两个看起来无关的现象，其实是同一个机制的两面：

```css
.box { transform: translateX(100px); }
```

元素视觉上右移 100px，后面的兄弟却纹丝不动，`offsetLeft` 一个像素都没变；页面还可能多出横向滚动条，但布局测量值不变。换成 `rotate(30deg)` 也一样：元素歪了，它在流里占的那块矩形没歪。

真正奇怪的是：子元素写 `position: fixed; top: 0; left: 0`，本该贴住视口左上；一旦给父元素加上 `transform: translateX(0)`（位移是 0），子元素突然贴到父元素上。父元素加 `transform: scale(1)`（倍数也是 1，外观没变），子元素的 `z-index: 9999` 依然被兄弟里 `z-index: 1` 的对象盖住。

**模型：`transform` 在布局结束后换掉的是局部坐标系，不是布局盒——兄弟不让位，但非 `none` 的 transform 会成为后代的参照并创建层叠上下文。**

![函数顺序示意：从右往左应用，平移向量会不会跟着转](figures/13-transform.svg)

*图 13-1 · 函数顺序示意：从右往左应用，平移向量会不会跟着转*

图并排画两条路径：左为 `rotate(30deg) translateX(100px)`，先在局部 X 轴平移 100px 再整体旋转 30deg，落点约 `(86.6px, 50px)`；右为 `translateX(100px) rotate(30deg)`，先旋转再沿屏幕 X 轴平移，落点 `(100px, 0)`。箭头上标"右先左后"，强调每个函数改的是随后的坐标系。

**这张图的一句话结论：列表里越靠右的函数越先作用到点上——这是矩阵乘法，不是"依次拖动物体"。**

术语落地：

- **局部坐标系**：元素自己使用的坐标框架，变换改的就是它，而不是元素在流里占的矩形。
- **矩阵乘法**：多个 transform 函数合成时按 `A × B × C × p` 计算，最右侧先作用于点。
- **命中区域**：鼠标点击实际命中的区域，随视觉形状一起变换，不跟布局盒走。
- **包含块**：绝对 / 固定定位后代计算尺寸与位置时的参照盒（第 06 篇）。

## 3. 可运行的 demo

先看一次"布局尺寸不变、视觉尺寸变了"，再读后面的坐标系规则。

[打开 demo：调角度，核对从右往左的落点](../../examples/minimal/13-transform.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/13-transform.html" title="调角度，核对从右往左的落点" loading="lazy"></iframe>

> **先预测**：宽 200px、高 100px 的元素从 0deg 转到 30deg，`offsetWidth` 会变吗？`getBoundingClientRect().width` 会变吗？各是多少？
>
> **验证**：打开 demo 拖动角度滑块，用页面显示的实时读数核对——`offsetWidth` 保持 200px，`getBoundingClientRect().width` 约 223px（`200 × cos30 + 100 × sin30 ≈ 223.2`）。

demo 只有两个控件：角度、函数顺序。核对时别只看形状：`scale(1)` 或 `translateX(0)` 这类"看起来没变"的变换同样会创建层叠上下文，demo 会单独提示这一点。

## 4. 原理与规则

### 4.1 布局完成后换坐标系

`transform` 位于布局之后、绘制之前：元素仍占原来的布局盒，自身尺寸与兄弟位置都不变；视觉溢出可能扩大滚动区域，但 `offsetWidth` 之类的布局测量值不变。

把"不变"和"会变"分开记：

- 不变：元素自身的布局盒尺寸、兄弟元素的位置、`offsetWidth` / `offsetHeight`。
- 会变：视觉位置与形状、命中区域、视觉溢出范围、后代的定位参照、整棵子树的层叠归属。

命中区域也跟着变换：鼠标按视觉位置命中，而不是按布局盒；缩放后的焦点环会被一起放大或压扁。**为什么不让兄弟让位？** 因为布局阶段已经结束，兄弟的位置早就算好了。普通小幅位移用 margin 或 gap 更合适；需要旋转、缩放或共享动画基准时才用 transform。把一组元素放在同一个父级 transform 下，旋转时它们共享一个坐标系，比每个元素各自旋转更容易保持相对关系。

**失效条件**：用它做小幅位移会绕开布局流，导致文档流与实际视觉位置不一致；大比例缩放会同时放大焦点环并改变命中区域，交互控件必须重新验证可点击区域与焦点是否可见。

### 4.2 多个函数从右往左应用（矩阵乘法）

对列表 `A B C`，浏览器算的是 `A × B × C × p`：最右侧的 C 先作用到点上，然后 B，最后 A。

```css
/* 先平移（沿局部 X 轴），再把结果旋转 30deg */
transform: rotate(30deg) translateX(100px);
/* 先旋转，再沿屏幕 X 轴平移 100px */
transform: translateX(100px) rotate(30deg);
```

默认原点下前者落点约 `(86.6px, 50px)`，后者是 `(100px, 0)`：平移向量也被旋转了。把坐标系想象成一支跟着元素走的笔：前一种写法先沿当前 X 轴推 100px 再转手腕 30deg，推的方向跟着一起转；后一种先转手腕再沿屏幕 X 推，落点自然不同。底层表示是 `matrix(a, b, c, d, e, f)`：a、b、c、d 管缩放、旋转和错切，e、f 管平移，两组写法的 e、f 不同正是数值证据。

**为什么不是从左到右？** 每个函数都在改写局部坐标系，而不是搬动画好的像素。调试时先只留一个函数，再逐个往左加，就能看清每一步坐标系怎么变。

**失效条件**：`perspective()` 写进列表时其位置会改变最终矩阵，放在最前面相当于先建立透视坐标系再做旋转；包含 `3D` 变换时不能再按纯 2D 直觉推断落点。

### 4.3 原点与百分比都参照自身

`transform-origin` 默认 `50% 50% 0`，旋转和缩放都绕这个点；改成 `0 0` 就绕左上角。`translate()` 的百分比也参照元素**自身**的参考盒（HTML 元素通常是 border-box），不是父容器：一个 200×100 的元素写 `translate(50%, 25%)`，位移是 `(100px, 25px)`。

**为什么两个"百分比"都指向自身？** 因为变换发生在元素自己的局部坐标系里，量尺自然是它自己的盒——这让"按自身尺寸做居中微调"变得可靠，但别把它当成父级宽度的百分比。`transform-origin` 可写三个值，第三个是 Z 轴偏移，必须是长度，不能写百分比。SVG 元素的参考盒可能按 viewBox 或 fill-box 算，旋转前先确认 `transform-box`。

原点改变的是轨迹而不是终点尺寸：绕中心旋转 45deg 与绕左上角旋转 45deg，包围盒大小可能相同，位置却差很多；`transform-origin: 20% 80%` 会让放大主要朝右上角生长。

**失效条件**：`transform-origin: 20% 80%` 决定绕哪儿转，`translate(20%, 80%)` 决定走多远——数值相同但作用完全不同；对 SVG 元素想当然地按 HTML 的 border-box 理解会选错支点。

### 4.4 3D 要透视，副作用要记牢

`rotateX()` / `rotateY()` 才会让元素"立起来"，`rotate(90deg)` 绕 Z 轴只是平面转圈。要看深度还需要 `perspective`：写在父级让多个子元素共享消失点，或作为 `perspective()` 写进列表只作用于本元素；父级 `perspective` 不改变父元素自身外观。透视距离越小近大远小越强，越大越接近正交投影。

默认 `transform-style: flat` 会把子元素压平，立方体的多个面无法共享空间；要保留 3D 位置需要 `preserve-3d`，而 `overflow` 非 visible、`opacity` 小于 1 等 grouping 属性可能强制扁平化。

**还有一个容易漏掉的副作用：** 非 `none` 的 transform 会成为 `position: fixed` / `absolute` 后代的**包含块**，并创建**层叠上下文**。所以"transform 完全不影响布局"是错的——它不改自身布局盒和兄弟位置，却改了后代的定位参照和整棵子树的层叠归属。排查弹层错位时，先看祖先链上有没有非 `none` 的 `transform`、`filter` 或 `perspective`。

**失效条件**：`scale(1)`、`translateX(0)` 这类外观没变的变换照样创建层叠上下文与包含块，不能按"看起来没变"判断；`overflow` 非 visible 或 `opacity` 小于 1 可能强制 3D 扁平化，嵌套强透视结果很难预测。性能上 transform 在合适条件可只走合成（第 25 篇）。

## 5. 常见坑

**坑 1：`transform` 移动后兄弟元素没有让位**

- **原因**：布局阶段已结束，变换只改绘制时的坐标系，兄弟位置是布局阶段算好的。
- **确认**：`offsetLeft` / `offsetWidth` 与变换前完全一致，只有 `getBoundingClientRect()` 变了。
- **修法**：要真正占位就用 margin / gap；要独立浮层就配合 `position: absolute` 并把 transform 只用于视觉微调。

**坑 2：父级 `transform: translateX(0)` 后 fixed 子元素不贴视口**

- **原因**：非 none 的 transform 成为 fixed 后代的包含块，定位参照从视口换成父元素。
- **确认**：滚动页面时子元素跟着父元素走，而不是固定在视口左上。
- **修法**：把 fixed 元素移出带 transform 的祖先链，或改用 `position: absolute` 按父元素定位；做不到就重新设计层级。

**坑 3：子元素 `z-index: 9999` 被兄弟里 `z-index: 1` 盖住**

- **原因**：父级 transform 创建了层叠上下文，子元素的 z-index 只在父级那张图内部有效。
- **确认**：在 DevTools 的 Layers 面板看父级是否形成独立层叠上下文。
- **修法**：提升父级自身 z-index，或去掉不必要的 transform / `opacity` / `filter`。

**坑 4：`translate(50%)` 位移和预期不符**

- **原因**：百分比参照元素自身参考盒，不是父容器；200px 宽的元素移动 100px。
- **确认**：用 `getBoundingClientRect()` 量实际位移，与自身宽度对照。
- **修法**：要按父容器比例移动就写具体长度或 `vw` / `%` 配合定位属性；SVG 元素先确认 `transform-box`。

## 6. 练习

1. **基础**：给宽 200px、高 100px 的元素设 `translate(50%, 25%)`，用 `getBoundingClientRect()` 对比变换前后。
   验收：水平位移 100px、垂直位移 25px；元素自身 `offsetWidth` / `offsetHeight` 不变。

2. **基础**：宽 200px、高 100px 的元素转 30deg，分别读 `offsetWidth` 与 `getBoundingClientRect().width`。
   验收：`offsetWidth` 为 200px；包围盒宽约 223px（`200 × cos30 + 100 × sin30`），与 demo 读数一致。

3. **进阶**：分别写 `rotate(30deg) translateX(100px)` 与 `translateX(100px) rotate(30deg)`，记录落点。
   验收：前者约 `(86.6px, 50px)`，后者 `(100px, 0)`，差别来自平移向量是否被旋转。

4. **进阶**：父元素设 `transform: translateX(0)`，子元素设 `position: fixed; top: 0; left: 0`，滚动页面观察。
   验收：子元素贴在父元素变换后坐标系左上、随页面滚动而移动；删掉父级 transform 后回到视口左上。

5. **挑战**：父元素 `opacity: 0.99` 且子元素 `z-index: 9999`，兄弟元素 `z-index: 1`，判断谁在上面，再用 transform 替换 opacity 重测。
   验收：两种情况下子元素都被兄弟盖住，因为 opacity 与 transform 都创建层叠上下文；移除父级相关属性后 9999 才直接进入根层叠上下文并翻到上面。

> 下一篇：[状态的变化](14-animation.md)
