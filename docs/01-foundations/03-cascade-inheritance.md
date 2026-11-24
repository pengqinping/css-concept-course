# 03 · 层叠、继承与 CSS 变量

> 学习目标：准确预测一条声明的胜负，理解哪些属性会继承，并用自定义属性构建可维护的主题系统。

## 1. 层叠的完整判断顺序

同一声明竞争时，按以下顺序判断（省略动画与过渡时）：

```text
1. 来源与重要性  ← 层在此步内部比较：普通声明后层强，重要声明顺序反转
2. 优先级        ← 四元组逐位比较
3. 作用范围      ← 仅 @scope 规则之间：离 scope 根更近的胜出
4. 源码顺序      ← 前面全部打平时，后写的胜出
```

完整顺序还要把 CSS 动画（高于所有普通声明、低于重要声明）和 CSS 过渡（高于所有声明，含重要声明）插入第 1 步与第 2 步之间。优先级再高也救不了来源和重要性更低的声明。

```css
p { color: red; }
p { color: blue; }
```

两条规则其他条件相同，后写的蓝色生效。

```css
p { color: red !important; }
p { color: blue; }
```

红色生效，因为重要性优先于优先级和源码顺序。

## 2. 来源与重要性

简化后的高低关系如下：

```text
重要用户代理样式
> 重要用户样式
> 重要作者样式
> 动画声明
> 普通作者样式
> 用户样式
> 用户代理样式
```

实际规范还区分 transition，并对同来源、同重要性的作者样式使用优先级和层顺序。开发时最值得记住的是：**用户的重要样式高于作者的重要样式**，因此不要用 `!important` 强行覆盖用户的无障碍设置。

## 3. `@layer` 用顺序代替优先级竞赛

```css
@layer reset, base, components, utilities;

@layer reset {
  * { box-sizing: border-box; }
  body { margin: 0; }
}

@layer base {
  body {
    font-family: system-ui, sans-serif;
    color: #24261f;
    background: #f4f1e9;
  }
}

@layer components {
  .button {
    padding: 0.6rem 1rem;
    border: 1px solid currentColor;
    background: transparent;
  }
}

@layer utilities {
  .u-hidden { display: none; }
}
```

层顺序在第一次声明时建立。普通声明中，后层覆盖前层，**即使前层选择器优先级更高**。重要声明会反转层顺序，因此尽量不要到处写 `!important`。

```text
reset → base → components → utilities
低优先级层                        高优先级层
```

嵌套层：

```css
@layer framework {
  @layer base, components;
}

@layer framework.components {
  .panel { padding: 1rem; }
}
```

## 4. 继承：子元素获得某些计算值

不是所有属性都继承。字体、颜色、行高、文字对齐等通常继承；尺寸、背景、边框、margin 通常不继承。

```html
<div class="parent">
  父元素文字
  <p>子元素会继承 color 和 font-family。</p>
</div>
```

```css
.parent {
  color: #3d601c;
  font-family: Georgia, serif;
}

p {
  color: inherit;
}
```

### 强制继承与控制

```css
.button {
  font: inherit;       /* 同时影响多个字体属性 */
  color: inherit;
}

.icon {
  /* 显式设置，不依赖继承 */
  color: currentColor;
}
```

`currentColor` 取当前元素的 `color` 计算值：

```css
.button {
  color: #3d601c;
  border: 1px solid currentColor;
  fill: currentColor;
}
```

### 全局关键字

```css
.child {
  color: inherit;
  all: unset;
}

.hidden {
  all: initial;
}
```

| 关键字 | 含义 |
| --- | --- |
| `inherit` | 取父元素计算值 |
| `initial` | 取属性规范定义的初始值，不一定是浏览器默认外观 |
| `unset` | 继承属性表现为 inherit，非继承属性表现为 initial |
| `revert` | 撤销作者样式，回退到用户/用户代理来源 |
| `revert-layer` | 回退到当前层之前的值 |

## 5. CSS 自定义属性

```css
:root {
  --color-brand: #3d601c;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --radius-md: 0.75rem;
}

.button {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--color-brand);
}
```

自定义属性会继承，可以在局部覆盖：

```css
.panel {
  --panel-accent: #8262d7;
  --panel-background: #f0ebfa;
  border-color: var(--panel-accent);
  background: var(--panel-background);
}
```

局部变量不会“泄漏”到面板外部，但会向内部后代继承。

## 6. 回退值

```css
.button {
  color: var(--button-color, #24261f);
  background: var(--button-background, #fbfaf6);
}
```

逗号后的值只在前一个变量无效时使用。

```css
.theme {
  --color-bg: var(--color-surface, #ffffff);
}
```

如果 `--color-surface` 也无效，最终 `color-bg` 同样无效。使用 `background: var(--color-bg)` 时，该声明在计算值时被视为“值无效”（IACVT），按 `unset` 处理：`background` 是非继承属性，因此表现为其初始值 `transparent`。也就是说，这里会出现初始值，但原因是 IACVT → `unset`，不是浏览器“忘了这条声明”。

## 7. 自定义属性与普通属性不同

```css
:root {
  --gap: 10px;
}

.card {
  --gap: 20px;
  gap: var(--gap);
}
```

普通属性在声明时就会解析语法并得到计算值；自定义属性基本按 token 流保存，在 `var()` 被使用时才参与替换。因此下面这种写法可能无效：

```css
:root { --input: 10; }
.box { width: calc(var(--input) * 1px); }
```

但下面有效：

```css
:root { --input: 10px; }
.box { width: calc(var(--input) * 2); }
```

同理，不能先声明 `--side: left`，再写 `border-var(--side)-color`，CSS 不会在属性名中做变量替换。

## 8. `@property`：注册自定义属性类型

```css
@property --angle {
  syntax: "<angle>";
  inherits: false;
  initial-value: 0deg;
}

.card {
  --angle: 0deg;
  background: conic-gradient(from var(--angle), #c8f35c, #8262d7);
  transition: --angle 400ms ease;
}

.card:hover { --angle: 120deg; }
```

注册后，浏览器知道变量是角度，可以进行类型检查、设置初始值，并在满足条件时补间动画。

```text
未注册：--angle 是不透明 token，通常离散跳变
已注册：--angle 是 <angle>，可以连续过渡
```

`inherits: false` 表示不继承。注册不会自动让所有值都可动画，还要满足可插值类型等条件。

## 9. 用变量构建主题

```css
:root {
  color-scheme: light;
  --bg: #f4f1e9;
  --surface: #fbfaf6;
  --text: #24261f;
  --text-muted: #686b61;
  --border: #d7d3c8;
  --accent: #3d601c;
  --accent-contrast: #ffffff;
}

[data-theme="dark"] {
  color-scheme: dark;
  --bg: #191b17;
  --surface: #22251f;
  --text: #f2efe7;
  --text-muted: #b3b6aa;
  --border: #3b4036;
  --accent: #c8f35c;
  --accent-contrast: #24261f;
}

body {
  color: var(--text);
  background: var(--bg);
}
```

变量名应表达用途，而不是只表达颜色：

```css
/* 不推荐：改主题时容易不知道用途 */
--green: #c8f35c;

/* 推荐：语义清晰 */
--color-accent: #c8f35c;
--color-accent-contrast: #24261f;
```

## 10. 调试覆盖问题

按这个顺序检查：

1. 元素是否真的命中规则。
2. 是否被同优先级的后续规则覆盖。
3. 是否存在更高优先级选择器或 `@layer`。
4. 是否被 `!important` 覆盖。
5. 属性是否不适用于当前元素。
6. 值是否无效，被浏览器丢弃。
7. 是否被 shorthand 重置。
8. 是否被继承值或动画值影响。

```css
.button {
  background: red;
  background-color: blue;
}
```

这里是 `background-color` 生效。反过来先写长属性再写 `background`，则可能被重置。

## 关联示例

- [层叠、层与主题](../../examples/foundations/cascade-layers-theme.html)：交互比较来源、重要性、层顺序与全局关键字。
- [自定义属性与类型注册](../../examples/foundations/custom-properties.html)：观察变量继承、局部覆盖、回退值与 `@property`。

## 11. 练习

1. 用 `@layer` 实现 reset、base、components 三层，让工具类无需 `!important` 覆盖组件。
2. 写一个局部主题，只改变某个卡片的主色，不影响页面其他区域。
3. 用 `currentColor` 统一按钮边框、图标和文字颜色。
4. 解释为什么 `border-var(--side)-color` 无效。
5. 用 `@property` 注册一个 `--progress` 百分比变量，并实现宽度过渡。

> 下一篇：[盒模型与尺寸](04-box-model.md)。
