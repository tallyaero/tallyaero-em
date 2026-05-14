# Building TallyAero EM Diagram

Phase 6 deliverable. This document covers building a desktop bundle from
source. The signing/notarization steps require external certificates we
don't include in the repo.

---

## Quick build (unsigned, local development)

```bash
make install-build    # one-time: installs PyInstaller into ./venv
make build            # produces dist/TallyAero EM/ + dist/TallyAero EM.app
```

Single-step from scratch:

```bash
venv/bin/python -m pip install pyinstaller
venv/bin/python -m PyInstaller tallyaero_em.spec --noconfirm --clean
open "dist/TallyAero EM.app"        # macOS
# Windows: double-click dist/TallyAero EM/TallyAero EM.exe
# Linux:   ./dist/TallyAero\ EM/TallyAero\ EM
```

First launch picks a free localhost port, starts the Dash server in a
background thread, waits for it to respond, then opens the user's default
browser to that URL. The launcher (`launcher.py`) survives until the user
quits via the dock/tray.

Expected bundle size on Apple Silicon: **~385 MB** unsigned. Breakdown
measured 2026-05-14 (after the `pandas` exclude):

| Item | Size | Notes |
|---|---|---|
| `kaleido/` (bundled Chromium) | 232 MB | needed for PDF/PNG export via `plotly.io.write_image` |
| `dash/` | 29 MB | core framework + vendored JS |
| `airports/` | 18 MB | 49,128-airport JSON ships in the bundle |
| `plotly/` | 9 MB | charting library |
| `numpy/` | 7 MB | |
| `python3.11/` runtime | 7 MB | |
| `PIL/` | 5 MB | indirect kaleido dependency |
| everything else | ~75 MB | dash-bootstrap, pydantic_core, deps, our own code |

The plan target was **< 250 MB**. We're 50 % over it because of kaleido's
bundled Chromium. To hit the budget, rewrite `callbacks/export.py` to use
client-side `Plotly.toImage()` instead of `plotly.io.write_image()`, then
drop `kaleido` from `hiddenimports` and add it to `excludes`. That trims
the bundle to ~150 MB but loses the server-side rendering of complex
multi-trace exports (the client-side path is good enough for most cases).
Tracked as a Phase 6 follow-up — not blocking the unsigned-ship.

---

## What's in the spec

`tallyaero_em.spec` declares:

- **Entry point:** `launcher.py` (NOT `app.py` — the launcher wraps the
  Dash server so the .app behaves like a real desktop app).
- **Bundled data:** `aircraft_data/` (110 JSONs), `airports/airports.json`
  (49,128 airports), `assets/` (CSS/JS), `VERSION`, `LICENSE`,
  `PHYSICS_AUDIT_PLAN.md`. All available via `_MEIPASS` at runtime.
- **Hidden imports:** Dash, Plotly, Kaleido, dash-bootstrap, NumPy, Pandas,
  Pydantic, Flask, Werkzeug, plus our own packages (`core`, `callbacks`,
  `layouts`, `components`, `services`).
- **Exclusions:** matplotlib, scipy, tkinter, PyQt/PySide, IPython,
  notebook — trims ~80 MB of weight.
- **macOS:** wraps the bundle in a `.app` via `BUNDLE()`, declares
  `LSMinimumSystemVersion = 11.0`, `NSHighResolutionCapable = True`.

---

## What's NOT in this push (Phase 6 follow-ups)

Signing, notarization, installers, auto-update, and CI/CD are all blocked
on resources the repo doesn't carry:

### 1. macOS code signing + notarization

Requires:
- Apple Developer ID Application certificate ($99/yr) in the system Keychain
- `xcrun notarytool` credentials (App Store Connect app-specific password)

Steps once the cert is in place:

```bash
# Sign the .app bundle
codesign --deep --options runtime \
  --sign "Developer ID Application: <Your Name> (<TeamID>)" \
  "dist/TallyAero EM.app"

# Notarize
ditto -c -k --keepParent "dist/TallyAero EM.app" /tmp/TallyAero.zip
xcrun notarytool submit /tmp/TallyAero.zip \
  --keychain-profile "tallyaero-notary" \
  --wait

# Staple the ticket so Gatekeeper doesn't need a network call to verify
xcrun stapler staple "dist/TallyAero EM.app"
```

Without these, macOS users will see "TallyAero EM cannot be opened because
the developer cannot be verified" on first run.

### 2. Windows code signing

Requires an OV (Organization Validation) code-signing certificate from
DigiCert, Sectigo, etc. (~$200–400/yr). Without it Windows SmartScreen
shows "Windows protected your PC" — most users will not click through.

```powershell
signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 ^
  /a "dist\TallyAero EM\TallyAero EM.exe"
```

### 3. Installers

- **macOS `.dmg`:** `pip install dmgbuild; dmgbuild -s installer/macos/dmgbuild.py "TallyAero EM" "TallyAero EM.dmg"`
- **Windows installer:** Inno Setup or NSIS. The repo has no `.iss` file yet — write one once Windows signing is in place.
- **Linux:** `.AppImage` via `appimagetool`; `.deb` via `fpm`.

### 4. Auto-update banner

On launch, fetch `https://api.github.com/repos/tallyaero/tallyaero-em/releases/latest`
and compare `tag_name` against the bundled `VERSION`. Show a dismissible
banner if newer. Don't auto-install.

### 5. CI/CD

GitHub Actions matrix (`macos-14` arm64, `macos-13` x64, `ubuntu-22.04`,
`windows-2022`) — each builds + uploads to a draft release. Manual
promote to public release after a smoke test on a clean machine.

---

## Testing the unsigned build

After `make build`:

1. Open `dist/TallyAero EM.app` (macOS) — first time may require
   right-click → Open to bypass Gatekeeper because the bundle is unsigned.
2. Browser opens to a free localhost port.
3. EM Diagram renders.
4. Pick Cessna 172P, slide altitude, see the chart respond.
5. Open the drawer (`D` key), tweak overlays.
6. Test PNG export — confirms kaleido is bundled correctly.

If any of those fail, the missing piece is almost certainly a hidden
import — PyInstaller's static analysis can miss dynamic imports.
Check `dist/TallyAero EM/TallyAero EM.app/Contents/MacOS/` for the
launcher process output (run from terminal: `./dist/TallyAero\ EM.app/Contents/MacOS/TallyAero\ EM`).
