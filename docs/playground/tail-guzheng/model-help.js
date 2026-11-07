/* Clickable, keyboard-accessible explanations; no overlay and no audio dependencies. */
(()=>{
 const section=document.getElementById('new-fit');if(!section)return;
 const terms={
  strict:['严格逐弦：强约束对照','这是人为加入的较强对照假设，不是尾巴运动必须服从的定律。允许往返，但跨过中间已建模弦时必须触发。真实尾巴可能擦过、滑过或弹开，接触力和弦位移不足时未必有效发声；因此严格组拟合失败不能判假。'],
  relaxed:['允许跳弦：较宽松假设','允许经过弦却不有效触发，例如抬起、擦过或弹开，也允许路径附近的额外触发。更贴近这种可能性，但拟合更好不自动代表真实。v4在同一路径上扩展候选事件并放松最低触发量；v5另外搜索允许空过的离散路径。它仍有候选位置、弦序与路径约束，不是随意拼接录音。'],
  timbre:['逐次自由音色 / 每弦共享音色','v4让同一弦每次触发都可换一套模态比例、相位和衰减混合，容易更贴近原音。v5让同一弦共用一种响应，每次只改变一个共同的有符号强度。v4与v5的路径也不同，不能把拟合差异全归于音色。'],
  phase:['相位','同一个频率的波，可以从波峰、波谷或中间位置开始，这个相对位置就是相位。多个波叠加时会互相加强或抵消。改变相位可以显著改变逐样本误差，但不等于改变了拨弦节奏。'],
  mode:['模态','这里把声音写成若干振动成分的叠加，每个成分有中心频率、幅度、相位和衰减。这些是拟合模型中的成分；没有验证它们一一对应真实古筝的独立振动方式。'],
  harmonic:['基频与泛音','基频通常决定主要音高，泛音是更高的频率成分。理想弦常接近整数倍，因此图中用“≈几倍”归类；Hz显示实际拟合中心，并非强制精确整数倍。“无拟合 / 0”只是该弦模型没有该槽位，不代表原音中没有这种成分。'],
  decay:['衰减与余振','触弦后声音会逐渐消退，但不同成分互相干涉，可使曲线短暂起伏。图中曲线按每次触发的峰值归一，比较形状而不是绝对音量。当前柱高还包含该弦先前触发留下的余振；它不是从原录音分离出的单弦频谱。'],
  error:['拟合误差与相关','NRMSE是逐样本差异的相对大小，越小越贴近，0表示完全一致；比较前为每条音轨求了一个最优有符号总增益。相关越接近1表示波形越相似。它们不是听感分数、真假概率，也不是留出样本的预测成绩。'],
  unconstrained:['不受接触约束的参考','这条参考不要求“尾巴什么时候碰哪根弦”，而是直接使用从原音估计的时变窄带包络重合成。它仍受这组模态字典限制，并非所有东西都无限自由。它用于看信号重构能多接近，不属于可行尾巴扫弦；公开演示不提供这条参考音。'],
  path:['两琴与路径假设','图上的触点由声音拟合和假设几何得到，不是视频实测。21+21根弦、D调五声音阶、均匀间隔与空隙都是假设。两琴只能经相向边缘接续，也不强制碰第二琴。本轮路径只使用一琴；v5只约束20ms步间速度变化，不证明真实连续三维运动可行。'],
  overfit:['这次为什么刻意过拟合','目标是尽量解释这一段录音，探索这些假设与自由度可以拟合到什么程度，所以整段都参与调参。自由度更多通常更容易拟合得像，但这既不是找到了全局最优解，也不能单凭相似度判断视频真假。']
 };
 const box=document.createElement('aside');box.className='model-explainer';box.setAttribute('aria-label','模型比较与术语说明');
 box.innerHTML='<h3>先分清：两种触弦规则 × 两种音色模型</h3><div class="rule-summary"><p><strong>严格逐弦：强约束对照</strong><br>可以往返，但模型要求经过中间弦时必须触发。</p><p><strong>允许跳弦：较宽松假设</strong><br>可空过、擦过不响或额外触发，仍受候选路径约束。</p></div><p class="model-key">每组都能选 v4「每次声音可变」或 v5「同一弦共用音色」。两者都按原录音调参后合成。尾巴掠过或弹开未必有效触响，不能凭严格组失败判假，也不能凭放宽组拟合得好判真。</p><p class="model-key"><strong>当前是旧条件对照：</strong>v4/v5允许中途停顿或折返，尚未施加“每半周期端到端、途中不停不折返”的新约束；新拟合将另行更新。</p><div class="term-list" aria-label="点问号查看术语"></div><div class="concept-detail" id="model-term-detail" role="region" aria-live="polite"><button type="button" class="term-close" aria-label="关闭术语说明">×</button><strong class="term-heading">读图提示</strong><p class="term-description">点术语旁的问号查看解释。说明在这里展开，不覆盖图表；手机可点，键盘可用 Tab 和 Enter，按 Esc 关闭。</p></div>';
 section.querySelector('.grid').before(box);
 const detail=box.querySelector('.concept-detail'),heading=box.querySelector('.term-heading'),description=box.querySelector('.term-description');let active=null;
 function reset(){active=null;heading.textContent='读图提示';description.textContent='点术语旁的问号查看解释。说明在这里展开，不覆盖图表；手机可点，键盘可用 Tab 和 Enter，按 Esc 关闭。';document.querySelectorAll('[data-model-term]').forEach(b=>b.setAttribute('aria-expanded','false'));detail.dataset.term='';}
 function show(key){if(active===key){reset();return}active=key;heading.textContent=terms[key][0];description.textContent=terms[key][1];detail.dataset.term=key;document.querySelectorAll('[data-model-term]').forEach(b=>b.setAttribute('aria-expanded',String(b.dataset.modelTerm===key)));}
 function button(key){const b=document.createElement('button');b.type='button';b.className='term-question';b.textContent='?';b.dataset.modelTerm=key;b.setAttribute('aria-label','解释'+terms[key][0]);b.setAttribute('aria-expanded','false');b.setAttribute('aria-controls','model-term-detail');b.onclick=()=>{show(key);detail.scrollIntoView({behavior:'smooth',block:'nearest'});detail.focus({preventScroll:true})};return b}
 detail.tabIndex=-1;
 for(const key of Object.keys(terms)){const item=document.createElement('span');item.className='term-item';item.append(document.createTextNode(terms[key][0]),button(key));box.querySelector('.term-list').append(item)}
 section.querySelectorAll('.grid>div>h3').forEach((h,i)=>{h.firstChild.textContent=i===0?'严格逐弦 · 对照假设':'允许跳弦 · 宽松假设';h.append(button(i===0?'strict':'relaxed'))});
 box.querySelector('.term-close').onclick=reset;
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&active)reset()});
 const reference=section.querySelector('audio[src*="unconstrained"]');if(reference){const p=document.createElement('p');p.className='reference-explainer';p.textContent='这里是信号重构参考，不是第三种可行扫弦模型。它直接用原音估计的时变包络，去掉了接触事件与路径要求。';p.append(button('unconstrained'));reference.before(p)}
})();
