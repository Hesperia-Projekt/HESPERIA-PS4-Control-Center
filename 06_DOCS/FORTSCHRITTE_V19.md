# HESPERIA PS4 Control Center v19

- Fixed the standalone EXE: the web UI, source catalog, and retro runtime metadata are bundled into the application instead of being expected beside it.
- Portable user data (downloads, USB exports, logs, and library) is stored in `HESPERIA_Data` beside the EXE. When the EXE is in the complete project, existing project folders remain in use.
- Added a custom black/graphite app icon with restrained neon-blue accents, embedded into the Windows EXE and supplied separately as PNG and ICO.
- Packaged as a windowless desktop launcher that opens the local control center in the browser; `HESPERIA_NO_BROWSER=1` is available for diagnostics.
- Verified the packaged EXE starts and serves its status endpoint from the standalone output location.
