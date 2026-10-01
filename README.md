# HESPERIA PS4 Control Center

Local Windows control center with a browser-based dashboard for managing package downloads, USB export folders, and Remote Package Installer handoff on a PS4 you own. The PS4 browser can open the dashboard over the same private LAN.

## Contents

- `03_SERVER/server.py` — local HTTP server, PS4/RPI discovery, package serving, and transfer endpoints.
- `02_WEB_UI/` — responsive black/graphite UI with restrained neon-blue accents.
- `04_CONFIG/sources.json` — community package catalog and source metadata.
- `01_START/HESPERIA_PS4_Control_Center_v19.exe` — standalone Windows build with bundled web UI/config and embedded app icon.
- `work/pyinstaller-v12/HESPERIA_PS4_Control_Center_v19.spec` — build definition for the standalone EXE.

No game dumps, ROMs, BIOS files, keys, or licenses are included. Use software and packages only when you have the rights to do so. Remote installation requires GoldHEN and a running Remote Package Installer on a PS4 you own; the app does not jailbreak or enable a console by itself.

## Run

On Windows, start `01_START/HESPERIA_PS4_Control_Center_v19.exe`. It opens the local dashboard in the default browser and displays the LAN address for the PS4. Allow the app through Windows Firewall on private networks if prompted. The standalone build stores writable data in `HESPERIA_Data` beside the EXE.

Alternatively, with Python 3 installed, run `python 03_SERVER/server.py` from the repository root.

## Build the Windows EXE

```powershell
python -m pip install pyinstaller==5.13.2
python -m PyInstaller --noconfirm --clean --distpath dist --workpath build `
  work/pyinstaller-v12/HESPERIA_PS4_Control_Center_v19.spec
```

The spec bundles the UI, catalog, and retro runtime metadata as read-only resources; logs, downloads, USB exports, and the library remain writable local data.

## Network and safety notes

Keep the PC and PS4 on a trusted private network. The dashboard binds to the local network so the PS4 can reach it. Do not expose its port to the public internet. Review package sources before installing, and keep local downloads and console credentials out of commits.

## License

No license is granted by this repository unless a separate license file is added. Third-party names, projects, and package sources remain subject to their respective owners' terms.
