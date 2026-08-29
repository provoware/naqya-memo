# 🚦 GO / NO-GO – V0.12

## V0.12 Hardening Core
**🟢 PASS** – 89/89 automatisierte Kern-/Hardening-Tests.

## V1.0 Release Candidate / produktionsreif
# 🔴 NO-GO

Nicht weil der Kern rot ist, sondern weil zwingende externe Evidence noch fehlt:

1. 8h+ Langzeit-/Endurance-Test
2. Chromium Visual/A11y Gate in uneingeschränktem Runner
3. Firefox Visual/A11y Gate
4. Android echtes Gerät / Build / Permissions / Reminder / Mikrofon
5. iOS echtes Gerät / Xcode Build / Permissions / Reminder / Mikrofon
6. physische Linux-Mikrofonaufnahme
7. native Disk-full-/Read-only-Tests auf Zielsystemen

**Freigaberegel:** Erst wenn alle sieben Punkte echte Evidence besitzen, darf `V1.0 RC` gesetzt werden.
