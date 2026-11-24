# 17 · 渲染性能与调试

> 学习目标：知道哪些操作昂贵、如何用 Performance 与 DevTools 定位布局抖动和绘制问题，并形成可重复的 CSS 排查流程。

## 1. 浏览器渲染不是一次性完成

```text
样式变更
  ↓
样式计算
  ↓
布局 Layout（必要时）
  ↓
绘制 Paint（必要时）
  ↓
合成 Composite
```

不是每次样式变化都会完整走完四步，但理解失效范围能帮助你选择更好的实现。

## 2. 重排、重绘与合成

| 操作 | 常见例子 | 成本与特点 |
| --- | --- | --- |
| 重排 Layout | width、height、top、left、margin、font-size | 重新计算几何信息，可能影响其他元素 |
| 重绘 Paint | color、background、box-shadow | 几何不变，但需要重新绘制像素 |
| 合成 Composite | transform、opacity（满足条件时） | 通常由已有图层合成，但不保证永远无重绘 |

### 昂贵写法

```css
.item {
  transition: width 300ms, height 300ms, top 300ms;
}
```

宽度变化会影响内部文字换行和兄弟布局，动画期间可能每帧触发布局。

### 通常更优的写法

```css
.item {
  transform-origin: left center;
  transition: transform 300ms ease;
  will-change: transform;
}

.item.is-expanded {
  transform: scaleX(1);
}
```

视觉上可能相似，但 transform 不改变布局尺寸。若展开内容必须可访问、可复制或参与布局，不能仅用 scale 掩盖内容。

## 3. transform 与 opacity 的边界

`transform` 并不总是不触发布局之外的阶段。大面积图层、模糊滤镜、复杂 3D、过多图层仍可能增加显存和合成成本。

`opacity` 动画常可走合成，但祖先透明度改变也可能影响渲染策略。

```css
/* 不推荐长期滥用 */
.everything { will-change: transform, opacity; }
```

`will-change` 会提示浏览器提前准备图层。只用于即将发生变化的少量元素，动画结束后移除。

## 4. 布局抖动 Layout Thrashing

在同一个同步任务中交替读取布局、写入样式，会迫使浏览器反复计算：

```js
// 反模式
for (const el of elements) {
  el.style.width = el.offsetWidth + 10 + 'px';
}
```

```js
// 先批量读取，再批量写入
const widths = elements.map(el => el.offsetWidth);
elements.forEach((el, index) => {
  el.style.width = widths[index] + 10 + 'px';
});
```

更现代的方案是使用 `requestAnimationFrame` 批量处理视觉更新，或使用 Web Animations API 管理动画。

## 5. 长任务与交互响应

大量同步 DOM 操作、复杂选择器、超大树和昂贵滤镜都可能拖慢交互。CSS 选择器本身通常不是首要瓶颈，不要过早优化到牺牲可读性。

优先检查：

- 一次更新是否改动了几千个节点。
- 是否有无限 CSS 动画在屏幕外运行。
- 是否创建了超大滤镜、阴影或模糊区域。
- 是否有频繁读取 offset/Top 等布局信息。
- 图片是否缺少尺寸导致加载后页面跳动。

## 6. 使用 Performance 面板

1. 打开 DevTools → Performance，开启 Screenshots。
2. 点击 Record，执行卡顿操作，停止录制。
3. 查看 Main 主线程火焰图。
4. 寻找黄色 Layout、紫色 Recalculate Style、绿色 Paint 等片段。
5. 放大长任务，查看调用栈与耗时。
6. 优化后使用相同操作、相同环境重复录制。

```text
一次交互
├── Recalculate Style  30ms
├── Layout             80ms
├── Paint              20ms
└── Composite          4ms
```

重点关注是否存在本可避免的重复 Layout。单个数值没有统一“安全线”，应结合设备、帧预算与真实体验判断。

## 7. 使用 Rendering 面板

打开 More tools → Rendering，可检查：

- Paint flashing：重绘区域。
- Layout Shift Regions：布局偏移区域。
- Frame rendering stats：帧耗时。
- Layer borders：图层边界。
- Emulate CSS media feature：模拟 prefers-color-scheme、reduced-motion。

## 8. CLS：累计布局偏移

图片、广告、异步模块如果没有尺寸，加载后会推动内容：

```css
.media {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

```html
<img src="banner.jpg" alt="活动横幅" width="1600" height="900" />
```

HTML 的 width/height 属性可提供宽高比，帮助浏览器提前预留空间。CSS 仍需确保响应式显示。

## 9. content-visibility

```css
.offscreen-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 600px;
}
```

`content-visibility: auto` 允许浏览器跳过屏幕外内容的渲染工作。需要给一个合理的内在尺寸估值，否则滚动条尺寸和锚点跳转可能不稳定。

`contain` 相关属性也能建立性能与布局边界，但过强隔离可能改变百分比、absolute 或 sticky 的参照，使用前需要验证。

## 10. 实用优化清单

- 动画优先 transform/opacity。
- 避免动画 box-shadow、filter 等昂贵效果，或限制范围。
- 图片提供尺寸，避免加载后布局跳动。
- 使用 CSS 变量批量修改主题，但不要建立过深变量依赖。
- 用 `gap` 代替大量 margin。
- 避免过大的模糊、多层阴影与全屏混合模式。
- 屏幕外无限动画考虑暂停。
- 不在滚动事件中同步读取和写入布局。
- 使用 `content-visibility` 前测试滚动体验。

## 11. 系统化调试流程

### 元素位置不对

1. 检查 `position`。
2. 查找最近包含块。
3. 检查父级 transform/overflow。
4. 检查 inset 与 margin/padding。
5. 检查 writing-mode 与逻辑属性。

### 尺寸不对

1. 查看 Computed width/height。
2. 检查 box-sizing。
3. 检查 min/max 尺寸。
4. 检查 flex-basis/flex-shrink 或 Grid 轨道。
5. 检查是否被内容撑开。

### 样式没生效

1. 选择器是否命中。
2. 声明是否被划掉。
3. 是否有同优先级后续规则。
4. 是否被 shorthand 重置。
5. 属性值是否合法。
6. 是否处于更高 @layer 或被 important 覆盖。
7. 是否有动画或 transition 覆盖。

### 页面横向滚动

1. 用 DevTools 查找 scrollWidth 大于 clientWidth 的元素。
2. 检查固定宽度、长文本、图片、transform 越界。
3. 检查 Grid `1fr` 的最小内容尺寸。
4. 检查 Flex item 的 min-width: auto。
5. 修复根因，不要直接用 body overflow-x: hidden 掩盖。

## 关联示例

- [性能容器与长列表](../../examples/engineering/performance-containment.html)：`content-visibility`、`contain-intrinsic-size` 与 `contain` 副作用。

## 12. 练习

1. 录制一个 left 动画和一个 transform 动画，比较 Performance 中 Layout 活动。
2. 用 Paint flashing 找出页面中不必要的重绘区域。
3. 给异步加载图片预留 16:9 空间，并观察 CLS 提示。
4. 写一个布局抖动示例，再通过先读后写修复。
5. 为一个长页面使用 content-visibility，验证滚动条、锚点和搜索体验。

> 下一篇：[CSS 架构与工程化](../06-engineering/18-architecture.md)。
