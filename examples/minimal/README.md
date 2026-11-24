# 概念课最小 demo

对应 [CSS 概念课](../../docs/course/README.md) 的 12 篇教程。每个文件只演示一个概念，只有 1–2 个可调参数，都带"先预测 → 揭晓核对"环节。单文件、无依赖，双击即可打开。

| demo | 对应章节 | 要预测什么 |
| --- | --- | --- |
| [01-computed.html](01-computed.html) | [从规则到像素](../../docs/course/01-pipeline.md) | 切换冲突声明后，占位宽度增加多少？ |
| [02-cascade.html](02-cascade.html) | [谁说了算](../../docs/course/02-cascade.md) | 层、`!important`、书写顺序依次开启时，谁赢？ |
| [03-inheritance.html](03-inheritance.html) | [值从哪里来](../../docs/course/03-inheritance.md) | 哪个关键字让边框色跟随父元素？ |
| [04-box-model.html](04-box-model.html) | [元素到底占多大](../../docs/course/04-box-model.md) | padding 增加 10px，两种 box-sizing 各增加多少？ |
| [05-containing-block.html](05-containing-block.html) | [百分比是谁的百分比](../../docs/course/05-containing-block.md) | 切换 absolute 后，50% 宽度增加多少？ |
| [06-bfc.html](06-bfc.html) | [为什么布局会塌](../../docs/course/06-bfc.md) | 建立 BFC 后父元素高度怎么变？ |
| [07-stacking-context.html](07-stacking-context.html) | [谁盖住谁](../../docs/course/07-stacking-context.md) | z-index 9999 能否盖住更高家族里的元素？ |
| [08-flex-space.html](08-flex-space.html) | [一维空间怎么分](../../docs/course/08-flex.md) | 600px 容器里第一项最终多少像素？ |
| [09-grid.html](09-grid.html) | [二维空间怎么画](../../docs/course/09-grid.md) | 150px 1fr 2fr 时，1fr 轨道分到多少？ |
| [10-container-query.html](10-container-query.html) | [组件自己的断点](../../docs/course/10-container-query.md) | 小于 420px 断点时卡片是几列？ |
| [11-units.html](11-units.html) | [单位各以谁为参照](../../docs/course/11-units.md) | 调大根字号后哪个单位的像素值不变？ |
| [12-rendering.html](12-rendering.html) | [变化如何发生](../../docs/course/12-rendering.md) | 改 width 还是改 transform 不会让兄弟元素位移？ |

交互式学习站 [course-site/index.html](../../course-site/index.html) 已把这些 demo 内嵌到对应章节旁边；也可以单独打开某个 demo 做快速验证。
