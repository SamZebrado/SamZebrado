"""Audit geometry, continuous full-recording motion, physical-string responses and rendering."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import argparse,json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from two_bank_model import *


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--source',type=Path);a=ap.parse_args();P=a.directory;model=json.loads((P/'shared_parameters.json').read_text());meta=model['metadata'];route=model['route'];knots=np.array(route['endpoint_times']);h=np.diff(knots);L,R=route['endpoints'];span=R-L
    events=crossing_events(route,meta['active_intervals']);force_lookup={(g['bank'],g['string_index'],e['half_cycle']):float(force) for g in model['groups'] for e,force in zip(g['events'],g['strengths'])}
    for e in events:
        e['strength']=force_lookup.get((e['bank'],e['string_index'],e['half_cycle']),0.)
        if e['enabled']:e['status']='weak_below_0.05' if abs(e['strength'])<.05 else 'fitted_contact'
    x,v,acc=trajectory(route,np.arange(0,meta['duration'],.02));xx,vv,aa=trajectory(route,knots)
    bad_speed=0;outside=0.;eq=0;crossing_error=0.
    for k,(t0,t1) in enumerate(zip(knots[:-1],knots[1:])):
        tt=t0+(t1-t0)*np.linspace(1e-6,1-1e-6,1001);xs,vs,_=trajectory(route,tt);direction=1 if (k+route['start_endpoint'])%2==0 else -1
        bad_speed+=int(np.sum(vs*direction<=0));outside=max(outside,float(np.max(np.maximum(L-xs,xs-R))));eq+=int(np.sum((xs==L)|(xs==R)))
    tx=np.array([e['time'] for e in events]);ex,ev,_=trajectory(route,tx);crossing_error=float(np.max(abs(ex-np.array([e['coordinate'] for e in events]))))
    assert bad_speed==0 and outside<=1e-12 and crossing_error<1e-10
    assert all(not 20<e['coordinate']<26 for e in events)
    active=[e for e in events if e['enabled']];groups=model['groups'];initial=model['initial_states'];response_n=sum(2*np.array(g['response_real']).size for g in groups);strength_n=sum(len(g['strengths']) for g in groups);init_n=sum(2*np.array(i['real']).size for i in initial)
    bank_info={}
    for bank in ['B','A']:
        bg=[g for g in groups if g['bank']==bank];be=[e for e in events if e['bank']==bank];fs=np.concatenate([np.array(g['strengths']) for g in bg]) if bg else np.array([])
        bank_info[bank]={'physical_response_count':len(bg),'string_pitch_indices':[g['string_index'] for g in bg],'coordinates':[g['coordinate'] for g in bg],
          'geometric_crossings':len(be),'modeled_enabled_crossings':len(fs),'weak_strengths_below_0.05':int(np.sum(abs(fs)<.05)),'exact_zero_strengths':int(np.sum(fs==0)),
          'response_real_coefficients':sum(2*np.array(g['response_real']).size for g in bg),'strength_abs_max':float(np.max(abs(fs))) if len(fs) else 0}
    audit={'two_bank_geometry':{'B_coordinates':list(range(21)),'A_coordinates':list(range(26,47)),'gap_coordinate_interval':[20,26],'count':42,
       'claim':'All 42 latent points retained, not two six-note blocks pasted together. Pitch direction is independently hypothesized per bank; only facing edges connect.'},
      'selected_candidate':model['selection']['selected_geometry_candidate'],'orientation_B_A':route['orientation_B_A'],'endpoints':route['endpoints'],'span_string_spacings':span,
      'endpoint_law':'C2 quintic with derivative ±(R-L)*30u²(1-u)²/T, strictly signed in each open half-cycle. Reverses only at endpoints; no independent stop or phase reset at recording gaps.',
      'planned_half_cycles':len(h),'completed_half_cycles_within_audio':int(np.sum(knots[1:]<=meta['duration'])),'final_cycle_truncated_by_audio':bool(knots[-1]>meta['duration']),'final_endpoint_after_audio_s':float(max(0,knots[-1]-meta['duration'])),
      'half_period_s':{'min':float(h.min()),'median':float(np.median(h)),'max':float(h.max()),'assumed_lower':route['assumed_half_period_min_s'],'assumed_upper':route['assumed_half_period_max_s']},
      'half_period_boundary_hits':{'minimum_grid':int(np.sum(np.isclose(h,np.ceil(route['assumed_half_period_min_s']/.01)*.01))),'maximum':int(np.sum(np.isclose(h,route['assumed_half_period_max_s'])))},
      'maximum_speed_string_spacings_s':float(np.max(1.875*span/h)),'maximum_acceleration_string_spacings_s2':float(np.max(10/np.sqrt(3)*span/h**2)),
      'maximum_jerk_string_spacings_s3':float(np.max(60*span/h**3)),
      'adjacent_two_sweep_cycle_frequency_Hz':{'min':float(np.min(1/(h[:-1]+h[1:]))),'median':float(np.median(1/(h[:-1]+h[1:]))),'max':float(np.max(1/(h[:-1]+h[1:])))},
      'numeric_audit':{'interior_speed_sign_violations':bad_speed,'max_outside_endpoint_amount':outside,'position_tolerance':1e-12,'near_endpoint_float_equality_count':eq,'near_endpoint_equality_is_float_rounding':True,'geometric_crossing_coordinate_max_error':crossing_error,'endpoint_max_abs_velocity':float(abs(vv).max()),'endpoint_max_abs_acceleration':float(abs(aa).max())},
      'candidate_crossing_counts':{'all_spatial_strings':len(events),'modeled_enabled':len(active),'unmodeled_strings_assumed_skipped':sum(e['status']=='unmodeled_string_assumed_skipped' for e in events),'recording_gap_disabled':sum(e['status']=='recording_gap_disabled' for e in events),'gap_sound_events':0},
      'banks':bank_info,'degrees_of_freedom':{'physical_shared_response_groups':len(groups),'shared_response_real_coefficients':response_n,'aggregate_initial_state_real_coefficients':init_n,'signed_crossing_strengths':strength_n,'total_acoustic_real_coefficients':response_n+init_n+strength_n,'independent_per_physical_string_scale_gauges':len(groups),'generic_acoustic_dimension_after_scale_gauges':response_n+init_n+strength_n-len(groups),'route_internal_endpoint_time_choices':len(knots)-2,'route_time_grid_s':.01,'independent_event_time_parameters':0,'mode_frequencies_reused_from_input_recording':45,'final_evaluation_gain':1},
      'physical_limits':'No measured full string points, pitch orientation, endpoint reach or 3D contact. Spacings not length-calibrated. Speed50 and half-period2.0 are explicit search assumptions, not proven biological feasibility. The broader span must be crossed, with no interior string or gap jumps. Contacts outside six inherited pitch groups are assumed silent.',
      'silence_handling':route['silence_handling'],'optional_contact_threshold':{'RMS_units':.05,'applied_to_audio':False,'interpretation':'Operational visualization threshold, not measured audibility or proof of real pluck.'}}
    tt,Z,zi,bz=render_modal(model);s=modal_to_audio(meta,tt,Z);reference=P/'shared_raw.npy';err=None
    if reference.exists():
        raw=np.load(reference);err=float(abs(s-raw).max());assert err<1e-10
    init_audio=modal_to_audio(meta,tt,zi);bank_audio={b:modal_to_audio(meta,tt,z) for b,z in bz.items()}
    audit['parameter_roundtrip_max_abs_error']=err;audit['reference_raw_present_for_roundtrip']=reference.exists();audit['initial_state_component_energy_over_total']=float(np.sum(init_audio**2)/np.sum(s**2))
    audit['isolated_component_energy_ratios']={b:float(np.sum(bs**2)/np.sum(s**2)) for b,bs in bank_audio.items()};audit['isolated_component_energy_caveat']='These are component energies, not fractional source attribution; coherent components can cancel or reinforce.'
    audit['bank_interference_energy_over_total']=float((np.sum((bank_audio['B']+bank_audio['A'])**2)-sum(np.sum(z**2) for z in bank_audio.values()))/np.sum(s**2))
    if a.source:
        sr,y=wavfile.read(a.source);y=y.astype(float)/(32768 if y.dtype==np.int16 else 1);audit['metrics_recomputed']=metrics(y,s)
    time=np.arange(0,meta['duration'],.02);ci=np.clip(np.searchsorted(knots,time,side='right')-1,0,len(h)-1)
    frames={'frame_rate_Hz':20,'time':tt[::5].tolist(),'definition':'Model modal envelope magnitudes rendered from parameters; not source FFT, source Z or recorded analysis. Equal-pitch bank responses are independent and add coherently.','families':{}}
    for key,matrix in [('shared',Z),('shared_B',bz['B']),('shared_A',bz['A']),('initial_state',zi)]:frames['families'][key]={'mode_ids':list(range(len(meta['modes']))),'amplitudes':np.round(abs(matrix[::5]),8).tolist()}
    frames['families']['shared']['audio_filename']='v7_two_bank_shared_parameter_render.wav'
    viz={'version':'v7_two_bank_endpoint_sweeps','metadata':meta,'analytic_route':route,'time':time.tolist(),'position':x.tolist(),'velocity':v.tolist(),'acceleration':acc.tolist(),'half_cycle_index':ci.tolist(),'direction':np.where((ci+route['start_endpoint'])%2==0,1,-1).tolist(),'recording_interval':interval_ids(time,meta['active_intervals']).tolist(),'candidate_crossings':events,'modal_amplitude_frames':frames,'weak_strength_threshold_RMS_units':.05,'weak_threshold_changes_main_audio':False,'audit':audit}
    (P/'trajectory_visualization.json').write_text(json.dumps(viz,separators=(',',':')));(P/'audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2),flush=True)

if __name__=='__main__':main()
