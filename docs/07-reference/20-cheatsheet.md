# 20 · CSS 属性速查表

> 用法：先根据问题找到对应类别，再回到对应章节理解约束。本表用于回忆，不替代规范与浏览器验证。

## 1. 基础与盒模型

| 属性 | 作用 | 高频值 / 提醒 |
| --- | --- | --- |
| `display` | 外部与内部布局 | block、inline、flex、grid、none |
| `box-sizing` | width/height 的尺寸语义 | 项目常用 border-box |
| `width` / `height` | 尺寸 | auto、百分比、min()/max() |
| `min-width` / `max-width` | 尺寸约束 | Flex/Grid 子项常用 min-width: 0 |
| `margin` | 外边距 | auto 可用于特定轴居中 |
| `padding` | 内边距 | 背景默认延伸到 border 外缘 |
| `border` | 边框简写 | 会触发视觉与尺寸变化 |
| `border-radius` | 圆角 | 支持斜杠分别描述横纵半径 |
| `aspect-ratio` | 首选宽高比 | 内容可能突破，需要时裁剪 |
| `overflow` | 溢出与滚动 | visible、hidden、clip、scroll、auto |
| `visibility` | 可见性 | hidden 保留布局 |

## 2. 排版与文字

| 属性 | 作用 | 提醒 |
| --- | --- | --- |
| `font-family` | 字体栈 | 最后放通用字体族 |
| `font-size` | 字号 | rem 适合全局基准，em 适合局部相对尺寸 |
| `font-weight` | 字重 | 需字体文件支持 |
| `font-style` | 字形 | normal、italic、oblique |
| `line-height` | 行高 | 无单位值会随字号缩放 |
| `letter-spacing` | 字间距 | 中文标题不宜过散 |
| `word-spacing` | 词间距 | 对中文影响有限 |
| `text-align` | 水平对齐 | start/end 更适合逻辑方向 |
| `text-indent` | 首行缩进 | 常用 2em |
| `text-decoration` | 装饰线 | 可分别控制样式、颜色、粗细 |
| `text-overflow` | 单行省略 | 需配合 overflow 与 white-space |
| `white-space` | 空白与换行 | nowrap、pre、pre-wrap |
| `overflow-wrap` / `word-break` | 长文本断行 | anywhere 更适合避免长 URL 溢出 |
| `text-wrap` | 换行质量 | balance、pretty |
| `writing-mode` | 书写模式 | 影响 inline/block 方向 |

## 3. 颜色、背景与视觉效果

| 属性 | 作用 | 高频值 |
| --- | --- | --- |
| `color` | 文字与 currentColor | 支持现代颜色函数 |
| `background` | 背景简写 | 会重置多个背景子属性 |
| `background-color` | 背景色 | 透明用 transparent |
| `background-image` | 背景图/渐变 | 支持多层逗号分隔 |
| `background-size` | 背景尺寸 | cover、contain、长度 |
| `background-position` | 背景位置 | center、百分比、逻辑位置 |
| `background-repeat` | 背景重复 | no-repeat、repeat-x |
| `background-clip` | 背景裁剪 | border-box、padding-box、text |
| `background-origin` | 背景定位区域 | padding-box、border-box |
| `background-attachment` | 背景附着 | fixed 在移动端可能有性能问题 |
| `box-shadow` | 盒阴影 | inset、模糊、扩散、颜色 |
| `outline` | 轮廓 | 不占布局，适合焦点样式 |
| `filter` | 滤镜 | blur、brightness、drop-shadow |
| `clip-path` | 裁剪路径 | circle、polygon、inset |
| `mask` | 遮罩 | 图片、渐变与遮罩模式 |
| `mix-blend-mode` | 混合模式 | 注意层叠上下文与可读性 |

## 4. Flex

| 属性 | 对象 | 作用 |
| --- | --- | --- |
| `flex-direction` | 容器 | row、column、reverse |
| `flex-wrap` | 容器 | nowrap、wrap、wrap-reverse |
| `justify-content` | 容器 | 主轴空间分配 |
| `align-items` | 容器 | 单行交叉轴对齐 |
| `align-content` | 容器 | 多行 flex line 分布 |
| `gap` | 容器 | 项目与行间距 |
| `flex` | item | grow shrink basis 简写 |
| `flex-grow` | item | 放大系数 |
| `flex-shrink` | item | 收缩系数 |
| `flex-basis` | item | 主轴初始基准 |
| `align-self` | item | 覆盖交叉轴对齐 |
| `order` | item | 视觉排序，谨慎影响无障碍 |

## 5. Grid

| 属性 | 作用 | 常用写法 |
| --- | --- | --- |
| `grid-template-columns` | 列轨道 | repeat(3, minmax(0, 1fr)) |
| `grid-template-rows` | 行轨道 | auto 1fr auto |
| `grid-template-areas` | 区域布局 | "header header" |
| `grid-column` | 列位置/跨度 | 1 / -1、span 2 |
| `grid-row` | 行位置/跨度 | 1 / 3 |
| `grid-area` | 区域或行列简写 | main |
| `grid-auto-flow` | 自动放置 | row、column、dense |
| `grid-auto-rows` | 隐式行尺寸 | minmax(4rem, auto) |
| `grid-auto-columns` | 隐式列尺寸 | minmax(12rem, 1fr) |
| `justify-items` / `align-items` | item 在单元格内对齐 | center、stretch |
| `justify-content` / `align-content` | 轨道整体分布 | space-between、center |
| `subgrid` | 继承父级轨道 | grid-template-rows: subgrid |

## 6. 定位与层叠

| 属性 | 作用 | 提醒 |
| --- | --- | --- |
| `position` | 定位方式 | static、relative、absolute、fixed、sticky |
| `inset` | top/right/bottom/left | 逻辑属性优先 inset-block/inline |
| `z-index` | 层叠顺序 | 仅在层叠上下文内有意义 |
| `isolation` | 创建独立层叠上下文 | isolate 常用于组件内部 |
| `float` / `clear` | 浮动与清除 | 新布局优先 Flex/Grid |
| `object-fit` | 替换内容适配 | cover、contain、fill |
| `object-position` | 替换内容位置 | center、50% 20% |

## 7. 响应式、容器查询与变量

| 属性 / 规则 | 作用 | 示例 |
| --- | --- | --- |
| `@media` | 视口/设备/用户偏好查询 | (min-width: 48rem) |
| `@container` | 容器尺寸/样式查询 | (min-width: 30rem) |
| `container-type` | 建立查询容器 | inline-size、size |
| `container-name` | 命名容器 | card-layout |
| `cqw` / `cqh` | 查询容器相对单位 | font-size: clamp(1rem, 5cqw, 2rem) |
| `clamp()` | 设置下限、首选值、上限 | clamp(1rem, 2vw + 1rem, 2rem) |
| `min()` / `max()` | 取最小/最大值 | width: min(100%, 60rem) |
| `calc()` | 尺寸计算 | calc(100% - 2rem) |
| `--custom` | 自定义属性 | --space-4: 1rem |
| `var()` | 读取变量 | var(--color-bg, white) |
| `@property` | 注册变量类型 | syntax: "<color>" |
| `@supports` | 特性检测 | (display: grid) |
| `@layer` | 声明层顺序 | @layer reset, base, components |

## 8. 变换、过渡与动画

| 属性 | 作用 | 常用值 |
| --- | --- | --- |
| `transform` | 坐标变换 | translate、rotate、scale、skew |
| `transform-origin` | 变换原点 | center、left top |
| `perspective` | 透视 | 800px |
| `translate` / `rotate` / `scale` | 独立变换属性 | 1rem、45deg、1.05 |
| `transition` | 状态补间 | property duration timing delay |
| `animation` | 关键帧动画简写 | name duration timing iteration |
| `animation-fill-mode` | 动画前后状态 | none、forwards、backwards、both |
| `animation-play-state` | 运行/暂停 | running、paused |
| `animation-timeline` | 时间线 | auto、scroll()、view() |
| `@keyframes` | 定义关键帧 | from、to、百分比 |
| `scroll-timeline` | 滚动时间线 | 配合匿名或命名时间轴 |
| `view-timeline` | 元素进入视口时间线 | 适合滚动显现 |

## 9. 一页式布局决策

```text
一维空间分配？ ── 是 ──▶ Flex
       │
       否
二维行列控制？ ── 是 ──▶ Grid
       │
       否
脱离普通流定位？ ─▶ absolute / fixed / sticky
       │
       否
保持普通流，必要时建立隔离 ─▶ display: flow-root
```

## 10. 最小初始化模板

```css
:root {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #24261f;
  background: #f4f1e9;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

*,
*::before,
*::after { box-sizing: border-box; }

body { margin: 0; min-height: 100vh; }

img,
picture,
video,
canvas,
svg { display: block; max-width: 100%; }

input,
button,
textarea,
select { font: inherit; }

button { cursor: pointer; }

:focus-visible {
  outline: 3px solid #8262d7;
  outline-offset: 3px;
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

按项目需要增删，不要把不同设计系统、框架和第三方库的初始化规则无脑合并。

> 更多可复制实现见 [常见布局方案](21-recipes.md)。
