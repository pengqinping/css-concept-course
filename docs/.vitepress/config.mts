import { defineConfig } from 'vitepress'
import { fileURLToPath } from 'node:url'

const chapters = [
  ['01-pipeline', '01 · 从规则到像素'], ['02-selectors', '02 · 选择器：精准找到元素'],
  ['03-cascade', '03 · 谁说了算'], ['04-inheritance', '04 · 值从哪里来'],
  ['05-box-model', '05 · 元素到底占多大'], ['06-containing-block', '06 · 百分比是谁的百分比'],
  ['07-bfc', '07 · 为什么布局会塌'], ['08-stacking-context', '08 · 谁盖住谁'],
  ['09-typography', '09 · 文字如何排版'], ['10-color', '10 · 颜色如何表达'],
  ['11-background-border', '11 · 盒子的表面'], ['12-display-overflow', '12 · 看见与看不见'],
  ['13-transform', '13 · 视觉变形'], ['14-animation', '14 · 状态的变化'],
  ['15-flex', '15 · 一维空间怎么分'], ['16-grid', '16 · 二维空间怎么画'],
  ['17-container-query', '17 · 组件自己的断点'], ['18-units', '18 · 长度以谁为参照'],
  ['19-responsive', '19 · 从视口到组件'], ['20-forms', '20 · 表单控件与状态'],
  ['21-tables', '21 · 表格、列表与计数'], ['22-native-ui', '22 · 原生弹层'],
  ['23-architecture', '23 · 样式架构与设计令牌'], ['24-accessibility', '24 · 无障碍与兼容性'],
  ['25-rendering', '25 · 变化如何发生'], ['26-scope-nesting', '26 · 嵌套、@scope 与 :has'],
  ['27-modern-features', '27 · 新交互平台'], ['28-print', '28 · 打印与分页媒体'],
  ['29-shapes-mix', '29 · 多列、形状与混合'], ['30-component-boundary', '30 · 交互状态与组件边界'],
]

const appendices = [
  ['appendix-a-cheatsheet', '附录 A · 属性速查'], ['appendix-b-recipes', '附录 B · 布局配方'],
  ['appendix-c-exercises', '附录 C · 练习与答案'], ['appendix-d-pitfalls', '附录 D · 常见问题'],
  ['appendix-e-glossary', '附录 E · 术语表'],
]

const group = (prefix, text, items) => ({
  text,
  items: items.map(([slug, title]) => ({ text: title, link: `/${prefix}/${slug}` })),
})

export default defineConfig({
  title: 'CSS 技术教程',
  description: '从规则到像素：能预测、能构建、能维护的 CSS 教程',
  base: '/css-concept-course/',
  cleanUrls: true,
  ignoreDeadLinks: [/^\/examples\//, /^\.\.\/\.\.\/examples\//],
  lastUpdated: true,
  head: [['meta', { name: 'theme-color', content: '#3f6b2a' }]],
  markdown: {
    config(md) {
      const core = md.core.ruler.getRules('inline').includes
      md.core.ruler.push('rewrite_demo_links', (state) => {
        for (const token of state.tokens) {
          if (!token.children) continue
          for (const child of token.children) {
            if (child.type !== 'link_open') continue
            const href = child.attrGet('href') || ''
            const m = href.match(/^(?:\.\.\/)+examples\/minimal\/(.+\.html)(?:#.*)?$/)
            if (m) {
              child.attrSet('href', `/css-concept-course/examples/minimal/${m[1]}`)
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
      { text: '课程总览', link: '/course/README' },
      { text: '写作规范', link: '/course/STYLE' },
    ],
    sidebar: [
      { text: '开始', items: [{ text: '课程总览', link: '/course/README' }] },
      group('course', '一 · 能预测（01–08）', chapters.slice(0, 8)),
      group('course', '二 · 能构建（09–22）', chapters.slice(8, 22)),
      group('course', '三 · 能维护（23–30）', chapters.slice(22)),
      group('course', '附录', appendices),
    ],
    search: { provider: 'local', options: { placeholder: '搜索教程、图示与 demo' } },
    outline: { level: [2, 3], label: '本页结构' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    footer: { message: 'CSS 技术教程 · 静态发布', copyright: '' },
    editLink: { pattern: 'https://github.com/pengqinping/css-concept-course/edit/main/docs/:path', text: '在 GitHub 上编辑' },
  },
})
