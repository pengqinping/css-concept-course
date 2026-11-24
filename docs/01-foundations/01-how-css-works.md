# 01 · CSS 是如何工作的

> 学习目标：知道一条 CSS 规则从编写到屏幕像素经历了什么，并能用浏览器的样式与布局工具验证自己的判断。

## 1. CSS 解决什么问题

HTML 负责内容与语义，CSS 负责表现层，JavaScript 负责交互与状态。把结构、表现和行为分开，可以让同一份 HTML 拥有不同主题，也让样式更易维护。

```html
<article class="card">
  <h2>CSS 学习手记</h2>
  <p>从规则到渲染，建立完整心智模型。</p>
</article>
```

```css
.card {
  padding: 1rem;
  border: 1px solid #d7d3c8;
  border-radius: 0.75rem;
  background: #fbfaf6;
}
```

样式表通过“选择器 + 声明块”描述规则：

```css
选择器 {
  属性: 值;
}
```

一条声明以分号结束；属性与值之间使用冒号。CSS 注释使用 `/* ... */`。

## 2. 样式从哪里来

页面最终样式并不只来自你写的 CSS。浏览器会合并多个来源：

```text
作者样式（你的 CSS）
        ↕ 按层叠规则竞争
用户样式（浏览器设置、用户样式表）
        ↕
用户代理样式（浏览器默认样式）
```

开发时应优先使用显式的作者样式覆盖默认样式，而不是依赖某个浏览器的默认外观。全局初始化不是越多越好，应有目的地设置盒模型、图片和基础排版。

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}

img,
picture,
video,
canvas,
svg {
  display: block;
  max-width: 100%;
}
```

## 3. 从样式表到屏幕

```text
HTML ──解析──▶ DOM
                  │
CSS ──解析──▶ CSSOM
                  │
                  ├──▶ 样式计算：哪些声明生效
                  ├──▶ 布局：元素在什么位置、占多大
                  ├──▶ 绘制：颜色、文字、边框、阴影
                  └──▶ 合成：图层交给 GPU/浏览器合成
```

### 样式计算

浏览器为每个元素计算最终生效的声明，考虑层叠、继承、默认值和依赖解析。例如 `width: 50%` 必须等包含块尺寸明确后才能得到最终像素值。

### 布局

布局回答两个问题：

1. 元素占多大空间？
2. 元素放在哪里？

不同布局模式给出不同答案：块级布局、Flex、Grid、表格布局和绝对定位的算法并不相同。

### 绘制与合成

文字、背景、边框、阴影通常需要绘制。`transform` 与 `opacity` 的某些动画可以仅通过合成完成，因而更可能保持流畅，但并不代表任何情况下都一定不会重绘。

## 4. 把 CSS 放进页面

### 外部样式表

适合正式项目，可缓存、易拆分。

```html
<link rel="stylesheet" href="/styles/main.css" />
```

### `<style>` 标签

适合单文件示例或关键样式内联。

```html
<style>
  body { margin: 0; }
</style>
```

### 行内样式

优先级高且难以维护，通常只用于确实需要动态设置单个 CSS 变量的场景。

```html
<div style="--progress: 68%"></div>
```

## 5. 一个可运行的最小示例

保存为 `basic.html`，用浏览器打开：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CSS 工作流程</title>
  <style>
    :root {
      color-scheme: light;
      font-family: system-ui, sans-serif;
      --accent: #3d601c;
      --surface: #fbfaf6;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #f4f1e9;
      color: #24261f;
    }

    .card {
      width: min(100% - 2rem, 28rem);
      padding: 1.5rem;
      border: 1px solid #d7d3c8;
      border-radius: 1rem;
      background: var(--surface);
      box-shadow: 0 1rem 2rem rgb(36 38 31 / 8%);
    }

    .card h1 {
      margin: 0 0 0.5rem;
      font-size: clamp(1.5rem, 5vw, 2rem);
    }

    .card p { margin: 0; color: #686b61; }
  </style>
</head>
<body>
  <article class="card">
    <h1>CSS 工作流程</h1>
    <p>内容 → 规则 → 样式计算 → 布局 → 绘制 → 合成</p>
  </article>
</body>
</html>
```

## 6. DevTools 是最重要的学习工具

在元素面板中重点查看：

- **Styles**：哪些规则命中，哪些声明被划掉，为什么被覆盖。
- **Computed**：最终计算值，确认继承和默认值。
- **Layout**：盒模型的 margin、border、padding、content 尺寸。
- **Elements → Accessibility**：语义、焦点顺序和可访问名称。
- **Rendering**：绘制边界、图层、布局偏移等信息。

常用操作：

- 临时禁用某条声明，验证它是否影响布局。
- 修改数值，观察包含块与兄弟元素如何变化。
- 勾选强制伪类，检查 `:hover`、`:focus-visible` 等状态。
- 使用 Computed 搜索 `display`、`position`、`box-sizing`。

## 7. 常见误区

| 误区 | 正确理解 |
| --- | --- |
| CSS 一定按书写顺序覆盖 | 还要考虑来源、层、优先级和重要性 |
| 修改 DOM 一定会触发全部重排 | 浏览器会尽量缩小失效范围，但仍需避免布局抖动 |
| CSS 属性越多越具体越好 | 过度约束会降低可维护性和适应性 |
| Computed 显示 16px，就是设置了 16px | 也可能是继承、默认值或相对单位计算后的结果 |
| 所有浏览器渲染完全一致 | 字体、抗锯齿、默认样式与特性实现可能存在差异 |

## 8. 练习

1. 创建一个包含标题、段落和按钮的页面，只用外部样式表完成排版。
2. 在 DevTools 中删除 `box-sizing`，观察固定宽度元素的整体尺寸如何变化。
3. 为同一个元素写两条冲突规则，分别改变来源顺序、选择器优先级和 `!important`，记录最终结果。
4. 使用 Computed 面板查找一个没有显式设置的 `font-size`，判断它来自哪里。

> 下一篇：[选择器与伪类](02-selectors.md)。先解决“选谁”的问题，再研究“怎么排”。
