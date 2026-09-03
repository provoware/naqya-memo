#!/usr/bin/env python3
from __future__ import annotations
import argparse, fnmatch, hashlib, json, zipfile
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'manifeste'/'MANIFEST_BASISPROJEKT__STATUS-AKTIV__V1.0.json'

class VerifyError(RuntimeError):
    pass

def load_contract():
    try:
        data=json.loads(CONTRACT.read_text(encoding='utf-8'))
    except Exception as exc:
        raise VerifyError(f'Basisprojekt-Vertrag ist nicht lesbar: {exc}') from exc
    if data.get('schema_version')!=1 or data.get('status')!='AKTIV':
        raise VerifyError('Basisprojekt-Vertrag ist nicht aktiv oder besitzt ein unbekanntes Schema.')
    return data

def safe_member(name):
    p=PurePosixPath(name)
    return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name

def excluded(name,patterns):
    posix=PurePosixPath(name).as_posix()
    return any(fnmatch.fnmatch(posix,p) for p in patterns)

def verify(zip_path,expected_head):
    contract=load_contract()
    if not zip_path.is_file():
        raise VerifyError(f'ZIP fehlt: {zip_path}')
    with zipfile.ZipFile(zip_path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):
            raise VerifyError('ZIP enthält doppelte Pfade.')
        if not all(safe_member(name) for name in names):
            raise VerifyError('ZIP enthält unsichere oder absolute Pfade.')
        manifest_name=contract['artifact_policy']['generated_manifest_name']
        if manifest_name not in names:
            raise VerifyError(f'{manifest_name} fehlt im ZIP.')
        try:
            manifest=json.loads(z.read(manifest_name).decode('utf-8'))
        except Exception as exc:
            raise VerifyError(f'Generiertes Manifest ist ungültig: {exc}') from exc
        if manifest.get('schema_version')!=1:
            raise VerifyError('Generiertes Manifest besitzt kein unterstütztes Schema.')
        if manifest.get('artifact_type')!='vollstaendiges_basisprojekt':
            raise VerifyError('Falscher Artefakttyp.')
        if manifest.get('project')!=contract.get('project'):
            raise VerifyError('Projektkennung stimmt nicht.')
        source_head=str(manifest.get('source_git_head') or '')
        if not source_head or source_head=='UNKNOWN':
            raise VerifyError('source_git_head fehlt oder ist UNKNOWN.')
        if expected_head and source_head!=expected_head:
            raise VerifyError(f'SHA-Abweichung: Manifest {source_head}, erwartet {expected_head}.')
        rows=manifest.get('files')
        if not isinstance(rows,list) or manifest.get('file_count')!=len(rows):
            raise VerifyError('file_count und Dateiliste stimmen nicht überein.')
        indexed={}
        for row in rows:
            if not isinstance(row,dict):
                raise VerifyError('Ungültiger Manifest-Dateieintrag.')
            rel=str(row.get('path') or '')
            if not safe_member(rel) or rel==manifest_name or rel in indexed:
                raise VerifyError(f'Ungültiger oder doppelter Manifestpfad: {rel!r}')
            indexed[rel]=row
        if set(names)!=(set(indexed)|{manifest_name}):
            raise VerifyError('ZIP-Dateiliste und Manifest-Dateiliste sind nicht identisch.')
        patterns=list(contract.get('exclude_globs') or [])
        for rel,row in indexed.items():
            if excluded(rel,patterns):
                raise VerifyError(f'Ausgeschlossene Datei im Basisprojekt: {rel}')
            data=z.read(rel)
            if len(data)!=row.get('size'):
                raise VerifyError(f'Größenabweichung: {rel}')
            digest=hashlib.sha256(data).hexdigest()
            if digest!=row.get('sha256'):
                raise VerifyError(f'SHA-256-Abweichung: {rel}')
    return manifest

def main():
    ap=argparse.ArgumentParser(description='Verifiziert ein vollständiges PROVOWARE-Basisprojekt unabhängig vom Builder.')
    ap.add_argument('zip_path',type=Path)
    ap.add_argument('--expected-head',default='')
    args=ap.parse_args()
    try:
        manifest=verify(args.zip_path.resolve(),args.expected_head.strip())
        print(f"PASS verified basis project sha={manifest['source_git_head']} files={manifest['file_count']}")
        return 0
    except (VerifyError, zipfile.BadZipFile) as exc:
        print(f'FEHLER BASISPROJEKT-ARTEFAKT: {exc}',file=__import__('sys').stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
