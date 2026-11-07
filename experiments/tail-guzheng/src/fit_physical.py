"""Shared-per-string causal impulse responses. One real strength per contact, no per-contact timbre.
This is an audio-constrained inverse fit, not a measured dog's motion or authenticity result.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['OMP_NUM_THREADS']='2'
import numpy as np,json,time
from pathlib import Path
from scipy import linalg
from scipy.io import wavfile
from common import settings
cfg=settings();ROOT=cfg.work_dir/'v5';P=ROOT/'physical';P.mkdir(parents=True,exist_ok=True);V4=cfg.work_dir/'v4';D=np.load(V4/'analysis_only.npz');Z=D['Z'];t=D['t'];base=json.load(open(ROOT/'physical_event_parameters.json'));r=np.load(ROOT/'strict_smooth_routing.npz');sr=base['sample_rate'];N=base['samples'];ts=np.arange(N)/sr
modes=base['modes'];taus=np.array([.12,.45,1.5]);offs=np.array([-.6,0,.6]);poles=[(a,b) for a in taus for b in offs];Q=len(poles)
mask=np.zeros(len(t),bool);maskaudio=np.zeros(N,bool)
for a,b in base['active_intervals']:mask|=(t>=a)&(t<b);maskaudio|=(ts>=a)&(ts<b)
# Independent recording-resume initial states per frequency, decaying with the same fixed 1.5s
# longest pole, and terminated at the next recorded silence. No freely time-varying state.
I=np.zeros((len(t),len(base['active_intervals'])),complex)
for k,(a,b) in enumerate(base['active_intervals']):
 ix=(t>=a)&(t<b);I[ix,k]=np.exp(-(t[ix]-a)/1.5)
notes=[5,6,7,8,9,10];rng=np.random.default_rng(20261107)
meta={'sample_rate':sr,'samples':N,'active_intervals':base['active_intervals'],'geometry':base['geometry'],'family':'Shared causal response per string, one signed real impulse strength per contact','strength_sign':'Signed force is free: one common sign flips ALL modal components of that contact together. No independent per-mode contact phase.','poles':poles,'modes':modes,'initial_state':'One complex amplitude per observed frequency per recording-resume interval, tau=1.5 s; reset only at recording silence.','fit_target':'Same in-sample complex modal analysis as v4; not heldout prediction; separate bounded-acceleration strict and optional-contact trajectories.','families':{}}

def cost(Zj,A,phase,g,theta,init):
 pred=np.empty_like(Zj)
 for mi in range(Zj.shape[1]):
  B=np.einsum('qte,e->tq',A,g*phase[:,mi],optimize=True)
  pred[:,mi]=B@theta[:,mi]+I@init[:,mi]
 return float(np.linalg.norm((pred-Zj)[mask])**2),pred

def fit_note(fam,j):
 r=np.load(ROOT/f'{fam}_smooth_routing.npz')
 evs=sorted((e for e in base['families'][fam]['contact_events'] if e['string_index']==notes[j]),key=lambda e:e['time'])
 et=np.array([e['time'] for e in evs]);E=len(et);ids=[k for k,m in enumerate(modes) if m['j']==j];freq=np.array([modes[k]['f'] for k in ids]);Zj=Z[:,ids];M=len(ids)
 if E==0:
  G=I.conj().T@I;ridge=max(np.trace(G).real/len(G),1e-8)*1e-7
  initial=linalg.solve(G+ridge*np.eye(len(G)),I.conj().T@Zj,assume_a='her');pred=I@initial
  zero=np.zeros((Q,M)).tolist()
  return ids,pred,{'note_index':j,'events':[],'strengths':[],'mode_ids':ids,'shared_response_real':zero,'shared_response_imag':zero,'initial_state_real':initial.real.tolist(),'initial_state_imag':initial.imag.tolist(),'history':[],'best_seed':None,'best_iteration':None,'fit_energy_error':float(np.linalg.norm((pred-Zj)[mask])**2),'strength_abs_min':0.0,'strength_abs_max':0.0}
 u=t[:,None]-et[None,:];valid=(u>=0)&mask[:,None];A=np.empty((Q,len(t),E),complex)
 for q,(tau,off) in enumerate(poles):A[q]=np.where(valid,(1-np.exp(-np.maximum(u,0)/.004))*np.exp((-1/tau+2j*np.pi*off)*np.maximum(u,0)),0)
 phase=np.exp(-2j*np.pi*et[:,None]*freq[None,:])
 # Physical phase reference is time since contact, not arbitrary global carrier phase.
 inits=[]
 dirg=[]
 for te in et:
  k=int(round(te/.01));lo=max(0,k-1);hi=min(len(t)-1,k+1);v=r['path'][hi]-r['path'][lo];dirg.append(np.sign(v) if np.isfinite(v) and v!=0 else 1)
 inits=[np.array(dirg,float),np.ones(E),rng.choice([-1.,1.],E)]
 best=None;hist=[]
 for si,g in enumerate(inits):
  old=1e99;theta=np.zeros((Q,M),complex);initial=np.zeros((I.shape[1],M),complex)
  for it in range(25):
   pred=np.zeros_like(Zj);Vs=[]
   # Refit the same response coefficients jointly across all contacts of each string.
   for mi in range(M):
    B=np.einsum('qte,e->tq',A,g*phase[:,mi],optimize=True);H=np.c_[B,I];G=H.conj().T@H;ridge=max(np.trace(G).real/len(G),1e-8)*1e-7
    th=linalg.solve(G+ridge*np.eye(len(G)),H.conj().T@Zj[:,mi],assume_a='her');theta[:,mi]=th[:Q];initial[:,mi]=th[Q:]
    V=np.einsum('qte,q->te',A,theta[:,mi],optimize=True)*phase[:,mi];Vs.append(V);pred[:,mi]=V@g+I@initial[:,mi]
   loss=float(np.linalg.norm((pred-Zj)[mask])**2)
   if best is None or loss<best[0]:best=(loss,g.copy(),theta.copy(),initial.copy(),pred.copy(),si,it)
   if it>3 and abs(old-loss)/max(old,1e-20)<2e-5:break
   old=loss
   G=np.zeros((E,E));rhs=np.zeros(E)
   for mi,V in enumerate(Vs):G+=(V.conj().T@V).real;rhs+=(V.conj().T@(Zj[:,mi]-I@initial[:,mi])).real
   ridge=max(np.trace(G)/max(E,1),1e-10)*1e-5;newg=linalg.solve(G+ridge*np.eye(E),rhs,assume_a='pos')
   # Scale indeterminacy removed by RMS normalization. Finite strengths, not unbounded cancelling forces.
   norm=np.sqrt(np.mean(newg**2))+1e-20;g=newg/norm;g=np.clip(g,-8,8)
   if fam=='strict':g=np.where(abs(g)<.05,np.where(g<0,-.05,.05),g)
  hist.append({'seed':si,'iterations':it+1,'loss':loss});print(fam,'note',j,'seed',si,'iter',it,'relative',np.sqrt(loss/np.linalg.norm(Zj[mask])**2),flush=True)
 loss,g,theta,initial,pred,si,it=best
 return ids,pred,{'note_index':j,'events':evs,'strengths':g.tolist(),'mode_ids':ids,'shared_response_real':theta.real.tolist(),'shared_response_imag':theta.imag.tolist(),'initial_state_real':initial.real.tolist(),'initial_state_imag':initial.imag.tolist(),'history':hist,'best_seed':si,'best_iteration':it,'fit_energy_error':loss,'strength_abs_min':float(abs(g).min()),'strength_abs_max':float(abs(g).max())}
for fam in ['strict','relaxed']:
 out=P/f'{fam}_shared_parameters.json';params=[];pred=np.zeros_like(Z)
 for j in range(6):
  ids,pr,pa=fit_note(fam,j);pred[:,ids]=pr;params.append(pa);json.dump(params,open(out,'w'),separators=(',',':'));np.save(P/f'{fam}_partial_modal.npy',pred)
 synth=np.zeros(N)
 for mi,m in enumerate(modes):
  z=pred[:,mi];a=np.interp(ts,t,z.real)+1j*np.interp(ts,t,z.imag);synth+=np.real(a*np.exp(2j*np.pi*m['f']*ts))
 synth*=maskaudio;np.save(P/f'{fam}_shared_raw.npy',synth);wavfile.write(P/f'{fam}_shared_float.wav',sr,synth.astype(np.float32))
 meta['families'][fam]={'contacts':sum(len(q['events']) for q in params),'shared_response_real_coefficients':2*Q*len(modes),'initial_state_real_coefficients':2*len(modes)*I.shape[1],'real_strength_coefficients':sum(len(q['events']) for q in params),'amplitude_floor_RMS_units':.05 if fam=='strict' else 0,'max_amplitude_RMS_units':8,'peak':float(max(abs(synth)))}
 json.dump(meta,open(P/'shared_metadata.json','w'),indent=2);print('DONE',fam,'peak',max(abs(synth)),flush=True)
