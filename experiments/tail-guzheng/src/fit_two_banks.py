"""Two ordered guzheng banks; in-sample damped-mode contact fit. No raw audio mixing."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['OMP_NUM_THREADS']='2'
import numpy as np,json,time
from scipy import signal,linalg,ndimage
from scipy.io import wavfile
from pathlib import Path
from common import settings
cfg=settings();P=cfg.work_dir/'v4';P.mkdir(parents=True,exist_ok=True)
sr,xi=wavfile.read(cfg.work_dir/'input.wav'); y=xi.astype(float)/32768; N=len(y);ts=np.arange(N)/sr;dt=.01;fs=100.;t=np.arange(0,N/sr,dt)
active=cfg.active_intervals
# 21-string D-pentatonic tuning is a hypothesis, not read from video.
midi=np.array([38,40,42,45,47,50,52,54,57,59,62,64,66,69,71,74,76,78,81,83,86]); fgrid=440*2**((midi-69)/12)
base_ix=np.array([5,6,7,8,9,10]); ideal=fgrid[base_ix]
fwel,pwel=signal.welch(y,sr,nperseg=65536)
peaks=signal.find_peaks(pwel,distance=3)[0]
def peak_near(fr,width):
 idx=peaks[np.abs(fwel[peaks]-fr)<width]
 if not len(idx):return fr,0.
 k=idx[np.argmax(pwel[idx])]; z=np.log(pwel[k-1:k+2]+1e-30);delta=.5*(z[0]-z[2])/(z[0]-2*z[1]+z[2]);return (k+delta)*(fwel[1]-fwel[0]),pwel[k]
fund=np.array([peak_near(f,3)[0] for f in ideal]); print('FUND',fund,flush=True)
# Complex narrowband analysis for onset evidence only. Coefficients later fitted separately.
def band(fr,bw=9):
 z=y*np.exp(-2j*np.pi*fr*ts)*2
 z=signal.resample_poly(z,1,110) # ~200.45 Hz; antialias before lowpass
 z=signal.sosfiltfilt(signal.butter(3,bw,fs=sr/110,output='sos'),z)
 return np.interp(t,np.arange(len(z))*110/sr,z.real)+1j*np.interp(t,np.arange(len(z))*110/sr,z.imag)
base=np.array([band(f) for f in fund]); env=ndimage.gaussian_filter1d(abs(base),1.0,axis=1)
drive=np.maximum(np.gradient(env,dt,axis=1)+env/.38,0)
# Reward strongest onset with amplitude weighting, reward contact only close to a physical string.
reward=drive/(np.sqrt(np.mean(drive**2,axis=1,keepdims=True))+1e-9)
reward=np.minimum(reward,8)**2
# Dynamic programming on a connected geometric chain. Two half-string steps per string,
# four half-string steps in seam. Speed <=50 string spacings/s, and no jumps at seam.
def route(orient):
 orders=[np.arange(21) if o==1 else np.arange(20,-1,-1) for o in orient]
 notes=np.r_[orders[0],orders[1]]; coords=np.r_[np.arange(21),22+np.arange(21)].astype(float)
 states=np.arange(0,42+.001,.5);contact=np.exp(-.5*((states[:,None]-coords[None,:])/.30)**2)
 weights=np.zeros((len(coords),len(base_ix)))
 for q,k in enumerate(notes):
  if k in base_ix:weights[q,np.where(base_ix==k)[0][0]]=1
 R=contact@weights@reward
 path=np.full(len(t),np.nan); total=0
 for a,b in active:
  ids=np.where((t>=a)&(t<b))[0];cost=np.zeros(len(states));backs=np.zeros((len(ids),len(states)),np.int16)
  for it,k in enumerate(ids):
   options=np.stack([np.r_[-1e20,cost[:-1]]-.015,cost,np.r_[cost[1:],-1e20]-.015])
   ix=np.argmax(options,axis=0);cost=options[ix,np.arange(len(states))]+R[:,k];backs[it]=np.arange(len(states))+ix-1
  s=int(cost.argmax());total+=cost[s]
  for it in range(len(ids)-1,-1,-1):path[ids[it]]=states[s];s=backs[it,s]
 return total,path,notes,coords
routes=[]
for orient in [(1,1),(1,-1),(-1,1),(-1,-1)]:
 score,path,notes,coords=route(orient);routes.append((score,path,notes,coords,orient)); print('route',orient,score,flush=True)
best=max(routes,key=lambda x:x[0]);score,path,notes,coords,orient=best
# Contact events only while within 0.35 string spacings of path. A repeated contact on a dwelling
# string is allowed every 70ms, representing vertical contact/release. All modes of a string share event times.
events=[[] for _ in range(42)]
for q,(k,x) in enumerate(zip(notes,coords)):
 if k not in base_ix:continue
 j=np.where(base_ix==k)[0][0];contact=(np.abs(path-x)<=.35); valid=drive[j]*contact
 pk,_=signal.find_peaks(valid,distance=7,prominence=max(valid)*.025 if max(valid)>0 else 1)
 events[q]=list(t[pk])
 # Include start state (ringing unknown after recording cuts), flagged separately.
 for a,b in active:
  if abs(path[np.argmin(abs(t-a))]-x)<=.35:events[q].append(a)
 events[q]=sorted(set(events[q]))
print('events',sum(map(len,events)),[(q,len(e)) for q,e in enumerate(events) if e],flush=True)
# Per-note union across same pitch banks: identical frequencies unidentifiable from mono audio.
# Keep assignment to physical bank in events. Mode fitting sums their separate contact atoms.
noteevents=[]
for k in base_ix:
 pairs=sorted((te,q) for q in range(42) if notes[q]==k for te in events[q]); noteevents.append(pairs)
# Identify partial peaks near integer harmonics, allowing tuning/nonharmonic detuning. Each physical
# resonant frequency assigned to one parent string to avoid duplicate D3 harmonic/D4 fundamental.
cand=[]
for j,f in enumerate(fund):
 for h in range(1,13):
  fr,pow=peak_near(f*h,max(2,fr*.012) if False else max(2,f*h*.012))
  if fr>4000:continue
  cand.append(dict(j=j,h=h,f=fr,power=pow,basepower=peak_near(f,2)[1]))
cand=sorted(cand,key=lambda a:(a['h']==1,a['basepower']/a['h']),reverse=True);modes=[]
for m in cand:
 if all(abs(m['f']-o['f'])>2.0 for o in modes):modes.append(m)
modes.sort(key=lambda a:a['f']); print('modes',len(modes),flush=True)
# Fit complex demodulated amplitude using sums of causal exponential responses.
# A free sine/cosine coefficient is equivalent to fitted displacement & velocity initial conditions.
# Three decay scales / two close poles broaden the modal family; NOT a measured string response.
taus=[.12,.45,1.5];offsets=[-.6,0,.6]; synth=np.zeros(N); fitted=[]
fit_t=t;mask=np.zeros(len(t),bool)
for a,b in active:mask|=(t>=a)&(t<b)
for mi,m in enumerate(modes):
 pairs=noteevents[m['j']];ets=np.array([p[0] for p in pairs]);
 if len(ets)==0:continue
 z=band(m['f'],7.5)
 cols=[];spec=[]
 for et,q in pairs:
  u=fit_t-et;pos=u>=0
  for tau in taus:
   for off in offsets:
    b=np.zeros(len(t),complex);b[pos]=(1-np.exp(-u[pos]/.004))*np.exp((-1/tau+2j*np.pi*off)*u[pos]);b[~mask]=0
    cols.append(b);spec.append((et,q,tau,off))
 A=np.stack(cols,axis=1)
 # Least squares with tiny numerical ridge, in-sample only. Include shared observed initial ringing at cuts
 # via contact event at onset only; no repeated envelope reinitializations every five seconds.
 G=A.conj().T@A;rhs=A.conj().T@z; ridge=np.max(np.diag(G).real)*1e-6
 c=linalg.solve(G+ridge*np.eye(len(c:=rhs)),rhs,assume_a='her')
 pred=A@c
 for co,(et,q,tau,off) in zip(c,spec):
  if abs(co)<1e-8:continue
  start=max(0,int(np.ceil(et*sr)));end=min(N,int((et+tau*14)*sr));u=ts[start:end]-et
  synth[start:end]+=np.real(co*(1-np.exp(-u/.004))*np.exp((-1/tau+2j*np.pi*off)*u)*np.exp(2j*np.pi*m['f']*ts[start:end]))
 fitted.append({'fundamental_index':int(m['j']),'harmonic':m['h'],'frequency':m['f'],'coefficients':[[float(c.real),float(c.imag)] for c in c],'atoms':[list(s) for s in spec]})
 print('fit',mi,m['f'],'atoms',len(spec),'env_err',np.linalg.norm(pred[mask]-z[mask])/np.linalg.norm(z[mask]),flush=True)
maskaudio=np.zeros(N)
for a,b in active:maskaudio[(ts>=a)&(ts<b)]=1
synth*=maskaudio
np.save(P/'model_raw.npy',synth);wavfile.write(P/'two_bank_modal_fit.wav',sr,np.int16(np.clip(synth,-1,1)*32767))
np.savez(P/'routing.npz',t=t,path=path,notes=notes,coordinates=coords,drive=drive,envelopes=env,fundamentals=fund)
json.dump({'sample_rate':sr,'samples':N,'active_intervals':active,'tunings_midi_assumed':midi.tolist(),'orientation':orient,'route_scores':[{'orientation':r[4],'onset_route_score':r[0]} for r in routes],'path_max_speed_string_spacings_per_s':50,'seam_gap_string_units':2,'events':[{'time':te,'point_index':q,'bank': 'A' if q<21 else 'B','string_index':int(notes[q])} for q,es in enumerate(events) for te in es],'modes':fitted,'decay_times':taus,'mode_detunings':offsets},open(P/'parameters.json','w'),indent=2)
print('DONE',float(np.max(abs(synth))),flush=True)
