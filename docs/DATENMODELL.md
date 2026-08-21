# Datenmodell V1

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

### settings
- key
- value

## Regel

Dokumente, Audio und spätere Transkripte bleiben über stabile UUIDs miteinander verknüpft. Migrationen erhöhen `DB_VERSION` und dürfen bestehende Datensätze nicht stillschweigend verwerfen.
