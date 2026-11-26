import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const src = path.join(root, 'examples', 'minimal')
const dst = path.join(root, 'docs', 'public', 'examples', 'minimal')
fs.rmSync(dst, { recursive: true, force: true })
fs.mkdirSync(dst, { recursive: true })

let count = 0
for (const file of fs.readdirSync(src)) {
  if (!file.endsWith('.html')) continue
  let html = fs.readFileSync(path.join(src, file), 'utf8')
  html = html.replace(
    /\.\.\/\.\.\/docs\/course\/([0-9]{2}-[a-z-]+)\.md/g,
    (_, slug) => `/css-concept-course/course/${slug}`,
  )
  // 从 iframe 内点击时必须跳到顶层页面，否则只在小窗里导航。
  html = html.replace(
    /<a href="(\/css-concept-course\/course\/[0-9]{2}-[a-z-]+)">/g,
    (_, href) => `<a target="_top" href="${href}">`,
  )
  fs.writeFileSync(path.join(dst, file), html)
  count++
}
console.log(`copied ${count} demos -> ${dst}`)
