# 23 · 原生表单、表格与原生 UI

> 学习目标：先分清浏览器原生外观与作者可控制的样式边界，再掌握表单状态、布局与无障碍、表格语义与响应式、列表 marker 与计数器，以及 `details`、`dialog`、popover 的 CSS 状态。最终能做到“保留原生能力，只在必要处改外观”。

## 1. 先建立心智模型：HTML 负责能力，CSS 负责表达

原生控件不是普通 `div`。一个 `input` 同时包含：

- **语义**：类型、名称、必填、自动填充、校验信息；
- **交互**：键盘操作、指针操作、焦点、系统粘贴与选择；
- **外观**：由 UA 样式、操作系统主题与作者 CSS 共同决定。

```text
HTML 能力
  ├─ 类型与语义 ───────────────┐
  ├─ 键盘与焦点 ───────────────┤
  ├─ 校验与状态 ───────────────┼─> 可用、可访问的原生控件
  └─ 浏览器默认外观 ──┐        │
                      ├─> CSS 增量覆盖
作者设计令牌与布局 ───┘
```

因此第一条原则是：**先用正确的 HTML，再决定 CSS 要不要接管外观**。例如给邮箱输入框加 `type="email"`，不是为了让边框变圆，而是为了键盘、校验与自动填充。

CSS 不能替代的事情包括：

- 为输入框生成可访问名称；
- 让一个普通 `div` 自动具备复选框的键盘行为；
- 根据校验结果自动宣布错误；
- 为对话框管理完整焦点流程；
- 让 popover 自动具备模态行为。

## 2. 原生外观的边界：`appearance`、`accent-color`、`color-scheme`

### 2.1 `appearance`：是否采用平台原生绘制

`appearance` 控制元素是否使用平台/UA 提供的控件外观。常见值：

- `auto`：交给 UA 决定；
- `none`：去掉该控件特定的原生绘制路径，由作者重新绘制；
- 部分平台还提供 `textfield` 等历史或实验值，工程中不宜依赖。

```css
.text-input {
  appearance: none;
  border: 1px solid #8a8f98;
  background: #fff;
  color: #172033;
}
```

**代价**：去掉 `appearance` 后，你要自己补回焦点环、状态差异、校验图标、尺寸与对比度。checkbox/radio 尤其不能只写 `appearance: none`，否则可能出现“能点，但看不出选中”的空盒子。

**反例**：

```css
/* 不推荐：为了换颜色，把所有控件都变成空白画布 */
input,
select,
textarea {
  appearance: none;
}
```

### 2.2 `accent-color`：给原生控件换强调色

`accent-color` 适合 checkbox、radio、range、progress 等控件的强调区域。它不是继承属性，因此通常写在控件类或组件根上并显式命中目标。

```css
.choice input,
.meter {
  accent-color: #3157d5;
}
```

它不会把文本输入框、textarea、select 的边框统一变成品牌色，也不会解决所有平台上的勾选标记对比度问题。**必须实际测试选中态**，不要只看未选中的边框。

### 2.3 `color-scheme`：告诉 UA 页面采用哪种主题

```css
:root {
  color-scheme: light dark;
  --field-bg: light-dark(#fff, #171a21);
  --field-text: light-dark(#172033, #f4f6fa);
  --field-border: light-dark(#767e8c, #9ca5b5);
}
```

`light dark` 表示 UA 可根据用户偏好选择。它不是“自动把页面变暗”的开关；页面背景、文字与边框仍需作者样式负责。也可以固定 `color-scheme: light`，避免系统深色模式改变原生控件。

`light-dark()` 与 `color-scheme` 的配合需要目标浏览器支持；不支持时提供普通颜色兜底。

## 3. 文本控件的颜色、边框、焦点与状态

### 3.1 一份稳健的基础样式

```css
.field input,
.field textarea,
.field select {
  box-sizing: border-box;
  inline-size: 100%;
  min-inline-size: 0;
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--field-border, #767e8c);
  border-radius: 0.45rem;
  background: var(--field-bg, #fff);
  color: var(--field-text, #172033);
  font: inherit;
}

.field input:focus-visible,
.field textarea:focus-visible,
.field select:focus-visible {
  outline: 3px solid #3157d5;
  outline-offset: 2px;
}
```

`box-sizing: border-box` 让 `inline-size: 100%` 包含 padding 与 border；`min-inline-size: 0` 避免 Grid/Flex 子项被内容最小宽度撑破。

### 3.2 状态要表达不同信息

| 状态 | 推荐选择器/属性 | 表达的信息 |
| --- | --- | --- |
| 键盘焦点 | `:focus-visible` | 当前键盘操作位置 |
| 指针聚焦 | `:focus`（谨慎使用） | 控件已获得焦点 |
| 禁用 | `:disabled` | 不可交互、通常不参与提交 |
| 只读 | `:read-only`、HTML `readonly` | 可聚焦、可复制，但不可编辑 |
| 原生校验失败 | `:invalid` | 当前值不满足约束 |
| 已由应用标记错误 | `[aria-invalid="true"]` | 需要向辅助技术传达错误 |
| 占位符可见 | `:placeholder-shown` | 当前显示 placeholder |

注意：`:read-only` 的定义是“用户不可编辑”，并不只匹配带 `readonly` 属性的文本框；disabled 或某些天然不可编辑元素也可能匹配。不要把它当作 readonly 属性的完全同义词。

推荐将视觉错误状态与 HTML 状态属性关联：

```css
.field input[aria-invalid="true"],
.field textarea[aria-invalid="true"] {
  border-color: #b42318;
}

.field input[aria-invalid="true"]:focus-visible,
.field textarea[aria-invalid="true"]:focus-visible {
  outline-color: #b42318;
}
```

**反例**：

```css
input:invalid {
  border: 2px solid red;
}
```

页面刚打开，未填写的 `required` 邮箱就会变红，仿佛用户已经犯错。更稳妥的策略是：默认保留中性边框，提交失败、失焦后校验或应用确认错误时，再加 `aria-invalid="true"` 和错误文案。`required` 的提示应同时存在于 HTML 与可见说明中，不能只靠颜色。

### 3.3 `disabled` 与 `readonly`

```css
.field :disabled {
  cursor: not-allowed;
  opacity: 0.65;
  background: #eef0f3;
}

.field textarea[readonly] {
  background: #f5f6f8;
}
```

disabled 控件通常不会获得焦点；readonly 控件仍可聚焦、选择和复制。如果必须降低 disabled 的不透明度，要检查文字与背景对比度，避免“看不清但还要读懂”。

### 3.4 placeholder 不是 label

```css
.field input::placeholder {
  color: #626b79;
  opacity: 1;
}
```

placeholder 是短暂提示，会在输入后消失；label 是持久名称。Firefox 可能给 placeholder 默认不透明度，显式写 `opacity: 1` 可避免过浅，但颜色仍需保证对比度。

**不要用 placeholder 替代以下信息**：字段名称、格式示例、必填说明、错误原因、密码要求。也不要通过 `::placeholder` 假装已经填入内容。

## 4. checkbox、radio、select 与 range

### 4.1 checkbox / radio：优先保留原生绘制

```html
<label class="choice">
  <input type="checkbox" name="newsletter" />
  <span>接收产品更新</span>
</label>

<label class="choice">
  <input type="radio" name="plan" value="basic" checked />
  <span>基础版</span>
</label>
```

```css
.choice {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-block-size: 2.75rem;
  cursor: pointer;
}

.choice input {
  inline-size: 1.15rem;
  block-size: 1.15rem;
  margin: 0;
  accent-color: #3157d5;
}
```

整行 label 都能点击，点击区域也更大。原生 radio 还负责同组互斥与方向键切换；自己画 `span` 不会自动获得这些能力。

如果必须自定义外观，应使用 `appearance: none`，并同时实现未选中、选中、焦点、禁用、高对比度与系统主题。建议先用伪元素或背景图形绘制，再测试键盘和读屏，不要通过 `display: none` 隐藏真实 input。

### 4.2 select：自定义箭头时保留原生语义

```css
.select-wrap select {
  appearance: none;
  padding-inline-end: 2.5rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'%3E%3Cpath d='m3 6 5 5 5-5' fill='none' stroke='%23555' stroke-width='2'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.8rem center;
}
```

自定义箭头只是外观；下拉列表仍由浏览器实现。多选、optgroup、键盘搜索等能力不应通过替换成普通 `div` 丢失。原生 option 的可定制程度因平台而异，跨端要求高时应评估成熟的自定义 select 组件及其无障碍成本。

### 4.3 range 与 progress

```css
.range {
  inline-size: min(100%, 28rem);
  accent-color: #3157d5;
}

.meter {
  inline-size: 100%;
  block-size: 0.75rem;
  accent-color: #16805a;
}
```

range 的轨道和拇指在不同引擎中的 `::-webkit-slider-*`、`::-moz-range-*` 支持并不一致。先接受 `accent-color` 的跨平台方案，确有设计需求再分别适配，并保留焦点可见性。

## 5. 表单布局与可访问性

### 5.1 布局结构图

```text
form
├─ fieldset + legend（一组相关选项）
│  ├─ label → input（包裹或 for/id）
│  │  ├─ 控件
│  │  ├─ 说明文字（aria-describedby）
│  │  └─ 错误文字（aria-describedby）
│  └─ label → input
└─ 操作区（提交、重置、状态提示）
```

- 每个控件都要有可访问名称。显式 `<label for="email">` 与 `<input id="email">` 最清晰；包裹式 label 也可以。
- 一段说明或错误文字如果不在 label 内，用 `aria-describedby` 关联。
- 真正提交失败时设置 `aria-invalid="true"`，并提供文本原因；不要只写“输入有误”。
- 相关 radio/checkbox 用 `fieldset` + `legend` 分组。
- 使用 `autocomplete` 帮助用户填写姓名、邮箱、地址等信息。
- 保持 DOM 顺序与阅读顺序一致，不要只用 CSS `order` 重排字段。
- 错误提示应靠近字段，并在提交后让用户容易发现；焦点管理通常需要少量 JS。

### 5.2 完整示例：可访问的双列登记表单

```html
<form class="profile-form">
  <div class="field">
    <label for="name">姓名</label>
    <input
      id="name"
      name="name"
      type="text"
      autocomplete="name"
      required
      aria-describedby="name-help"
    />
    <p class="help" id="name-help">请填写真实姓名。</p>
  </div>

  <div class="field">
    <label for="email">邮箱</label>
    <input
      id="email"
      name="email"
      type="email"
      autocomplete="email"
      required
      aria-describedby="email-help"
    />
    <p class="help" id="email-help">用于接收确认邮件。</p>
  </div>

  <div class="field field--full">
    <label for="bio">个人简介</label>
    <textarea
      id="bio"
      name="bio"
      rows="4"
      maxlength="200"
      aria-describedby="bio-help"
    ></textarea>
    <p class="help" id="bio-help">最多 200 字。</p>
  </div>

  <fieldset class="field field--full">
    <legend>通知方式</legend>
    <label class="choice">
      <input type="radio" name="notify" value="email" checked />
      <span>邮件</span>
    </label>
    <label class="choice">
      <input type="radio" name="notify" value="none" />
      <span>不接收</span>
    </label>
  </fieldset>

  <div class="form-actions field--full">
    <button type="submit">保存</button>
  </div>
</form>
```

```css
.profile-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
  max-inline-size: 46rem;
  padding: 1.5rem;
  border: 1px solid #d5d9e0;
  border-radius: 0.75rem;
  background: #fff;
  color: #172033;
}

.field {
  display: grid;
  align-content: start;
  gap: 0.4rem;
  min-inline-size: 0;
}

.field > label,
.field legend {
  font-weight: 650;
}

.field input,
.field textarea {
  box-sizing: border-box;
  inline-size: 100%;
  min-inline-size: 0;
  padding: 0.7rem 0.8rem;
  border: 1px solid #767e8c;
  border-radius: 0.4rem;
  background: #fff;
  color: inherit;
  font: inherit;
}

.field textarea {
  resize: vertical;
}

.field input:focus-visible,
.field textarea:focus-visible,
.profile-form button:focus-visible {
  outline: 3px solid #3157d5;
  outline-offset: 2px;
}

.field input[aria-invalid="true"],
.field textarea[aria-invalid="true"] {
  border-color: #b42318;
}

.help {
  margin: 0;
  color: #525c6b;
  font-size: 0.875rem;
}

.field--full,
.form-actions {
  grid-column: 1 / -1;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.profile-form button {
  min-block-size: 2.75rem;
  padding: 0.65rem 1.2rem;
  border: 0;
  border-radius: 0.4rem;
  background: #2548bd;
  color: #fff;
  font: inherit;
  font-weight: 650;
  cursor: pointer;
}

@media (max-width: 40rem) {
  .profile-form {
    grid-template-columns: 1fr;
  }
}
```

这个示例只提供静态样式；提交后的错误关联、焦点移动和成功提示仍需应用逻辑。不要把“CSS 能画出错误”误认为“表单已经可访问”。

## 6. 表格：语义先于视觉

### 6.1 基本模型

```text
caption：表格名称与用途
thead
└─ tr
   └─ th scope="col"：列标题
tbody
└─ tr
   ├─ th scope="row"：行标题
   └─ td：数据
tfoot（可选）
```

`table-layout` 决定列宽如何计算：

- `auto`：根据内容计算，灵活但可能不稳定；
- `fixed`：使用表格、col、首行单元格声明的宽度，后续内容通常不改变列宽；
- `fixed` 不代表表格自动适配，超长内容仍可能溢出，需要 `overflow-wrap` 或容器滚动。

`border-collapse`：

- `separate`：单元格边框独立，配合 `border-spacing`；
- `collapse`：相邻边框合并，冲突时按级联规则选择胜出的边框。

`border-spacing` 在 `collapse` 下无效。`border-radius` 在 `border-collapse: collapse` 下也更容易失去预期效果。

### 6.2 表头关联

简单二维表用 `scope="col"` 和 `scope="row"`。复杂表如果简单 scope 不足，可用 `headers` 明确引用表头 ID，并用 `id` 标识表头。

```html
<th id="price" scope="col">价格</th>
<td headers="price product-name">199 元</td>
```

不要为了样式把 `th` 换成 `td`；表头语义不是背景色和粗体。`caption` 应描述表格，而不是重复页面标题。视觉上隐藏 caption 可以，但不要从辅助技术树中隐藏。

## 7. 完整示例：响应式、斑马纹与悬停表格

```html
<div class="table-scroll" tabindex="0" role="region" aria-labelledby="orders-caption">
  <table class="data-table">
    <caption id="orders-caption">本周订单，按日期排序</caption>
    <colgroup>
      <col class="col-order" />
      <col class="col-customer" />
      <col class="col-date" />
      <col class="col-status" />
      <col class="col-amount" />
    </colgroup>
    <thead>
      <tr>
        <th scope="col">订单号</th>
        <th scope="col">客户</th>
        <th scope="col">日期</th>
        <th scope="col">状态</th>
        <th scope="col" class="numeric">金额</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th scope="row">#1042</th>
        <td>林晓</td>
        <td><time datetime="2026-11-23">11 月 23 日</time></td>
        <td><span class="status status--done">已完成</span></td>
        <td class="numeric">¥ 328.00</td>
      </tr>
      <tr>
        <th scope="row">#1043</th>
        <td>周宁</td>
        <td><time datetime="2026-11-24">11 月 24 日</time></td>
        <td><span class="status status--pending">处理中</span></td>
        <td class="numeric">¥ 169.50</td>
      </tr>
      <tr>
        <th scope="row">#1044</th>
        <td>陈可</td>
        <td><time datetime="2026-11-25">11 月 25 日</time></td>
        <td><span class="status status--done">已完成</span></td>
        <td class="numeric">¥ 899.00</td>
      </tr>
    </tbody>
  </table>
</div>
```

```css
.table-scroll {
  max-inline-size: 100%;
  overflow-x: auto;
  border: 1px solid #d5d9e0;
  border-radius: 0.6rem;
}

.data-table {
  inline-size: 100%;
  min-inline-size: 42rem;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  color: #172033;
  font-variant-numeric: tabular-nums;
}

.data-table caption {
  padding: 0.8rem 1rem;
  text-align: start;
  font-weight: 700;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  border-block-end: 1px solid #e3e6eb;
  text-align: start;
  vertical-align: middle;
}

.data-table thead th {
  position: sticky;
  inset-block-start: 0;
  z-index: 1;
  background: #eef1f6;
  box-shadow: inset 0 -1px 0 #c8ced8;
}

.data-table tbody th {
  font-weight: 650;
}

.data-table tbody tr:nth-child(even) {
  background: #f7f8fa;
}

.data-table tbody tr:hover {
  background: #eaf0ff;
}

.data-table tbody tr:last-child > * {
  border-block-end: 0;
}

.col-order { inline-size: 7rem; }
.col-customer { inline-size: 10rem; }
.col-date { inline-size: 10rem; }
.col-status { inline-size: 8rem; }
.col-amount { inline-size: 9rem; }

.numeric {
  text-align: end;
}

.status {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 650;
}

.status--done {
  background: #dcf5e9;
  color: #135c40;
}

.status--pending {
  background: #fff0cf;
  color: #744600;
}
```

### 7.1 边界与替代方案

- 滚动容器加 `tabindex="0"`，让只用键盘的用户也能横向滚动；`role="region"` 与 `aria-labelledby` 给它一个可识别名称。
- 不要在每个设备上把表格强行压成六列；允许横向滚动通常比缩小到不可读更好。
- 如果每个记录天然是卡片，可以在小屏把每个 `tr` 改成块级卡片，并用 `data-label` + `::before` 显示字段名。但这会改变表格的视觉阅读结构，必须测试读屏顺序，且不要把 `display: block` 当作语义转换。
- 斑马纹与 hover 是辅助追踪手段，不应承担唯一的信息表达。状态文字和图标仍需存在。
- sticky 表头只在滚动容器内生效；`z-index` 要受控，避免盖住单元格内容。
- 表格内容很多时，分页、排序、虚拟滚动属于应用能力，不是 `table-layout` 能解决的。

## 8. 列表 marker、`::marker`、`content` 与 CSS 计数器

### 8.1 marker 是列表项外面的标记

```css
.list {
  padding-inline-start: 1.25rem;
  list-style: square outside;
}

.list li::marker {
  color: #3157d5;
  font-size: 1.1em;
}
```

`list-style` 是 `list-style-type`、`list-style-position`、`list-style-image` 的简写。`inside` 会改变换行文本与 marker 的关系，通常用于短项目；长列表常用 `outside`。

`::marker` 能设置 marker 的颜色、字体、内容等有限属性，但不能像普通伪元素一样任意布局、加背景或定位。`li::before` 看起来更自由，但会产生额外盒模型和辅助技术内容，不应无条件替代 marker。

### 8.2 CSS counters：让编号与 DOM 结构联动

计数器包含三个动作：

```css
counter-reset: step;      /* 建立/重置 */
counter-increment: step;  /* 递增 */
content: counter(step);   /* 输出 */
```

嵌套列表可以使用 `counters()` 输出多级编号。自定义 `@counter-style` 还能定义符号与后缀，但简单需求先用标准列表或 marker 即可。

### 8.3 完整示例：带标记与自定义编号的步骤列表

```html
<ol class="steps">
  <li>
    <h3>确认信息</h3>
    <p>检查姓名与邮箱是否正确。</p>
  </li>
  <li>
    <h3>选择方案</h3>
    <p>根据团队规模选择通知方式。</p>
  </li>
  <li>
    <h3>保存设置</h3>
    <p>提交后可以在账户页继续修改。</p>
  </li>
</ol>

<nav class="toc" aria-label="本页目录">
  <a href="#overview">概述</a>
  <a href="#layout">布局</a>
  <a href="#testing">测试</a>
</nav>
```

```css
.steps {
  display: grid;
  gap: 1rem;
  max-inline-size: 42rem;
  margin: 0;
  padding-inline-start: 1.5rem;
  list-style: none;
  counter-reset: step;
}

.steps > li {
  position: relative;
  counter-increment: step;
  padding: 1rem 1rem 1rem 3.4rem;
  border: 1px solid #d5d9e0;
  border-radius: 0.6rem;
  background: #fff;
}

.steps > li::before {
  content: counter(step);
  position: absolute;
  inset-block-start: 1rem;
  inset-inline-start: 1rem;
  display: grid;
  place-items: center;
  inline-size: 1.8rem;
  block-size: 1.8rem;
  border-radius: 50%;
  background: #3157d5;
  color: #fff;
  font-weight: 750;
}

.steps h3,
.steps p {
  margin: 0;
}

.toc {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem 1rem;
  margin-block-start: 1.5rem;
  counter-reset: toc;
}

.toc a {
  counter-increment: toc;
}

.toc a::after {
  content: "." counter(toc, decimal-leading-zero);
  color: #626b79;
  font-variant-numeric: tabular-nums;
}
```

这里使用 `::before` 是为了绝对定位圆形序号；如果只需要普通圆点或数字，优先使用原生 marker。`content` 生成的文字不保证被所有辅助技术稳定朗读，不能把“删除”“警告”等关键含义只写在生成内容里。

## 9. `details` / `summary`：原生展开，不要重写状态

```html
<details class="faq">
  <summary>为什么我的列表编号没有出现？</summary>
  <div class="faq__body">
    <p>检查是否设置了 <code>list-style: none</code>，以及是否误删了列表语义。</p>
  </div>
</details>
```

```css
.faq {
  max-inline-size: 42rem;
  border: 1px solid #d5d9e0;
  border-radius: 0.5rem;
  background: #fff;
}

.faq summary {
  padding: 0.9rem 1rem;
  cursor: pointer;
  font-weight: 650;
}

.faq summary:focus-visible {
  outline: 3px solid #3157d5;
  outline-offset: -3px;
}

.faq__body {
  padding: 0 1rem 1rem;
  color: #434c5b;
}

.faq[open] .faq__body {
  border-block-start: 1px solid #e3e6eb;
  padding-block-start: 0.9rem;
}
```

`details[open]` 是原生状态，不需要额外的 `is-open` 类。不要为了动画随意给内容加 `display: none`，否则可能破坏原生展开逻辑。`summary` 的默认三角由 UA 提供，`::marker` 或较新的 `list-style`/`disclosure` 相关能力可用于定制，但应验证目标浏览器。

## 10. `dialog` 与 popover：顶层 UI 的 CSS 状态

### 10.1 概念图

```text
普通文档流/z-index 层叠上下文
        │ showModal() / 非模态 open
        ▼
dialog ── :modal 表示模态状态，::backdrop 位于其后方
        │ showPopover()
        ▼
popover ── :popover-open 表示打开状态，::backdrop 可设置
        │
        └─ top layer：不受普通祖先 overflow/z-index 的正常裁剪
```

“进入 top layer”不是“把 `z-index` 调到 999999”。top layer 独立于普通层叠上下文，普通父容器的 `overflow: hidden` 通常不能像裁剪普通 fixed 元素那样裁剪它；但尺寸、定位与 inset-modified containing block 仍需检查。

### 10.2 状态速查

| 能力 | dialog | popover |
| --- | --- | --- |
| 打开方式 | `showModal()` 或 `open` 属性 | `showPopover()` 或 `popovertarget` |
| 打开状态选择器 | `[open]` | `:popover-open` |
| 模态状态选择器 | `:modal` | 无等价模态伪类 |
| 背景伪元素 | `dialog::backdrop` | `[popover]::backdrop` |
| 焦点与背景隔离 | `showModal()` 提供模态能力 | 默认不是模态，不自动让其余页面 inert |
| 关闭 | `close()`、`method="dialog"` 表单 | light dismiss、`hidePopover()`、`popovertarget` |
| 适合场景 | 确认、编辑、必须聚焦的流程 | 提示、非阻塞菜单、轻量浮层 |

`dialog[open]` 包括非模态对话框，因此仅凭 `[open]` 不能判断它是否模态。`position: fixed` + `inset: 0` 常用于让模态面板居中；`margin: auto` 与 `max-block-size` 处理居中及小屏高度。

### 10.3 完整示例：对话框与 popover 共用视觉语言

```html
<button class="trigger" id="open-dialog">编辑资料</button>
<button class="trigger" popovertarget="help-popover" type="button">查看帮助</button>

<dialog class="sheet" id="edit-dialog" aria-labelledby="dialog-title">
  <form method="dialog" class="sheet__panel">
    <h2 id="dialog-title">编辑资料</h2>
    <label class="sheet__field">
      昵称
      <input name="nickname" value="小林" />
    </label>
    <div class="sheet__actions">
      <button value="cancel" formnovalidate>取消</button>
      <button value="default">保存</button>
    </div>
  </form>
</dialog>

<div id="help-popover" popover class="note" aria-labelledby="help-title">
  <h2 id="help-title">填写帮助</h2>
  <p>昵称会显示在公开资料中，随时可以修改。</p>
  <button class="note__close" popovertarget="help-popover" popovertargetaction="hide" type="button">
    关闭
  </button>
</div>

<script>
  const dialog = document.querySelector("#edit-dialog");

  document.querySelector("#open-dialog").addEventListener("click", () => {
    dialog.showModal();
  });

  // 实际项目应保存 opener，并在关闭/取消后按业务规则恢复焦点。
  dialog.addEventListener("close", () => {
    document.querySelector("#open-dialog").focus();
  });
</script>
```

```css
.sheet {
  position: fixed;
  inset: 0;
  inline-size: min(calc(100% - 2rem), 32rem);
  max-block-size: calc(100dvh - 2rem);
  margin: auto;
  padding: 0;
  border: 1px solid #c8ced8;
  border-radius: 0.8rem;
  background: #fff;
  color: #172033;
  overflow: auto;
}

.sheet::backdrop {
  background: rgb(16 24 40 / 55%);
  backdrop-filter: blur(3px);
}

.sheet__panel {
  display: grid;
  gap: 1rem;
  padding: 1.4rem;
}

.sheet__panel h2,
.note h2 {
  margin: 0;
}

.sheet__field {
  display: grid;
  gap: 0.4rem;
}

.sheet__field input {
  padding: 0.65rem 0.75rem;
  border: 1px solid #767e8c;
  border-radius: 0.4rem;
  font: inherit;
}

.sheet__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.note {
  position: fixed;
  inset: auto 1rem 1rem auto;
  inline-size: min(calc(100% - 2rem), 20rem);
  margin: 0;
  padding: 1rem;
  border: 1px solid #c8ced8;
  border-radius: 0.6rem;
  background: #fff;
  color: #172033;
  box-shadow: 0 12px 32px rgb(16 24 40 / 20%);
}

.note::backdrop {
  background: rgb(16 24 40 / 12%);
}

.note:popover-open {
  animation: note-in 140ms ease-out;
}

.note__close {
  margin-block-start: 0.8rem;
  padding: 0.45rem 0.7rem;
  border: 1px solid #767e8c;
  border-radius: 0.35rem;
  background: #fff;
  color: inherit;
  font: inherit;
  cursor: pointer;
}

@keyframes note-in {
  from {
    opacity: 0;
    translate: 0 0.5rem;
  }
  to {
    opacity: 1;
    translate: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .note:popover-open {
    animation: none;
  }
}
```

### 10.4 CSS 与 JS/HTML 的责任边界

CSS 可以负责：位置、尺寸、背景、遮罩、边框、动画、打开状态的视觉变化。

HTML/JS 通常需要负责：

- 调用 `showModal()`、`showPopover()`，而不是只添加 `open` 属性来假装模态；
- 关闭后恢复合适的焦点；
- 在复杂模态中管理焦点圈定与初始焦点；
- 锁定背景滚动，并处理多滚动容器；
- 给非模态 popover 提供明确触发、关闭和焦点策略；
- 根据业务给对话框设置 `aria-labelledby`、`aria-describedby`、错误关联；
- 如需让背景不可交互，正确使用原生 `inert` 或等效模态机制。

**反例**：

```css
/* 这只会改变颜色，不会让背景 inert */
.note:popover-open::backdrop {
  background: rgb(0 0 0 / 50%);
}
```

`overlay` 属性用于离散过渡期间延迟元素退出 top layer；它不是打开、关闭或焦点管理 API，详见下一章的进入/退出过渡。

## 11. 易错点清单

1. **所有 input 一起 `appearance: none`**：丢失 native 绘制后没有补状态与焦点。
2. **`accent-color` 包办一切**：它不统一文本框和 select 的边框。
3. **未触碰的 required 立即标红**：应结合 `aria-invalid` 和校验时机。
4. **placeholder 当 label**：输入后名称消失，辅助技术与认知负担都变差。
5. **禁用与只读混用**：disabled 通常不提交、不聚焦；readonly 仍可聚焦和复制。
6. **用 `div` 模拟 checkbox/radio**：容易丢失键盘、分组与语义。
7. **表格换成一堆 div**：视觉相似不等于表头关系存在。
8. **`border-collapse` 与 `border-spacing` 同时期待生效**：collapse 下 spacing 无效。
9. **移动端硬缩表格**：优先保留语义并提供横向滚动或明确的卡片结构。
10. **marker 与 `::marker` 混为一谈**：前者是列表项外的标记盒，后者是设置它的伪元素。
11. **用 `content` 表达关键警告**：生成内容不保证进入可访问名称或被朗读。
12. **给 `details` 再维护一套 open 类**：状态容易与原生 `[open]` 脱节。
13. **用巨大 `z-index` 模拟 top layer**：无法解决祖先层叠上下文与顶层语义。
14. **以为 `dialog` 的 CSS 能完成焦点管理**：视觉、模态行为与焦点策略是不同层。
15. **popover 加遮罩就当模态**：默认 popover 不会让其余内容 inert。

## 12. 兼容性与验证方式

原生控件是跨平台差异最明显的区域之一。不要根据一篇旧博客判断“某版本一定支持”，建议按以下顺序验证：

1. 查 [MDN CSS 参考](https://developer.mozilla.org/zh-CN/docs/Web/CSS/Reference) 对应属性的 Baseline 标识与兼容表；再用 [Can I use](https://caniuse.com/) 看目标用户分布。
2. 用 `CSS.supports()` 做快速检测，例如：

   ```js
   console.log({
     appearance: CSS.supports("appearance", "none"),
     accentColor: CSS.supports("accent-color", "#3157d5"),
     colorScheme: CSS.supports("color-scheme", "light dark"),
     focusVisible: CSS.supports("selector(:focus-visible)"),
   });
   ```

3. 在真实浏览器与设备上测试，而不只依赖解析支持：
   - Windows/macOS 的浅色与深色主题；
   - iOS Safari 与 Android Chrome；
   - 键盘 Tab、Shift+Tab、方向键、Enter/Space、Escape；
   - 200% 缩放、窄屏、强制色彩/高对比度模式；
   - 浏览器自动填充后，label、背景与图标是否仍清楚。
4. 对 `dialog`、popover，分别测试 `showModal()` 与非模态 `open`、`showPopover()` 与 light dismiss，不要只测静态 `[open]`。
5. 用浏览器可访问性树检查名称、角色、状态；用读屏抽查错误提示与表头关联。

`CSS.supports()` 只能说明浏览器是否解析某声明，不能证明操作系统绘制的勾选标记、原生下拉或焦点行为符合预期。

## 关联示例

- [表单状态实验台](../../examples/forms/form-states.html)：复选、单选、开关、滑块、`:indeterminate` 和 `:user-invalid`。
- [原生 UI 组件](../../examples/forms/native-ui.html)：dialog、popover、details、表格和 CSS 计数器。

## 13. 练习

1. 把一个“placeholder 充当 label”的表单改为显式 label，并加上说明文字关联与提交失败时的 `aria-invalid`。
2. 为 checkbox/radio 设计一套点击区域至少 44px 的样式，仅使用 `accent-color`，在浅色与深色主题中测试选中态。
3. 给一个五列订单表增加 caption、`scope`、数字对齐和横向滚动，并让滚动容器可用键盘操作。
4. 分别用 `border-collapse: collapse` 与 `separate` 实现相同视觉边框，记录圆角、sticky 表头和边框粗细的差异。
5. 用 `::marker` 修改导航列表颜色，再用 `counter-reset`/`counter-increment` 做步骤编号；解释为什么第二种用了 `::before`。
6. 实现一个 `details` FAQ，确保展开、收起、键盘焦点与打印样式都正常。
7. 对比 `dialog.showModal()` 与 popover：记录焦点、Escape、背景点击、背景滚动和 `::backdrop` 的差异。
8. 为一个模态编辑流程写出“CSS 负责什么、HTML/JS 负责什么”的清单，并检查关闭后的焦点恢复。

> 上一篇：[常见布局方案](21-recipes.md)。
>
> 下一篇：[现代 CSS 特性](24-modern-features.md)。
>
> 相关：[定位与层叠](../03-layout/09-positioning-stacking.md)、[过渡与动画](../05-advanced/16-animation.md)、[CSS 速查](20-cheatsheet.md)。
>
> 返回：[CSS 学习手记](../README.md)。
