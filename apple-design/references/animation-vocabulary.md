# Animation Vocabulary · 动画术语表

> **来源**：emilkowalski/skills 的 animation-vocabulary，将模糊描述转换为精确术语。
> **用途**：当用户描述一个效果但不知道它的名字时，使用此表查找正确术语。

---

## 入场与退出——元素如何出现和消失

- **Fade in / Fade out** — 通过改变透明度使元素出现或消失。
- **Slide in** — 元素从屏幕外滑入（左、右、上或下）。
- **Scale in** — 元素在出现时从小变大，通常与淡入配对。
- **Pop in** — 元素出现时带有轻微过冲，像弹入位置。
- **Reveal** — 内容逐渐被揭开，通常通过动画 clip-path 或 mask。
- **Enter / Exit** — 元素被添加到或从屏幕移除时播放的动画。

## 排序与计时——协调多个元素或时刻

- **Keyframes** — 动画中的定义点（0%, 50%, 100%），浏览器填充间隙。
- **Interpolation / Tween** — 在起始和结束值之间生成所有中间帧，使运动连续。
- **Stagger** — 一个接一个动画多个元素，每个之间有小延迟，创建级联效果。
- **Orchestration** — 故意计时多个动画，使它们感觉像一个协调的运动。
- **Delay** — 动画开始前的时间。
- **Duration** — 动画花费多长时间。
- **Fill mode** — 动画开始前或结束后元素是否保持其第一帧或最后一帧的样式。
- **Stepped animation** — 分成离散步的动画，如倒计时器。

## 移动与变换——改变元素的位置、大小或角度

- **Translate** — 沿X或Y轴移动元素。
- **Scale** — 使元素变大或变小。
- **Rotate** — 围绕点旋转元素。
- **Skew** — 沿X或Y轴倾斜元素。
- **3D tilt / Flip** — 在3D空间中旋转（rotateX / rotateY）以增加深度。
- **Perspective** — 3D效果的强度——较低的值夸大深度。
- **Transform origin** — 缩放或旋转生长或围绕的锚点。
- **Origin-aware animation** — 元素从其触发动画出来，如弹窗从打开它的按钮生长而不是从自己的中心。

## 状态间过渡——连接一个状态、视图或元素到另一个

- **Crossfade** — 一个元素淡出时另一个淡入，在同一位置。
- **Continuity transition** — 通过视觉连接前后保持用户方向的变化。
- **Morph** — 一个形状平滑地变成另一个形状，如灵动岛。
- **Shared element transition** — 元素从一个位置旅行并变换到另一个位置，如缩略图扩展为卡片。
- **Layout animation** — 当元素的大小或位置改变时，它动画到新位置而不是吸附。
- **Accordion / Collapse** — 部分平滑扩展和折叠其高度以显示或隐藏内容。
- **Direction-aware transition** — 内容向前滑动一个方向，向后滑动相反方向。

## 滚动——与滚动或导航视图相关的运动

- **Scroll reveal** — 元素在进入视口时淡入或滑入位置。
- **Scroll-driven animation** — 进度直接系于滚动位置的动画。
- **Parallax** — 背景和前景在滚动时以不同速度移动，创造深度。
- **Page transition** — 从一个页面或路由导航到另一个时播放的动画。
- **View transition** — 浏览器在两个状态或页面之间变形，连接共享元素。

## 反馈与交互——响应用户操作

- **Hover effect** — 光标移到元素上时的视觉变化。
- **Press / Tap feedback** — 元素被点击时的微妙缩小，使其感觉物理。
- **Hold to confirm** — 用户按住按钮时填充的进度效果。
- **Drag** — 通过抓取移动元素，释放时通常带动量。
- **Drag to reorder** — 在列表中拖动项目以重新排列。
- **Swipe to dismiss** — 将元素拖出屏幕以关闭。
- **Rubber-banding** — 拖过边界时的抵抗和回弹（iOS过度滚动感）。
- **Shake / Wiggle** — 快速左右抖动，表示错误或拒绝输入。
- **Ripple** — 从点击点扩展的圆圈，确认按下。

## 缓动——速度如何在动画中变化

- **Easing** — 动画加速或减速的速率。
- **Ease-out** — 开始快，结束慢。大多数UI和响应用户的默认值。
- **Ease-in** — 开始慢，结束快。通常避免；感觉迟钝。
- **Ease-in-out** — 慢、快、慢。适合已在屏幕上的元素从A移到B。
- **Linear** — 恒定速度。避免用于UI；保留给跑马灯或进度条。
- **Cubic-bezier** — 自定义缓动曲线。
- **Asymmetric easing** — 以不同速率加速和减速的曲线。感觉比对称的更有生命力。

## 弹簧动画——基于物理的运动

- **Spring** — 由物理（张力、质量、阻尼）驱动的运动，而不是固定持续时间。
- **Stiffness / Tension** — 弹簧拉向目标的强度。更高感觉更快。
- **Damping** — 弹簧稳定的速度。较低阻尼意味着更多弹跳和振荡。
- **Mass** — 动画元素感觉有多重。更多质量使它更慢更迟钝。
- **Bounce** — 过冲并稳定的弹簧，增加俏皮感。
- **Perceptual duration** — 弹簧感觉完成的时间，即使它在下面继续微稳定。
- **Momentum** — 携带速度的运动，特别是拖拽或中断后。
- **Velocity** — 元素移动的速度和方向。弹簧在中断时将其带入下一个动画。
- **Interruptible animation** — 可以在飞行中平滑重定向而不是先完成的动画。

## 循环与环境运动——自行运行的动画

- **Marquee** — 在循环中连续滚动的文本或内容。
- **Loop** — 重复的动画，有限次或无限次。
- **Alternate (yoyo)** — 每次迭代前进然后反转的循环。
- **Orbit** — 元素围绕另一个元素连续路径环绕。
- **Pulse** — 重复的缩放或透明度变化以吸引注意。
- **Float** — 温和的连续上下漂移，使静态元素感觉有生命。
- **Idle animation** — 元素只是坐在那里等待交互时播放的微妙运动。

## 打磨与效果——区分好与棒的小触感

- **Blur** — 用于软化元素或掩盖微小缺陷的模糊滤镜。
- **Clip-path** — 将元素裁剪为形状，用于揭示、遮罩和前后滑块。
- **Mask** — 使用形状或渐变隐藏或揭示元素部分。
- **Before / after slider** — 可拖动的分隔器，在两个叠加图像之间擦除以比较。
- **Line drawing** — 自己画入的SVG路径，像无形的笔在描。
- **Text morph** — 文本在变化时逐字符动画。
- **Skeleton / Shimmer** — 内容加载时显示的带有移动光泽的占位符。
- **Number ticker** — 数字滚动或计数到值。
- **Tabular numbers** — 固定宽度数字，数字变化时不会移动。
- **Typewriter** — 文本一次出现一个字符，像在打字。

## 性能——保持运动流畅而非卡顿

- **Frame rate (FPS)** — 每秒绘制的帧。60fps是流畅运动的基准。
- **Jank** — 浏览器因跟不上动画而掉帧时的可见卡顿。
- **Dropped frame** — 浏览器错过绘制截止日期的帧。
- **Compositing** — 让GPU在自己的图层上移动或淡入元素，无需重做布局或绘制。
- **will-change** — 元素即将动画的CSS提示，浏览器可以提前提升到自己的图层。
- **Layout thrashing** — 动画 width、height、top 或 left 等属性，迫使浏览器每帧重新计算布局。

## 需要知道的原则——指导何时和如何动画的概念

- **Purposeful animation** — 运动应该服务于功能——定向、给反馈、显示关系——而不仅仅是装饰。
- **Anticipation** — 移动前在相反方向的小蓄力，暗示即将发生什么。
- **Follow-through** — 元素的部分在主运动停止后继续移动并稍微稳定，增加重量。
- **Squash & stretch** — 在移动时变形元素以传达重量、速度和灵活性。
- **Perceived performance** — 正确的动画使界面感觉更快，即使不是。
- **Frequency of use** — 用户看到动画的频率越高，它应该越短越微妙。
- **Spatial consistency** — 动画时使元素在状态间保持其身份和位置。
- **Hardware acceleration** — 动画 transform 和 opacity 让GPU保持运动流畅。
- **Reduced motion** — 通过减弱或移除运动来尊重用户的 prefers-reduced-motion 设置。

---

## 使用示例

**用户**："那个弹窗打开时的弹性效果叫什么？"
**回答**：**Pop in** — 元素出现时带有轻微过冲，像弹入位置。接近的替代：**Spring**（如果由物理驱动）或 **Bounce**（如果有明显弹跳）。

**用户**："iOS滚动拉过头时的那个回弹。"
**回答**：**Rubber-banding** — 拖过边界时的抵抗和回弹（iOS过度滚动感）。

**用户**："图片变成另一个图片的那个。"
**回答**：**Morph** — 一个形状平滑地变成另一个形状。接近的替代：**Crossfade**（如果只是在同一位置淡入淡出）、**Shared element transition**（如果元素旅行并变换位置）。
