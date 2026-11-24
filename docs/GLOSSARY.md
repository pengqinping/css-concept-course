# CSS 术语表

> 快速回忆用。每个术语都对应一个可观察的行为或约束；深入解释请回到正文章节。

| 术语 | 含义 | 相关章节 |
| --- | --- | --- |
| DOM | HTML 解析出的节点树，表达内容与结构 | [工作原理](01-foundations/01-how-css-works.md) |
| CSSOM | CSS 解析出的样式规则树 | [工作原理](01-foundations/01-how-css-works.md) |
| UA 样式 | 浏览器提供的默认样式 | [工作原理](01-foundations/01-how-css-works.md) |
| 层叠 Cascade | 多条声明竞争时决定最终值的过程 | [层叠与继承](01-foundations/03-cascade-inheritance.md) |
| 来源 Origin | 作者、用户、用户代理等样式来源 | [层叠与继承](01-foundations/03-cascade-inheritance.md) |
| 层 Layer | `@layer` 建立的显式优先级顺序 | [层叠与继承](01-foundations/03-cascade-inheritance.md) |
| 优先级 Specificity | 选择器优先级的三组计数 | [选择器](01-foundations/02-selectors.md) |
| 继承 Inheritance | 子元素获得父元素某些计算值 | [层叠与继承](01-foundations/03-cascade-inheritance.md) |
| 自定义属性 | 以 `--` 开头、可通过 `var()` 使用的变量 | [层叠与继承](01-foundations/03-cascade-inheritance.md) |
| 设计令牌 | 表达颜色、间距、字体等设计决策的变量 | [CSS 工程化](06-engineering/18-architecture.md) |
| 包含块 Containing block | 尺寸与位置计算的参照盒 | [盒模型](01-foundations/04-box-model.md) |
| 内容盒 Content box | 内容所在区域 | [盒模型](01-foundations/04-box-model.md) |
| 内边距 Padding | 内容与边框之间的空间 | [盒模型](01-foundations/04-box-model.md) |
| 外边距 Margin | 盒子外部的空间 | [盒模型](01-foundations/04-box-model.md) |
| 自动最小尺寸 | Flex/Grid 项目避免过度收缩的内容尺寸 | [Flexbox](03-layout/10-flexbox.md) |
| 普通流 Normal flow | 默认的块级与行内排列方式 | [文档流](03-layout/08-normal-flow.md) |
| BFC | 块级格式化上下文，可隔离布局与 margin | [文档流](03-layout/08-normal-flow.md) |
| IFC | 行内格式化上下文 | [文档流](03-layout/08-normal-flow.md) |
| FFC | Flex 格式化上下文 | [Flexbox](03-layout/10-flexbox.md) |
| GFC | Grid 格式化上下文 | [Grid](03-layout/11-grid.md) |
| 格式化上下文 | 定义一组子盒如何布局的环境 | [文档流](03-layout/08-normal-flow.md) |
| margin 折叠 | 普通流中相邻垂直 margin 合并 | [文档流](03-layout/08-normal-flow.md) |
| 主轴 Main axis | Flex 项目排列与分配空间的主要方向 | [Flexbox](03-layout/10-flexbox.md) |
| 交叉轴 Cross axis | 与 Flex 主轴垂直的方向 | [Flexbox](03-layout/10-flexbox.md) |
| flex line | Flex 换行后的一行项目集合 | [Flexbox](03-layout/10-flexbox.md) |
| 轨道 Track | Grid 的行或列空间 | [Grid](03-layout/11-grid.md) |
| 网格线 Grid line | 轨道之间的分界线 | [Grid](03-layout/11-grid.md) |
| 隐式轨道 | 自动放置生成的额外行或列 | [Grid](03-layout/11-grid.md) |
| subgrid | 子网格继承外层部分轨道的机制 | [Grid](03-layout/11-grid.md) |
| 查询容器 | 为 `@container` 提供尺寸或样式条件的祖先 | [容器查询](03-layout/12-container-queries.md) |
| 媒体查询 | 根据视口、设备或用户偏好应用规则 | [响应式设计](04-responsive/13-responsive-design.md) |
| 断点 Breakpoint | 布局规则发生切换的尺寸条件 | [响应式设计](04-responsive/13-responsive-design.md) |
| 移动优先 | 先写窄屏基础样式，再逐步增强 | [响应式设计](04-responsive/13-responsive-design.md) |
| 逻辑属性 | 用 inline/block 描述方向的属性 | [排版](02-visual/05-typography.md) |
| 替换元素 | 内容由外部资源决定，如图片、视频 | [视觉格式](02-visual/07-formatting-overflow.md) |
| 内在尺寸 | 由内容或资源本身决定的尺寸 | [视觉格式](02-visual/07-formatting-overflow.md) |
| 层叠上下文 | 独立参与绘制与 z-index 排序的环境 | [定位与层叠](03-layout/09-positioning-stacking.md) |
| 包含块祖先 | 为定位元素提供参照的祖先 | [定位与层叠](03-layout/09-positioning-stacking.md) |
| 变换 Transform | 在布局后改变视觉坐标系 | [变换](05-advanced/15-transforms.md) |
| 过渡 Transition | 状态变化时的属性补间 | [动画](05-advanced/16-animation.md) |
| 关键帧 | 定义动画中间状态的时间点 | [动画](05-advanced/16-animation.md) |
| 合成 Composite | 将图层组合成最终画面 | [性能](05-advanced/17-performance-debugging.md) |
| 重排 Layout | 重新计算元素几何信息 | [性能](05-advanced/17-performance-debugging.md) |
| 重绘 Paint | 重新生成像素绘制结果 | [性能](05-advanced/17-performance-debugging.md) |
| 布局抖动 | 交替读写布局导致重复计算 | [性能](05-advanced/17-performance-debugging.md) |
| CLS | 累计布局偏移，衡量非预期视觉移动 | [性能](05-advanced/17-performance-debugging.md) |
| 渐进增强 | 先保证核心内容，再按支持程度增强 | [兼容与无障碍](06-engineering/19-compatibility-accessibility.md) |
| 特性检测 | 使用 `@supports` 等判断能力是否可用 | [兼容与无障碍](06-engineering/19-compatibility-accessibility.md) |
| 焦点可见性 | 明确显示键盘当前聚焦位置 | [兼容与无障碍](06-engineering/19-compatibility-accessibility.md) |
| 减弱动态效果 | 尊重用户减少非必要动画的系统偏好 | [兼容与无障碍](06-engineering/19-compatibility-accessibility.md) |
| 多列布局 | 用 `column-count` / `column-width` 等把连续内容自动分栏；不是 Grid，也不等于打印分页 | [补充属性与专题](07-reference/27-additional-properties.md) |
| 形状环绕 | 浮动元素用 `shape-outside` / `shape-margin` 改变文字避让轮廓，不裁剪自身绘制 | [补充属性与专题](07-reference/27-additional-properties.md) |
| 混合模式 | 按像素运算合成颜色；`mix-blend-mode` 作用于元素与背景，`background-blend-mode` 作用于背景层 | [补充属性与专题](07-reference/27-additional-properties.md) |
| 隔离 | `isolation: isolate` 建立层叠与混合边界，不裁剪、不建立 BFC，也不等于 `contain` | [补充属性与专题](07-reference/27-additional-properties.md) |
| 滚动吸附 | 用 `scroll-snap-type` / `scroll-snap-align` 让滚动容器停在预设停止点；不是分页逻辑 | [现代 CSS 特性](07-reference/24-modern-features.md) |
| 容器单位 | `cqw` / `cqi` 等以查询容器尺寸为基准的长度；不是 `vw` 或百分比 | [单位与函数](04-responsive/14-units-functions.md) |
| 锚点定位 | 用 `anchor-name` / `position-anchor` / `position-area` 让浮层跟随命名元素，并保留基础定位回退 | [现代 CSS 特性](07-reference/24-modern-features.md) |
| 视图过渡 | 用 `document.startViewTransition()` 捕获旧、新视图，再由 `::view-transition` 伪树定义动画 | [现代 CSS 特性](07-reference/24-modern-features.md) |
| Shadow DOM | 附着在元素上的独立文档树，隔离 DOM 查询和多数作者样式，但继承属性、自定义属性与事件仍可跨界 | [补充属性与专题](07-reference/27-additional-properties.md) |
| `::part()` | 按影子树内部显式 `part` 名称暴露的样式入口，不公开整个组件结构 | [补充属性与专题](07-reference/27-additional-properties.md) |
| 打印分页 | 浏览器把文档切成纸张页面的过程，由 `@page`、`break-*`、`orphans` / `widows` 等共同影响 | [打印与分页媒体](07-reference/25-print-paged-media.md) |

> 返回 [文档首页](README.md)。
