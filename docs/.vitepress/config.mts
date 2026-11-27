import { defineConfig } from 'vitepress'

const tutorialBasics = [
  ['01-how-css-works', '01 · 你写的 CSS 是怎么变成画面的'], ['02-selectors', '02 · 选择器：精准选中元素'],
  ['03-cascade-inheritance', '03 · 谁说了算：层叠与继承'], ['04-box-model', '04 · 盒子到底占多大'],
  ['05-units', '05 · 单位：长度以谁为基准'], ['06-colors-backgrounds', '06 · 颜色与背景'],
  ['07-typography', '07 · 文字排版'], ['08-display-flow', '08 · display 与文档流'],
]

const tutorialAdv = [
  ['09-position', '09 · position：定位的参照系'], ['10-flex', '10 · Flexbox：一行空间怎么分'],
  ['11-grid', '11 · Grid：二维空间怎么画'], ['12-responsive', '12 · 响应式：从视口到组件'],
  ['13-transform-transition', '13 · transform 与过渡'], ['14-animation', '14 · animation：关键帧与时间轴'],
  ['15-custom-properties', '15 · 自定义属性与主题'], ['16-pseudo-elements', '16 · 伪类与伪元素进阶'],
]

const tutorialPro = [
  ['17-overflow-scroll', '17 · overflow 与滚动'], ['18-stacking-context', '18 · 层叠上下文'],
  ['19-bfc-containing-block', '19 · BFC、包含块与行内布局'], ['20-container-query', '20 · 容器查询与现代选择器'],
  ['21-rendering-performance', '21 · 渲染与性能'], ['22-architecture', '22 · 架构与影响范围'],
  ['23-accessibility', '23 · 可访问性与渐进增强'], ['24-forms', '24 · 表单控件与状态'],
  ['25-tables-lists', '25 · 表格、列表与计数'], ['26-modern-platform', '26 · 现代平台特性'],
  ['27-print', '27 · 打印与分页媒体'], ['28-shapes-multicol', '28 · 多列、形状与混合'],
]

const group = (prefix, text, items) => ({
  text,
  items: items.map(([slug, title]) => ({ text: title, link: `/${prefix}/${slug}` })),
})

export default defineConfig({
  title: 'CSS 教程',
  description: '按知识点的 CSS 教程：基础、进阶、高级，每个知识点配图示、可交互 demo 与常见问题',
  base: '/css-concept-course/',
  cleanUrls: true,
  ignoreDeadLinks: [/^\/examples\//, /^\.\.\/\.\.\/examples\//],
  lastUpdated: true,
  head: [['meta', { name: 'theme-color', content: '#3f6b2a' }]],
  markdown: {
    config(md) {
      md.core.ruler.push('rewrite_demo_links', (state) => {
        for (const token of state.tokens) {
          if (!token.children) continue
          for (const child of token.children) {
            if (child.type !== 'link_open') continue
            const href = child.attrGet('href') || ''
            const m = href.match(/^(?:\.\.\/)+examples\/(.+\.html)(?:#.*)?$/)
            if (m) {
              child.attrSet('href', `/css-concept-course/examples/${m[1]}`)
              // 直接打开 demo 时另开标签页，避免离开当前教程页。
              child.attrSet('target', '_blank')
              child.attrSet('rel', 'noopener noreferrer')
            }
          }
        }
      })
    },
  },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '教程总览', link: '/tutorial/README' },
    ],
    sidebar: [
      { text: '开始', items: [{ text: '教程总览（按知识点）', link: '/tutorial/README' }] },
      group('tutorial', '基础篇 · 写出样式', tutorialBasics),
      group('tutorial', '进阶篇 · 布局与动效', tutorialAdv),
      group('tutorial', '高级篇 · 机制与驾驭', tutorialPro),
    ],
    search: { provider: 'local', options: { placeholder: '搜索教程、图示与 demo' } },
    outline: { level: [2, 3], label: '本页结构' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    footer: { message: 'CSS 教程 · 静态发布', copyright: '' },
    editLink: { pattern: 'https://github.com/pengqinping/css-concept-course/edit/main/docs/:path', text: '在 GitHub 上编辑' },
  },
})
