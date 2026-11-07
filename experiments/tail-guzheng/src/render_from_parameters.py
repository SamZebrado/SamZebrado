"""Re-render the synthetic fits using saved parameters only, without reading recorded audio."""
from pathlib import Path
import numpy as np,json
from scipy.io import wavfile
from common import settings
cfg=settings();P=cfg.work_dir/'v4';OUT=cfg.render_output or P;OUT.mkdir(parents=True,exist_ok=True)
gains=json.load(open(P/'playback_gains.json'))
p=json.load(open(P/'comparison_parameters.json'));sr=p['sample_rate'];N=p['samples'];t=np.arange(0,N/sr,.01);ts=np.arange(N)/sr
mask=np.zeros(len(t),bool);maskaudio=np.zeros(N,bool)
for a,b in p['active_intervals']:mask|=(t>=a)&(t<b);maskaudio|=(ts>=a)&(ts<b)
for family in ['strict','relaxed']:
 params=json.load(open(P/f'{family}_coefficients.json'));pred=np.zeros((len(t),len(p['modes'])),complex)
 for group in params:
  cols=[]
  for et,q,kind,tau,off in group['atoms']:
   u=t-et;pos=u>=0;a=np.zeros(len(t),complex);a[pos]=(1-np.exp(-u[pos]/.004))*np.exp((-1/tau+2j*np.pi*off)*u[pos]);a[~mask]=0;cols.append(a)
  C=np.array(group['coefficients_real'])+1j*np.array(group['coefficients_imag']);pred[:,group['mode_ids']]=np.stack(cols,axis=1)@C
 synth=np.zeros(N)
 for mi,m in enumerate(p['modes']):
  z=pred[:,mi];a=np.interp(ts,t,z.real)+1j*np.interp(ts,t,z.imag);synth+=np.real(a*np.exp(2j*np.pi*m['f']*ts))
 synth*=maskaudio;out=OUT/f'{family}_rerender.wav';wavfile.write(out,sr,synth.astype(np.float32))
 ref=P/f'{family}_raw.npy';err=float(max(abs(synth-np.load(ref)))) if ref.exists() else None
 print(family,'samples',len(synth),'max_parameter_roundtrip_difference',err,'output',out.name)

 wavfile.write(OUT/f'{family}_full.wav',sr,np.int16(np.clip(synth*gains[family],-1,1)*32767))
