"""Bounded velocity-and-acceleration Viterbi path on the same two ordered banks."""
from pathlib import Path
import numpy as np,json
from scipy import signal
from common import settings
cfg=settings();P=cfg.work_dir/'v5';P.mkdir(parents=True,exist_ok=True);V4=cfg.work_dir/'v4';r=np.load(V4/'comparison_routing.npz');base=json.load(open(V4/'comparison_parameters.json'))
t=r['t'][::2];dt=.02;step=.1;coords=r['coordinates'];notes=r['notes'];midi=base['tunings_midi_assumed'];di=r['drive'][:,::2]; reward=np.minimum(di/(np.sqrt(np.mean(di**2,axis=1,keepdims=True))+1e-9),8)**2
xgrid=np.arange(0,46.0001,step);vel=np.arange(-10,11);mvel=50.;macc=750.;edges=3 # velocity increment 5, delta<=3 every20ms
contact=np.exp(-.5*((xgrid[:,None]-coords[None,:])/.30)**2);W=np.zeros((42,6))
for q,n in enumerate(notes):
 if n in [5,6,7,8,9,10]:W[q,n-5]=1
R=contact@W@reward;path=np.full(len(t),np.nan);velpath=np.full(len(t),np.nan);scores=[]
for a,b in base['active_intervals']:
 ids=np.where((t>=a)&(t<b))[0];C=np.full((21,len(xgrid)),-1e15);C[10]=np.where(xgrid>=26,1e-7,0) # only symmetry representative tie break
 backs=np.empty((len(ids),21,len(xgrid)),np.int8)
 for it,k in enumerate(ids):
  D=np.full_like(C,-1e15)
  for vi,v in enumerate(vel):
   cand=[];prevs=[]
   for delta in range(-edges,edges+1):
    pv=vi-delta
    if pv<0 or pv>=21:continue
    z=np.full(len(xgrid),-1e15)
    if v>0:z[v:]=C[pv,:-v]
    elif v<0:z[:v]=C[pv,-v:]
    else:z=C[pv].copy()
    z-=.05*(delta**2)+.003*(v**2)
    cand.append(z);prevs.append(pv)
   cand=np.stack(cand);idx=cand.argmax(axis=0);D[vi]=cand[idx,np.arange(len(xgrid))]+R[:,k]*(abs(v)/10);backs[it,vi]=np.array(prevs,np.int8)[idx]
  C=D
 vi,xi=np.unravel_index(np.argmax(C),C.shape);scores.append(float(C[vi,xi]))
 for it in range(len(ids)-1,-1,-1):
  path[ids[it]]=xgrid[xi];velpath[ids[it]]=vel[vi]*5;pv=backs[it,vi,xi];xi-=vel[vi];vi=pv
 print('segment',a,b,'score',scores[-1],flush=True)
# Exact intersection times along each linear integration step; preserve all crossings.
strict=[]
for k in range(1,len(t)):
 if not np.isfinite(path[k-1:k+1]).all() or path[k]==path[k-1]:continue
 for q,c in enumerate(coords):
  if (path[k-1]<c<=path[k]) or (path[k-1]>c>=path[k]):
   tm=float(t[k-1]+(c-path[k-1])/(path[k]-path[k-1])*dt);strict.append({'time':tm,'point_index':q,'bank':'B' if q<21 else 'A','string_index':int(notes[q])})
# Onset-driven optional contacts only near the same path, with no geometric teleportation.
relaxed=list(strict)
for q,(n,c) in enumerate(zip(notes,coords)):
 if n not in [5,6,7,8,9,10]:continue
 near=np.abs(path-c)<=.35;drive=di[n-5]*near
 peaks,_=signal.find_peaks(drive,distance=4,prominence=max(drive)*.025 if max(drive)>0 else 1)
 for pk in peaks:
  tm=float(t[pk])
  if all(e['point_index']!=q or abs(e['time']-tm)>.015 for e in relaxed):relaxed.append({'time':tm,'point_index':q,'bank':'B' if q<21 else 'A','string_index':int(n)})
# Interpolate only within individual recorded intervals, never across silences.
path100=np.full(len(r['t']),np.nan)
for a,b in base['active_intervals']:
 ix=(t>=a)&(t<b);jj=(r['t']>=a)&(r['t']<b);path100[jj]=np.interp(r['t'][jj],t[ix],path[ix])
np.savez(P/'smooth_routing.npz',t=r['t'],path=path100,notes=notes,coordinates=coords,dt_integration=dt,velocity_at_20ms=velpath,time_20ms=t,path_20ms=path)
base['families']={'strict':{'contact_events':sorted(strict,key=lambda e:e['time'])},'relaxed':{'contact_events':sorted(relaxed,key=lambda e:e['time'])}}
base['geometry']['max_acceleration_string_spacings_s2']=macc;base['geometry']['trajectory_model']='Viterbi with velocity state, hard v<=50 and |dv|/dt<=750, dt=20ms, position grid0.1; no teleportation within recorded intervals.';base['geometry']['score']=scores
json.dump(base,open(P/'smooth_event_parameters.json','w'),indent=2)
print('counts',len(strict),len(relaxed),'banks',set(e['bank'] for e in strict),'range',np.nanmin(path),np.nanmax(path),flush=True)
