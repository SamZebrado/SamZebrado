"""Bounded six-candidate in-sample two-bank endpoint fitting, not measured animal motion."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
import argparse,json,time,copy
from pathlib import Path
import numpy as np
from scipy import linalg
from scipy.io import wavfile
from two_bank_model import *


def search_route(t,drive,orientation,endpoints,duration,max_speed=50,max_half=2.,penalty=2.5):
    dt=float(t[1]-t[0]);L,R=endpoints;minimum=1.875*(R-L)/max_speed
    steps=np.arange(int(np.ceil(minimum/dt)),int(np.floor(max_half/dt))+1);T=int(np.ceil(duration/dt));tt=np.arange(T+1)*dt
    if len(steps)==0:raise ValueError('No feasible half-cycle under declared speed and duration limits')
    strings=geometry(orientation);modeled=[s for s in strings if s['note_index'] is not None and L<s['coordinate']<R]
    raw=drive/(np.sqrt(np.mean(drive**2,axis=1,keepdims=True))+1e-9);reward=np.log1p(np.minimum(raw,8)**2)
    edge=np.full((2,T+1,len(steps)),-np.inf);ends=tt[:,None];lens=steps[None,:]*dt;starts=ends-lens
    fractions=[inverse_smoothstep((s['coordinate']-L)/(R-L)) for s in modeled]
    for target in (0,1):
        value=np.zeros_like(starts)
        for string,f in zip(modeled,fractions):value+=np.interp(starts+(f if target==1 else 1-f)*lens,t,reward[string['note_index']],left=0,right=0)
        value-=penalty+.2*((lens-1.2)/1.2)**2;value[starts<0]=-np.inf;edge[target]=value
    dp=np.full((T+1,2),-np.inf);dp[0]=0;back=np.full((T+1,2),-1,int)
    for end in range(1,T+1):
        valid=steps<=end;ss=steps[valid]
        for target in (0,1):
            vals=dp[end-ss,1-target]+edge[target,end,valid]
            if len(vals):idx=int(vals.argmax());dp[end,target]=vals[idx];back[end,target]=ss[idx]
    state=int(dp[T].argmax());end=T;knots=[T*dt]
    while end:
        step=back[end,state]
        if step<=0:raise RuntimeError('No continuous complete-sweep route')
        end-=step;state=1-state;knots.append(end*dt)
    knots=knots[::-1]
    return {'law':'quintic_smoothstep_C2','equation':'x=L+(R-L)S(u) forward; x=R-(R-L)S(u) reverse; S=10u^3-15u^4+6u^5',
      'orientation_B_A':list(orientation),'orientation_definition':'+1 pitch index rises with spatial coordinate; -1 falls. Not measured from video.',
      'endpoints':list(endpoints),'endpoint_times':knots,'start_endpoint':state,'string_geometry':strings,
      'assumed_max_speed_string_spacings_s':max_speed,'assumed_half_period_min_s':float(minimum),'assumed_half_period_max_s':max_half,'route_grid_seconds':dt,'sweep_penalty':penalty,
      'duration_prior':'0.2*((half_period-1.2)/1.2)^2; heuristic, not biological evidence',
      'route_objective':'sum log(1+normalized_onset_drive^2) at modeled geometric crossings minus disclosed sweep and duration penalties',
      'route_score':float(dp[T].max()),'observation_status':'Only two-bank order/facing edges are visually supported. 21+21 points, spacing, tuning, orientation, span and reach are hypotheses.',
      'silence_handling':'One continuous analytic trajectory through all recording gaps. Gap events disabled. Contact ringing resets at recording silence; one initial state per observed pitch/mode per resume.',
      'unmodeled_strings':'All 42 spatial points are retained. Crossed strings outside the inherited six-pitch dictionary are explicitly assumed to have zero effective pluck. Gap 20..26 has no sound source.'}


def fit_shared(meta,route,Z,t,out,iterations=8,seeds=1):
    mask=interval_ids(t,meta['active_intervals'])>=0;I=initial_atoms(t,meta['active_intervals']);poles=meta['poles'];modes=meta['modes'];all_ev=crossing_events(route,meta['active_intervals']);groups=[];initial_states=[];pred=np.zeros_like(Z)
    for j in range(6):
        ids=[k for k,m in enumerate(modes) if m['j']==j];M=len(ids);Q=len(poles);Zj=Z[:,ids];entries=[]
        for bank in ['B','A']:
            ev=[e for e in all_ev if e['enabled'] and e['note_index']==j and e['bank']==bank]
            if not ev:continue
            A=response_atoms(t,ev,poles,meta['active_intervals']);phase=np.exp(-2j*np.pi*np.array([e['time'] for e in ev])[:,None]*np.array([modes[k]['f'] for k in ids])[None,:])
            entries.append({'bank':bank,'events':ev,'A':A,'phase':phase,'size':len(ev)})
        assert entries
        split=np.cumsum([0]+[e['size'] for e in entries]);E=int(split[-1]);K=len(entries);best=None;history=[]
        for seed in range(seeds):
            g=np.concatenate([np.array([v['direction'] for v in e['events']],float) if seed==0 else np.ones(e['size']) for e in entries]);old=np.inf
            for it in range(iterations):
                theta=np.zeros((K,Q,M),complex);initial=np.zeros((I.shape[1],M),complex);pr=np.zeros_like(Zj);Vs=[]
                for mi in range(M):
                    Bs=[np.einsum('qte,e->tq',e['A'],g[split[k]:split[k+1]]*e['phase'][:,mi],optimize=True) for k,e in enumerate(entries)]
                    H=np.column_stack(Bs+[I]);G=H.conj().T@H;ridge=max(np.trace(G).real/len(G),1e-8)*1e-7;th=linalg.solve(G+ridge*np.eye(len(G)),H.conj().T@Zj[:,mi],assume_a='her')
                    theta[:,:,mi]=th[:K*Q].reshape(K,Q);initial[:,mi]=th[K*Q:]
                    V=np.column_stack([np.einsum('qte,q->te',e['A'],theta[k,:,mi],optimize=True)*e['phase'][:,mi] for k,e in enumerate(entries)]);Vs.append(V);pr[:,mi]=V@g+I@initial[:,mi]
                loss=float(np.linalg.norm((pr-Zj)[mask])**2)
                if best is None or loss<best[0]:best=(loss,g.copy(),theta.copy(),initial.copy(),pr.copy(),seed,it)
                if it>3 and abs(old-loss)/max(old,1e-20)<2e-5:break
                old=loss;G=np.zeros((E,E));rhs=np.zeros(E)
                for mi,V in enumerate(Vs):G+=(V.conj().T@V).real;rhs+=(V.conj().T@(Zj[:,mi]-I@initial[:,mi])).real
                ridge=max(np.trace(G)/max(E,1),1e-10)*1e-5;newg=linalg.solve(G+ridge*np.eye(E),rhs,assume_a='pos')
                for k,e in enumerate(entries):
                    ss=slice(split[k],split[k+1]);g[ss]=np.clip(newg[ss]/(np.sqrt(np.mean(newg[ss]**2))+1e-20),-8,8)
            history.append({'seed':seed,'iterations':it+1,'modal_relative_error':float(np.sqrt(loss/np.linalg.norm(Zj[mask])**2))});print(out.parent.name,'pitch',j,'physical strings',K,history[-1],flush=True)
        loss,g,theta,initial,pr,seed,it=best;pred[:,ids]=pr
        for k,e in enumerate(entries):
            groups.append({'bank':e['bank'],'string_index':5+j,'note_index':j,'coordinate':e['events'][0]['coordinate'],'mode_ids':ids,'events':e['events'],'strengths':g[split[k]:split[k+1]].tolist(),
              'response_real':theta[k].real.tolist(),'response_imag':theta[k].imag.tolist(),'joint_pitch_fit_history':history,'best_seed':seed,'best_iteration':it})
        initial_states.append({'note_index':j,'mode_ids':ids,'real':initial.real.tolist(),'imag':initial.imag.tolist()})
        json.dump({'metadata':meta,'route':route,'groups':groups,'initial_states':initial_states},open(out,'w'),separators=(',',':'))
    return {'metadata':meta,'route':route,'groups':groups,'initial_states':initial_states},pred


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--v4',type=Path,required=True);p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--coarse-iterations',type=int,default=8);p.add_argument('--refine-iterations',type=int,default=18);args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    base=json.load(open(args.v4/'comparison_parameters.json'));D=np.load(args.v4/'analysis_only.npz');r=np.load(args.v4/'comparison_routing.npz');Z=D['Z'];t=D['t'];sr,y=wavfile.read(args.source);y=y.astype(float)/(32768 if y.dtype==np.int16 else 1)
    assert y.ndim==1 and sr==base['sample_rate'] and len(y)==base['samples']
    meta={'sample_rate':sr,'samples':len(y),'duration':len(y)/sr,'analysis_dt':float(t[1]-t[0]),'active_intervals':base['active_intervals'],'modes':[{k:m[k] for k in ['j','h','f']} for m in base['modes']],
      'poles':[(tau,off) for tau in [.12,.45,1.5] for off in [-.6,0,.6]],'family':'Independent shared response for each physical bank x string, one signed force per crossing; equal-pitch bank contributions sum in mono.',
      'fit_scope':f'Same supplied {len(y)/sr:.9f}s mono recording; in-sample fitting, no independent validation, no source mixing or authenticity/biomechanical feasibility claim.',
      'geometry_assumptions':'Two ordered 21-string banks B 0..20, A 26..46, nonsounding six-spacing gap; 21+21 D-pentatonic tuning hypothetical. Full 42 points retained, only inherited six-pitch modal dictionary excited.',
      'initial_state':'One complex state per observed mode per five recording-resume intervals, tau=1.5s; aggregate initial state not assigned arbitrarily to a bank.',
      'prior_version_caveat':'v6 was A-only. v4/v5 allowed interior reversals/stops. v6/v7 reset ringing at recording gaps; v4/v5 masked gaps but let old contacts decay after resume.',
      'search_bound_change':'Maximum speed remains 50 string-spacings/s. Max half-cycle expanded explicitly from v6 0.9s to v7 2.0s so larger spans can be traversed slowly. Not video-calibrated.'}
    candidates=[('full_Bup_Aup',(1,1),(4.5,36.5)),('full_Bup_Adown',(1,-1),(4.5,41.5)),('full_Bdown_Aup',(-1,1),(9.5,36.5)),('full_Bdown_Adown',(-1,-1),(9.5,41.5)),('partial_B1_A6',(-1,1),(14.5,36.5)),('partial_B2_A6',(-1,1),(13.5,36.5))]
    results={};best=None
    for name,orientation,endpoints in candidates:
        folder=args.out/name;folder.mkdir(exist_ok=True);route=search_route(t,r['drive'],orientation,endpoints,len(y)/sr)
        print('ROUTE',name,'span',endpoints[1]-endpoints[0],'min_half',route['assumed_half_period_min_s'],'segments',len(route['endpoint_times'])-1,flush=True)
        model,pred=fit_shared(meta,route,Z,t,folder/'parameters.json',args.coarse_iterations,1);s=modal_to_audio(meta,t,pred);m=metrics(y,s);model['evaluation']=m
        json.dump(model,open(folder/'parameters.json','w'),separators=(',',':'));np.save(folder/'raw.npy',s)
        results[name]={'orientation_B_A':list(orientation),'endpoints':list(endpoints),'metrics':m,'physical_string_response_groups':len(model['groups']),'shared_response_real_coefficients':sum(2*np.array(g['response_real']).size for g in model['groups']),'strength_count':sum(len(g['strengths']) for g in model['groups']),'route_score':route['route_score'],'assumed_min_half_s':route['assumed_half_period_min_s']}
        json.dump(results,open(args.out/'candidate_metrics.json','w'),indent=2);print('RESULT',name,m,flush=True)
        if best is None or m['waveform_NRMSE']<best[0]:best=(m['waveform_NRMSE'],name,model,s)
    _,name,coarse,old_s=best;folder=args.out/'refined';folder.mkdir(exist_ok=True)
    refined,pred=fit_shared(meta,coarse['route'],Z,t,folder/'parameters.json',args.refine_iterations,2);s=modal_to_audio(meta,t,pred);m=metrics(y,s);refined['evaluation']=m;json.dump(refined,open(folder/'parameters.json','w'),separators=(',',':'));np.save(folder/'raw.npy',s)
    final,final_s=(refined,s) if m['waveform_NRMSE']<coarse['evaluation']['waveform_NRMSE'] else (coarse,old_s)
    final['selection']={'selected_geometry_candidate':name,'coarse_iterations':args.coarse_iterations,'coarse_seeds':1,'refine_iterations':args.refine_iterations,'refine_seeds':2,'candidate_count':len(candidates),'selected_refined':final is refined,'not_global_optimum':True}
    json.dump(final,open(args.out/'shared_parameters.json','w'),separators=(',',':'));np.save(args.out/'shared_raw.npy',final_s)
    report={'metric_scope':'Same original full waveform; signed scalar LS gain; all samples; in-sample only.','selected_candidate':name,'shared':final['evaluation'],'refined_candidate_metrics':m,'candidates':results,'single_bank_v6_comparison':{'waveform_NRMSE':.5468594849140688,'correlation':.8372244047953229,'snr_db':5.2424850187033964}}
    json.dump(report,open(args.out/'metrics.json','w'),indent=2);print('FINAL',name,final['evaluation'],flush=True)

if __name__=='__main__':main()
