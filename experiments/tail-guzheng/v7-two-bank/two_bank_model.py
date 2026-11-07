"""Two actual ordered latent banks, one continuous endpoint sweep, separate string responses."""
import numpy as np
from sweep_math import smoothstep,inverse_smoothstep,trajectory,interval_ids,initial_atoms,response_atoms,modal_to_audio,metrics


def geometry(orientation):
    result=[]
    for bank,offset,ori in [('B',0,orientation[0]),('A',26,orientation[1])]:
        for i in range(21):
            k=i if ori==1 else 20-i
            result.append({'bank':bank,'spatial_string_index':i,'string_index':k,'coordinate':offset+i,
                'point_index':i if bank=='B' else 21+i,'note_index':k-5 if 5<=k<=10 else None})
    return result


def crossing_events(route,intervals):
    L,R=route['endpoints'];events=[]
    for string in route['string_geometry']:
        c=string['coordinate']
        if not L<c<R:continue
        f=inverse_smoothstep((c-L)/(R-L))
        for k,(a,b) in enumerate(zip(route['endpoint_times'][:-1],route['endpoint_times'][1:])):
            direction=1 if (k+route['start_endpoint'])%2==0 else -1
            te=a+(b-a)*(f if direction==1 else 1-f)
            block=next((i for i,(start,end) in enumerate(intervals) if start<=te<end),-1)
            events.append(dict(string,time=float(te),half_cycle=k,direction=direction,recorded_interval=block,
                enabled=block>=0 and string['note_index'] is not None,
                status='recording_gap_disabled' if block<0 else ('modeled_crossing' if string['note_index'] is not None else 'unmodeled_string_assumed_skipped')))
    return sorted(events,key=lambda e:e['time'])


def render_modal(parameters):
    meta=parameters['metadata'];t=np.arange(0,meta['duration'],meta['analysis_dt']);modes=meta['modes'];pred=np.zeros((len(t),len(modes)),complex);initial_pred=np.zeros_like(pred);bank_pred={b:np.zeros_like(pred) for b in ['B','A']}
    I=initial_atoms(t,meta['active_intervals'])
    for group in parameters['groups']:
        ev=group['events'];ids=group['mode_ids'];A=response_atoms(t,ev,meta['poles'],meta['active_intervals']);g=np.asarray(group['strengths']);theta=np.array(group['response_real'])+1j*np.array(group['response_imag'])
        phase=np.exp(-2j*np.pi*np.array([e['time'] for e in ev])[:,None]*np.array([modes[i]['f'] for i in ids])[None,:])
        for n,mi in enumerate(ids):
            B=np.einsum('qte,e->tq',A,g*phase[:,n],optimize=True);z=B@theta[:,n]
            pred[:,mi]+=z;bank_pred[group['bank']][:,mi]+=z
    for initial in parameters['initial_states']:
        ids=initial['mode_ids'];coeff=np.array(initial['real'])+1j*np.array(initial['imag']);initial_pred[:,ids]=I@coeff;pred[:,ids]+=initial_pred[:,ids]
    return t,pred,initial_pred,bank_pred
