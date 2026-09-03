# DONOR-TRANSFER-001 · Clean Basisprojekt & Schnellstart

Status: Draft / NO-GO · Infrastrukturtransfer, keine Produktfunktion

## Ausgangslage

- qualifizierte Recovery-Basis: `b2e4220ddb95bf91743d6796a93847e3d06e38f9`
- eingefrorener Donor PR #104: `09836a73885adcdd1400216ad39d3ab2571f6ae7`
- Donor bleibt ausschließlich Hardening-/Infrastruktur-Spender.
- Keine UI-, Produktversions-, ERROR-UX- oder VISUAL-UX-Datei wird aus PR #104 übernommen.

## Übernommener Infrastruktur-Scope

- `SCHNELLSTART.sh`
- `requirements.txt`
- `manifeste/MANIFEST_BASISPROJEKT__STATUS-AKTIV__V1.0.json`
- `tools/build_basisprojekt.py`
- `tools/verify_basisprojekt_artifact.py`
- `tests/release_gate/test_basisprojekt_standard.py`
- minimaler BASIS-EXPORT-Anschluss in `.github/workflows/quality.yml`
- explizite immutable Freigabe von `actions/upload-artifact` auf `ea165f8d65b6e75b540449e92b4886f43607fa02`

## Bewusste Anpassungen an die neue kanonische Lineage

Der Donor wird nicht blind kopiert:

1. `registry/PRODUCT_BASELINE.json` ist Pflichtbestandteil des Basisprojekts.
2. Das erzeugte `BASISPROJEKT_MANIFEST.json` bindet Produktversion, Produktrevision, UI-Vertragsversion, Acceptance-Track/-Revision, erforderlichen Vorfahren-SHA und exakten Quell-HEAD getrennt.
3. Builder und unabhängiger Verifier lehnen Symlinks und Spezialdateien in exportierten Quellpfaden fail-closed ab.
4. Der Verifier berechnet die erwartete Dateiliste selbst aus dem Exportvertrag und vergleicht ZIP-Dateien bytegenau mit dem aktuellen Quellbaum.
5. Ausgabeordner innerhalb exportierter Quellordner werden abgelehnt, um Selbstinklusion zu verhindern.
6. Der ZIP-Dateiname trägt Produktversion und einen SHA-Kurzbezug; der vollständige SHA steht im generierten Manifest und im CI-Artefaktnamen.
7. Quality baut und veröffentlicht das ZIP erst nach allen bestehenden Source-/Security-/Mobile-Gates und nach dem Evidence-Boundary-Schritt.

## Nicht übertragen

Insbesondere nicht aus PR #104 übernommen:

- `ui/**` oder mobile WebAssets
- `app/**` Produktcode
- `registry/VERSION.json`
- ERROR-UX
- VISUAL-UX
- spätere HTTP-/Browser-Hardening-Slices
- sonstige Donor-Produktänderungen

## Abnahmebedingung

DONOR-TRANSFER-001 ist erst qualifiziert, wenn auf exakt demselben neuen Head-SHA:

- Product Lineage Guard: PASS
- Quality: PASS
- Profile Blanco Truthfulness: PASS
- V0.12.2.2 = 13/13
- V0.12.2.3 = 7/7
- V0.12.2.4 = 9/9
- V0.12.2.5 = 14/14
- Basisprojekt-Standard: PASS
- Builder: PASS
- unabhängiger ZIP-Verifier: PASS
- genau ein CI-ZIP-Artefakt vorhanden

Reale Browser-, Mikrofon-, Android- und iPhone-Gates bleiben davon unberührt.
