# 🖥️ **V0.12.2.5 – REAL VIEWPORT UX FIX**
> **Feature-Freeze:** 🔒 aktiv  
> **gezielte Regression + Geometrie:** 🟢 **89/89 PASS**  
> **Offline-Chromium-Geometrie:** 🟢 **8/8 Viewportfälle PASS**  
> **Navigation:** 🟢 normal breit + einklappbar; kein buchstabenweiser Umbruch  
> **Ansicht-Leiste:** 🟢 eigene volle Headerzeile statt gequetschter Statusspalte  
> **Technik:** 🟢 eigener Drawer statt Overlay über dem Arbeitsbereich  
> **Info-Seitenleiste:** 🟢 kompakt, einklappbar, bei 200 % automatisch Drawer  
> **Dashboard:** 🟢 kompakter, weniger Leerraum  
> **150/200 %:** 🟢 eigener High-Magnification-Modus  
> **Mobile:** 🟢 Schnellleiste ohne horizontalen Overflow  
> **Android/iOS-WebAssets:** 🟢 bytegleich zur Referenzoberfläche  
> **echtes Loopback-Browser-E2E:** 🟡 weiterhin auf realem Linux auszuführen  
> **CI-Bootstrap-Main:** `de9f25f…` · GitHub Actions `quality` 🟢 SUCCESS  
> **Main-CI-Backup:** `backup/pre-v0.12.2.5-main-ci-20260829` → `de9f25f…`  
> **PR #56 Source-CI:** 🟢 SUCCESS · bleibt Draft wegen nachfolgendem Viewport-Fix  
> **Release:** 🔴 `NO-GO` · weiterhin **1/7 reale Gates**

### Automatisch geprüfte Ansichten

`1920×1080` · `1600×900` · `1366×768` · `1600×900 @ 150 %` · `1920×1080 @ 200 %` · `1100×800` · `900×760` · `390×844`

Das Offline-Geometriegate rendert **das echte Produktions-HTML und -CSS in Chromium**, benutzt aber absichtlich kein Backend/Netzwerk. Es beweist deshalb Layout/Überlauf, ersetzt jedoch **nicht** das reale Loopback-E2E.

Die erzeugten PNG-Screenshots bleiben im vollständigen ZIP-Snapshot. Im GitHub-Quellbaum werden nur der reproduzierbare Runner und der JSON-Geometriebericht versioniert, damit das Repository schlank bleibt.

---

## 🚀 Ein-Befehl-GitHub-Sync für V0.12.2.5

Nach dem Entpacken im Projektordner genügt:

```bash
./GITHUB_SAFE_SYNC_STARTEN.sh
```

Der Start schreibt **nicht auf `main`**. Er prüft Authentifizierung, bekannte Remote-SHAs, lokale Acceptance, Visual-E2E soweit auf dem Zielrechner möglich, Secrets, SHA-Dateimanifest und Konfliktmarker. Erst danach wird ausschließlich der V0.12.2.5-Reviewbranch aktualisiert und ein Draft-PR angelegt.


# 🧷 GITHUB-BACKUP- UND REVIEW-ZUSTAND

> **Repository:** `provoware/naqya-memo`  
> **Historischer 0.5.1-E7-Backup:** `backup/pre-v0.12.2.3-20260829` → `334dd292…`  
> **Post-PR54-Backup:** `backup/pre-full-tree-v0.12.2.3-20260829` → `a2e4767…`  
> **PR #55:** ✅ **gemergt**  
> **Aktueller GitHub-main:** `a05ea824…` → vollständiger V0.12.2.3-Projektbaum  
> **Pre-V0.12.2.4-Backup:** `backup/pre-v0.12.2.4-20260829` → `a05ea824…`  
> **V0.12.2.4 Review-Branch:** `review/v0.12.2.4-release-ux-20260829` → Basis `a05ea824…`  
> **Remote V0.12.2.3-Baum:** 🟢 vollständig auditiert  
> **Aktueller lokaler Nachfolger:** `0.12.2.4-RELEASE-UX-CONTROL-PLANE`  
> **Release:** 🔴 `NO-GO` · weiterhin **1/7 reale Gates**

### Sicherheitsprinzip

Der vollständige V0.12.2.3-Baum liegt inzwischen auf `main`. Vor V0.12.2.4 wurde dieser Zustand deshalb erneut unverändert auf `backup/pre-v0.12.2.4-20260829` eingefroren. Die neue UX-/Control-Plane-Härtung wird ausschließlich auf einem separaten Review-Branch gespiegelt; kein Force-Push und kein automatischer Main-Push.

---


# 🎯 **V0.12.2.4 – RELEASE UX + GITHUB CONTROL PLANE**
> **Feature-Freeze:** 🔒 aktiv  
> **gezielte Acceptance:** 🟢 **69/69 PASS**  
> **Navigation:** 🟢 getrennte Icon-/Text-Hierarchie  
> **Orientierung:** 🟢 pro Modul konkret statt generischem Techniktext  
> **Hilfen:** 🟢 abhängig vom Hilfemodus entdichtet  
> **Footer:** 🟢 normale Ansicht vereinfacht; Technik aufklappbar  
> **Touch/Fokus:** 🟢 44px + sichtbarer Tastaturfokus  
> **Reduced Motion:** 🟢  
> **GitHub Control Plane:** 🟢 lokal wiederhergestellt  
> **Android/iOS-WebAssets:** 🟢 bytegleich zur Referenzoberfläche  
> **echtes Browser-Visual-Gate:** 🟡 auf realem Linux noch auszuführen  
> **Release:** 🔴 NO-GO · weiterhin **1/7 reale Gates**

**Leitlinie:** weniger Dauerrauschen, klarere Handlungshierarchie, kein Verlust der GitHub-Sicherheitssteuerung.

---


# 🧩 **V0.12.2.3 – UI SIMPLIFICATION & INPUT GUIDANCE**
> **Feature-Freeze:** 🔒 aktiv  
> **Eingabefarbe:** 🟢 neutrales Silber/Graphit – bewusst außerhalb Türkis/Lila/Gelb  
> **Optionale Feldvorgaben:** 🟢 für alle benutzbaren Feldkategorien  
> **Versionsinfo:** 🟢 genau **1 sichtbare Stelle** (`TOOL-INFO`)  
> **Statuskacheln:** 4 → **3**  
> **Dashboardkarten:** 6 → **4**  
> **Darstellung:** 🟢 oben im Dashboard, hervorgehoben  
> **Navigation:** 🟢 Größen-/Überlaufregeln optimiert  
> **Schrift:** 80–200 %  
> **Arbeitsbereich:** 80–200 % mit adaptiver Neuanordnung  
> **gezielte Regression:** 🟢 **57/57 PASS**  
> **echtes Browser-Visual-Gate:** 🟡 BLOCKED im Build-Runner; Zielrechner-Runner enthalten  
> **Release:** 🔴 NO-GO · weiterhin **1/7 reale Gates**

**Leitlinie:** weniger doppelte Information, klare Eingaben, keine Überdeckung durch Zoom.

---

# 🎛️ **V0.12.2.2 – RELEASE UI CONSISTENCY**
> **Feature-Freeze:** 🔒 aktiv  
> **UI-/Service-Zieltests:** 🟢 **53/53 PASS**  
> **Versions-Single-Source:** 🟢  
> **Eingabefeld-Kontrast:** 🟢  
> **linke Navigation:** 🟢 Größen-/Überlaufvertrag gehärtet  
> **Darstellung:** 🟢 oben im Dashboard hervorgehoben  
> **Schrift:** 80–200 % · persistent  
> **Arbeitsbereich:** 80–200 % · adaptive Layout-Tiers  
> **Browser-Screenshot-Gate:** 🟡 BLOCKED im Build-Runner – realer Linux-Lauf erforderlich  
> **Release:** 🔴 NO-GO · unverändert **1/7 reale Gates**

**Wichtig:** Diese Iteration ist ausschließlich Release-UI-Härtung. Keine neue Produktfunktion wurde aufgenommen.

---
# 🛠️ **V0.12.2.1 STARTUP PORT GUARD**
> **Release-Freeze:** 🔒 unverändert  
> **Release-Status:** 🔴 NO-GO / 1 von 7 reale Gates  
> **Behobener Fehler:** `OSError: [Errno 98] Address already in use` beim Linux-Start  
> **Neue Startregel:** belegten Port niemals automatisch beenden; gleiche laufende Instanz wiederverwenden oder sicheren freien Ersatzport wählen.

## Start
```bash
./STARTEN_LINUX.sh
```

Bei belegtem Standardport `8765` wird automatisch ein freier Port bis `8795` gewählt.  
Wer einen Port strikt erzwingen will:
```bash
PROVOWARE_PORT=8765 PROVOWARE_PORT_STRICT=1 ./STARTEN_LINUX.sh
```

Sofortiger Workaround für die ältere V0.12.2:
```bash
PROVOWARE_PORT=8766 ./STARTEN_LINUX.sh
```

---
# 📱 **OI - PROVOWARE - IO · V0.12.2**
## **MOBILE RUNTIME COMPLETION · VARIANTE 2**

> **Strategie:** Multi-Platform V1.0 bleibt das Ziel.  
> **Feature Freeze:** 🔒 AKTIV – Ausnahme ausschließlich für Android/iOS-Parität.  
> **Mobile Runtime Source:** 🟢 **PASS**  
> **Cross-Runtime-Parität Python ↔ Mobile:** 🟢 **PASS**  
> **Desktop-Regressions-Sanity:** 🟢 **78/78 PASS**  
> **Android:** 🟢 Runtime-Quellcode vollständig · 🟡 APK/Device-Evidence offen  
> **iOS:** 🟢 echtes Xcode-App-Target vollständig · 🟡 Build/Signing/iPhone-Evidence offen  
> **Reale Release-Gates:** **1/7 PASS**  
> **V1.0 RC:** 🔴 **NO-GO**

## 🟢 Was Variante 2 jetzt konkret geändert hat

Die früheren Zustände `BUILD_STRUCTURE_ONLY` und `BUILD_CONCEPT_ONLY` sind nicht mehr der aktuelle Entwicklungsstand. Android und iOS besitzen jetzt eine echte Mobile-Laufzeitquelle mit der gemeinsamen Oberfläche, eigener persistenter Mobile-Datenschicht und nativen OS-Bridges.

### Android
`WebView → Mobile API → IndexedDB → NativeBridge → MediaRecorder / AlarmManager / NotificationManager / Share Intent / Dateiauswahl`

### iOS
`WKWebView → Mobile API → IndexedDB → NativeBridge → AVAudioRecorder / UNUserNotificationCenter / UIActivityViewController`

### Mobile-Datenschutz und Profile
- Profilwahl/-anlage beim Start,
- PIN exakt vier Ziffern,
- PBKDF2-SHA256 mit zufälligem Salt,
- kein Klartext-PIN,
- PIN wird pro App-Session erneut verlangt,
- PIN bleibt ausdrücklich **keine Datenverschlüsselung**,
- Daten/Assets/Einstellungen werden profilbezogen getrennt.

### Device-Acceptance bereits vorbereitet
Android und iOS enthalten einen eingebauten Acceptance-Modus. Auf echten Geräten prüft er Memo/Todo/Termin, echte Mikrofonaufnahme, Reminder-Pfad und Persistenz nach Prozess-Neustart. Nur dieser reale Nachweis darf Gate 06/07 auf `PASS` setzen.

## ⚠️ Noch kein Multi-Platform Release

Diese Linux-Laufzeit besitzt weder Android SDK/ADB noch macOS/Xcode. Deshalb wurden **kein APK und kein signiertes iOS-App** als bestanden ausgegeben. Die vollständige vierfache Binär-Asset-Backupredundanz auf Mobile ist umgesetzt und im Mobile-Core-Test mit vier Generationen, SHA-256-Prüfung und Restore nachgewiesen.

## 🚦 Aktueller Release-Gate-Stand

| Gate | Status |
|---|---|
| 8h Soak | 🟡 PRECHECK_PASS |
| Chromium | 🟡 BLOCKED |
| Firefox | 🟡 BLOCKED |
| Linux Mikrofon | 🟡 BLOCKED |
| echter Storage Failure | 🟢 PASS |
| Android APK + Device | 🟡 BLOCKED |
| iPhone X / iOS 16.7.16 | 🟡 BLOCKED |

**Release-Entscheidung: NO-GO.** Die neue Mobile-Source-Schicht beseitigt den Architekturblocker, ersetzt aber keine echten Builds und Geräte-Evidence.

---

# 📦 **V0.12.2 RELEASE-KONSOLIDIERUNG**
> **Status-/Versionsregistry:** 🟢 synchronisiert  
> **Mobile Source Acceptance:** 🟢 PASS  
> **Cross-Runtime-Parität:** 🟢 PASS  
> **4× Binär-Asset-Backup + Restore:** 🟢 PASS  
> **Android Runtime Source Paket:** 🟢 erstellt  
> **iOS Xcode Source Paket:** 🟢 erstellt  
> **Android nativer Build/Device:** 🟡 BLOCKED – Android SDK/ADB fehlt im aktuellen Runner  
> **iOS nativer Build/iPhone X:** 🟡 BLOCKED – macOS/Xcode fehlt im aktuellen Runner  
> **Reale Release-Gates:** **1/7 PASS**  
> **V1.0 RC:** 🔴 **NO-GO**


# 🔒 **OI - PROVOWARE - IO · V0.12.1**
## **RELEASE-GATE CLOSURE · FEATURE FREEZE**

> **Status:** 🔴 **NO-GO**  
> **Echte Release-Gates:** **1/7 PASS**  
> **V0.12 Kernbasis:** 🟢 **89/89 PASS**  
> **V0.12.1 Regression-Sanity:** 🟢 **29/29 PASS**  
> **Geschlossen:** echter Linux Storage-Failure  
> **Offen:** 8h-Soak · Chromium · Firefox · Linux-Mikrofon · Android · iPhone X/iOS 16.7.x  
> **Feature Freeze:** 🔒 AKTIV  
> **V1.0 RC:** **nicht freigegeben**

### Entscheidende Regel
Der Status kann nur durch `tools/release_gate/evaluate_release_gate.py` auf **GO** wechseln, wenn **7/7 Gates exakt `PASS`** melden.

---

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.12.0-RC-HARDENING**

> **V0.12 Hardening Core:** 🟢 PASS  
> **Automatisierte Regression:** 🟢 **89/89**  
> **100k Stress:** 🟢 PASS  
> **Asset-Kill/Recovery:** 🟢 PASS  
> **Full Restore DB+Assets:** 🟢 PASS  
> **Linux Portable E2E:** 🟢 PASS  
> **V1.0 RC / produktionsreif:** 🔴 **NO-GO** – externe Pflicht-Evidence fehlt noch  
> **Nächster Schritt:** offene Release-Gates schließen, keine neuen Features.

## 🚦 Warum noch kein V1.0?
Kern und Hardening sind grün. Offen bleiben 8h+-Soak, echte Chromium/Firefox-A11y-Evidence, Android/iOS-Gerätetests, physische Mikrofonaufnahme sowie native Disk-full/Read-only-Zielsystemtests.

## 📊 V0.12 Messwerte
| Bereich | Ergebnis |
|---|---:|
| Automatische Tests | **89/89 PASS** |
| 100k Insert | **2,202 s** |
| 100k DB-Größe | **~48,1 MiB** |
| Latest-100 Query | **21,12 ms** |
| große Assets | **40 / ~80 MiB** |
| Asset Backup | **40/40 verifiziert** |
| Service Startup | **0,622 s** |
| CI-Soak | **834 Ops / 10,01 s / integrity ok** |

---

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.11.0-NATIVE-MEDIA-PACKAGING**

> **Status:** 🟢 V0.11 FUNKTIONS-/PACKAGING-GATE GRÜN  
> **Audio-Staging/Commit:** 🟢  
> **Linux Aufnahme-Adapter:** 🟢 implementiert · Hardware-Mikrofon-Evidence 🟡 offen  
> **PDF Viewer:** 🟢 lokaler read-only Asset-Viewer  
> **TXT/MD Editor:** 🟢 revisionsgesichert  
> **Asset-Revisionshistorie:** 🟢  
> **Linux Portable:** 🟢 PASS  
> **Android:** 🟡 BUILD_STRUCTURE_ONLY  
> **iOS:** 🟡 BUILD_CONCEPT_ONLY  
> **Regression:** 🟢 43/43 PASS  
> **Nächster Schritt:** V0.12 Release-Candidate-Härtung / GO-NO-GO

**Produktfortschritt: ca. 96 %.**

---

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.10.0-CALENDAR-REMINDER-PLATFORM**

> **Status:** 🟢 V0.10 CORE-GATE GRÜN  
> **Kalender:** 🟢 Tag · Woche · Monat · Jahr  
> **Reminder Engine:** 🟢 Fälligkeit + Dedup  
> **Linux Capability Evidence:** 🟢 NATIVE_RUNTIME_PROBE  
> **Android:** 🟡 CONTRACT_ONLY – kein reales Gerät geprüft  
> **iOS:** 🟡 CONTRACT_ONLY – kein reales Gerät geprüft  
> **Chromium Visual/A11y:** 🟡 BLOCKED  
> **Firefox Visual/A11y:** 🟡 BLOCKED  
> **Regression:** 🟢 35/35 PASS  
> **Nächster Schritt:** V0.11 native Sprachaufnahme + PDF/Dokument-Viewer/-Editor + Packaging

**Produktfortschritt: ca. 91 %.**

---

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.9.0-ASSET-SAFETY**

> **Status:** 🟢 ASSET-SAFETY-GATE GRÜN  
> **Audio/Dokument Asset Intake:** 🟢  
> **Temp→fsync→Hash→Commit:** 🟢  
> **SHA-256 Asset-Manifeste:** 🟢  
> **Quota:** 🟢  
> **Quarantäne:** 🟢  
> **Asset Backup Verify:** 🟢  
> **Persistente Playlist:** 🟢  
> **Native Mikrofon-/PDF-Editor:** 🟡 bewusst noch Adapter-Gate  
> **Nächster Schritt:** V0.10 Kalender Tag/Woche/Jahr + Reminder Acceptance + Accessibility/Platform Gates

**Produktfortschritt: ca. 86 %.**

---
# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.8.0-INTERACTION-CALENDAR-ACCEPTANCE**

> **Status:** 🟢 V0.8 CORE-/INTERACTION-GATE GRÜN  
> **Regression:** 🟢 **58/58 PASS**  
> **Memo/Todo/Termin bearbeiten:** 🟢  
> **Monatskalender:** 🟢  
> **5er-Legende + Tagesfärbung:** 🟢  
> **Papierkorb-Wiederherstellung:** 🟢  
> **Diagnose-Privacy-Vorschau:** 🟢  
> **Chromium Visual Gate:** 🟡 BLOCKED durch `ERR_BLOCKED_BY_ADMINISTRATOR` in dieser Laufzeit  
> **Firefox Visual Gate:** 🟡 BLOCKED, Firefox-Engine hier nicht installiert  
> **Nächster Schritt:** V0.9 Sprachmemo + Dokument/PDF + Audioplayer + Asset-Safety

## 📊 Aktueller Stand

| Bereich | Zustand |
|---|---|
| Memo CRUD + Edit + Trash/Restore | 🟢 |
| Todo CRUD + Edit + Complete + Trash/Restore | 🟢 |
| Kalender Event Edit | 🟢 |
| echter Monatskalender | 🟢 |
| Tagesfarbe per Klick | 🟢 |
| fünf editierbare Kalenderfarben | 🟢 |
| persistentes Undo/Redo | 🟢 |
| Diagnose-TXT mit Privacy-Vorschau | 🟢 |
| direkte SQLite-Zugriffe aus UI | **0** |
| automatisierte Core-/Service-Regression | **58/58 PASS** |

**Produktfortschritt: ca. 80 %.**

---

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.7.0 · SERVICE-UI-BINDING**

> **Status:** 🟢 Memo/Todo/Kalender + Quick-Note an lokale Services angebunden  
> **Start unter Linux:** `STARTEN_LINUX.sh`  
> **Wichtig:** HTML nicht mehr direkt per `file://` öffnen; dadurch fehlte im Screenshot die Service-/CSS-Laufumgebung.  
> **Sicherheitsweg:** UI → localhost API → Domain → Mutation Queue → SQLite  

## 🚀 Schnellstart
1. ZIP entpacken.
2. `STARTEN_LINUX.sh` doppelklicken bzw. ausführen.
3. Browser öffnet `http://127.0.0.1:8765/index.html`.
4. Alle Daten bleiben im lokalen Projektordner `runtime/projektordner/`.

## 🟢 V0.7 neu
- Memo-UI mit sicherem Papierkorb
- Todo-UI mit Termin/Reminder und Abhaken
- Kalender-UI mit 5 Farben
- nächste 10 echte Aufgaben/Termine im Header
- Header-Schnelleingabe → feste TXT-Datei
- Datei öffnen über Standardprogramm
- Teilen über Mailclient, niemals Auto-Versand
- Undo/Redo
- lokale API-E2E-Tests

---
# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.6.0-PRESENTATION-SHELL · RESPONSIVE PRESENTATION SHELL**

> **Status:** 🟢 V0.6 SHELL GATE GRÜN  
> **Presentation-Code:** erstmals vorhanden  
> **Fachlogik in UI:** **0** – verbindlich getrennt  
> **Layouts:** Desktop · Kompakt · Mobil · Extra-klein  
> **Themes:** 4  
> **Schrift:** 80–200 %  
> **Bereichszoom:** 80–150 %  
> **Nächster Schritt:** V0.7 Service-Anbindung Memo/Todo/Kalender

## 🧭 UI-Umfang
**Header-Dashboard → Menü → Schnellstartleiste → leerer Arbeitsbereich → Kontextleiste → Footer/Debug → Mobile Drawer.**

Das visuelle Konzept orientiert sich am vorgegebenen dunklen Neon-Dashboard, bleibt aber ein eigenständiges, responsives System.

## 🛡️ Schutzregel
Schnelleingabe und Fachbuttons schreiben in V0.6 absichtlich **keine Daten**. Erst V0.7 darf sie über die vorhandenen Application/Domain-Services verbinden.

---

## 📚 Frühere Spezifikation
# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.5.0-STARTUP-PROFILE-CAPABILITY · PROFILE / SETTINGS / GUIDED FIRST START**

> **Status:** 🟢 V0.5 STARTUP/CAPABILITY GATE GRÜN  
> **UI-Code:** weiterhin bewusst **0 %**  
> **Daten-Schema:** V2 + geprüfte Migration V1→V2  
> **PIN:** 4-stellig, gesalzen gehasht, ausdrücklich keine Verschlüsselung  
> **Start:** System → Capability → Rechte → Projektordner → Profil/Settings → Checkpoint  
> **Nächster Schritt:** V0.6 responsive Presentation Shell nach Referenzmuster

## 📊 **Stand**
| Bereich | Zustand |
|---|---|
| Profile | 🟢 |
| 4-stelliger PIN | 🟢 |
| PIN-Zugriffsprotokoll | 🟢 |
| 4 persistente Themes | 🟢 Datenvertrag |
| Schrift 80–200 % | 🟢 Datenvertrag |
| Hilfemodus 1/2/3 | 🟢 |
| Projektordner-Preflight | 🟢 |
| Guided First Start | 🟢 |
| Linux Capability Adapter | 🟢 Referenz |
| Android Capability Contract | 🟢 Vertrag / native Evidence später |
| iOS Capability Contract | 🟢 Vertrag / native Evidence später |
| ausgelagerte deutsche Texte | 🟢 |
| finale UI | ⚪ 0 % |

**Produktfortschritt: ca. 57 %.**

---

## 📚 Frühere Versionen und fortgeltende Grundlagen

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.4.0-DOMAINMODULE · MEMO + TODO + KALENDER DOMAIN**

> **Status:** 🟢 DOMAIN GATE GRÜN  
> **UI-Code:** weiterhin bewusst 0 %  
> **Neu:** Memo · Todo · Kalender als echte Domainmodule  
> **Nächster Schritt:** V0.5 Profile + PIN + Einstellungen + Guided First Start + Capability/Berechtigungen

**Produktfortschritt: ca. 46 %.**

---

## Frühere Spezifikation

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.3.0-RECOVERY-ACCEPTANCE · TRANSACTION-KILL & RECOVERY ACCEPTANCE**

> **Status:** 🟢 V0.3 RECOVERY GATE GRÜN  
> **UI-Code:** weiterhin **0 %**  
> **Mutation Queue:** implementiert/geprüft  
> **Projekt-Locking:** implementiert/geprüft  
> **Fresh Restore:** implementiert/geprüft  
> **Kill Acceptance:** echte Subprozess-Kills vor/während/nach Commit  
> **Nächster Schritt:** V0.4 Memo + Todo + Kalender Domainmodule

## 📊 Aktueller Stand
| Bereich | Status |
|---|---|
| Persistenzkern | 🟢 |
| Mutation Queue | 🟢 |
| Projekt-Lock | 🟢 |
| Fresh Restore | 🟢 |
| Kill vor BEGIN | 🟢 |
| Kill nach BEGIN | 🟢 |
| Kill nach Write/vor Commit | 🟢 |
| Kill nach Commit | 🟢 |
| DB locked | 🟢 |
| beschädigte Entity | 🟢 erkannt |
| beschädigtes Backup | 🟢 abgelehnt |
| Undo/Redo-Semantik | 🟢 |
| OS-native Disk-full/Permission-Injection | 🟡 Plattform-Gate |

**Produktfortschritt: ca. 36 %.**

---

## 📚 Frühere Spezifikation und Grundlagen

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.2.0-DATENKERN · DATENKERN & PERSISTENCE CONTRACT**

> **Status:** 🟢 V0.2 DATENKERN-REFERENZ + CONTRACTS GEPRÜFT  
> **UI-Code:** weiterhin bewusst **nicht begonnen**  
> **Kanonische Persistenz:** SQLite + Datei-Assets  
> **Datenmutation:** Revision + Konfliktschutz + Journal + Checksums  
> **Backup:** konsistenter SQLite-Snapshot + SHA-256 + Restore-Öffnung/Integrity-Check  
> **Nächster Gate:** V0.3 Transaction-Kill & Recovery Acceptance

## 📊 **Stand**
| Bereich | Zustand |
|---|---|
| Architektur V0.1 | 🟢 FREIGEGEBEN |
| SQLite Schema V1 | 🟢 IMPLEMENTIERT |
| Referenz-Datenkern | 🟢 IMPLEMENTIERT |
| Revision-/Konfliktschutz | 🟢 GEPRÜFT |
| Soft Delete/Papierkorb-Grundlage | 🟢 GEPRÜFT |
| Atomare Dateioperation | 🟢 GEPRÜFT |
| Backup-Snapshot | 🟢 GEPRÜFT |
| Backup Integrity-Verifikation | 🟢 GEPRÜFT |
| echter Crash-/Kill-Nachweis | 🟡 V0.3 |
| finale Produkt-UI | ⚪ 0 % |

**Produktfortschritt gesamt: ca. 27 %.**

---

## 📚 V0.1-Grundlagen / fortgeltende Spezifikation

# 🟦🟪🟨 **OI - PROVOWARE - IO**
## **Multi-Memo-Modul-Tool 2026 / OI - Naqya - IO**
### **V0.1.0-ARCHITEKTUR · ARCHITEKTUR-/SPEZIFIKATIONSSTAND**

> **Status:** 🟡 ARCHITEKTUR DEFINIERT · UI-CODE NOCH NICHT BEGONNEN  
> **Zielplattformen:** Android · Linux · iPhone/iOS  
> **Prinzip:** Offline-first · modular · laiengeführt · datensicher · reparierbar · barrierearm  
> **Designfarben:** Neon-Türkis · leuchtendes Lila · Knallgelb + davon unabhängige Kontrastfarben  
> **Referenzbild:** Dashboard-Orientierungsmuster aus der Projektvorgabe; kein 1:1-Klon.

---

## 🧭 **Projektstatus auf einen Blick**

| Bereich | Zustand | Fortschritt |
|---|---:|---:|
| Anforderungen | 🟢 weitgehend definiert | 97 % |
| Architektur | 🟢 V0.1 spezifiziert | 100 % |
| Sicherheits-/Datenverträge | 🟢 V0.1 spezifiziert | 100 % |
| Datenmodell | 🟢 V0.1 spezifiziert | 100 % |
| Plattformadapter | 🟢 Schnittstellen geplant | 100 % |
| Gate-State-Machine | 🟢 spezifiziert | 100 % |
| UI-Implementierung | ⚪ bewusst noch nicht begonnen | 0 % |
| Runtime/Backend | ⚪ noch nicht begonnen | 0 % |
| Automatische Tests | 🟡 Architektur definiert | 20 % |
| Release-Pipeline | 🟡 Konzept definiert | 15 % |

**Gesamtfortschritt Produktentwicklung:** **≈ 18 %**  
**Gesamtfortschritt Planungs-/Spezifikationsphase V0.1:** **100 %**

---

## 🎯 **Produktziel**

Ein plattformübergreifendes, extrem einfach bedienbares Organisations- und Memo-Werkzeug für:

- Textmemos und Textdokumente
- Sprachmemos
- Todos mit Termin, Erinnerung, Abhaken und Archiv
- Kalender mit Tages-, Wochen-, Monats- und Jahresansicht
- fünf frei benennbare Kalenderfarben mit persistenter Legende
- Dokument-/PDF-Anzeige und später kontrollierter Bearbeitung
- Audio-Player mit persistenter Playlist
- frei speicherbare Zitate mit zufälliger Dashboard-Anzeige
- Debugging, Diagnose, Recovery und Self-Repair
- Profile mit 4-stelligem PIN als **Zugangsbarriere, nicht Verschlüsselung**
- sichere lokale Projektordner
- Undo/Redo, Papierkorb, Checkpoints und Generationen-Backups
- geführte Startprüfung mit transparenter Vor-/Nachvalidierung

---

## 🛡️ **Unverhandelbare Sicherheitsregeln**

1. **Keine destruktive Aktion ohne Vorprüfung und nachvollziehbare Vorschau.**
2. **Schreibvorgänge sind transaktional:** Temp → Prüfen → fsync/flush → atomarer Commit → Nachprüfung.
3. **Mindestens vier Wiederherstellungsstände:** zwei ältere, aktueller Zustand, zwei nachgelagerte Generationen soweit technisch möglich.
4. **Löschen bedeutet standardmäßig Papierkorb/Archiv – nicht endgültiges Vernichten.**
5. **Externe Ordner benötigen eine ausdrückliche Button-Bestätigung.**
6. **Keine automatische Ausführung importierter Dateien.**
7. **Diagnosedaten werden vor Versand gefiltert und angezeigt.**
8. **E-Mail-Teilen erfolgt nur nach expliziter Nutzerfreigabe.**
9. **Mehrfachinstanzen und parallele Schreibzugriffe werden gesperrt oder serialisiert.**
10. **Jede kritische Mutation besitzt PRE-, ACTION-, POST-, ROLLBACK- und EVIDENCE-Regeln.**

---

## 🏗️ **Architekturprinzip**

```text
UI / Dashboard / Bedienlogik
        │
Application Services / Use Cases
        │
Mutation Queue + Validation Contracts
        │
Domain-Kern / Datenmodelle
        │
Repositories / Persistence
        │
Platform Adapter
 ┌────────────┬────────────┬────────────┐
 Android      Linux        iOS
```

Die Plattformen teilen **Datenmodell, Kernlogik, Verträge, Testlogik und Designregeln**.  
Dateizugriff, Berechtigungen, Teilen, Benachrichtigungen, Hintergrundbetrieb und Standardeditor werden über getrennte Adapter gelöst.

---

## 🧩 **Geplante Kernmodule**

**Memo · Sprache · Todo · Kalender · Dokumente · PDF · Audio · Suche · Profil · Einstellungen · Hilfe · Backup/Recovery · Diagnose · Export/Import · Statistiken · Belohnungssystem · Entwicklerbereich · Self-Repair**

---

## 📁 **Dokumente in diesem Paket**

- `README.md` – Einstieg, Status und Regeln
- `TODO.md` – priorisierte, abhakbare Roadmap
- `AGENTS.md` – Agenten-/Entwicklungsregeln
- `BRAIN.md` – belastbare technische Erfahrungen und Fehlerwissen
- `GPT_TAGE_UND_WISSENSBUCH.md` – internes Arbeits-/Wissensbuch für GPT, max. 2000 Zeilen
- `CHANGELOG.md` – nachvollziehbare Änderungen
- `UPGRADE_POTENZIAL.md` – Verbesserungs-/Erweiterungspool
- `docs/ARCHITEKTUR__STATUS-FREIGEGEBEN__V0.1.md`
- `docs/SICHERHEIT_UND_DATENVERTRAEGE__STATUS-FREIGEGEBEN__V0.1.md`
- `docs/DATENMODELL__STATUS-FREIGEGEBEN__V0.1.md`
- `docs/GATE_STATE_MACHINE__STATUS-FREIGEGEBEN__V0.1.md`
- `docs/ENTWICKLUNGSDOKUMENTATION__STATUS-AKTIV__V0.1.md`
- `docs/PLATTFORM_ADAPTER__STATUS-ENTWURF__V0.1.md`
- `manifeste/*`
- `registry/PROJECT_STATUS.json`
- `registry/VERSION.json`
- `registry/FILE_STATUS_REGISTRY.json`

---

## 🚦 **Nächster freigegebener Schritt**

**V0.2 – Datenkern & Persistence Contract – ohne finale UI.**

Reihenfolge:

**Schema → Repositories → atomare Dateioperationen → Backup/Restore → Mutation Queue → Crash-/Kill-Tests → Evidence → erst danach UI-Anbindung.**

---

## ⚡ **Sofort-Hinweise**

- iOS kann keine beliebige Desktop-Self-Repair-Logik ausführen; deshalb Adapterprinzip.
- PIN ≠ Verschlüsselung.
- Hintergrund-Erinnerungen müssen pro Plattform separat akzeptanzgetestet werden.
- Ein Backup gilt erst als funktionsfähig, wenn ein automatischer Restore-Test bestanden wurde.
- README, TODO, CHANGELOG, BRAIN und PROJECT_STATUS werden bei jeder relevanten Iteration synchron aktualisiert.
