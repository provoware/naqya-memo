from __future__ import annotations

import json
from dataclasses import dataclass


_STATUS_BY_CODE = {
    'REVISION_CONFLICT': 409,
    'ASSET_REVISION_CONFLICT': 409,
    'MEMO_NOT_FOUND': 404,
    'TODO_NOT_FOUND': 404,
    'EVENT_NOT_FOUND': 404,
    'ENTITY_NOT_FOUND': 404,
    'NOTE_FILE_NOT_FOUND': 404,
    'REQUEST_HOST_REJECTED': 403,
    'REQUEST_ORIGIN_REJECTED': 403,
    'REQUEST_CONTENT_TYPE_REQUIRED': 415,
    'REQUEST_BODY_TOO_LARGE': 413,
    'UPLOAD_TOO_LARGE': 413,
    'MUTATION_DEGRADED_MODE': 503,
}

_DEFAULT_HINT = 'Bitte Eingabe prüfen und den Schritt danach erneut ausführen.'
_READ_RECOVERY_HINT = 'Bitte die Ansicht neu laden. Wenn der Fehler wiederkehrt, das Tool über SCHNELLSTART.sh neu starten.'
_MUTATION_RECOVERY_HINT = (
    'Bitte zuerst die Ansicht neu laden und prüfen, ob die letzte Änderung bereits übernommen wurde. '
    'Nicht erneut speichern, bevor der aktuelle Stand sichtbar ist. Danach das Tool über SCHNELLSTART.sh neu starten.'
)
_DEGRADED_HINT = (
    'Schreibzugriffe sind vorsorglich gesperrt. Lesen bleibt möglich. '
    'Bitte aktuellen Stand prüfen und das Tool anschließend über SCHNELLSTART.sh sauber neu starten.'
)


@dataclass(frozen=True)
class PublicError:
    code: str
    status: int
    message: str
    recovery_hint: str
    degraded_mode: bool
    activate_mutation_barrier: bool = False

    def payload(self) -> dict:
        return {
            'ok': False,
            'code': self.code,
            'message': self.message,
            'recovery_hint': self.recovery_hint,
            'degraded_mode': self.degraded_mode,
        }


def _exception_code(exc: BaseException) -> str:
    if isinstance(exc, (json.JSONDecodeError, UnicodeDecodeError)):
        return 'REQUEST_JSON_INVALID'
    args = getattr(exc, 'args', None)
    if args:
        return str(args[0])
    return str(exc)


def classify_public_error(
    exc: BaseException,
    messages: dict[str, str],
    requested_status: int | None = None,
    *,
    mutation_context: bool = False,
) -> PublicError:
    """Return a privacy-safe, stable client error contract.

    Only explicitly allow-listed error codes may cross the HTTP boundary.
    Unknown exceptions are always INTERNAL_ERROR. During a mutation an unknown
    exception additionally requests a fail-closed mutation barrier, because the
    caller cannot safely know whether the write committed before the failure.
    """
    code = _exception_code(exc)
    if code in messages:
        status = requested_status if requested_status is not None else _STATUS_BY_CODE.get(code, 400)
        degraded = code == 'MUTATION_DEGRADED_MODE'
        hint = _DEGRADED_HINT if degraded else _DEFAULT_HINT
        return PublicError(code, status, messages[code], hint, degraded, False)

    if mutation_context:
        return PublicError(
            'INTERNAL_ERROR',
            500,
            'Die Aktion konnte nicht sicher abgeschlossen werden. Interne Details bleiben verborgen.',
            _MUTATION_RECOVERY_HINT,
            True,
            True,
        )

    return PublicError(
        'INTERNAL_ERROR',
        500,
        'Ein interner Fehler ist aufgetreten. Interne Details bleiben verborgen.',
        _READ_RECOVERY_HINT,
        False,
        False,
    )
