from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'manifeste'/'MANIFEST_BASISPROJEKT__STATUS-AKTIV__V1.0.json'
def main():
    d=json.loads(M.read_text(encoding='utf-8'))
    assert d['schema_version']==1 and d['status']=='AKTIV'
    assert d['artifact_policy']['output']=='vollstaendiges_basisprojekt'
    assert d['artifact_policy']['include_logs'] is False and d['artifact_policy']['include_runtime_data'] is False
    for rel in ('SCHNELLSTART.sh','requirements.txt','tools/build_basisprojekt.py'): assert (ROOT/rel).is_file(),rel
    s=(ROOT/'SCHNELLSTART.sh').read_text(encoding='utf-8')
    assert 'STARTEN_LINUX.sh' in s and 'Python 3.12.x' in s and 'requirements.txt' in s and 'exec ' in s
    active=[x.strip() for x in (ROOT/'requirements.txt').read_text(encoding='utf-8').splitlines() if x.strip() and not x.lstrip().startswith('#')]
    assert all('==' in x for x in active)
    ex=set(d['exclude_globs'])
    for req in ('runtime/**','tests/**','ci/**','.github/**','**/*.log','RUN_*'): assert req in ex,req
    p=subprocess.run([sys.executable,'-S',str(ROOT/'tools'/'build_basisprojekt.py'),'--check'],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode==0,p.stderr or p.stdout
    assert 'PASS basis project contract' in p.stdout
    print('PASS basis project standard')
if __name__=='__main__': main()
