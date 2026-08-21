# Datenmodell V2

## Stores

### entries
- id: UUID
- type: note | appointment | deadline | task | text | document | audio | dictation | chronology
- title
- text
- date
- createdAt
- updatedAt
- priority
- status
- projectId
- category
- tags[]
- fileIds[]
- audioSessionId
- deleted
- system
- meta

### projects
- id
- name
- description
- status
- createdAt

### files
- id
- name
- type
- size
- blob
- createdAt
- sourceSessionId
- recovered

### settings
- key
- value

### audioSessions
- id
- kind: audio | dictation
- status: recording | stopping | finalized | recovered | recoverable | empty
- createdAt
- updatedAt
- mimeType
- segmentMs
- segments
- transcriptDraft
- entryId
- fileId
- bytes
- error

### audioSegments
- id: `sessionId:sequenz`
- sessionId
- seq
- createdAt
- size
- type
- blob

Indizes:
- sessionId
- createdAt

### models
- id
- name
- type
- size
- sha256
- createdAt
- status
- blob

## Migration V1 → V2

`DB_VERSION` steigt von 1 auf 2. Bestehende Stores werden nicht gelöscht. Neu hinzu kommen:

- `audioSessions`
- `audioSegments`
- `models`

Die Migration ist additiv und darf vorhandene 0.1-Daten nicht verändern.

## Audio-Integrität

Während einer Aufnahme ist `audioSegments` die persistente Recovery-Quelle. Erst beim normalen Abschluss oder bei Recovery entsteht die dauerhafte Datei im `files`-Store.

Nach erfolgreicher Finalisierung werden temporäre Segmente entfernt und die Sitzung bleibt als technischer Nachweis mit Status erhalten.

## Backup

Backup-Schema 2 serialisiert Nutzdateien mit Base64 und optionalem SHA-256. Sprachmodell-Binärdaten sind bewusst nicht Bestandteil des normalen Nutzbackups, da sie wiederbeschafft oder separat importiert werden können.

## Grundregel

Dokumente, Audio, Transkripte und Projekte bleiben über stabile UUIDs miteinander verknüpft. Datenbankmigrationen erhöhen `DB_VERSION` und dürfen bestehende Datensätze niemals stillschweigend verwerfen.
