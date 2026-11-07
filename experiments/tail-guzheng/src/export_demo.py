"""Reusable local-only page export from fitted coefficients and four synthesized WAVs."""
import argparse
import html
import json
from pathlib import Path
import shutil
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--parameters', type=Path, required=True)
parser.add_argument('--audio', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
a = parser.parse_args()
v4 = json.loads((a.parameters / 'v4/comparison_parameters.json').read_text())
v5 = json.loads((a.parameters / 'v5/physical/shared_metadata.json').read_text())
ages = np.arange(0, 1.50001, .025)


def response(C, poles, ids, modes):
    def kernel(t):
        u = np.asarray(t)[:, None]
        return (1 - np.exp(-u / .004)) * np.exp(u * np.array([-1 / tau + 2j * np.pi * off for tau, off in poles])[None, :])
    amplitudes = abs((kernel([.04]) @ C)[0])
    energy = np.sum(abs(kernel(ages) @ C) ** 2, axis=1)
    return {'frequencies': [modes[i]['f'] for i in ids],
            'harmonics': [modes[i]['h'] for i in ids],
            'profile': (amplitudes / max(float(np.linalg.norm(amplitudes)), 1e-30)).tolist(),
            'decay': (energy / max(float(energy.max()), 1e-30)).tolist()}


conditions = {}
for version in ['v4', 'v5']:
    meta = v4 if version == 'v4' else v5
    for family in ['strict', 'relaxed']:
        path = a.parameters / (f'v4/{family}_coefficients.json' if version == 'v4' else f'v5/physical/{family}_shared_parameters.json')
        groups = json.loads(path.read_text())
        entries = []
        for g in groups:
            ids = g['mode_ids']
            events = []
            if version == 'v4':
                C = np.array(g['coefficients_real']) + 1j * np.array(g['coefficients_imag'])
                atoms = g['atoms']
                indices = {}
                for i, atom in enumerate(atoms):
                    if atom[2] == 'contact':
                        indices.setdefault(tuple(atom[:3]), []).append(i)
                for (time, point, _), ix in sorted(indices.items()):
                    events.append({'time': time, 'strength': None, **response(C[ix], [atoms[i][3:5] for i in ix], ids, meta['modes'])})
            else:
                C = np.array(g['shared_response_real']) + 1j * np.array(g['shared_response_imag'])
                shared = response(C, meta['poles'], ids, meta['modes'])
                for event, strength in zip(g['events'], g['strengths']):
                    events.append({'time': event['time'], 'strength': strength, **shared})
            entries.append({'string_index': 5 + g.get('fundamental_index', g.get('note_index')),
                        'harmonics': [meta['modes'][i]['h'] for i in ids],
                        'frequencies': [meta['modes'][i]['f'] for i in ids], 'events': events})
        conditions[f'{version}_{family}'] = entries
assets = a.out / 'assets'
assets.mkdir(parents=True, exist_ok=True)
for name in ['strict_full.wav', 'relaxed_full.wav', 'strict_shared_full.wav', 'relaxed_shared_full.wav']:
    shutil.copyfile(a.audio / name, assets / name)
# Only parameter-derived event responses are embedded. No original spectra or envelopes.
data = json.dumps(conditions, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>尾巴古筝 · 可复现合成模型</title>
<style>body{max-width:1000px;margin:40px auto;padding:0 20px;background:#142921;color:#e8f0e8;font:16px/1.7 system-ui}h1,h2{line-height:1.25}section{background:#213a30;padding:24px;border-radius:16px;margin:20px 0}audio{width:100%}select,button{padding:9px;margin:5px;border-radius:7px}canvas{width:100%;height:210px;background:#10241b}small{color:#b5cbbd}footer{margin:40px 0}</style>
<h1>尾巴拨弦：声音拟合实验</h1><p>四条声音均由参数重合成，不混入原音。参数来自同一输入录音的拟合，不是独立物理验证，也不能用声音相似度鉴定视频真假。</p>
<section><h2>选择模型与候选弦</h2><select id="condition"><option value="v4_strict">v4 严格逐弦 / 逐事件自由音色</option><option value="v4_relaxed">v4 允许空过 / 逐事件自由音色</option><option value="v5_strict">v5 严格逐弦 / 每弦共享音色</option><option value="v5_relaxed">v5 允许空过 / 每弦共享音色</option></select><select id="string"></select><audio id="player" controls preload="metadata"></audio><p><button id="previous">上一触发</button><button id="next">下一触发</button><span id="info"></span></p><p><label for="harmonic-page">名义谐波分页：</label><select id="harmonic-page" aria-label="选择六个固定名义谐波槽位"></select></p><canvas id="profile" width="900" height="210" aria-label="触发后40毫秒归一化模态幅度，每页六个固定谐波槽位"></canvas><small>触发后 40ms 的归一化模态幅度。每页固定六个名义谐波槽位：h1–6、h7–12，更多模式继续分页；没有拟合模态的槽位置零。下方 Hz 是实际拟合中心，不强行设为 h 倍基频，也不是瞬时音高。归一化始终包含全部模式，不随分页变化；v5 同一弦各触发的归一化比例完全相同。</small><canvas id="decay" width="900" height="210" aria-label="触发后0到1.5秒归一化模态能量"></canvas><small>0–1.5 秒模态幅度平方和，按峰值归一。含起音与分量干涉，不是校准的物理能量，也不是原声分离谱。初始余振参与声音，但不显示成尾巴触发。</small></section>
<section><h2>做法与边界</h2><p><strong>严格逐弦是人为设置的强约束对照，不是真实必然规则。</strong>尾巴可能擦过、滑过或弹开，并不一定使经过的弦发声。</p><p><strong>当前公开 v4/v5 允许路径中途停顿和折返。</strong>它们不满足后来提出的“仅到端点再折返、途中不停不折返且可跳弦”新模型；新模型另行开展，不能把这里的试听当作该要求已实现。</p><ol><li>将有权使用的 WAV 转为单声道 22050 Hz，保留时间轴。窄带分析得到起音证据及模态拟合目标。</li><li>在假设的两组有序弦列上搜索路线。v4 各事件自由拟合模态幅相；v5 每弦共享响应，每次仅用一个共同实数强度。</li><li>保存系数、事件及试听增益，脱离原音重渲染四条音轨，再导出此页面。</li></ol><p>21+21 弦、D 调五声调弦、均匀间距及 6 弦距空隙都是假设。v5 的速度和加速度约束只作用于 20ms 离散路线，不等于连续加速度或真实三维运动已验证。拟合误差不是留出集预测误差；两版也不只改变了音色一项。</p><p>原案例 v4 严格/放宽有 70,380 / 111,384 个实数声学系数，v5 为 1,886 / 1,883（共享响应810、初始余振450、强度626/623）；事件时间、路线和固定频率另计。新输入的计数会变化。</p></section><footer>只包含合成音与参数派生展示。新输入适用范围见代码 README。</footer>
<script>const DATA=__DATA__;
const C=document.querySelector('#condition'),S=document.querySelector('#string'),A=document.querySelector('#player'),H=document.querySelector('#harmonic-page');
let index=0;
const names={v4_strict:'strict_full.wav',v4_relaxed:'relaxed_full.wav',v5_strict:'strict_shared_full.wav',v5_relaxed:'relaxed_shared_full.wav'};
const maxH=Math.max(1,...Object.values(DATA).flatMap(groups=>groups.flatMap(g=>g.harmonics)));
H.innerHTML=Array.from({length:Math.ceil(maxH/6)},(_,p)=>`<option value="${p}">第 ${p+1} 页 · h${p*6+1}–h${p*6+6}</option>`).join('');
function currentString(){return DATA[C.value][+S.value]}
function events(){return currentString()?.events||[]}
function profileSlots(e){
 const group=currentString(),start=+H.value*6+1;
 return Array.from({length:6},(_,i)=>{
  const harmonic=start+i,ids=(group?.harmonics||[]).flatMap((h,k)=>h===harmonic?[k]:[]);
  return {harmonic,missing:ids.length===0,amplitude:Math.sqrt(ids.reduce((sum,k)=>sum+(e?.profile[k]||0)**2,0)),frequencies:ids.map(k=>group.frequencies[k])};
 });
}
function draw(){
 const es=events();index=Math.max(0,Math.min(index,es.length-1));const e=es[index];
 document.querySelector('#info').textContent=e?`${index+1}/${es.length} · ${e.time.toFixed(3)}s · ${e.strength===null?'自由模态系数':'共同强度 '+e.strength.toFixed(3)}`:'此弦无接触事件';
 const canvas=document.querySelector('#profile'),ctx=canvas.getContext('2d'),slots=profileSlots(e);
 canvas.dataset.slotCount=String(slots.length);canvas.dataset.harmonics=slots.map(s=>s.harmonic).join(',');
 canvas.dataset.missingHarmonics=slots.filter(s=>s.missing).map(s=>s.harmonic).join(',');
 ctx.clearRect(0,0,900,210);ctx.font='13px system-ui';ctx.textAlign='center';
 slots.forEach((slot,i)=>{
  const center=25+(i+.5)*850/6,height=slot.amplitude*135;
  ctx.strokeStyle='#638171';ctx.beginPath();ctx.moveTo(center-48,155);ctx.lineTo(center+48,155);ctx.stroke();
  ctx.fillStyle=slot.missing?'#93aa9c':'#c4e59a';ctx.fillRect(center-40,155-height,80,height);
  if(slot.amplitude===0)ctx.fillText('0',center,146);
  ctx.fillText('h'+slot.harmonic,center,176);
  ctx.fillText(slot.missing?'无拟合模态':slot.frequencies.map(f=>f.toFixed(1)+' Hz').join(' / '),center,197);
 });
 const decay=document.querySelector('#decay').getContext('2d');decay.clearRect(0,0,900,210);if(!e)return;
 decay.fillStyle='#c4e59a';decay.strokeStyle='#c4e59a';decay.beginPath();
 e.decay.forEach((v,i)=>{const x=25+i*850/(e.decay.length-1),y=170-v*140;i?decay.lineTo(x,y):decay.moveTo(x,y)});
 decay.stroke();decay.fillText('0 s',25,195);decay.fillText('1.5 s',850,195);
}
function choose(){A.pause();A.src='assets/'+names[C.value];S.innerHTML=DATA[C.value].map((s,i)=>`<option value="${i}">候选弦 ${s.string_index}</option>`).join('');index=0;draw()}
C.onchange=choose;S.onchange=()=>{index=0;draw()};H.onchange=draw;
for(const [id,d] of [['previous',-1],['next',1]])document.querySelector('#'+id).onclick=()=>{index+=d;draw();const e=events()[index];if(e)A.currentTime=e.time};
A.ontimeupdate=()=>{const es=events();if(es.length){let k=0;while(k+1<es.length&&es[k+1].time<=A.currentTime)k++;index=k;draw()}};
choose();</script></html>'''
(a.out / 'index.html').write_text(page.replace('__DATA__', data))
print('Exported standalone synthesized-audio page:', a.out / 'index.html')
