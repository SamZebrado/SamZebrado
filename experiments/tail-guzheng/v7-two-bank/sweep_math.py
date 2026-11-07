"""Reusable C2 endpoint-sweep math, causal atoms and modal synthesis.

The spatial units and string layout are explicitly hypothetical. This is an
in-sample acoustic explanation, not video motion recovery or an authenticity test.
"""
import numpy as np
from scipy.optimize import brentq


def smoothstep(u):
    # Symmetry avoids cancellation near u=1; sub-ULP endpoint distances
    # may still round to an endpoint, which is not a mathematical plateau.
    u=np.asarray(u);w=1-u
    return np.where(u<=.5,u**3*(10+u*(-15+6*u)),1-w**3*(10+w*(-15+6*w)))


def inverse_smoothstep(y):
    return brentq(lambda u: smoothstep(u)-y, 0., 1.)


def trajectory(route, times):
    """C2 across knots, with strictly positive speed magnitude inside each sweep."""
    t=np.asarray(times); knots=np.asarray(route['endpoint_times']); lo,hi=route['endpoints']
    k=np.clip(np.searchsorted(knots,t,side='right')-1,0,len(knots)-2)
    h=knots[k+1]-knots[k]; u=np.clip((t-knots[k])/h,0,1)
    up=(k+route['start_endpoint'])%2==0; direction=np.where(up,1.,-1.)
    x=lo+(hi-lo)*np.where(up,smoothstep(u),1-smoothstep(u))
    v=direction*(hi-lo)*30*u*u*(1-u)**2/h
    a=direction*(hi-lo)*60*u*(1-u)*(1-2*u)/h**2
    return x,v,a


def interval_ids(times, intervals):
    labels=np.full(len(times),-1,int)
    for k,(a,b) in enumerate(intervals): labels[(times>=a)&(times<b)]=k
    return labels


def response_atoms(t,events,poles,intervals):
    et=np.array([e['time'] for e in events]); u=t[:,None]-et[None,:]
    # Contact ringing is reset at each observed recording silence, rather than
    # pretending there is a measured physical tail position or acoustic state there.
    lab=interval_ids(t,intervals); elab=np.array([e['recorded_interval'] for e in events])
    valid=(u>=0)&(lab[:,None]==elab[None,:])&(lab[:,None]>=0)
    u=np.maximum(u,0)
    return np.stack([np.where(valid,-np.expm1(-u/.004)*np.exp((-1/tau+2j*np.pi*off)*u),0)
                     for tau,off in poles])


def initial_atoms(t,intervals):
    I=np.zeros((len(t),len(intervals)),complex)
    for k,(a,b) in enumerate(intervals):
        ix=(t>=a)&(t<b);I[ix,k]=np.exp(-(t[ix]-a)/1.5)
    return I


def modal_to_audio(meta,t,Z):
    sr=meta['sample_rate'];ts=np.arange(meta['samples'])/sr;out=np.zeros(len(ts))
    for mi,m in enumerate(meta['modes']):
        z=np.interp(ts,t,Z[:,mi].real)+1j*np.interp(ts,t,Z[:,mi].imag)
        out+=np.real(z*np.exp(2j*np.pi*m['f']*ts))
    out[interval_ids(ts,meta['active_intervals'])<0]=0
    return out


def metrics(y,s):
    gain=float(np.dot(y,s)/np.dot(s,s));error=y-gain*s
    ratio=float(np.dot(error,error)/np.dot(y,y))
    return {'gain':gain,'waveform_NRMSE':float(np.sqrt(ratio)),
            'correlation':float(np.corrcoef(y,s)[0,1]),'snr_db':float(-10*np.log10(ratio)),
            'residual_energy_fraction':ratio}
