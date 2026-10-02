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
| `src-tauri/src/management_api.rs` | `management_endpoint()` hardcoded the `/v8/management` prefix, but the plugin panel routes and the plugin quota API only exist on the v0 mux. Paths that already start with `v0/` are now passed through untouched. |
| `src/services/quotaService.ts` | New `plugin` quota provider. Providers served by the bundled plugins are resolved through `/v0/management/plugins/<id>/refresh` instead of an upstream endpoint, and the shared `summary` / `accounts[].checkin` payload becomes quota rows. |
| `src/pages/QuotaPage.tsx` | Adds the `Plugins` group (label, icon, ordering). |
| `src/i18n/{locales/zh-CN,locales/en,ja}.ts` | `quota.plugin.*` messages. `zhTW` derives from `zhCN` automatically. |
| `src/assets/icons/{trae,qoder,mimo,plugin}.svg` | Icons for the new cards and the quota group (`workbuddy.png` and `zcode.png` already exist in the repo). |

## Plugin quota cards

The bundled `cpa-multi-plugins` providers report their own numbers; the CPA core cannot ask
them for quota (`POST /v0/management/quota/fetch` answers `501 no quota provider available for
credential`, and every plugin declares `supports_quota: false`). The fork therefore reads the
plugin panel API directly, which shares one payload shape across providers:

- `summary.total_remain` / `summary.total_size` / `summary.pack_count` → the package-quota row.
- `summary.<region>_size` pairs → per-region rows, only when more than one region holds quota.
- `accounts[].checkin` → the sign-in credit row (WorkBuddy).

The plugin panel remains the authoritative view
(`/v0/resource/plugins/<id>/panel`); these rows are a convenience mirror of it.

## Regenerating the patch after an upstream change

```bash
git checkout <upstream-tag>            # must be a clean worktree
python3 .fork/apply-changes.py
git add -N src/assets/icons/{trae,qoder,mimo,plugin}.svg
git diff -- src src-tauri > .fork/cpa-plugins.patch
git checkout HEAD -- src src-tauri
rm -f src/assets/icons/{trae,qoder,mimo,plugin}.svg
```

Then commit `.fork/cpa-plugins.patch`. The build workflow fails loudly when the patch no
longer applies, which is the signal to regenerate it.

Two things to keep in mind:

- `apply-changes.py` must keep LF line endings, and it must run against a clean tree — it
  rewrites every matched file, so a half-patched tree silently doubles the diff.
- The pathspec must be `src src-tauri`: `src/` alone does **not** match `src-tauri/`.
