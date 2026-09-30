from pathlib import Path
import json, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'manifeste'/'MANIFEST_BASISPROJEKT__STATUS-AKTIV__V1.0.json'
W=ROOT/'.github'/'workflows'/'quality.yml'

def git_head():
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def main():
    d=json.loads(M.read_text(encoding='utf-8'))
    assert d['schema_version']==1 and d['status']=='AKTIV'
    assert d['artifact_policy']['output']=='vollstaendiges_basisprojekt'
    assert d['artifact_policy']['include_logs'] is False and d['artifact_policy']['include_runtime_data'] is False
    assert d['artifact_policy']['generated_manifest_name']=='BASISPROJEKT_MANIFEST.json'
    ci=d['ci_export']
    assert ci['enabled'] is True
    assert ci['publish_after_all_quality_gates'] is True
    assert ci['exactly_one_zip'] is True
    assert ci['require_source_git_head_match'] is True
    assert ci['upload_action_sha']=='ea165f8d65b6e75b540449e92b4886f43607fa02'
    assert ci['source_sha_policy']=='pull_request_head_or_push_sha'
    for rel in ('SCHNELLSTART.sh','requirements.txt','tools/build_basisprojekt.py','tools/verify_basisprojekt_artifact.py'):
        assert (ROOT/rel).is_file(),rel
    s=(ROOT/'SCHNELLSTART.sh').read_text(encoding='utf-8')
    assert 'STARTEN_LINUX.sh' in s and 'Python 3.12.x' in s and 'requirements.txt' in s and 'exec ' in s
    active=[x.strip() for x in (ROOT/'requirements.txt').read_text(encoding='utf-8').splitlines() if x.strip() and not x.lstrip().startswith('#')]
    assert all('==' in x for x in active)
    ex=set(d['exclude_globs'])
    for req in ('runtime/**','tests/**','ci/**','.github/**','**/*.log','RUN_*'):
        assert req in ex,req

    workflow=W.read_text(encoding='utf-8')
    assert 'Build and independently verify basis project' in workflow
    assert 'Publish verified basis project' in workflow
    assert 'actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02' in workflow
    assert 'if-no-files-found: error' in workflow
    assert 'PROVOWARE_Naqya-Memo_BASISPROJEKT_' in workflow
    assert 'SOURCE_SHA: ${{ github.event.pull_request.head.sha || github.sha }}' in workflow
    assert 'ref: ${{ env.SOURCE_SHA }}' in workflow
    assert '--expected-head "$SOURCE_SHA"' in workflow
    assert 'name: PROVOWARE-Naqya-Memo-Basisprojekt-${{ env.SOURCE_SHA }}' in workflow
    assert '--expected-head "$GITHUB_SHA"' not in workflow
    assert workflow.index('Evidence boundary') < workflow.index('Build and independently verify basis project') < workflow.index('Publish verified basis project')

    p=subprocess.run([sys.executable,'-S',str(ROOT/'tools'/'build_basisprojekt.py'),'--check'],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode==0,p.stderr or p.stdout
    assert 'PASS basis project contract' in p.stdout

    with tempfile.TemporaryDirectory(prefix='naqya-basis-contract-') as td:
        outdir=Path(td)
        build=subprocess.run([sys.executable,'-S',str(ROOT/'tools'/'build_basisprojekt.py'),'--output-dir',str(outdir)],cwd=ROOT,text=True,capture_output=True)
        assert build.returncode==0,build.stderr or build.stdout
        zips=sorted(outdir.glob('PROVOWARE_Naqya-Memo_BASISPROJEKT_*.zip'))
        assert len(zips)==1,zips
        verify=subprocess.run(
            [sys.executable,'-S',str(ROOT/'tools'/'verify_basisprojekt_artifact.py'),str(zips[0]),'--expected-head',git_head()],
            cwd=ROOT,text=True,capture_output=True,
        )
        assert verify.returncode==0,verify.stderr or verify.stdout
        assert 'PASS verified basis project' in verify.stdout

    print('PASS basis project standard + CI export contract')

if __name__=='__main__':
    main()
