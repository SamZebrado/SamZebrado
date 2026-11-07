"""Render v5 shared responses from parameters only: never reads recorded waveform or analysis."""
from pathlib import Path
import json,numpy as np
from scipy.io import wavfile
from common import settings
cfg=settings();P=cfg.work_dir/'v5/physical';OUT=cfg.render_output or P;OUT.mkdir(parents=True,exist_ok=True);meta=json.load(open(P/'shared_metadata.json'));metrics=json.load(open(P/'metrics.json'));sr=meta['sample_rate'];N=meta['samples'];t=np.arange(0,N/sr,.01);ts=np.arange(N)/sr;modes=meta['modes'];poles=meta['poles'];mask=np.zeros(len(t),bool);maskaudio=np.zeros(N,bool);I=np.zeros((len(t),len(meta['active_intervals'])),complex)
for k,(a,b) in enumerate(meta['active_intervals']):
 ix=(t>=a)&(t<b);mask|=ix;maskaudio|=(ts>=a)&(ts<b);I[ix,k]=np.exp(-(t[ix]-a)/1.5)
audit={}
for family in ['strict','relaxed']:
 groups=json.load(open(P/f'{family}_shared_parameters.json'));pred=np.zeros((len(t),len(modes)),complex);initpred=np.zeros_like(pred)
 for group in groups:
  E=group['events'];et=np.array([e['time'] for e in E]);g=np.array(group['strengths']);theta=np.array(group['shared_response_real'])+1j*np.array(group['shared_response_imag']);initial=np.array(group['initial_state_real'])+1j*np.array(group['initial_state_imag']);ids=group['mode_ids'];u=t[:,None]-et[None,:];valid=(u>=0)&mask[:,None];A=np.stack([np.where(valid,(1-np.exp(-np.maximum(u,0)/.004))*np.exp((-1/tau+2j*np.pi*off)*np.maximum(u,0)),0) for tau,off in poles]);phase=np.exp(-2j*np.pi*et[:,None]*np.array([modes[k]['f'] for k in ids])[None,:])
  for j,k in enumerate(ids):
   B=np.einsum('qte,e->tq',A,g*phase[:,j],optimize=True);initpred[:,k]=I@initial[:,j];pred[:,k]=B@theta[:,j]+initpred[:,k]
  del A
 synth=np.zeros(N);init_audio=np.zeros(N)
 for mi,m in enumerate(modes):
  z=pred[:,mi];a=np.interp(ts,t,z.real)+1j*np.interp(ts,t,z.imag);carrier=np.exp(2j*np.pi*m['f']*ts);synth+=np.real(a*carrier)
  z=initpred[:,mi];a=np.interp(ts,t,z.real)+1j*np.interp(ts,t,z.imag);init_audio+=np.real(a*carrier)
 synth*=maskaudio;init_audio*=maskaudio
 ref=P/f'{family}_shared_raw.npy';err=float(max(abs(synth-np.load(ref)))) if ref.exists() else None
 pcm=np.int16(np.clip(synth*metrics[family]['gain'],-1,1)*32767);wavfile.write(OUT/f'{family}_shared_full.wav',sr,pcm)
 audit[family]={'roundtrip_max_absolute_error':err,'initial_ringing_component_energy_over_total_energy':float(np.sum(init_audio**2)/np.sum(synth**2)),'shared_response_real_coefficients':sum(np.array(q['shared_response_real']).size*2 for q in groups),'initial_state_real_coefficients':sum(np.array(q['initial_state_real']).size*2 for q in groups),'strength_count':sum(len(q['strengths']) for q in groups),'min_absolute_strength':min((q['strength_abs_min'] for q in groups if q['strengths']),default=0.0),'max_absolute_strength':max((q['strength_abs_max'] for q in groups if q['strengths']),default=0.0),'render_without_source_audio':True,'negative_strength_allowed':True}
 print(family,audit[family],flush=True)
json.dump(audit,open(OUT/'render_audit_v5.json','w'),indent=2)
