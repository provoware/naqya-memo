# Lokale Whisper-Modelle

Dieses Verzeichnis ist für optionale, mit einem Desktop-Release gebündelte `whisper.cpp`-Modelle vorgesehen.

Empfohlene Dateinamen:

- `ggml-tiny.bin` – Profil **Schnell**
- `ggml-base.bin` – Profil **Ausgewogen**
- `ggml-small.bin` – Profil **Genau**
- `ggml-medium.bin` – Profil **Maximum**

Modelldateien werden bewusst nicht in Git eingecheckt. Ein Release-Build kann ein lokal vorhandenes Modell in dieses Verzeichnis legen. NAQYA sucht zusätzlich im persistenten App-Datenverzeichnis `models/` und bevorzugt dort installierte Modelle.
