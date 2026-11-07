"""Compare continuous-contact crossing events vs optional/extra contact, same two-bank topology.
Reproduce: OPENBLAS_NUM_THREADS=2 python fit_comparison.py
"""
from pathlib import Path
src=Path(__file__).with_name('fit_two_banks.py').read_text()
# Reuse the deterministic audio analysis and constrained path-search implementation.
exec(src.split('# Per-note union')[0].replace('22+np.arange(21)','26+np.arange(21)').replace('42+.001','46+.001'))
# The two identical-tuned banks have reflection ambiguity. Choose an A-only representative:
# B occupies x=0..20, a 6-string-spacing gap, A occupies x=26..46.
path=46-path; notes=notes[::-1]; orient=(-1,-1)
np.savez(P/'comparison_routing.npz',t=t,path=path,notes=notes,coordinates=coords,drive=drive,envelopes=env,fundamentals=fund)
# Reflect earlier candidate events to the same representative.
optional={41-q:es for q,es in enumerate(events)}
strict={q:[] for q in range(42)}
for k in range(1,len(t)):
 if not np.isfinite(path[k-1:k+1]).all() or path[k]==path[k-1]:continue
 for q,c in enumerate(coords):
  if (path[k-1]<c<=path[k]) or (path[k-1]>c>=path[k]):strict[q].append(float(t[k]))
# At exactly touching/turning around, do not duplicate a touch. No crossed string omitted.
strict={q:sorted(set(v)) for q,v in strict.items()}
relaxed={q:sorted(set(strict[q]+optional.get(q,[]))) for q in range(42)}
mask=np.zeros(len(t),bool)
for a,b in active:mask|=(t>=a)&(t<b)
# Modal dictionary, fitted from the same recording (no evaluation split).
cand=[]
for j,f in enumerate(fund):
 for h in range(1,13):
  fr,pow=peak_near(f*h,max(2,f*h*.012))
  if fr<=4000:cand.append(dict(j=j,h=h,f=fr,power=pow,basepower=peak_near(f,2)[1]))
cand.sort(key=lambda a:(a['h']==1,a['basepower']/a['h']),reverse=True);modes=[]
for m in cand:
 if all(abs(m['f']-o['f'])>2.0 for o in modes):modes.append(m)
modes.sort(key=lambda a:a['f']);taus=[.12,.45,1.5];offsets=[-.6,0,.6]
Z=np.stack([band(m['f'],7.5) for m in modes],axis=1)
np.savez_compressed(P/'analysis_only.npz',Z=Z,t=t,frequencies=[m['f'] for m in modes])
metadata={'sample_rate':sr,'samples':N,'duration':N/sr,'active_intervals':active,'tunings_midi_assumed':midi.tolist(),'geometry':{'bank_order':'B then gap then A','gap_string_spacings':6,'max_speed_string_spacings_s':50,'orientation_representative':orient,'route_scores':[{'orientation':r[4],'score':r[0]} for r in routes],'bank_ambiguity':'Four route scores tie; A-only is a reflection-equivalent representative, not identified source.'},'families':{},'modes':modes,'decay_times':taus,'mode_detunings':offsets,'scope':'Same fitted onset route, independent acoustic coefficient fits. Not a proven global optimum over all possible trajectories.','source_mixing':False}
# Exact analysis reference for this dictionary without contact restrictions, distinct nonphysical ceiling.
ceiling=np.zeros(N)
for mi,m in enumerate(modes):
 z=Z[:,mi];a=np.interp(ts,t,z.real)+1j*np.interp(ts,t,z.imag);ceiling+=np.real(a*np.exp(2j*np.pi*m['f']*ts))
maskaudio=np.zeros(N)
for a,b in active:maskaudio[(ts>=a)&(ts<b)]=1
ceiling*=maskaudio;np.save(P/'unconstrained_modal_reference.npy',ceiling)
for family,evmap in [('strict',strict),('relaxed',relaxed)]:
 pred=np.zeros_like(Z);params=[];floors=[];paramcount=0
 for j,k in enumerate(base_ix):
  pairs=sorted((te,q,'contact') for q in range(42) if notes[q]==k for te in evmap[q])
  # Unknown ringing at each discontinuous recording start is a fitted initial state, not a tail contact.
  pairs+= [(a,-1,'initial_state') for a,b in active];pairs=sorted(set(pairs))
  specs=[];cols=[]
  for et,q,kind in pairs:
   u=t-et;pos=u>=0
   for tau in taus:
    for off in offsets:
     a=np.zeros(len(t),complex);a[pos]=(1-np.exp(-u[pos]/.004))*np.exp((-1/tau+2j*np.pi*off)*u[pos]);a[~mask]=0
     cols.append(a);specs.append((et,q,kind,tau,off))
  A=np.stack(cols,axis=1); ids=[mi for mi,m in enumerate(modes) if m['j']==j]
  G=A.conj().T@A; ridge=np.max(np.diag(G).real)*1e-6; rhs=A.conj().T@Z[:,ids]
  C=linalg.solve(G+ridge*np.eye(len(G)),rhs,assume_a='her');paramcount+=2*C.size
  # Strict: every geometric crossing has a nonzero excitation. Enforce isolated fundamental response
  # RMS >=5% of median event RMS. This explicit floor prevents the zero-amplitude skip loophole.
  # It is an operational assumption, not a measured audibility/contact threshold.
  if family=='strict':
   energy=[]
   for ei,(et,q,kind) in enumerate(pairs):
    ci=slice(ei*9,(ei+1)*9); idx=(t>=et)&(t<et+.25); energy.append(np.sqrt(np.mean(abs(A[idx,ci]@C[ci,0])**2)) if idx.any() else 0)
   med=np.median([e for e,pair in zip(energy,pairs) if pair[2]=='contact']) if any(pair[2]=='contact' for pair in pairs) else 0
   floor=.05*med
   for ei,((et,q,kind),en) in enumerate(zip(pairs,energy)):
    if kind=='contact' and en<floor and en>1e-12:
     C[ei*9:(ei+1)*9]*=floor/en;floors.append({'time':et,'point':q,'before_rms':float(en),'required_rms':float(floor)})
  pred[:,ids]=A@C
  params.append({'fundamental_index':j,'mode_ids':ids,'atoms':[list(s) for s in specs],'coefficients_real':C.real.tolist(),'coefficients_imag':C.imag.tolist()})
  print('family',family,'note',j,'events',len(pairs),'coeff',C.size,'error',np.linalg.norm(pred[:,ids][mask]-Z[:,ids][mask])/np.linalg.norm(Z[:,ids][mask]),flush=True)
 synth=np.zeros(N)
 for mi,m in enumerate(modes):
  a=np.interp(ts,t,pred[:,mi].real)+1j*np.interp(ts,t,pred[:,mi].imag)
  synth+=np.real(a*np.exp(2j*np.pi*m['f']*ts))
 synth*=maskaudio;np.save(P/f'{family}_raw.npy',synth)
 # No peak loudness change for quantitative audio. A shared listening attenuation comes later if needed.
 wavfile.write(P/f'{family}_fit_float.wav',sr,synth.astype(np.float32))
 json.dump(params,open(P/f'{family}_coefficients.json','w'),separators=(',',':'))
 evs=[{'time':te,'point_index':q,'bank':'B' if q<21 else 'A','string_index':int(notes[q])} for q,tes in evmap.items() for te in tes]
 metadata['families'][family]={'contact_events':evs,'number_of_contacts':len(evs),'real_acoustic_coefficients':paramcount,'strict_floor_fraction':.05 if family=='strict' else 0,'floor_adjustments':floors,'initial_state_events':len(active)*len(base_ix),'free_modes':len(modes),'peak':float(max(abs(synth)))}
 print('DONE',family,max(abs(synth)),flush=True)
json.dump(metadata,open(P/'comparison_parameters.json','w'),indent=2)
