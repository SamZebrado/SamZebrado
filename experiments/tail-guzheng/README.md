# 尾巴古筝：可复用的拟合、重合成与展示代码

版本入口：[双琴端点往返 v7 的参数与代码](v7-two-bank/)。本目录原流程仍为 v4/v5 旧路径对照，不会自动变为 v7；下文后续约束的描述保留旧版语境。

这是同一段录音约束下的逆向声音拟合实验。所有试听由保存的模型参数生成，没有叠加或拼接原波形。**拟合参数来自原录音；“参数独立渲染”不等于“独立于原录音的物理验证”**，也不能凭相似度判断视频真假。

此目录提供两种可复现路径：

1. **无需原音**：用已保存的派生系数，重渲染作品集中的四条完整合成 WAV，并生成一个自包含演示页。
2. **重新拟合**：自行提供有权使用的 WAV，完成预处理 → v4 分析/路线/拟合 → v5 两路线/共享音色拟合 → 指标/试听增益 → 参数渲染 → 演示页。

原录音、原视频、原声处理音、不受接触约束的近直接重构、源音时频包络及分析数组均不随代码分发。代码会在本地产生这些研究中间量，但页面导出仅允许四条合成音及参数派生的展示信息。请不要把整个工作输出目录直接上传。

## 安装与一条命令重现试听

在本目录运行，建议 Python 3.12。已验证 Python 3.12.14、NumPy 2.3.5、SciPy 1.17.0，运行时将 BLAS/OMP 线程设为 2。没有 ffmpeg、GPU、Matplotlib、前端打包器或在线服务依赖。

```bash
python -m venv .venv
# macOS / Linux
. .venv/bin/activate
# Windows PowerShell 使用 .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python pipeline.py render --out outputs/reference
```

输出：

- `outputs/reference/audio/strict_full.wav`：v4 严格逐弦。
- `outputs/reference/audio/relaxed_full.wav`：v4 允许空过/补触发。
- `outputs/reference/audio/strict_shared_full.wav`：v5 严格逐弦、共享每弦音色。
- `outputs/reference/audio/relaxed_shared_full.wav`：v5 允许空过/补触发、共享每弦音色。
- `outputs/reference/audio/sha256_check.json`：与已交付四条 WAV 的校验。
- `outputs/reference/site/index.html` 和 `assets/`：仅合成音的本地演示。

直接打开 HTML 即可使用；也可 `python -m http.server 8000 --directory outputs/reference/site` 后在浏览器打开本机 8000 端口。服务器仅供本地测试，请按实际网络环境限制访问。

四条参考音频都是单声道 PCM16、22050 Hz、1,050,127 样本，约 47.624807 秒。已在上述数值环境中确认 SHA256 与交付试听完全一致。不同 BLAS/CPU/依赖版本可能在极小浮点舍入后产生 PCM 边界差别，因此校验失败会显式报错，而不会宣称逐字节复现。

## 用自己的授权音频重新拟合

```bash
python pipeline.py fit --input input/authorized.wav --out outputs/my_fit
```

`input/authorized.wav` 是用户自行提供的文件，不在仓库中。默认把完整输入时段视为有声区间。若录音有明显静音/重新开始，可以给 JSON 数组，例如 `[[0.2,3.4],[4.0,6.8]]`：

```bash
python pipeline.py fit --input input/authorized.wav --intervals input/intervals.json --out outputs/my_fit
```

输出目录必须是新目录，避免覆盖已有输入和分析。预处理接受 WAV 的整型或浮点采样，声道算术平均，必要时用多相滤波重采样到 22050 Hz，量化成 PCM16；不裁时间、不去噪、不做声源分离。音量越界会限幅并在 `config.json` 记录数量。静音输入会拒绝。活动区间必须排序、不重叠且位于音频内；每段至少 40 ms，整个输入至少 0.5 秒。

历史案例使用的直接输入已经是 22050 Hz 单声道 PCM16 WAV。本代码不包含从原视频取得该输入的流程或素材。若自行持有获授权且逐样本相同的输入，历史有效段见 `parameters/reference_intervals.json`：

```bash
python pipeline.py fit --input input/authorized_reference.wav --intervals parameters/reference_intervals.json --out outputs/reference_refit
```

### 适用范围，不是任意旋律的一键转录器

可复用的是输入、执行顺序、输出和页面管线；声学/几何假设仍针对本实验。默认 D 调五声音阶 21 弦，拟合六个候选音 D3/E3/F♯3/A3/B3/D4，MIDI 50/52/54/57/59/62，约 146.83–293.66 Hz。模式中心在这些基音及其附近泛音上搜索，最高 4000 Hz。另有同调 21 弦琴，构成两个有序点列。

**不支持自动任意转调、任意弦数、任意音域或真实三维尾巴追踪。** 单纯更换输入不会使模型自动适配这些情况。音频不含这些音、时长极短、接触证据弱或大量其他声源时，程序仍可能给出差的候选拟合；它不是来源识别。更改模型假设需同步修改路线及拟合部分并重新验证。小样测试只证明这条管线可执行，不是广泛输入适用性的验证。

### 实际执行顺序及文件依赖

`pipeline.py fit` 按以下顺序运行，子脚本均支持 `--work-dir outputs/my_fit`：

1. `src/preprocess.py` 生成私有工作区中的 `input.wav`、`config.json`。
2. `src/fit_comparison.py` 复用 `fit_two_banks.py` 的分析/初始路径前半段，再采用 6 弦距琴间空隙与反射等价代表，输出 v4 严格/放宽系数、分析及路线。该源码复用方式沿袭原实验，不是另行假定的处理顺序。
3. `src/smooth_route.py` 搜索允许经过未建模弦的有限速度/离散加速度路线；`src/strict_smooth_route.py` 对跨越未建模弦加入极大惩罚。
4. `src/merge_routes.py` 将严格路线的接触与放宽路线中六个建模音的接触组合，保存独立的两条路线；放宽路线经过其他弦时视为不接触，不把它们伪装成已发声。
5. `src/fit_physical.py` 用 v4 的同源模态分析目标和合并事件，交替拟合固定每弦响应、逐接触共同实数强度及各有声段的初始余振。
6. `src/evaluate.py` 对各候选声音拟合一个全局有符号标量增益，计算同样本波形 NRMSE/相关/SNR。`render_from_parameters.py` 和 `render_shared.py` 从系数生成四条试听，再由 `export_demo.py` 导出页面。

`fit_shared.py` 是保持 v4 原路径、只改为共享音色的控制对照，可加 `--with-control` 运行；不替代最终 v5 两条路线。`fit_two_banks.py` 的完整单独执行是较早中间模型（默认 2 弦距空隙），不是四条最终试听的独立生成入口。

局部单独执行例子：

```bash
python src/strict_smooth_route.py --work-dir outputs/my_fit
python src/render_shared.py --work-dir parameters --render-output outputs/shared_only
python src/export_demo.py --parameters parameters --audio outputs/reference/audio --out outputs/another_site
```

## 展示导出的功能范围

生成页提供四模型切换、六弦选择、音频播放、前/后候选触发跳转、触发后 40 ms 模态比例和 0–1.5 s 归一化衰减曲线。它直接从系数计算，不读取原音或原分析数组。v4 可看到同弦逐事件音色变化，v5 同弦每次归一化曲线固定。柱图按名义谐波序号固定每页六列（h1–6、h7–12，若最大序号更高继续分页），不随当前弦的模式数重排。缺失槽位为 0，并标“无拟合模态”；所有拟合模式保留，归一化基于全部模式而非当前页。Hz 标签始终来自实际拟合模态中心，不强制取 h 倍基频。

这是便于复用的**最小展示页**，不是作品集正式页面的逐字节副本：不包含原正式页全部排版、连续时变合成幅度视图或两琴路线动画。该导出不依赖原正式网页的路径、私有素材或既有构建目录。

## 模型自由度与解释边界

**严格逐弦是人为设置的强约束对照，不是真实尾巴运动必然遵守的规则。** 真实尾巴可能擦过、滑过或弹开，并不一定使经过的弦发声。

**当前公开的 v4/v5 允许路径中途停顿和折返。** 它们不满足后来提出的“仅到端点再折返、途中不停不折返且可跳弦”新模型。新模型另行开展，本目录及其试听不能冒充该要求已实现；“严格”和“放宽”只指这里已经实现的操作定义。

- v4 严格/放宽分别有 **70,380 / 111,384** 个实数声学系数。每次接触、每个模态可以独立改变幅相，拟合很好并不意味着机制可信。
- v5 的同弦响应共享，仅每次触发一个共同实数强度：810 个实数响应系数 + 450 个初始状态系数 + 626/623 个强度 = **1,886 / 1,883**。频率、路线及事件时间另计，不是完整统计自由度。正负强度自由，不要求符号与扫弦方向一致，也没有力的物理单位。
- 上述数字对应已交付案例。新输入的接触、模态及区间数会改变计数。原案例 v4 波形 NRMSE 为 0.304195/0.296452，v5 为 0.555485/0.532601，均用全部同源样本拟合与评价，无留出验证。v4 与 v5 同时改变了路线与音色约束，差异不能全部归因于音色。
- 两组各 21 弦、D 调、均匀间距、琴间 6 弦距及朝向均是模型假设。原案例四个朝向等分，展示 A 琴活动的反射等价代表，没有识别来源琴；两条最终路线没有实际跨琴，不能声称验证了跨琴可达性。
- v5 的速度 ≤50 弦距/秒、相邻 **20 ms 离散积分步**速度变化对应 ≤750 弦距/秒²。离散差分约束并不证明线性分段轨迹在节点处连续可微，也不是连续真实加速度的测量。尾巴长度、三维位置、关节约束、力和接触高度均未知。
- 原算法的严格路线对未建模弦用极大惩罚，而非形式化不可行状态；应检查输出是否满足预期，不将名称“严格/physical”当成物理可行性证明。
- 初始余振独立于尾巴接触，不能把初始状态拟合当成额外触发；v5 初始余振在各录音时段内按 1.5 s 衰减。
- 路线与声学参数分阶段搜索；不保证全局最优。参数来源拟合、同样本评价、信号表示和正向物理验证是不同问题。

## 测试

```bash
python tests/smoke.py
```

测试自行合成 4 秒、44100 Hz 双声道 float WAV，12 次六音扫描、每次三个阻尼谐波。实际跑通预处理、v4、两条 v5 路线、合并、最终共享拟合、增益、四 WAV、页面；再把参数单独复制到没有原音/分析的目录重渲染，四 WAV 必须逐字节相同。测试临时目录结束后自动清理，不读取或公开原录音。

本次已完成：Python 语法编译、上述端到端小样、四条历史试听 SHA256 精确复现、HTML/资源生成及 JavaScript 语法检查。详细记录见 `VALIDATION.md`。未重跑历史 47.6 秒完整原音拟合；可选 v4 路线共享控制对照未在这次小样中执行。最小展示页随后已在实际 Chrome 中验收：四模型 × 六弦 × 两页共 48 组合均固定六槽，桌面宽度 1180 px 无横向溢出；前后触发跳转、空格播放/暂停、时间推进及页面错误检查通过。未测试实体手机或拖动音频滑杆，不将这部分视为已验收。

## 改动、数据与许可

原 v4/v5 数值内核、搜索和交替拟合顺序保留。本公开版本新增相对目录 CLI、WAV 预处理、路线合并、统一评估、参数渲染编排和最小展示；只为原来会失败的零接触弦添加“仅初始状态”处理，并将初始状态事件计数改为随输入区间数计算。没有宣称对全部研究假设进行了独立验证。

`parameters/` 只保存已拟合事件、有限维声学系数、模式/模型元数据、播放增益和合成音哈希。没有原波形、源音 STFT、原分析复包络或近直接重构数组；但高维 v4 系数仍可编码这段录音的很多细节，应理解其来源相关性。

本快照**没有追加 MIT 或其他新的项目许可，也不通过 README 额外授权**；代码/素材的再使用权以权利人的实际授权为准。NumPy 与 SciPy 的已安装发行包许可证均为 BSD 三条款形式，归各项目权利人，具体完整条款和发行包中的第三方组件声明以其随附许可证为准。本目录只列依赖，不复制或重授权其源代码。

也可直接从参考元数据导出相同活动区间，而不手抄时间：

```bash
python -c "import json; from pathlib import Path; p=json.loads(Path('parameters/v4/comparison_parameters.json').read_text()); Path('reference_intervals.json').write_text(json.dumps(p['active_intervals']))"
python pipeline.py fit --input input/authorized_reference.wav --intervals reference_intervals.json --out outputs/reference_refit
```

完整重新优化不保证在不同机器逐位相同；本次逐字节核对的对象是**已保存参数重渲染出的四条试听**，不是完整原音重新优化。
