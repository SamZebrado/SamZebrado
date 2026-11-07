# SamZebrado · Selected work / 精选作品

**自我介绍 · 中文**

我是 SamZebrado，喜欢从实际使用中的小问题出发，做交互原型和实用工具。我能独立使用 Python、MATLAB，具备 C++ 基础，也会借助 AI 开发 Android 应用、轻量 Web 应用和 Windows 工具。

以前有点像“人形 GPT”，喜欢查资料、琢磨问题，再帮人想办法。现在有真正的 GPT，我能做更多事情了。

我关注 AI 应用、开发者工具和人机交互，也对 XR、游戏与创意应用感兴趣。希望从事 AI 应用开发、工具开发或交互原型工作，参与需求梳理、设计、实现和实际使用中的迭代。

我也喜欢查证传言、追问依据，愿意认真讨论，也会在讨论变成攻击时退出；不喜欢网络暴力和用刻板印象判断人。

**About me · English**

I'm SamZebrado. I like turning small problems from everyday use into interaction prototypes and practical tools. I can work independently with Python and MATLAB, have a basic grounding in C++, and use AI to help develop Android apps, lightweight web apps and Windows tools.

I used to be a bit of a “human GPT”: I liked looking things up, thinking problems through and helping people find a way forward. Now, with the real GPT, I can do more.

My interests include AI applications, developer tools and human–computer interaction, as well as XR, games and creative applications. I'm looking for work in AI application development, tool development or interaction prototyping, contributing to requirements, design, implementation and iteration through real use.

I also like checking rumors and asking what evidence supports a claim. I welcome thoughtful discussion and step away when it turns into personal attacks. I dislike online harassment and judging people by stereotypes.

**语言 / Languages**<br>
英语：可用于工作交流，具备听、说、读、写能力；日语：具备基础漫画阅读与不带字幕听懂日常内容的能力。<br>
English: comfortable with workplace communication across listening, speaking, reading and writing. Japanese: basic manga reading and listening comprehension of everyday content without subtitles.

**[Portfolio / 作品集 →](https://samzebrado.github.io/SamZebrado/)** — screenshots, project details and validation boundaries.

## Start here — Completed / In Use · 在用与已完成

- **[IslandSlowlyFall / 慢慢倒](https://github.com/SamZebrado/IslandSlonelyFall)** — `In Use · Stable / Maintenance`<br>
  作者实际在用的本地日常反思与低能量决策工具，帮助找到下一小步。<br>
  A local-first reflection and prioritization tool, used by its creator. [Web · No install / 网页免安装](https://samzebrado.github.io/IslandSlonelyFall/).
我的贡献：结合日常实际使用，提出需求与使用反馈；AI 承担大量实现。作者在用不等于更广泛的用户验收。<br>
My contribution: requirements and feedback from everyday use; AI contributes substantial implementation. Creator use does not establish wider user acceptance.

- **[NoisyGeese / 暴噪鹅](https://github.com/SamZebrado/NoisyGeese)** — `In Use · Author Field-tested`<br>
  浏览器本地录音、频谱／时频图查看与同频段、同长度对照；支持回听、WAV、CSV，以及包含原始 Float32 音频和标签的 .noise 备份导出／导入。<br>
  Browser-local recording, spectrum/spectrogram viewing and comparisons using the same band and duration. Supports playback, WAV, CSV and .noise backup export/import with raw Float32 audio and labels. [Web · No install / 网页免安装](https://samzebrado.github.io/NoisyGeese/).

作者实测：2026 年 11 月 6 日的一次现场使用中，从实录音频发现约 5413 Hz 的间歇性“滴滴”高频噪声线索，并确认 .noise 导出包含录音。这不代表已确定声源或完成多设备验证；dBFS 不是经过校准的 dB SPL，不能用于判断噪声是否超标。现场录音与位置标签未随作品集公开。<br>
Author field test: in one session on 6 November 2026, real recordings revealed a candidate near 5413 Hz associated with intermittent high-frequency beeps; the exported .noise file was confirmed to include audio. This does not establish source identification or multi-device validation. dBFS is not calibrated dB SPL and cannot determine noise-limit compliance. Field audio and location labels are not published with this portfolio.<br>
我的贡献：从实际噪声问题提出需求，使用工具录音、对照并反馈交互问题；AI 承担大量实现。<br>
My contribution: defining needs from a real noise problem, using the tool to record and compare sounds, and reporting interaction issues. AI contributes substantial implementation.

- **[Transparent Floating Browser](https://github.com/SamZebrado/TransparentFloatingBrowser)** — `Completed · Maintenance`<br>
  Android 多窗口透明 WebView，编辑／展示模式与受系统约束的触摸穿透。<br>
  Transparent Android overlays with multiple WebViews, edit/display modes and Android 12+ touch-through constraints. Real-device acceptance remains open.
- **[CheapLive](https://github.com/SamZebrado/CheapLive)** — `Completed · Maintenance`<br>
  浏览器本地 MediaPipe 面捕、程序化 Avatar 与 Android Capture 工作流，整合独立的 TransparentFloatingBrowser 作 Android 悬浮展示。<br>
  Browser-local face capture and procedural avatars, with an Android Capture client and the separate [TransparentFloatingBrowser](https://github.com/SamZebrado/TransparentFloatingBrowser) for Android overlay display. Real-device compatibility, capture quality and the integrated end-to-end experience remain unverified. [Interactive demo / 互动演示](https://samzebrado.github.io/CheapLive/src/contest-demo/contest-interactive-demo.html). [Live face capture / 实时面捕](https://samzebrado.github.io/CheapLive/src/face-tracking/) requires camera permission and WebGL; try a system browser. A cloud-browser WebGL failure does not establish failure on all devices.
我的贡献：选择把独立的透明悬浮浏览器整合进展示工作流；AI 承担大量实现。已有演示与界面检查不等于实机捕捉或整合验收。<br>
My contribution: choosing to integrate the separate floating browser into the display workflow; AI contributes substantial implementation. Demo and interface checks do not establish real capture or integration acceptance.

- **[牛马日记 / LocalStopWatch](https://github.com/SamZebrado/LocalStopWatch)** — `In Use · Stable / Maintenance`<br>
  作者实际在用的本地计时、分段记录与 CSV 导出工具；当前稳定维护。<br>
  A local stopwatch for interval records and CSV export, used by its creator. [Web · No install / 网页免安装](https://samzebrado.github.io/LocalStopWatch/).
- **[DeeSewSew](https://github.com/SamZebrado/DeeSewSew)** — `V1 Complete · Feature Frozen`<br>
  Browser embroidery with front/back thread topology / 正反面针线拓扑的浏览器刺绣。The separate 3D Lab remains experimental. [Web · No install / 网页免安装试玩](https://samzebrado.github.io/DeeSewSew/).

DeeSewSew continues to welcome public playtesting and bug reports within its completed V1.

## Currently Building · 正在开发

**[GrapePaper](https://github.com/SamZebrado/GrapePaper)** — `Active Development`<br>
原文优先的 PDF 中文伴读：手动确认已读、引用溯源与来源短摘录，将模型解释和原始材料分开。<br>
Original-text-first reading with a Chinese companion, explicit reading confirmation, citation trails and source excerpts. Live AI requires a configured service; real-model inference remains unverified. The Zotero excerpt bridge is experimental; no automatic paywalled full-text acquisition. [Reading preview](https://samzebrado.github.io/GrapePaper/).

**[guiLaTeX](https://github.com/SamZebrado/guiLaTeX)** — `Active Development · Web V1 Baseline Complete`<br>
Web V1 的单页可视化排版基线已完成；更完整的文档写作与真实 PDF 工作流仍在继续开发。<br>
The single-page Web V1 baseline is complete. The broader visual editor is actively continuing toward a practical document-writing and PDF workflow. Web V1 runs locally; the [功能与运行说明 / features and local setup](https://samzebrado.github.io/guiLaTeX/showcase/demo_index.html) page is static. [Development journal / 开发纪事](https://samzebrado.github.io/guiLaTeX/showcase/) is a secondary entry.

我的关注点：通过可直接操作的画布降低排版操作负担。需求与使用反馈由我参与梳理，AI 承担大量实现；已完成的是受限 Web V1 基线。<br>
My focus: making layout easier through a directly editable canvas. I help clarify requirements and usage feedback; AI contributes substantial implementation. The completed scope is the bounded Web V1 baseline.

## Awaiting Validation · 等待验证

**[BeatGarden](https://github.com/SamZebrado/BeatGarden)** — `Awaiting Human Playtest`<br>
Rhythm games, local-audio AutoChart and a Running survivor PWA / 节奏、本地音频与生存玩法。The next meaningful gate is human gameplay feedback; automated tests do not establish audio, touch or gameplay acceptance. [Web · No install / 网页免安装试玩](https://samzebrado.github.io/BeatGarden/).

## Developer Tools · 开发者工具

- **[MCP Agent Task Bus](https://github.com/SamZebrado/mcp-agent-bus)** — `Stable Tool` · Provider- and host-neutral persistent local MCP coordination. Native Codex capabilities suffice for Codex-only orchestration; real cross-host deployments remain unverified.
- **[Codex Session Workdir Migrator](https://github.com/SamZebrado/codex-session-workdir-migrator)** — `Stable · Compatibility-dependent` · Local planning, backup and migration utility. Compatibility depends on Codex state structures.

## Playground · 整活

**[狗尾巴扫古筝 / Tail and strings](https://samzebrado.github.io/SamZebrado/playground/tail-guzheng/)** — `Interactive experiment · Exploratory`<br>
四种合成模型与音色参数的互动实验。模型使用原录音拟合，公开版不附原声或滤波音。录音内拟合相似不等于真实接触可行，也不能据此鉴定视频真伪。<br>
Compare four synthesis conditions and explore their modal-amplitude and decay visualizations. In-sample similarity does not validate the physical motion or authenticate the video. [拟合与生成代码 / Source code](experiments/tail-guzheng/) · [整活目录 / Playground](https://samzebrado.github.io/SamZebrado/playground/).

## Learning & Reference · 学习与参考

**[GooseResearch](https://github.com/SamZebrado/GooseResearch)** — `Research Engineering Notes · Ongoing`<br>
科研工程与 AI 辅助开发的公开实践笔记和互动示例，聚焦可复现性、证据审查与明确的验证边界，并保留早期 MATLAB 工具。内容持续积累，只展示脱离具体项目的通用方法。<br>
Public field notes and interactive examples on research engineering and AI-assisted development, covering reproducibility, evidence review and explicit validation boundaries, alongside legacy MATLAB utilities. An ongoing, project-agnostic collection. [Demo index / 互动示例入口](https://samzebrado.github.io/GooseResearch/).

[hf-llm-agents-companion](https://github.com/SamZebrado/hf-llm-agents-companion) — bilingual Hugging Face course companion notes, growing with actual study / 随学习积累的中英伴读笔记。

AI contributes substantial implementation. My role varies by project and may include noticing problems, defining behavior and constraints, testing in use, and deciding whether results are acceptable.
