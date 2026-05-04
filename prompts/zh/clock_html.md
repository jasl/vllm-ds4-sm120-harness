---
tags: coding, html, long, subjective, user-report
max_tokens: 32768
temperature: 1.0
top_p: 1.0
min_chars: 1800
any_terms: setInterval, requestAnimationFrame
any_terms_hour_hand: hour, hourHand, 时针
any_terms_minute_hand: minute, minuteHand, 分针
any_terms_timezone: Asia/Shanghai, UTC+8, 北京时间, 中国标准时间, 北京时区
require_html_artifact: true
---
请帮我创建一个单文件 HTML 时钟应用，要求直接给出完整代码。

功能和视觉要求：
1. 时钟表盘是圆形，有刻度、数字、时针、分针、秒针，并在表盘内部显示当前时间和日期。
2. 表盘需要有简洁的高级感：白色背景、深色边框、轻微 3D 阴影。
3. 用 JavaScript 动态生成 60 个刻度，整点刻度更粗更深。
4. 时间必须转换为中国标准时间（北京时区，Asia/Shanghai）。
5. 写一个 updateClock() 函数，计算时针、分针、秒针角度；秒针需要尽量平滑运动。
6. 使用 setInterval 或 requestAnimationFrame 驱动刷新。
7. 代码需要兼容 Edge 浏览器。
