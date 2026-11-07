"""Allow-list export: parameters, derived renders and code, never input audio or analysis."""
from pathlib import Path
import argparse,json,hashlib,shutil,zipfile
CANDIDATES=['full_Bup_Aup','full_Bup_Adown','full_Bdown_Aup','full_Bdown_Adown','partial_B1_A6','partial_B2_A6']
FILES=['README.md','requirements.txt','sweep_math.py','two_bank_model.py','fit_two_bank_sweeps.py','render_two_bank.py','audit_two_banks.py','test_two_banks.py','export_public.py',
 'shared_parameters.json','metrics.json','candidate_metrics.json','audit.json','geometry_evidence.json','trajectory_visualization.json',
 'v7_two_bank_shared_parameter_render.wav','v7_two_bank_shared_parameter_render.audit.json','tests.log','public_render_verification.json']+[n+'/parameters.json' for n in CANDIDATES]

def sanitize(value):
 if isinstance(value,list):return [sanitize(v) for v in value]
 if isinstance(value,dict):
  out={}
  for key,v in value.items():
   if key.lower() in {'source_sha256','power','basepower'}:continue
   out[key]=[{k:m[k] for k in ['j','h','f']} for m in v] if key=='modes' and isinstance(v,list) else sanitize(v)
  return out
 return value

def main():
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent);args=p.parse_args();root=args.directory;dest=root/'public_export';dest.mkdir(exist_ok=True)
 manifest={'title':'v7 two-bank endpoint sweep reproducibility assets','original_audio_included':False,'source_analysis_arrays_included':False,'model_families':'Independent bank x string shared responses only','files':[]}
 for name in FILES:
  source=root/name;target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
  if source.suffix=='.json':target.write_text(json.dumps(sanitize(json.loads(source.read_text())),separators=(',',':')))
  else:shutil.copyfile(source,target)
  data=target.read_bytes();manifest['files'].append({'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
 with zipfile.ZipFile(root/'v7_two_bank_endpoint_sweeps.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in FILES+['manifest.json']:z.write(dest/name,arcname='v7_two_bank_endpoint_sweeps/'+name)
 print(json.dumps({'files':len(FILES)+1,'zip':str(root/'v7_two_bank_endpoint_sweeps.zip'),'original_included':False},indent=2))

if __name__=='__main__':main()
