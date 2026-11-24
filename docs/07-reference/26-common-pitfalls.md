# 26 · 常见问题速查

> 按症状定位，而不是凭经验堆属性。先复现问题，再用 DevTools 验证是哪条规则、哪个布局上下文或哪个尺寸约束导致。

## 1. 样式没有生效

| 症状 | 优先检查 | 常见修复 |
| --- | --- | --- |
| 整条规则没命中 | 选择器、DOM 层级、属性值 | 修正选择器或状态类 |
| 声明被划掉 | 同优先级后续规则、简写、important | 调整源码顺序或重构覆盖关系 |
| 改了颜色但没变化 | currentColor、动画、transition、继承 | 检查最终计算值与动画状态 |
| 属性完全没出现 | 值不合法、浏览器不支持 | 查看 DevTools 警告，使用 @supports |
| 工具类无法覆盖组件 | @layer 顺序或 important | 明确层顺序，避免提高选择器优先级 |

## 2. 尺寸与溢出

| 症状 | 根因 | 修复 |
| --- | --- | --- |
| width: 100% 仍溢出 | padding/border 未包含、子元素溢出 | box-sizing: border-box、约束子元素 |
| 块元素没占满一行 | max-width、margin、父级约束 | 查看包含块与 computed width |
| 图片溢出 | 缺少 max-width 或固定尺寸 | max-width: 100%; height: auto |
| Flex 子项不收缩 | min-width: auto | min-width: 0 + 文本换行 |
| Grid 长代码撑破布局 | 1fr 的最小内容尺寸 | minmax(0, 1fr)、min-width: 0 |
| 子元素比父级高 | 固定 height + 内容过多 | 使用 min-height、允许滚动或裁剪 |
| 百分比宽高不符合预期 | 包含块或高度链未确定 | 检查最近包含块与父级 height |
| 页面横向滚动 | 固定宽度、长文本、transform 越界 | 找出 scrollWidth 超限元素并修根因 |

## 3. 间距与对齐

| 症状 | 根因 | 修复 |
| --- | --- | --- |
| 上下间距相加了 | 误以为 margin 不折叠 | 使用 gap 或建立 BFC |
| 子元素把父级顶开 | 父子 margin 折叠 | display: flow-root 或 padding |
| justify-content 无效 | 不是 Flex 容器或没有剩余空间 | 检查 display 与子项尺寸 |
| align-items 无效 | 属性作用于交叉轴，或容器不是 Flex | 检查 flex-direction 与 display |
| align-content 无效 | 只有一行或容器不是 Flex | 使用 align-items 或开启换行 |
| Grid 项目不填满单元格 | justify-items/align-items 非 stretch | 改为 stretch 或设置尺寸 |
| 文字基线偏下 | 行盒与图片 baseline | display: block 或 Flex 对齐 |
| 行内元素宽高无效 | display: inline | inline-block/Flex/Grid |

## 4. 定位与层叠

| 症状 | 根因 | 修复 |
| --- | --- | --- |
| absolute 跑到页面角落 | 没有定位祖先 | 给预期父级 position: relative |
| fixed 被祖先裁剪/跟随滚动 | 祖先 transform/filter/contain | 移动浮层或移除祖先属性 |
| sticky 不吸顶 | 祖先 overflow、父级高度不足 | 检查滚动容器与边界 |
| sticky 被 Flex 拉伸 | align-items 默认 stretch | align-self: flex-start |
| z-index 无效 | 非定位元素、非 Flex/Grid 子项 | 建立定位或层叠上下文 |
| z-index 很大仍被遮挡 | 父级层叠上下文太低 | 提升父级或重构上下文 |
| 伪元素跑到背景后 | 父级没有独立层叠上下文 | isolation: isolate |
| opacity: 0 仍挡住点击 | 元素仍可命中 | visibility/pointer-events/inert |

## 5. 文本与排版

| 症状 | 根因 | 修复 |
| --- | --- | --- |
| 行高比预期大 | 字体度量、line-height、行盒 | 检查 font 与 vertical-align |
| 改父级 line-height 后异常 | 子元素继承数值的语义不同 | 使用无单位 line-height 或局部重置 |
| 中文每行只有几个字 | 容器过窄、字号过大 | 调整 minmax、字号与最大宽度 |
| 标题最后一行只有一个字 | 默认换行策略 | text-wrap: balance |
| 长 URL 不换行 | 默认不断词 | overflow-wrap: anywhere |
| 单行省略无效 | 缺少 nowrap/overflow/受限宽度 | 三项同时设置并约束宽度 |
| placeholder 颜色改不了 | 需要 ::placeholder 伪元素 | 单独设置并检查对比度 |
| font 简写丢失属性 | 简写重置了未指定的字体属性 | 拆分为长属性或完整书写 |

## 6. 响应式与容器查询

| 症状 | 根因 | 修复 |
| --- | --- | --- |
| 媒体查询不生效 | viewport meta、语法、加载顺序 | 检查 meta 与 range syntax |
| 100vh 在手机上过高 | 动态浏览器 UI | 使用 100dvh 并真机验证 |
| rem 不随用户设置缩放 | 根字号被固定 px 覆盖 | 根字号使用合理默认或百分比 |
| clamp 没有按预期变化 | 最小/最大值、单位或 calc 语法 | 拆开计算首选值 |
| 容器查询不生效 | 容器不是祖先、type 错误 | 检查容器层级与 inline-size |
| cqw 意外变化 | 查询容器选择错误 | 使用 container-name 明确目标 |
| 容器查询样式作用到自身 | 查询不能选择容器本身 | 查询内部后代 |

## 7. 动画与性能

| 症状 | 根因 | 修复 |
| --- | --- | --- |
| transition 不执行 | 没有起始状态、属性不可动画、display 切换 | 先渲染初始状态，再改状态 |
| 动画结束才跳变 | 元素在初始帧前已到终态 | 使用 @starting-style 或强制起始帧 |
| 展开动画直接跳变 | height: auto 不可插值 | Grid 0fr→1fr 或 JS 测量 |
| 动画卡顿 | 动画 width/top/box-shadow 等 | 改用 transform/opacity |
| will-change 后更卡 | 图层过多、长期占用资源 | 缩小范围并在结束后移除 |
| fixed 元素抖动 | 读写布局或 transform 冲突 | 批量读写，检查合成层 |
| 页面加载后内容跳动 | 图片/广告没有尺寸 | 提供 width/height 或 aspect-ratio |
| reduced-motion 仍动画 | 没有对应媒体查询 | 为动画与过渡提供降级 |

## 8. 快速诊断顺序

```text
问题能否稳定复现？
  ↓
元素是否命中预期规则？
  ↓
Computed 最终值是什么？
  ↓
值来自哪条声明、哪个层、哪种继承？
  ↓
盒模型与包含块是否正确？
  ↓
display / position / overflow 是否改变布局上下文？
  ↓
是否被内容最小尺寸或动画状态影响？
  ↓
修改一个变量，验证假设，再扩大修复范围。
```

## 9. 不应使用的“修复”

- 未找到根因就给所有元素加 `position: relative`。
- 用 `z-index: 99999` 掩盖层叠上下文问题。
- 用 `overflow-x: hidden` 隐藏页面横向溢出。
- 给 Flex/Grid 子项随意加 `width: 0`。
- 到处使用 `!important`。
- 为每个设备尺寸写独立规则。
- 用大量 transform 代替真正的布局。
- 删除焦点轮廓却没有替代样式。
- 为隐藏弹层只设置 opacity，不处理焦点与命中。

> 返回 [文档首页](../README.md)，按章节补齐对应心智模型。
