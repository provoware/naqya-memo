from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "app" / "server.py"
INDEX = ROOT / "ui" / "reference_web" / "index.html"
APP_JS = ROOT / "ui" / "reference_web" / "app.js"


def _frontend_claims_blanco() -> bool:
    html = INDEX.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")

    html_claim = re.search(
        r'<[^>]+id=["\']profileName["\'][^>]*>\s*Blanco\s*</[^>]+>',
        html,
        flags=re.IGNORECASE,
    )
    js_claim = re.search(
        r'profileName.{0,120}(?:textContent|innerText|innerHTML)\s*=\s*["\']Blanco["\']',
        js,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return bool(html_claim or js_claim)


def _backend_silently_activates_profile() -> bool:
    server = SERVER.read_text(encoding="utf-8")
    first_active_fallback = (
        "SELECT id,display_name FROM profiles WHERE status='ACTIVE' "
        "ORDER BY created_at LIMIT 1"
    ) in server
    implicit_standard_profile = "profile_service.create('Standardprofil', '0000')" in server
    return first_active_fallback or implicit_standard_profile


def test_ui_never_claims_blanco_while_backend_activates_real_profile() -> None:
    """Release gate: visible profile state must never contradict runtime ownership."""
    assert not (
        _frontend_claims_blanco() and _backend_silently_activates_profile()
    ), (
        "PROFILE_BLanco_TRUTHFULNESS_VIOLATION: Die UI behauptet 'Blanco', während "
        "app/server.py noch automatisch ein aktives/Standardprofil auswählt. Erst den "
        "Runtime-Blanco-Vertrag umsetzen; danach darf die Oberfläche 'Blanco' anzeigen."
    )
