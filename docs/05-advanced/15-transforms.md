# 15 · 变换与视觉状态

> 学习目标：能准确预测多个 transform 函数的组合顺序、百分比参照与变换原点，理解 2D/3D 透视和背面剔除的成立条件，并合理使用独立变换属性与 will-change。

## 1. 变换移动的是视觉结果，不是布局结果

`transform` 在布局完成后改变元素的坐标系与绘制结果。元素仍然占据原来的布局盒，但视觉上被移动、旋转、缩放或倾斜。

```text
布局阶段                        绘制阶段
┌──────────────┐               ┌──────────────┐
│ 原始布局盒     │  ──transform──▶│ 变换后的外观   │
└──────────────┘               └──────────────┘
     占空间                         不重新参与流布局
```

注意：“不改布局”指**元素自身的布局盒尺寸与兄弟元素的位置**不变；但非 `none` 的 `transform` 会成为固定/绝对定位后代的包含块，改变的是**后代的参照物**，见下文第 7 节。

这带来几个关键约束：

- `transform: translateX(100px)` 不会让后续兄弟元素自动让出 100px，可能造成视觉重叠。
- 变换后的视觉溢出可能扩大滚动区域，但不改变 `offsetWidth` 等布局尺寸。
- 非 `none` 的 transform 通常创建层叠上下文，也常成为固定/绝对定位后代的包含块。
- 变换不改变文字语义与 DOM 顺序，但会缩放文字、焦点环和阴影，可能降低可读性。
- 屏幕坐标、事件命中与视觉位置一起变换；布局测量工具通常仍显示原始盒。

因此，普通文档流中的小幅位移可以用 margin、gap 或布局属性完成；需要旋转、缩放、共享动画基准或不触发重新布局时，transform 才更合适。

## 2. 变换函数与组合顺序

### 2.1 2D 基础函数

```css
transform: translate(20px, -10px) rotate(12deg) scale(1.1, 0.9) skew(5deg, 0);
```

| 函数 | 作用 | 参数参照 |
| --- | --- | --- |
| `translate()` / `translateX()` / `translateY()` | 平移 | 长度，或相对自身参考盒的百分比 |
| `rotate()` | 绕 Z 轴旋转 | 角度，如 `30deg`、`0.5turn` |
| `scale()` / `scaleX()` / `scaleY()` | 缩放 | 无单位数字；负数产生镜像 |
| `skew()` / `skewX()` / `skewY()` | 沿轴错切 | 角度 |
| `matrix()` | 直接指定 2D 仿射矩阵 | 六个数字 a、b、c、d、e、f |

`scale(0.5)` 让外观变为一半；`scale(-1, 1)` 水平翻转；`scale(1, -1)` 垂直翻转。负缩放会同时改变局部坐标方向，可能让子元素里的文字和交互方向显得异常。

`skew` 容易让矩形变成平行四边形，使文字与控件变形。它不像 rotate 那样保持角度，也不像 scale 那样保持平行关系，界面中应谨慎使用。

### 2.2 多个函数不是“从左到右依次拖动物体”

CSS 把 transform 列表转换为矩阵。对列表 `A B C`，点向量的计算通常等价于 `A × B × C × p`，也就是先应用最右侧的 C，再应用 B，最后应用 A。

```css
/* 视觉结果：先把局部 X 轴移动 100px，再把整个结果旋转 30deg */
transform: rotate(30deg) translateX(100px);

/* 视觉结果：先旋转，再沿屏幕 X 轴移动 100px */
transform: translateX(100px) rotate(30deg);
```

以默认中心为原点：

```text
rotate(30deg) translateX(100px)
                    局部 X 轴 ↗
                 ┌───────────────╱
                 │      元素 ╱
                 └──────●╱─────────▶ 屏幕 X
                     原点

translateX(100px) rotate(30deg)
       屏幕 X 平移 100px
                 ┌───────────────╱
                 │      元素 ╱
                 └──────●╱─────────▶ 屏幕 X
                     原点
```

第一个结果的平移向量也被旋转，落点约为 `(86.6px, 50px)`；第二个结果先旋转，再把结果沿屏幕 X 轴平移 100px。调试复杂变换时，可暂时只保留一个函数，再逐个向左添加，观察每一步如何改变坐标系。

### 2.3 用独立属性表达常见意图

现代 CSS 允许把平移、旋转、缩放拆开：

```css
.card {
  translate: 0 0;
  rotate: 0deg;
  scale: 1;
  transform: none;
}

.card:hover {
  translate: 0 -0.5rem;
  rotate: -2deg;
  scale: 1.02;
}
```

独立属性不能与对应的 transform 函数混为一谈。浏览器按 `translate`、`rotate`、`scale`、`transform` 的顺序组合这些矩阵；整体上等价于：

```css
/* 若原有 transform 为 skewX(5deg)，整体等价于： */
transform: translate(0, -0.5rem) rotate(-2deg) scale(1.02) skewX(5deg);
```

这种顺序符合常见直觉：先在局部缩放，再旋转，最后把整体平移到目标位置。独立属性也便于 JavaScript 或不同样式规则分别更新一个维度，但项目内仍应统一约定，避免同一组件同时用两套方式控制同类变换。

## 3. 百分比、参考盒与 `transform-origin`

### 3.1 `translate` 的百分比相对谁

```css
.moved { transform: translate(50%, 25%); }
```

平移百分比通常相对元素自身的参考盒尺寸，而不是父容器。一个宽 200px、高 100px 的元素，`translate(50%, 25%)` 的位移是 `(100px, 25px)`。这使它非常适合做与自身尺寸相关的居中微调，但也意味着不能误以为 50% 是父容器的一半。

百分比位移仍受盒模型与 `transform-box` 影响；SVG 元素还需要额外注意参考盒。`translateZ()` 的百分比不是有效写法，深度位移使用长度。

### 3.2 `transform-origin` 改变旋转与缩放中心

```css
.door {
  transform-origin: left center;
  transform: rotateY(-80deg);
}

.zoom-card {
  transform-origin: 20% 80%;
  transform: scale(1.2);
}
```

默认原点是 `50% 50% 0`。设置 `0 0` 后，旋转和缩放围绕左上角，而不是中心；两个值时第三轴默认为 0。第三个值必须是长度，不能是百分比。

原点位置会显著改变运动轨迹：

```text
transform-origin: center          transform-origin: left center
        ┌───────┐                       ┌───────┐
        │   ●   │                       │●      │
        └───┬───┘                       └───┬───┘
            ↕ 旋转                           ╲ 绕左边缘旋转
```

`transform-origin` 的百分比参照参考盒，`translate` 的百分比也参照自身，但两者解决的是不同问题：前者决定“绕哪里变换”，后者决定“移动多远”。

### 3.3 `transform-box` 与 SVG

HTML 元素默认参考盒通常是 `border-box`。`transform-box` 可以改变参考盒：

| 值 | 参考盒 |
| --- | --- |
| `border-box` | 边框盒 |
| `padding-box` | 内边距盒 |
| `content-box` | 内容盒 |
| `fill-box` | SVG 对象填充盒 |
| `stroke-box` | SVG 对象描边盒 |
| `view-box` | 最近的 SVG viewBox |

这一属性对 SVG 尤其重要。`viewBox="0 0 100 100"` 中的图标即使显示得很小，`transform-origin: center` 与百分比参照也可能按 viewBox 坐标计算，而不是屏幕像素。需要围绕图标自身中心旋转时，可尝试 `transform-box: fill-box; transform-origin: center;`，并用实际图形验证。

## 4. 2D 到 3D：深度不是一个大一些的阴影

### 4.1 3D 函数

```css
.card {
  transform: perspective(800px) translateZ(40px) rotateX(15deg) rotateY(-20deg);
}
```

- `translateZ()` / `translate3d()`：沿深度轴移动。
- `rotateX()` / `rotateY()`：绕水平轴或垂直轴旋转。
- `rotate3d(x, y, z, angle)`：绕任意三维轴旋转。
- `scaleZ()` / `scale3d()`：缩放深度或三个轴。
- `matrix3d()`：直接指定 4×4 三维矩阵。

普通 2D 旋转默认绕 Z 轴。元素“立起来”通常需要 `rotateX()` 或 `rotateY()`；只写 `rotateZ()` 不会产生立体效果。

### 4.2 `perspective()` 与 `perspective` 属性

两者都定义透视，但作用范围不同：

```css
.scene {
  perspective: 800px;        /* 为子元素提供共享透视 */
  perspective-origin: 50% 40%;
}

.card {
  transform: rotateY(35deg); /* 子元素使用 scene 的透视 */
}

.isolated-card {
  transform: perspective(800px) rotateY(35deg); /* 变换列表自己的透视 */
}
```

透视距离越小，远近缩放差异越强；距离越大，透视越接近正交投影。应使用正长度，并根据场景尺寸调整。父级 `perspective` 不改变父元素自身外观，只影响其 3D 子元素的投影；`perspective-origin` 决定消失点位置。

`perspective()` 放在 transform 列表中的位置会影响最终矩阵。把它放在最前面，相当于先建立一个透视坐标系，再应用后续旋转和平移。不要在多个嵌套层反复叠加强烈透视，否则可能得到难以预测的夸张变形。

### 4.3 `transform-style` 与 3D 上下文

```css
.scene {
  transform-style: preserve-3d;
}

.face {
  backface-visibility: hidden;
}
```

默认 `transform-style: flat` 会把子元素压平到父元素平面，立方体的多个面无法共享同一个 3D 空间。`preserve-3d` 让子元素保留三维位置，适合立方体、翻牌与层叠卡片。

它并非无条件成立。`overflow` 非 visible、`opacity` 小于 1、`filter`、`clip-path`、containment 等 grouping 属性可能强制扁平化。CSS 的 3D 上下文也涉及绘制顺序与相交面的处理，不应假设浏览器会像完整 3D 引擎那样进行所有遮挡计算。

### 4.4 `backface-visibility`

```css
.flip-card {
  backface-visibility: hidden;
  transform-style: preserve-3d;
}

.flip-card.is-flipped { transform: rotateY(180deg); }
```

`backface-visibility: hidden` 在元素背面朝向观察者时隐藏其背面，常用于双面卡片与立方体。成立条件包括：

- 元素确实发生了 3D 旋转，背面朝向观察者。
- 父级允许 preserve-3d，否则元素可能先被压平。
- 不是把 `hidden` 当成 DOM 隐藏。背面的文字仍可能存在，可聚焦元素也可能成为问题。

对于可交互双面卡片，应在不可见面板上禁用焦点，切换时同步 `aria-hidden` / `inert`，而不是只依赖 backface-visibility。纯装饰立方体可以整体标记为 `aria-hidden="true"`，并把说明文字放在外部。

## 5. 矩阵与动画插值

`matrix(a, b, c, d, e, f)` 是 2D 变换的底层表示：

```text
[x']   [a c e] [x]
[y'] = [b d f] [y]
[ 1]   [0 0 1] [ 1]
```

通常不需要手写矩阵，但理解它有助于解释两件事：

1. **函数列表不同也可以插值**：如果两个状态都能分解为兼容的矩阵，浏览器可以在变换结果之间插值，不要求函数列表完全一致。
2. **特殊值会导致退化**：缩放为 0、矩阵不可逆时，浏览器会按规范退化处理，不一定得到你想象中的中间形态。

旋转角度动画还涉及最短路径与轴向问题。`rotate(0deg)` 到 `rotate(350deg)` 可能走反向 10deg，而不是正向 350deg；希望明确多圈旋转时，需要设计中间关键帧或拆分动画。三维旋转、函数列表不匹配与 `rotate3d` 的组合也更复杂，不能只看起止角度猜测轨迹。

## 6. `will-change` 是提前声明，不是性能开关

```css
.moving-card {
  will-change: transform;
}
```

`will-change` 告诉浏览器元素某个属性可能很快变化，让浏览器有机会提前准备资源。它可能：

- 提升为合成层，减少部分动画中的重绘。
- 提前创建层叠上下文或包含块。
- 增加显存与图层管理成本。
- 如果长期保留在大量元素上，反而降低性能。

推荐用法：

```css
@media (prefers-reduced-motion: no-preference) {
  .card {
    transition: translate 180ms ease, box-shadow 180ms ease;
  }

  .card:hover {
    translate: 0 -0.25rem;
  }
}
```

先写出合理的 transition，再测量。只有确认某个即将发生的大范围变换需要提前准备时，才在交互前短暂添加 will-change；长时间不要给所有卡片、列表项或全局选择器添加。

不要用 `will-change: transform` 试图让 `width`、`height`、`top` 动画变成 GPU 动画。它只声明 transform 可能变化，不会把布局属性变成合成属性。也不要为了修复 z-index 问题长期添加 will-change；正确做法是理清层叠上下文。

## 7. 完整示例一：可切换的 3D 立方体

保存为 `transform-cube.html`。这个立方体是纯装饰，真实说明文字位于外部；勾选标签可切换旋转状态。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>3D 变换立方体</title>
  <style>
    :root { font-family: system-ui, "PingFang SC", sans-serif; color: #20271b; }
    * { box-sizing: border-box; }
    body { margin: 0; min-block-size: 100vh; display: grid; place-items: center; padding: 2rem 1rem; background: #f4f2e9; }

    .lab {
      --size: clamp(9rem, 40vw, 13rem);
      --half: calc(var(--size) / 2);
      display: grid;
      justify-items: center;
      gap: 1.5rem;
    }

    .toggle { accent-color: #466a2b; }
    .toggle-label { font-weight: 700; cursor: pointer; }

    .scene {
      inline-size: var(--size);
      block-size: var(--size);
      perspective: 850px;
      perspective-origin: 50% 42%;
    }

    .cube {
      position: relative;
      inline-size: 100%;
      block-size: 100%;
      transform-style: preserve-3d;
      transform: rotateX(-20deg) rotateY(35deg);
      transition: transform 700ms cubic-bezier(0.2, 0.7, 0.2, 1);
    }

    .toggle:checked + .toggle-label + .scene .cube {
      transform: rotateX(-20deg) rotateY(215deg);
    }

    .face {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      border: 2px solid rgb(255 255 255 / 70%);
      color: white;
      background: rgb(63 107 42 / 92%);
      font-size: 1.5rem;
      font-weight: 800;
      backface-visibility: hidden;
    }

    .front  { transform: rotateY(0deg) translateZ(var(--half)); }
    .back   { transform: rotateY(180deg) translateZ(var(--half)); }
    .right  { transform: rotateY(90deg) translateZ(var(--half)); }
    .left   { transform: rotateY(-90deg) translateZ(var(--half)); }
    .top    { transform: rotateX(90deg) translateZ(var(--half)); background: rgb(126 160 98 / 92%); }
    .bottom { transform: rotateX(-90deg) translateZ(var(--half)); background: rgb(43 76 29 / 95%); }

    @media (prefers-reduced-motion: reduce) {
      .cube { transition-duration: 1ms; }
    }
  </style>
</head>
<body>
  <main class="lab">
    <input class="toggle" id="flip-cube" type="checkbox" />
    <label class="toggle-label" for="flip-cube">旋转立方体</label>
    <div class="scene">
      <div class="cube" aria-hidden="true">
        <div class="face front">前</div>
        <div class="face back">后</div>
        <div class="face right">右</div>
        <div class="face left">左</div>
        <div class="face top">上</div>
        <div class="face bottom">下</div>
      </div>
    </div>
    <p>透视由父级 scene 提供，preserve-3d 保留各面的空间关系。</p>
  </main>
</body>
</html>
```

## 8. 完整示例二：独立变换与不同原点

保存为 `transform-origin-lab.html`。分别悬停或用 Tab 聚焦三个元素，比较它们的运动轨迹。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>变换原点实验</title>
  <style>
    :root { font-family: system-ui, "PingFang SC", sans-serif; color: #20271b; }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 2rem 1rem; background: #f5f3ec; }
    main { max-inline-size: 52rem; margin-inline: auto; }
    h1 { text-wrap: balance; }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr));
      gap: 1rem;
      margin-block-start: 1.5rem;
    }

    .demo {
      min-block-size: 15rem;
      display: grid;
      place-items: center;
      border: 1px dashed #9da792;
      border-radius: 1rem;
      background: white;
    }

    .tile {
      inline-size: 9rem;
      block-size: 6rem;
      display: grid;
      place-items: center;
      border-radius: 0.75rem;
      color: white;
      background: #466a2b;
      font-weight: 700;
      translate: 0 0;
      rotate: 0deg;
      scale: 1;
      transition: translate 220ms ease, rotate 220ms ease, scale 220ms ease;
    }

    .demo:hover .tile,
    .tile:focus-visible {
      translate: 0 -0.5rem;
      rotate: -4deg;
      scale: 1.06;
      outline: 3px solid #203d16;
      outline-offset: 5px;
    }

    .door {
      transform-origin: left center;
      transition: rotate 500ms ease;
    }

    .demo.door-demo:hover .door,
    .door:focus-visible { rotate: -22deg; }

    .zoom {
      transform-origin: 15% 85%;
      transition: scale 400ms ease;
    }

    .demo.zoom-demo:hover .zoom,
    .zoom:focus-visible { scale: 1.25; }

    p { line-height: 1.6; }
    code { color: #3d5b2c; }
  </style>
</head>
<body>
  <main>
    <h1>同一组变换，不同原点</h1>
    <div class="grid">
      <section class="demo">
        <div class="tile" tabindex="0">独立变换</div>
      </section>
      <section class="demo door-demo">
        <div class="tile door" tabindex="0">左边缘旋转</div>
      </section>
      <section class="demo zoom-demo">
        <div class="tile zoom" tabindex="0">右下角缩放</div>
      </section>
    </div>
    <p>第一块使用 <code>translate</code>、<code>rotate</code>、<code>scale</code>；第二块绕左边缘旋转；第三块以右下角为缩放原点。焦点样式保证键盘用户也能看到状态。</p>
  </main>
</body>
</html>
```

## 9. 易错点

| 误区 | 原因与正确做法 |
| --- | --- |
| transform 列表从左到右作用于点 | 矩阵通常从最右侧函数开始应用；用单函数逐步叠加验证 |
| `translate: 50%` 相对父元素 | 它相对元素自身参考盒尺寸 |
| `rotate(90deg)` 能做出 3D 翻转 | 它绕 Z 轴；绕 X/Y 轴才会改变朝向 |
| 只给元素写 perspective() 就够了 | 多面共享透视通常需要在父级设置 perspective |
| 加 backface-visibility 就完成双面卡片 | 还需 3D 旋转与 preserve-3d，并处理背面交互和可访问性 |
| `will-change: transform` 能加速所有动画 | 它只声明 transform 可能变化，不能把 width/top 变成合成动画 |
| 所有元素都加 will-change 更流畅 | 过多图层消耗内存，可能降低性能 |
| 变换后布局尺寸也变了 | transform 不改变布局盒，只改变视觉结果与部分溢出区域 |
| SVG 的 center 一定是屏幕中心 | 参考盒可能是 viewBox 或 fill-box，需要 transform-box 配合 |

## 10. DevTools 与验证方法

1. **Computed 面板**：查看 transform 的最终 matrix/matrix3d，以及 translate、rotate、scale、transform-origin、transform-box 的合并结果。
2. **临时禁用函数**：从右向左逐项移除 transform 函数，确认每一步的坐标系变化。
3. **Layout 盒模型**：对比变换前后 offset 尺寸与绘制位置，理解布局盒没有改变。
4. **Layers 面板**：检查 3D 上下文、合成层和层叠顺序；如果立方体被压平，检查 overflow、opacity、filter 等 grouping 属性。
5. **开启动画减速**：在 DevTools 中放慢 transition，观察旋转方向、原点、消失点和背面剔除。
6. **键盘与触屏验证**：确保焦点环不被缩放压扁，点击区域仍可理解，背面的隐藏控件不可聚焦。
7. **性能面板**：分别测试 transform 与 top/left 动画，观察 Layout、Paint、Composite；不要仅凭是否出现图层下结论。
8. **减弱动画偏好**：验证 reduce 模式下仍能理解状态，不会用几乎不可见的快速旋转替代稳定反馈。

## 关联示例

- [变换原点与 3D](../../examples/motion/transform-origin.html)：比较不同 `transform-origin` 的运动轨迹和 3D 透视。

## 11. 练习

1. 分别实现 `rotate(30deg) translateX(100px)` 与 `translateX(100px) rotate(30deg)`，记录元素中心位置差异。
2. 为同一元素设置 center、left center、`0 0` 三个 transform-origin，观察 45deg 旋转后的包围盒。
3. 用父级 perspective 与 transform 内的 perspective() 制作两张卡片，比较共享消失点与独立透视。
4. 制作一个双面卡片，在切换时同步管理 inert / aria-hidden，并验证背面按钮不会被 Tab 聚焦。
5. 对一个列表分别测试无 will-change、悬停前添加和永久添加三种方案，用性能面板比较图层数量与内存影响。

> 上一篇：[视觉格式与溢出](../02-visual/07-formatting-overflow.md)。transform 改变视觉结果，overflow 决定哪些视觉结果可以被看见或滚动。
>
> 下一篇：[过渡与动画](16-animation.md)。在理解变换矩阵与图层边界后，进一步控制状态变化的时间轨迹。
