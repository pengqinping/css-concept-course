# 21 · 表格：语义先于视觉

> **前置**：知道第 05 篇的 `border` 是盒的一层、会占实际宽度；知道第 06 篇的包含块决定百分比以谁为基准。表格的行列语义由 HTML 给，不依赖 Flex / Grid 的布局模型。
>
> 上一篇：[表单控件与状态](20-forms.md) ｜ [本阶段目录](README.md)

## 1. 本章目标

- 能给订单表写出 `caption`、`thead` 的 `th scope="col"` 与 `tbody` 的 `th scope="row"`，并说明读屏软件读到金额时会同时听到什么。
- 能解释同样写 `border: 1px solid`，`separate` 下相邻两格显示 2px、`collapse` 下显示 1px 的原因。
- 能预测 `collapse` 下 `3px solid` 遇到邻格 `3px double` 谁赢，并说出裁决顺序。
- 能用 `table-layout: fixed; width: 600px`（列宽 100 / 200 / 300）预测往第二列塞 200 个连续字母后的结果。

**为什么现在学这个**：第 20 篇把控件语义讲清；表格同样先有语义再谈视觉，否则"画得像"会冒充"结构对"。第 22 篇的原生弹层延续同一原则：把行为交给浏览器。

## 2. 新增模型

看这段代码：

```html
<table class="sheet">
  <tr><td>姓名</td><td>邮箱</td></tr>
  <tr><td>林晓</td><td>lin@example.com</td></tr>
</table>
```

```css
.sheet td { border: 1px solid #c9d2d7; }
```

看着像表格，读屏软件却念不出"第一行是表头"：没有 `thead`、没有 `th`、没有 `caption`，"姓名"只是一个普通单元格。你以为画了网格就等于做了表格，实际 CSS 画出来的只是线，**结构信息一条都没生成**。另一个现象：给单元格写 `border: 1px solid` 后相邻两格之间出现 2px 双线，改成 `border-collapse: collapse` 才变成 1px——同样写 1px，线却不一样粗。

**模型：行列关系、表头关联和序号来自 HTML 与浏览器算法，CSS 只改算法的参数——别拿视觉冒充结构。**

![两种边框模型与列宽决策](figures/21-tables.svg)

*图 21-1 · 两种边框模型与列宽决策*

图的左半边是 `separate`：每个格子自带完整边框，相邻两条并排，中间隔着 `border-spacing`，所以 1px + 1px 看起来是 2px；右半边是 `collapse`：相邻边框合并成一条，宽度相同时按样式优先级裁决。下半部分是表头关联：读到 ¥ 328.00 时，读屏软件靠 `th scope="col"` 同时念出"金额"；CSS 画的线不进可访问性树。

**这张图的一句话结论：结构由 `table` / `th scope` / `caption` 决定，线和列宽由 `border-collapse` 与 `table-layout` 的算法决定。**

术语落地：

- **表头关联**：`th` 加 `scope` 让读屏软件在念数据时同时念出列头或行头，视觉样式做不到这件事。
- **边框冲突裁决**：`collapse` 模式下相邻边框合并时，决定哪一条胜出的规则。
- **序号计数器**：CSS 计数器在元素上递增、在伪元素里输出，用于生成序号文本。

## 3. 可运行的 demo

先切换一次边框模式，看线怎么变，再读下面的裁决规则。带着"为什么 spacing 明明写着却不生效"的疑问往下走，会比先背属性有效得多。

[打开 demo：切换边框与布局，看线和列宽怎么变](../../examples/minimal/21-tables.html)

<iframe class="demo-frame" src="/css-concept-course/examples/minimal/21-tables.html" title="切换边框与布局，看线和列宽怎么变" loading="lazy"></iframe>

> **先预测**：表格声明 `border-spacing: 6px`，相邻两格都写 `border: 1px solid`。把 `border-collapse` 从 `separate` 切到 `collapse`，相邻两格的盒间距从 6px 变成多少？哪种模式画的是单线共享？
>
> **验证**：拖动"使用 border-collapse: collapse"开关，核对页面"状态（浏览器实测）"里的"相邻两格盒间距"与"border-spacing 是否生效"两行读数。

如果你看到间距从 6px 跳到 0px、而 `border-spacing` 的声明值还写着 6px，说明你已经抓住"声明不等于生效"的要害。

## 4. 原理与规则

### 4.1 语义来自 HTML 标签

`caption` 给表格命名，`thead` / `tbody` 分组，`th scope="col"` 声明"这一格是整列的表头"，`th scope="row"` 声明"这一格是整行的表头"。

```html
<table class="sheet">
  <caption>本周订单</caption>
  <thead><tr><th scope="col">订单号</th><th scope="col">金额</th></tr></thead>
  <tbody>
    <tr><th scope="row">#1042</th><td>¥ 328.00</td></tr>
  </tbody>
</table>
```

**为什么不能用背景色和粗体代替 `th`？** 读屏软件靠 `th` + `scope` 建立"表头—数据"的对应关系，用户读到 ¥ 328.00 时才能同时听到"金额"。视觉样式不进入可访问性树，画得再像也只是装饰。复杂表里若 `scope` 不足以表达多对一关系，再给表头加 `id`、给单元格加 `headers` 引用这些 id——依旧是 HTML 层的事，CSS 帮不上忙。

**失效条件**：把 `th` 换成 `td` 或只靠背景色 / 粗体时，视觉还在但可访问性树里没有表头关联；`caption` 可以视觉隐藏，但不能从辅助技术里删掉，否则表格没有名字。

### 4.2 border-collapse 决定边框归谁

`separate`（默认）时每个单元格画自己的完整边框，两条相邻边框并排，中间还隔着 `border-spacing`。`collapse` 时相邻边框合并成一条：

```css
.sheet { border-collapse: collapse; }
.sheet th, .sheet td { border: 1px solid #c9d2d7; }
```

| 对照项 | `separate`（默认） | `collapse` |
| --- | --- | --- |
| 相邻边框 | 两条各自独立、并排 | 合并成一条 |
| `border-spacing` | 生效，控制格间距 | 无效 |
| `border-radius` | 单元格圆角正常 | 常失去预期圆角 |

合并不是"取平均"，而是一场冲突裁决：先淘汰 `hidden`（`none` 不参与），再选 `border-width` 更大的，宽度相同才比样式优先级 `double > solid > dashed > dotted`。

**为什么要记这套顺序？** 这样你才能解释"我明明给这格写了 `3px solid`，显示出来却是 `3px double`"——是邻格的 `3px double` 赢了，不是你的样式没生效。`separate` 也要记住，因为它才是默认值；不少"边框对不齐"的根源是只按折叠模式写了一半样式，却忘了两组属性在两种模式下含义不同。

**失效条件**：`border-spacing` 在 `collapse` 下虽然还写在声明里但完全无效；`border-radius` 在折叠表格上常失去预期圆角；"3px solid 显示成 3px double"是邻格胜出，别回头去改自己的 `border` 值。

### 4.3 列宽由 table-layout 与内容共同决定

```css
.sheet { table-layout: fixed; width: 600px; }
.sheet col:nth-child(1) { width: 100px; }
.sheet col:nth-child(2) { width: 200px; }
.sheet col:nth-child(3) { width: 300px; }
```

`fixed` 先看表格与首行（或 `col`）声明的宽度，列宽立刻确定：100 / 200 / 300，加起来正好 600px。后面单元格文字再长也不改变列宽，超出的内容要靠 `overflow-wrap` 或容器滚动处理。

`auto` 则要先读完所有单元格的内容才算列宽，`<td>` 里一段特别长的文字会把所在列撑宽，其他列被压缩。

**为什么 `auto` 要读完整张表？** 列宽取决于所有行里最宽的那格内容，浏览器必须缓冲整张表才能定轨道；内容多的表因此先渲染慢、再跳动。`fixed` 的代价是"不迁就内容"，换来的是只扫首行、列宽可预测。

**失效条件**：`fixed` 不迁就内容，200 个连续字母在 200px 列里会溢出或换行，不会把列撑宽，需要 `overflow-wrap` 或容器横向滚动兜底；`fixed` 也不等于响应式，窄屏下列宽仍固定，必须重新设计结构或允许滚动。

### 4.4 序号是数出来的，不是写出来的

CSS 计数器三个动作：在祖先上 `counter-reset` 建立并重置计数器，在每个项目上 `counter-increment` 递增，在伪元素里 `content: counter(名字)` 输出。

```css
.steps { counter-reset: step; list-style: none; }
.steps li { counter-increment: step; }
.steps li::before { content: counter(step) "."; }
```

`counter-reset: step` 从 0 起，第一项递增后输出 1、第二项 2、第三项 3。想从 5 开始写 `counter-reset: step 4`，第一项输出 5；嵌套结构用 `counters()` 输出多级编号。`counter-reset` 的作用域从声明它的元素延伸到后代与后续兄弟，嵌套列表里每层各自重置，内层序号才不会把外层带跑。

**为什么有时用 `::before` 而不是原生 marker？** 需要绝对定位的圆形序号时才用 `::before`；普通圆点直接用 `list-style` 和 `::marker` 更省事。`::marker` 能改颜色、字体，但不能像普通伪元素那样任意定位或加背景。

**失效条件**：`content` 生成的文字不保证进入可访问名称，"警告""必填"这类关键含义不能只写在生成内容里；普通圆点、`decimal` 序号用原生列表已经够了，动计数器只会多一层维护成本。

顺带一句历史用途：Flex / Grid 普及前，`display: table` / `table-cell` 常被借来做等高列和垂直居中；现在遇到这种需求优先用 Grid / Flex。

## 5. 常见坑

**坑 1：画成网格就当成表格**

- **原因**：语义来自 `table` / `th scope` / `caption`，CSS 只画视觉；`div` 画得再像也没有表头关联。
- **确认**：看可访问性树，读单元格时有没有同时出现列头名称。
- **修法**：补 `table`、`thead`、`th scope` 与 `caption`；代价是不能再用纯 `div` 的任意结构。

**坑 2：`border-collapse: collapse` 只是去掉一条线**

- **原因**：它触发边框冲突裁决，`border-spacing` 同时失效，圆角也可能丢失。
- **确认**：demo 里切到 collapse，"相邻两格盒间距"从 6px 变 0px，"border-spacing 是否生效"显示否。
- **修法**：明确接受单线共享与 spacing 失效；想保留 6px 格距就留在 `separate`，代价是双线视觉。

**坑 3：`table-layout: fixed` 等于响应式**

- **原因**：它固定的是列宽算法，超长内容仍会溢出。
- **确认**：窄屏下看 `scrollWidth > clientWidth`，或看 200 字母那列是否撑破 200px。
- **修法**：配 `overflow-wrap: anywhere` 或横向滚动，窄屏重新设计结构；`auto` 会读完整张表再定列宽，大表会先慢后跳动。

## 6. 练习

1. **基础**：写一个三列订单表，含 `caption`、`thead` 的 `th scope="col"` 和 `tbody` 每行的 `th scope="row"`。
   验收：在无障碍树里读 ¥ 328.00 时能听到"金额"这个列头；`caption` 显示为表格标题。

2. **基础**：相邻两格都写 `border: 3px solid`，再把第二格的 `border-left` 改成 `3px double`，设 `border-spacing: 0`，分别看 `separate` 与 `collapse`。
   验收：`separate` 下两格之间是并排两条 3px 边框（共 6px）；`collapse` 下合并为一条 3px double，因为宽度相同而 `double` 的优先级高于 `solid`。

3. **进阶**：写 `table-layout: fixed; width: 600px`，用 `col` 定 100 / 200 / 300，再往第二列塞 200 个连续字母。
   验收：三列仍为 100 / 200 / 300px；字母在 200px 列里溢出或换行（取决于 `overflow-wrap`），不会把列撑宽。

4. **进阶**：写 `counter-reset: step 4` 的列表，再写一层嵌套列表用 `counters()`。
   验收：外层第一项输出 5、第二项 6；嵌套层用 `counters()` 输出 `5.1` 这样的多级编号，内层重置不会把外层序号带跑。

5. **挑战**：不改 HTML，只用 CSS 把第 2 段代码那张表改成"1px 线、格距 6px"，同时保持读屏能听到列头。
   验收：computed `border-collapse` 为 `separate`、`border-spacing` 为 6px、相邻两格实测间距 6px；`th scope="col"` 仍存在于可访问性树中。

> 下一篇：[原生弹层](22-native-ui.md)
