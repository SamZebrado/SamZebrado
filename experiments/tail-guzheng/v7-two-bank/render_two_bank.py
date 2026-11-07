"""Parameter-only renderer: never loads source recording or source analysis."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import argparse,json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from two_bank_model import render_modal,modal_to_audio


def main():
    p=argparse.ArgumentParser();p.add_argument('--parameters',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();model=json.loads(a.parameters.read_text());t,Z,initial,banks=render_modal(model);s=modal_to_audio(model['metadata'],t,Z);gain=model['evaluation']['gain'];out=s*gain
    wavfile.write(a.out,model['metadata']['sample_rate'],np.int16(np.clip(out,-1,1)*32767))
    audit={'parameters_only':True,'samples':len(s),'sample_rate':model['metadata']['sample_rate'],'gain':gain,'unclipped_peak':float(abs(out).max()),'clipped_samples':int(np.sum(abs(out)>1))}
    a.out.with_suffix('.audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit),flush=True)

if __name__=='__main__':main()
