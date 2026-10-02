# cpa-multi-plugins edition

This fork rebuilds upstream [EasyCLIProxyAPI](https://github.com/router-for-me/EasyCLIProxyAPI)
with third-party CPA plugins bundled in.

## What `.github/workflows/watch-upstream.yml` does

1. Resolves the latest upstream release tag (or a manually supplied one).
2. Checks out that exact upstream tag, then applies `.fork/cpa-plugins.patch`.
3. Builds the GUI with the upstream toolchain (bun 1.3.14 + Rust 1.97).
4. Downloads `cpa-multi-plugins` and copies the DLLs to
   `cpa-core/plugins/windows/amd64` (Windows amd64 only; other platforms ship without plugins).
5. Generates `portable-update-windows.json` pointing at **this** repository and publishes
   a release with the **same tag name** as upstream.

## What the patch changes

| File | Change |
| --- | --- |
| `src-tauri/src/main.rs` | `APP_UPDATE_MANIFEST_URL` (3 platforms) and `APP_RELEASE_DOWNLOAD_PREFIX` point at this fork. The core constants (`RELEASE_PAGE_URL`, `RELEASE_ATOM_URL`, `RELEASE_DOWNLOAD_PREFIX`) stay on the official CLIProxyAPI repo, so kernel updates remain upstream's. |
| `src-tauri/src/app_update.rs` | The trusted `release_url` path prefix is changed to this fork, otherwise the client rejects the manifest with "Untrusted application update release URL". |
| `src/pages/ManagementPages.tsx` | Adds WorkBuddy / Trae / Qoder / ZCode / MiMo cards to the OAuth page. The Rust commands (`start_oauth_login`, `get_oauth_status`, `submit_oauth_callback`) are already provider-agnostic, so no Rust change is needed. |
| `src/pages/AuthFileManagementPage.tsx` | The credential card icon map falls back to the Gemini icon for unknown providers; the five plugin providers are registered so their own icons are used. |
| `src/assets/icons/{trae,qoder,mimo}.svg` | Icons for the new cards (`workbuddy.png` and `zcode.png` already exist in the repo). |

## Regenerating the patch after an upstream change

```bash
git checkout <upstream-tag>
python3 .fork/apply-changes.py
git add -N src/assets/icons/trae.svg src/assets/icons/qoder.svg src/assets/icons/mimo.svg
git diff > .fork/cpa-plugins.patch
git checkout HEAD -- src/
rm -f src/assets/icons/{trae,qoder,mimo}.svg
```

Then commit `.fork/cpa-plugins.patch`. The build workflow fails loudly when the patch no
longer applies, which is the signal to regenerate it.

Note: `apply-changes.py` must keep LF line endings. Writing these files with CRLF makes
`git diff` report a full-file rewrite.
