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


def test_initial_profile_status_is_informative_and_accessible() -> None:
    """The pre-API state must explain itself and announce the resolved profile accessibly."""
    html = INDEX.read_text(encoding="utf-8")
    match = re.search(
        r'<dd\s+id=["\']profileName["\'][^>]*>(.*?)</dd>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    assert match, "PROFILE_STATUS_MISSING: Das sichtbare Profilstatus-Element fehlt."

    element = match.group(0)
    text = re.sub(r"<[^>]+>", "", match.group(1)).strip().lower()
    assert "wird geprüft" in text, (
        "PROFILE_STATUS_AMBIGUOUS: Vor /api/state muss der Nutzer erkennen können, "
        "dass der Profilstatus noch geprüft wird."
    )
    assert re.search(r'role=["\']status["\']', element, flags=re.IGNORECASE), (
        "PROFILE_STATUS_A11Y_ROLE_MISSING: Profilstatus benötigt role='status'."
    )
    assert re.search(r'aria-live=["\']polite["\']', element, flags=re.IGNORECASE), (
        "PROFILE_STATUS_A11Y_LIVE_MISSING: Profilwechsel muss höflich angekündigt werden."
    )
    assert re.search(r'aria-atomic=["\']true["\']', element, flags=re.IGNORECASE), (
        "PROFILE_STATUS_A11Y_ATOMIC_MISSING: Der Profilstatus muss vollständig angekündigt werden."
    )
