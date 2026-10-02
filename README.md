# Selected Projects / 精选项目

软件、交互产品与 Agent 工具。<br>
Software, interactive products, and agent tooling.

**[Portfolio / 项目主页](https://samzebrado.github.io/SamZebrado/)**

## Products & Interactive Systems / 产品与交互系统

### [GrapePaper](https://github.com/SamZebrado/GrapePaper)

正在开发的 PDF 中文伴读工具，保留英文原文，支持手动阅读确认与实验版 Zotero 选段桥接。引用证据链支持手动核对来源与定位本地短摘录，并将模型解释与原文分开；实时 AI 需自配服务，真实模型推理尚未验证。<br>
An actively developing PDF reading companion with original text, explicit reading confirmation, and an experimental Zotero excerpt bridge. Its citation trail supports manual source checks and exact local excerpts, keeping model interpretation separate. Live AI requires a configured service; real model inference remains unverified.

`React` · `TypeScript` · `PDF.js` · `excerpt provenance`

[Repository](https://github.com/SamZebrado/GrapePaper) · [Read / 阅读](https://samzebrado.github.io/GrapePaper/)

### [CheapLive](https://github.com/SamZebrado/CheapLive)

一个已基本完成、进入维护阶段的低成本虚拟形象面捕项目，提供浏览器端 MediaPipe 面捕、程序化 Avatar 与 Android Capture 客户端。维护候选的 Android 构建已在本地验证；真实设备表现仍待验证。<br>
An essentially completed face-capture project in maintenance, with browser MediaPipe tracking, procedural avatars, and an Android Capture client. The Android maintenance candidate builds locally; real-device behavior remains unverified.

`MediaPipe` · `browser + Android` · `local processing` · `procedural avatars`

[Repository](https://github.com/SamZebrado/CheapLive) · [Try face capture](https://samzebrado.github.io/CheapLive/src/face-tracking/)

### [BeatGarden](https://github.com/SamZebrado/BeatGarden)

一个包含程序化节奏玩法、本地音频 AutoChart 与 Running survivor 模式的 PWA。实现暂停，等待人工试玩；自动测试不代表音频、触控与游戏体验已获验收。<br>
A PWA with procedural rhythm play, local-audio AutoChart, and a Running survivor mode. Implementation is paused for human playtesting; automated tests do not establish audio, touch, or gameplay acceptance.

`TypeScript` · `PWA` · `Web Audio` · `offline lifecycle` · `deterministic state`

[Repository](https://github.com/SamZebrado/BeatGarden) · [Play](https://samzebrado.github.io/BeatGarden/)

### [DeeSewSew](https://github.com/SamZebrado/DeeSewSew)

V1 已完成并冻结功能、接受公开试玩的浏览器刺绣工作室，支持正反面针线拓扑、本机保存和 JSON／PNG 导出。独立 3D Lab 仍属实验展示；不声称完整材料物理模拟。<br>
A completed, feature-frozen V1 browser embroidery studio open to public playtesting, with front/back thread topology, local saving, and JSON/PNG export. The separate 3D Lab remains experimental and does not model full material physics.

`TypeScript` · `Canvas` · `front/back topology` · `local-first`

[Repository](https://github.com/SamZebrado/DeeSewSew) · [Playtest / 试玩](https://samzebrado.github.io/DeeSewSew/)

### [guiLaTeX](https://github.com/SamZebrado/guiLaTeX)

一个功能已完成并冻结、接受公开试玩与缺陷反馈的 Web-first 可视化编辑器，面向受限单页 LaTeX 格式，支持文字、图片、部分公式排版与项目导入导出。在线链接为静态展示，编辑器在本地服务中运行。<br>
A completed, feature-frozen Web-first visual editor open to public playtesting and bug reports. It supports text, images, a bounded equation subset, and import/export within a single-page LaTeX format. The online link is a static showcase; the editor runs on a local server.

`Web-first` · `visual layout` · `bounded LaTeX format` · `local loopback server` · `import/export`

[Repository](https://github.com/SamZebrado/guiLaTeX) · [Showcase / 项目展示](https://samzebrado.github.io/guiLaTeX/showcase/)

### [Transparent Floating Browser](https://github.com/SamZebrado/TransparentFloatingBrowser)

一个核心功能已完成、仅做缺陷维护的 Kotlin Android 悬浮浏览器，支持多窗口透明 WebView、编辑／展示模式，以及 Android 12+ 触摸穿透限制的处理。真实设备验收仍待完成。<br>
A completed Kotlin Android floating browser in bug-fix maintenance, with multi-window transparent WebViews, edit/display modes, and handling of Android 12+ touch-through restrictions. Real-device acceptance remains open.

`Kotlin` · `Android overlays` · `WebView` · `system constraints`

[Repository](https://github.com/SamZebrado/TransparentFloatingBrowser)

### [IslandSlowlyFall / 慢慢倒](https://github.com/SamZebrado/IslandSlonelyFall)

一个本地优先的日常记录与低能量决策工具，用结构化反思、微习惯和优先级工具帮助用户觉察状态，并找到当下能做的一小步。<br>
A local-first daily reflection and low-energy decision-making tool that uses structured reflection, micro-habits, and prioritization to help users notice their state and find a manageable next step.

`human-centered product design` · `local-first privacy` · `structured reflection` · `vanilla web app`

[Repository](https://github.com/SamZebrado/IslandSlonelyFall) · [Try it](https://samzebrado.github.io/IslandSlonelyFall/)

## Agent & Developer Tools / Agent 与开发者工具

### [MCP Agent Task Bus](https://github.com/SamZebrado/mcp-agent-bus)

一个稳定、不绑定提供商或宿主的本地 MCP 任务总线，以 SQLite 保存权威任务状态与事件，为独立 MCP 会话提供持久化交接。仅在 Codex 内编排时，原生能力已足够；真实跨宿主部署仍待验证。<br>
A stable, provider- and host-neutral local MCP task bus with SQLite-authoritative tasks and events for persistent handoffs between independent MCP sessions. Native Codex capabilities suffice for Codex-only orchestration; real deployments across hosts remain unverified.

`MCP` · `SQLite` · `task lifecycle` · `leases` · `explicit acceptance`

[Repository](https://github.com/SamZebrado/mcp-agent-bus)

### [Codex Session Workdir Migrator](https://github.com/SamZebrado/codex-session-workdir-migrator)

一个非官方、本地运行的工具，用于规划、备份、验证和跨目录或跨设备迁移 Codex session state，并默认采用 dry-run 和保守的结构化状态修改。它依赖特定 Codex 状态结构，不保证兼容所有版本。<br>
An unofficial, local utility for planning, backing up, verifying, and migrating Codex session state across directories or machines, with dry-run safety and conservative structured-state edits by default. Compatibility depends on the Codex state schema and is not guaranteed across versions.

`dry-run safety` · `structured-state migration` · `backups` · `verification` · `portable bundles`

[Repository](https://github.com/SamZebrado/codex-session-workdir-migrator)

## Learning Notes / 学习笔记

[hf-llm-agents-companion](https://github.com/SamZebrado/hf-llm-agents-companion)：Hugging Face LLM／Agents 课程的中英伴读笔记，随实际学习积累，并回链课程来源。<br>
Bilingual companion notes for Hugging Face LLM/Agents courses, growing with actual study and linking back to course sources.

---

部分项目采用 AI-assisted development workflow；需求定义、review、QA 和最终发布验收由人负责。<br>
Some projects use AI-assisted development workflows with human-owned specification, review, QA, and release acceptance.
