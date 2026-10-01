# HESPERIA PS4 Control Center v20

## Dashboard redesign

- Rebuilt the single-page interface around the supplied dashboard concept: compact black console-style sidebar, top-level PS4 status/manual connection, three-step setup, live download summary, package cards, and recent activity.
- Added working navigation for Dashboard, Packages, Downloads, USB Builder, Console diagnostics, and Settings. Each view is backed by the local API and shared selection state.
- Added catalog search, category filter, presets, package selection, and per-card download/install actions.
- Added local library selection, PKG import from any view, and USB export using the existing server endpoints.
- Added first-run RPI setup guidance, persistent step checkmarks, copyable PS4 dashboard address, and a console view showing verified RPI status and scan results.
- Preserved the black-first palette and kept neon blue as a restrained focus/progress accent.
- YouTube is shown as a local-import card, not as a false direct download: this catalog has no verified source for a distributable YouTube PKG.
- Kept live PC download rate/ETA and independent PC-to-PS4 transfer progress.

## Honest boundaries

- GoldHEN state cannot be detected through the current RPI API; the user marks setup steps 1–2 manually. RPI reachability and port are verified automatically.
- Console customization is limited to operations actually exposed by GoldHEN/RPI and the available package sources. The app does not claim to change firmware or console system settings directly.
