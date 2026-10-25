# SVG 重绘规范（FDE 培训教材配图）

## 目标
把 配图/ 下的 PNG 示意图重绘为矢量 SVG，风格统一、文字可选中、缩放不糊。目测效果要像同一套设计系统产出的图。

## 画布
- viewBox 优先 `0 0 880 520`；如果原图偏宽，可用 `0 0 960 480`；偏方用 `0 0 720 560`。
- 不要写 width/height 属性（由 HTML 控制），只写 viewBox + xmlns + role="img" + aria-label。
- 背景留白，不画整块底色；如需分组卡片，用 `fill="#ffffff"` + `stroke="#e2e8f0"` + `rx="12"`。

## 字体
- font-family: `system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif`
- 标题 16–18px / font-weight 600，正文 13–14px，注释 12px，最小不低于 11.5px。
- 中文不要用 letter-spacing；行长超过约 22 个汉字必须手动换行（多行 <text><tspan x=.. dy=..>）。

## 配色（只使用这几个）
- 主文字 #0f172a，次级文字 #475569，弱文字 #64748b
- 蓝 #2563eb / 浅蓝底 #eff6ff / 蓝边 #bfdbfe
- 绿 #059669 / 浅绿底 #ecfdf5 / 绿边 #a7f3d0
- 橙 #d97706 / 浅橙底 #fffbeb / 橙边 #fde68a
- 红 #dc2626 / 浅红底 #fef2f2 / 红边 #fecaca
- 紫 #7c3aed / 浅紫底 #f5f3ff / 紫边 #ddd6fe
- 分隔线 #e2e8f0，箭头/连线 #94a3b8
- 渐变可用同色系 linearGradient，浅色起浅色终，不要花哨。

## 图形
- 卡片圆角 rx=12，描边 1px，阴影不要用 filter（印刷糊），靠描边和浅底区分层次。
- 流程箭头用 <path> + marker-end（在 <defs> 里定义 arrow），线宽 1.5，颜色 #94a3b8。
- 图标一律用简单几何（圆/方/线）自绘，不要用 emoji，不要引外部图片。
- 数字/编号徽章：圆形 r=13，底色用主色，白色数字 12px。

## 内容要求
- 原图里的**全部文字**都要出现（标题、卡片标题、说明、图例、数字），用简洁准确的措辞压缩长句，但不能丢信息、不能编造新内容。
- 层次要和原图一致：谁包含谁、箭头指向、左右/上下顺序。
- 同一张图里层级不超过 3 层；文字超过 3 行就要考虑拆成卡片。

## 输出
- 文件写到 `配图/svg/<原文件名去扩展名>.svg`，UTF-8 无 BOM，缩进 2 空格，自包含。
- 写完后用 read 复查一遍：确认 xmlns、viewBox、没有 width/height、没有外部引用。
