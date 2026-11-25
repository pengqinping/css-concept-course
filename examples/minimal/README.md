# 技术教程最小 demo

对应 [CSS 技术教程](../../docs/course/README.md) 的 30 篇正文。每个文件只演示一个模型，只有 1–2 个可调参数，都带"先预测 → 揭晓核对"环节。单文件、无依赖，双击即可打开。

| demo | 对应章节 | 演示什么 | 先预测什么 |
| --- | --- | --- | --- |
| [01-computed.html](01-computed.html) | [01 · 从规则到像素](../../docs/course/01-pipeline.md) | 改一条声明，看四道关哪道被触发 | 给一个已有元素分别改 width、color、transform，哪一次会触发布局、哪次只触发绘制、哪次可能… |
| [02-selectors.html](02-selectors.html) | [02 · 精准找到元素](../../docs/course/02-selectors.md) | 把选择器拆成筛选关卡 | 把 .post > p 改成 .post p，那个嵌在 <blockquote> 里的 p 会不会被选中？ |
| [03-cascade.html](03-cascade.html) | [03 · 谁说了算](../../docs/course/03-cascade.md) | 三个开关，看胜出声明怎么变 | 只开启「后写规则」时按钮是什么颜色？ |
| [04-inheritance.html](04-inheritance.html) | [04 · 值从哪里来](../../docs/course/04-inheritance.md) | 切换关键字，看值怎么在父子间流动 | 父元素设 color: #16794a; border: 2px solid #b8860b，子元素分别用 … |
| [05-box-model.html](05-box-model.html) | [05 · 元素到底占多大](../../docs/course/05-box-model.md) | 调 padding 和 border，实时算占位宽度 | width: 300px 固定，把 padding 从 0 调到 20px、border 从 0 调到 5px。 |
| [06-containing-block.html](06-containing-block.html) | [06 · 百分比是谁的百分比](../../docs/course/06-containing-block.md) | 切换 position，看 50% 换尺子 | 把子元素从 static 改成 absolute（父元素带 400px content、20px paddi… |
| [07-bfc.html](07-bfc.html) | [07 · 为什么布局会塌](../../docs/course/07-bfc.md) | 一键切换边界，看 margin 和浮动怎么变 | 打开「BFC 开关」后，父元素的位置会下移还是内部出现空隙？ |
| [08-stacking-context.html](08-stacking-context.html) | [08 · 谁盖住谁](../../docs/course/08-stacking-context.md) | 9999 逃不出父级 | 把 .a 的 z-index 从 1 改到 3，9999 会不会赢？ |
| [09-typography.html](09-typography.html) | [09 · 文字如何排成节奏](../../docs/course/09-typography.md) | 把固定行高换成无单位数 | 父级 font-size: 16px、line-height: 28px 时，一个 font-size: 3… |
| [10-color.html](10-color.html) | [10 · 颜色如何表达](../../docs/course/10-color.md) | 把文字放到真实背景上算对比度 | 把 #3f6b2a 与白按 50:50 混合后的颜色当作白底上的文字色，对比度大约是多少？ |
| [11-background-border.html](11-background-border.html) | [11 · 表面画在哪一层](../../docs/course/11-background-border.md) | 切换裁剪区域与阴影来源 | 把 background-clip 从 border-box 改为 padding-box，那圈 10px … |
| [12-display-overflow.html](12-display-overflow.html) | [12 · 看见与看不见](../../docs/course/12-display-overflow.md) | 四种隐藏方式，谁还占位、谁还能点 | 把浮层从 opacity: 0 改成 visibility: hidden，底下的按钮能点了吗？ |
| [13-transform.html](13-transform.html) | [13 · 视觉变形](../../docs/course/13-transform.md) | 调角度，核对从右往左的落点 | rotate(30deg) translateX(100px) 的元素中心最终落在哪里（相对原点的 x, y）？ |
| [14-animation.html](14-animation.html) | [14 · 状态的变化](../../docs/course/14-animation.md) | 把 duration 调到 0，看插值怎么消失 | 一个方块从浅色过渡到深色，transition-duration 为 300ms 时中途出现灰；把它拖到 0… |
| [15-flex-space.html](15-flex-space.html) | [15 · 一维空间怎么分](../../docs/course/15-flex.md) | 拖动容器宽度，看每一项实际分到多少 | 容器 600px、gap 16px、三项 basis 各 100px、grow 为 2:1:1 时，第一项最… |
| [16-grid.html](16-grid.html) | [16 · 二维空间怎么画](../../docs/course/16-grid.md) | 改模板，看轨道怎么变 | 容器宽 600px、grid-template-columns: 150px 1fr 2fr、gap: 12… |
| [17-container-query.html](17-container-query.html) | [17 · 组件自己的断点](../../docs/course/17-container-query.md) | 拖动容器宽度，看同一张卡片重排 | 一个 container-type: inline-size 的容器，初始宽 320px，卡片用 @cont… |
| [18-units.html](18-units.html) | [18 · 长度以谁为参照](../../docs/course/18-units.md) | 同屏显示各类单位的实时计算值 | 根字号 16px、视口宽 1000px，一个 400px 宽的查询容器里，1.5rem、1.5em（元素自身… |
| [19-responsive.html](19-responsive.html) | [19 · 从视口到组件](../../docs/course/19-responsive.md) | 拖动视口宽度，看断点在哪一像素生效 | 卡片在视口 900px 时两列、700px 时一列，断点写在 min-width: 46rem（根字号 16… |
| [20-forms.html](20-forms.html) | [20 · 表单控件与状态](../../docs/course/20-forms.md) | 切换状态，看哪个伪类先亮 | 一个空的必填邮箱框，页面刚打开时 :invalid 和 :user-invalid 哪个命中？ |
| [21-tables.html](21-tables.html) | [21 · 表格：语义先于视觉](../../docs/course/21-tables.md) | 切换边框与布局，看线和列宽怎么变 | 把 border-collapse 从 separate 切到 collapse，相邻两格之间的边框厚度会从… |
| [22-native-ui.html](22-native-ui.html) | [22 · 原生弹层](../../docs/course/22-native-ui.md) | 三种弹层逐个开，看焦点和背景怎么变 | 打开模态 dialog 后，Tab 会不会跑到背景里的按钮？ |
| [23-architecture.html](23-architecture.html) | [23 · 样式架构与设计令牌](../../docs/course/23-architecture.md) | 改一处，看影响范围有多大 | 把一条 .card__title 规则改成全局 h2 { ... }，页面上原本不受影响的标题会不会变色？ |
| [24-accessibility.html](24-accessibility.html) | [24 · 页面是给谁用的](../../docs/course/24-accessibility.md) | 删掉 outline 之后，谁还能完成任务 | 一个按钮同时删掉 outline、把菜单改成只在 :hover 出现、给文字加 opacity: 0.6。 |
| [25-rendering.html](25-rendering.html) | [25 · 变化如何发生](../../docs/course/25-rendering.md) | width 与 transform，同一段位移两种代价 | 两根绿条从 120px 变到 300px，哪一根会在 Performance 的 Main 轨道里出现 La… |
| [26-scope-nesting.html](26-scope-nesting.html) | [26 · 谁真的缩小了范围](../../docs/course/26-scope-nesting.md) | 三个轴，各切一次 | 把 .card { & button { color: red } } 展开成扁平选择器后，嵌在卡片里的第三… |
| [27-modern-features.html](27-modern-features.html) | [27 · 让浏览器替你算](../../docs/course/27-modern-features.md) | 关掉原生能力，看谁还在算 | 一个跟随按钮的提示框，关掉锚点定位后它会掉回哪里？ |
| [28-print.html](28-print.html) | [28 · 屏幕上的长页，怎么落到有限的纸上](../../docs/course/28-print.md) | 段落数与 break-inside，看断点落在哪里 | 模拟页面区高 480px，每段 40px，图块 160px。 |
| [29-shapes-mix.html](29-shapes-mix.html) | [29 · 分栏、绕行与叠色，各管一层](../../docs/course/29-shapes-mix.md) | 切换 isolation，看图片跟谁混色 | 图片设了 mix-blend-mode: multiply，卡片背景米色、页面背景深绿。 |
| [30-component-boundary.html](30-component-boundary.html) | [30 · 状态何时成立，样式到哪里为止](../../docs/course/30-component-boundary.md) | 两道开关，看谁改得动影子树里的按钮 | 页面写 button { color: red }，影子树内部按钮会变红吗？ |

在线教程 <https://pengqinping.github.io/css-concept-course/> 已把这些 demo 内嵌到对应章节旁边；也可以单独打开某个 demo 做快速验证。
