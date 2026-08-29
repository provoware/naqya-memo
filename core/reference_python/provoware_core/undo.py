from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class UndoEntry:
    label: str
    undo: Callable[[], Any]
    redo: Callable[[], Any]

class UndoRedoJournal:
    """In-memory reference journal.

    Product persistence of the journal is deliberately deferred until V0.4,
    but semantics are proven here.
    """
    def __init__(self, limit: int = 100):
        self.limit = limit
        self._undo: list[UndoEntry] = []
        self._redo: list[UndoEntry] = []

    def record(self, entry: UndoEntry):
        self._undo.append(entry)
        if len(self._undo) > self.limit:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self):
        if not self._undo:
            raise RuntimeError("UNDO_EMPTY")
        entry = self._undo.pop()
        result = entry.undo()
        self._redo.append(entry)
        return result

    def redo(self):
        if not self._redo:
            raise RuntimeError("REDO_EMPTY")
        entry = self._redo.pop()
        result = entry.redo()
        self._undo.append(entry)
        return result

    @property
    def can_undo(self): return bool(self._undo)

    @property
    def can_redo(self): return bool(self._redo)
