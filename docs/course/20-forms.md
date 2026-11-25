# 20 · 表单控件与状态

> 一句话模型：表单控件先是一个带语义和行为的原生部件，CSS 只是在它已有的外观与状态上做增量覆盖——先接受，再决定要不要接管；伪类也不是同义反复，它们在不同的时机点亮。

## 先看一个现象

一个必填邮箱框，刚打开页面就红了：

```css
input:invalid { border: 2px solid #b42318; }
```
```html
<input id="email" type="email" required />
```

用户还没碰过它，空值当然不满足约束，于是 `:invalid` 立刻命中。你以为在提示错误，其实在冤枉用户。

另一个现象：为了换个颜色写下 `appearance: none`，checkbox 变成空白方框——能点，但看不出是否选中；键盘 Tab 到它，也没有焦点环。

你以为：CSS 画出了控件。实际：HTML 已经给了控件语义与行为，CSS 只是覆盖了外观；覆盖过头，就把"看得见的状态"一起弄丢了。

## 先建立直觉

:::figure 20-forms|控件状态的触发时机
图是一条时间轴：页面加载 → 用户交互（输入或点击）→ 失焦或提交。轴上标出各伪类点亮的时刻：`:invalid` 在加载时就能亮（空的 `required`），值一变就重算；`:user-invalid` 要等用户交互并失焦后才亮；`:checked` 选中即亮；`:indeterminate` 由脚本设置后亮；`:focus` 只要获得焦点就亮；`:focus-visible` 只在键盘等启发式场景亮。看图时只问一句：这个伪类说的是"值满足什么"，还是"人做过什么"？
:::

这张图要记住的不是伪类清单，而是**把"当前值"和"用户是否已交互"分开**。两者混用，就会在用户还没填写时提前报错。

## 机制拆成四步

### 1. 先接受原生，再决定覆盖多少

一个 `input` 同时带着三层东西：HTML 的语义（类型、名称、必填、校验）、浏览器的交互（键盘、焦点、粘贴、选择）、以及 UA 样式。前两层是 CSS 给不了的。

```css
.choice input {
  inline-size: 1.15rem;
  block-size: 1.15rem;
  accent-color: #3157d5; /* 只改强调色，保留原生绘制与行为 */
}
```

`accent-color` 改的是 checkbox、radio、range 等控件的强调区域，改动最小、风险最低。它不负责文本输入框或 select 的边框，也保证不了所有平台上的勾选标记对比度，仍要实测选中态。

`color-scheme` 是另一层：它告诉 UA 页面采用浅色还是深色主题，原生控件与滚动条据此调整；它不会自动把你的背景和文字改暗。

`appearance: none` 则撤掉控件的原生绘制路径，由作者重新画：

```css
.custom { appearance: none; }
```

**为什么不能只写 `appearance: none` 就完事？** 撤掉的是绘制，不是行为——Tab、空格切换、分组互斥仍然存在，但选中态、焦点环、禁用态和对比度都得你自己补回来。只改颜色优先用 `accent-color`；必须自定义时，用伪元素或背景画出每一种状态，并保持键盘可操作。

### 2. label 给控件一个可访问名称

```html
<label for="email">邮箱</label>
<input id="email" type="email" autocomplete="email" required
       aria-describedby="email-help" />
<p id="email-help">用于接收确认邮件。</p>
```

辅助技术读的是**可访问名称**，不是你画的边框。`for` / `id` 显式关联最清晰，包裹式 label 也可以；说明文字不在 label 里时用 `aria-describedby` 关联；一组 radio 或 checkbox 用 `fieldset` + `legend` 分组。

**为什么 placeholder 不能当 label？** 它会在输入后消失，用户回看表单时就失去了字段名；它也不是稳定的可访问名称。字段名称、必填说明、格式要求和错误原因，都要写在真正可见、可关联的文本里。

### 3. 焦点：`:focus` 与 `:focus-visible`

```css
.field input:focus-visible {
  outline: 3px solid #3157d5;
  outline-offset: 2px;
}
```

`:focus` 只要元素获得焦点就命中，鼠标点一下也算。`:focus-visible` 由浏览器的启发式判断命中，通常在键盘操作或文本输入场景出现，鼠标点击一般不出现。

**为什么要分开？** 键盘用户必须看见当前位置，否则等于盲操作；而鼠标用户点了输入框还弹出粗焦点环，视觉上很吵。两者兼顾的办法是把明显的焦点环交给 `:focus-visible`，而不是写 `outline: none` 把焦点提示彻底删掉。

文本输入框是一个例外：只要它获得焦点，`:focus-visible` 通常就会命中，因为你必然要往里打字；按钮和复选框才真正由浏览器判断输入方式。

### 4. 状态伪类的触发时机不同

| 伪类 | 何时点亮 | 典型误区 |
| --- | --- | --- |
| `:checked` | 控件处于原生选中态 | 以为脚本改外观就等于选中 |
| `:indeterminate` | 脚本把 `indeterminate` 设为 true | 以为"未选中"就是 indeterminate |
| `:valid` / `:invalid` | 当前值是否满足约束，加载时即计算 | 以为只有提交后才判断 |
| `:user-invalid` | 用户交互并失焦后仍不满足约束 | 以为它和 `:invalid` 等价 |

**为什么需要 `:user-invalid`？** 空的 `required` 在页面加载时就违反约束，`:invalid` 立即命中；如果用 `:invalid` 标红边框，用户还没开始填就被判错。`:user-invalid` 把判定推迟到用户交互之后，更适合作为"现在真的需要修"的视觉信号：

```css
.field input:user-invalid { border-color: #b42318; }
.field input[aria-invalid="true"] { border-color: #b42318; }
```

视觉提示与语义状态要一致：需要向辅助技术播报错误时，配合 `aria-invalid="true"` 和具体错误文案，而不是只靠颜色。

`:indeterminate` 也不是 `:checked` 的反面：它是第三种状态，表示"部分选中/尚未决定"，由脚本设置，点击后会被清除并进入 `:checked`。

## 动手验证

:::demo 20-forms|切换状态，看哪个伪类先亮
先预测：一个空的必填邮箱框，页面刚打开时 `:invalid` 和 `:user-invalid` 哪个命中？用鼠标点进文本框和用 Tab 键聚焦旁边的按钮，`:focus-visible` 分别怎样？写下答案再揭晓。
验证：打开 demo，用开关切换"用户已交互"，分别用鼠标和键盘聚焦控件，状态文本会列出当前命中的伪类。核对加载时只有 `:invalid`、交互失焦后 `:user-invalid` 才出现。
:::

## 容易误判的地方

- **"`invalid` 一亮就标红边框"** → 加载即命中；改用 `:user-invalid` 或在提交失败后设置 `aria-invalid`。
- **"`appearance: none` 只是换个颜色"** → 原生绘制被撤掉后，焦点环、选中态、禁用态和对比度都要自己补。
- **"用 `div` 画 checkbox 更自由"** → 键盘操作、分组互斥、语义和名称全都要自己实现；优先原生控件加 `accent-color`。

## 自己再做一次

1. 写 `<label for="email">邮箱</label>`、`<input id="email" type="email" required>` 和一个 `<button>保存</button>`，打开页面不填。**预期结果：`:invalid` 命中、`:user-invalid` 不命中；Tab 聚焦按钮时按钮 `:focus-visible` 命中、鼠标点击按钮时通常不命中；邮箱框因为是文本输入，鼠标点进去时 `:focus-visible` 也命中。**
2. 给 checkbox 加 `accent-color: #3157d5`，再在开发者工具里改成 `appearance: none` 且不写任何替代样式。**预期结果：前者勾选标记变蓝且键盘可操作；后者方框变空白、选中态不明显，但 Tab 与空格仍能切换——行为来自 HTML，不是 CSS。**
3. 用脚本把 checkbox 的 `indeterminate` 设为 true，再点它一次。**预期结果：点击前 `:indeterminate` 命中、显示横杠而非对勾、`:checked` 不命中；点击后 `indeterminate` 被清除、变为 `:checked`，`:indeterminate` 熄灭。**

> 下一篇：[表格：语义先于视觉](21-tables.md)
