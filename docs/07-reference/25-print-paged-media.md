# 25 · 打印与分页媒体

> 学习目标：为文档、报表和票据设计可靠的打印样式，理解 `@media print`、分页属性和屏幕布局的差异。

## 1. 打印样式不是缩小版网页

屏幕依赖滚动、悬停、动画和交互，打印依赖固定纸张、分页与静态内容。

```text
屏幕                            打印
可滚动长页面          ──▶      多张固定尺寸页面
hover 提示            ──▶      不可用，信息需静态呈现
动画与视频            ──▶      通常移除或提供替代内容
交互式导航            ──▶      可显示目录或隐藏
深色背景             ──▶      通常改为白底黑字节省墨水
```

```css
@media print {
  body {
    color: #000;
    background: #fff;
  }
}
```

## 2. 分离打印样式

小项目可直接写在 `@media print` 中；内容较多的文档建议单独文件：

```html
<link rel="stylesheet" href="print.css" media="print" />
```

浏览器通常仍会下载打印样式，因此不要把大量图片或字体仅用于打印。

## 3. 页面尺寸与边距

```css
@page {
  size: A4;
  margin: 18mm 16mm;
}

@page :first {
  margin-block-start: 24mm;
}
```

`size` 支持 A4、A5、letter 等命名尺寸，也支持 `210mm 297mm`。浏览器打印对话框中的纸张、缩放和页眉页脚设置仍可能覆盖页面效果，不能把打印结果完全交给 CSS 控制。

## 4. 避免在元素中间分页

```css
h1,
h2,
h3 {
  break-after: avoid;
  page-break-after: avoid;
}

figure,
table,
pre,
blockquote {
  break-inside: avoid;
  page-break-inside: avoid;
}
```

`break-inside: avoid` 是请求而不是绝对保证；元素高于一页时仍会被拆分。

```css
p {
  orphans: 3;
  widows: 3;
}
```

- `orphans`：页面底部至少保留的行数。
- `widows`：页面顶部至少保留的行数。

## 5. 链接、URL 与补充信息

屏幕链接通常不显示地址。打印文档可显示：

```css
@media print {
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-size: 0.85em;
    overflow-wrap: anywhere;
  }
}
```

注意：

- 不要给页内锚点附加无意义 URL。
- 很长 URL 可能破坏排版，应允许换行或只显示域名。
- 重要信息不能只存在于链接目标中。

## 6. 图片、背景与颜色

```css
@media print {
  img {
    max-width: 100% !important;
    height: auto;
  }

  .no-print { display: none !important; }

  * {
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
}
```

`print-color-adjust: exact` 是提示浏览器尽量保留颜色和背景，并不保证所有用户都会开启背景图形。**关键内容不能只靠背景色表达**，例如状态应同时有文字。

## 7. 表格

```css
@media print {
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10pt;
  }

  thead { display: table-header-group; }
  tfoot { display: table-footer-group; }
  tr { break-inside: avoid; }
  th,
  td { border: 1px solid #777; padding: 0.35em; }
}
```

跨页表格重复表头能显著提升可读性。避免固定高度和 `overflow: hidden`，否则内容可能被裁掉。

## 8. 代码与长内容

```css
pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-size: 9pt;
}
```

代码行仍可能过长。打印场景可考虑：

- 显示行号而不是保留工具栏。
- 用更小字号并设置上下限。
- 把超长代码拆成多个块。
- 对可横向滚动的代码表使用专门的横向页面。

```css
@page wide {
  size: A4 landscape;
}

.wide-section {
  page: wide;
}
```

命名页面适合大型技术文档，但浏览器对 `page` 属性的支持与分页行为存在差异，需要实测。

## 9. 完整打印样式示例

```html
<article class="report">
  <header>
    <h1>季度报告</h1>
    <p class="meta">2026 年第三季度</p>
  </header>
  <nav class="toolbar"><button>打印</button></nav>
  <section>
    <h2>摘要</h2>
    <p>这是一段需要打印的正文。</p>
  </section>
  <table>
    <thead><tr><th>项目</th><th>数值</th></tr></thead>
    <tbody><tr><td>收入</td><td>100</td></tr></tbody>
  </table>
</article>
```

```css
@media print {
  @page { size: A4; margin: 18mm; }

  body { font: 11pt/1.6 serif; color: #000; background: #fff; }
  .toolbar { display: none; }
  .report { max-width: none; }
  h1 { font-size: 22pt; }
  h2 { break-after: avoid; }
  table { width: 100%; border-collapse: collapse; }
  thead { display: table-header-group; }
  tr { break-inside: avoid; }
  th, td { padding: 0.4em; border: 1px solid #777; }
}
```

## 10. 常见问题

| 症状 | 排查方向 |
| --- | --- |
| 背景没有打印 | 用户是否开启背景图形；内容是否依赖背景 |
| 标题孤立在页底 | `break-after: avoid` 是否生效，标题是否被容器包裹 |
| 图片被裁切 | 固定宽高、object-fit、overflow、缩放比例 |
| 表格跨页没有表头 | thead 的 display 是否被覆盖 |
| 一页塞入过多内容 | 浏览器缩放、字号、行高、margin |
| 打印按钮被打印 | `.no-print` 或 media print 隐藏 |
| URL 过长导致溢出 | `overflow-wrap: anywhere` 或只显示短文本 |

## 11. 验证方法

1. 在目标浏览器中使用“打印预览”。
2. 分别测试 A4 纵向、横向和不同缩放比例。
3. 检查首页、表格跨页、长代码块、图片和图注。
4. 确认按钮、导航、弹层和装饰元素被合理隐藏。
5. 保存为 PDF 后再次检查字体、分页与链接。
6. 如面向正式交付，至少在 Chrome、Edge、Safari 中抽查。

## 关联示例

- [打印与分页布局](../../examples/engineering/print-layout.html)：`@page`、分页规则、表头、孤行和打印颜色，可直接调用浏览器打印预览验证。

## 12. 练习

1. 为一篇技术文章添加打印样式，隐藏导航并显示外部链接地址。
2. 制作跨页表格，要求每页重复表头且行不被拆开。
3. 给宽表格设置横向页面，并验证浏览器实际分页结果。
4. 实现黑白打印主题，确保只靠颜色区分的状态仍有文字说明。

> 返回 [文档首页](../README.md)。
