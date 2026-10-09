import base64
import io
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)

def replace(path, pairs):
    full = os.path.join(ROOT, path)
    with open(full, 'r', encoding='utf-8', newline='') as handle:
        text = handle.read()
    # The repository mixes LF and CRLF files; match whichever the target uses.
    eol = '\r\n' if '\r\n' in text else '\n'
    for old, new in pairs:
        old = old.replace('\n', eol)
        new = new.replace('\n', eol)
        if old not in text:
            if new in text:
                print('  already applied in %s' % path)
                continue
            raise SystemExit('PATTERN NOT FOUND in %s:\n%s' % (path, old[:200]))
        text = text.replace(old, new, 1)
    with open(full, 'w', encoding='utf-8', newline='') as handle:
        handle.write(text)
    print('patched %s (%s)' % (path, 'crlf' if eol == '\r\n' else 'lf'))

# --- Plugins on by default ---------------------------------------------------
# Upstream defaults `plugins.enabled` to false, and the GUI exposes no toggle for
# it. This build ships cpa-multi-plugins, so a fresh install must load them -
# otherwise the bundled providers never appear and the build looks broken.

replace('src-tauri/src/main.rs', [
    (
        '            plugins_enabled: false,\n'
        '            routing_strategy: "round-robin".to_string(),',
        '            // This build ships cpa-multi-plugins and the GUI has no toggle for\n'
        '            // plugins.enabled, so load them by default.\n'
        '            plugins_enabled: true,\n'
        '            routing_strategy: "round-robin".to_string(),',
    ),
])

# --- Enable every plugin that is actually on disk ----------------------------
# Core 8.0.13+ ignores a plugin DLL unless `plugins.configs.<id>.enabled` is true:
# the file alone leaves it configured=false and never registered, so a fresh
# install shows no providers. The GUI has no toggle for that field either, and
# shipping a config file for it is not an option - the app rewrites config.yaml on
# first launch and would clobber the user's own settings. So fill the flag in at
# the point where the GUI writes the managed kernel settings, only for plugins
# that are really installed, and never touch an entry the user already set.

replace('src-tauri/src/core_config/settings.rs', [
    (
        '        changed |= set_core_yaml_nested_value(\n'
        '            document,\n'
        '            "plugins",\n'
        '            "enabled",\n'
        '            serde_norway::Value::Bool(config.plugins_enabled),\n'
        '        )?;\n',
        '        changed |= set_core_yaml_nested_value(\n'
        '            document,\n'
        '            "plugins",\n'
        '            "enabled",\n'
        '            serde_norway::Value::Bool(config.plugins_enabled),\n'
        '        )?;\n'
        '        if config.plugins_enabled {\n'
        '            for plugin_id in installed_plugin_ids() {\n'
        '                changed |= set_core_yaml_path_value(\n'
        '                    document,\n'
        '                    &["plugins", "configs", plugin_id.as_str(), "enabled"],\n'
        '                    serde_norway::Value::Bool(true),\n'
        '                )?;\n'
        '            }\n'
        '        }\n',
    ),
    (
        'pub(crate) fn is_example_core_api_key(api_key: &str) -> bool {',
        '/// Collect the plugin ids present in the kernel plugin directory. The file\n'
        '/// stem is the id the core reports, so no id list is hardcoded here.\n'
        'fn installed_plugin_ids() -> Vec<String> {\n'
        '    let Ok(plugin_dir) = core_install_dir().map(|dir| dir.join("plugins")) else {\n'
        '        return Vec::new();\n'
        '    };\n'
        '    let Ok(platform_dir) = std::fs::read_dir(plugin_dir) else {\n'
        '        return Vec::new();\n'
        '    };\n'
        '    let mut ids: Vec<String> = Vec::new();\n'
        '    for os_entry in platform_dir.flatten() {\n'
        '        let Ok(arch_dir) = std::fs::read_dir(os_entry.path()) else {\n'
        '            continue;\n'
        '        };\n'
        '        for arch_entry in arch_dir.flatten() {\n'
        '            let arch_path = arch_entry.path();\n'
        '            if !arch_path.is_dir() {\n'
        '                continue;\n'
        '            }\n'
        '            let Ok(files) = std::fs::read_dir(arch_path) else {\n'
        '                continue;\n'
        '            };\n'
        '            for file in files.flatten() {\n'
        '                let path = file.path();\n'
        '                if path.extension().and_then(|ext| ext.to_str()) != Some("dll") {\n'
        '                    continue;\n'
        '                }\n'
        '                let Some(stem) = path.file_stem().and_then(|stem| stem.to_str()) else {\n'
        '                    continue;\n'
        '                };\n'
        '                if stem.is_empty() || ids.iter().any(|id| id.as_str() == stem) {\n'
        '                    continue;\n'
        '                }\n'
        '                ids.push(stem.to_string());\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '    ids.sort();\n'
        '    ids\n'
        '}\n'
        '\n'
        'pub(crate) fn is_example_core_api_key(api_key: &str) -> bool {',
    ),
])

OLD_REPO = 'router-for-me/EasyCLIProxyAPI'
NEW_REPO = 'shiranzby/EasyCLIProxyAPI'

replace('src-tauri/src/main.rs', [
    ('https://github.com/%s/releases/latest/download/portable-update-windows.json' % OLD_REPO,
     'https://github.com/%s/releases/latest/download/portable-update-windows.json' % NEW_REPO),
    ('https://github.com/%s/releases/latest/download/portable-update-linux.json' % OLD_REPO,
     'https://github.com/%s/releases/latest/download/portable-update-linux.json' % NEW_REPO),
    ('https://github.com/%s/releases/latest/download/portable-update-darwin-v2.json' % OLD_REPO,
     'https://github.com/%s/releases/latest/download/portable-update-darwin-v2.json' % NEW_REPO),
    ('"https://github.com/%s/releases/download/"' % OLD_REPO,
     '"https://github.com/%s/releases/download/"' % NEW_REPO),
])

replace('src-tauri/src/app_update.rs', [
    ('"/%s/releases/tag/v"' % OLD_REPO, '"/%s/releases/tag/v"' % NEW_REPO),
])


PLUGIN_ICON_IMPORTS = (
    "import workbuddyIcon from '../assets/icons/workbuddy.png';\n"
    "import traeIcon from '../assets/icons/trae.png';\n"
    "import qoderIcon from '../assets/icons/qoder.png';\n"
    "import zcodeIcon from '../assets/icons/zcode.png';\n"
    "import mimoIcon from '../assets/icons/mimo.png';"
)

replace('src/pages/AuthFileManagementPage.tsx', [
    ("import kimiIcon from '../assets/icons/kimi-light.svg';",
     "import kimiIcon from '../assets/icons/kimi-light.svg';\n" + PLUGIN_ICON_IMPORTS),
    ("const providerIcons: Record<string, string> = {\n"
     "  antigravity: antigravityIcon,\n"
     "  claude: claudeIcon,\n"
     "  codex: codexIcon,\n"
     "  gemini: geminiIcon,\n"
     "  kimi: kimiIcon,\n"
     "  vertex: vertexIcon,\n"
     "  xai: grokIcon,\n"
     "  devin: devinIcon,\n"
     "  meta: metaIcon,\n"
     "};",
     "const providerIcons: Record<string, string> = {\n"
     "  antigravity: antigravityIcon,\n"
     "  claude: claudeIcon,\n"
     "  codex: codexIcon,\n"
     "  gemini: geminiIcon,\n"
     "  kimi: kimiIcon,\n"
     "  vertex: vertexIcon,\n"
     "  xai: grokIcon,\n"
     "  devin: devinIcon,\n"
     "  meta: metaIcon,\n"
     "  workbuddy: workbuddyIcon,\n"
     "  trae: traeIcon,\n"
     "  qoder: qoderIcon,\n"
     "  zcode: zcodeIcon,\n"
     "  mimo: mimoIcon,\n"
     "};"),
])

# --- Plugin quota cards -------------------------------------------------------
# The bundled cpa-multi-plugins providers report their quota through the plugin's
# own management API (`/v0/management/plugins/<id>/refresh`), which the core only
# exposes on the v0 mux. management_endpoint() hardcodes /v8/management, so allow
# an explicit v0/ prefix to pass through untouched.

replace('src-tauri/src/management_api.rs', [
    ('    Ok(format!("{origin}/v8/management/{path}"))\n}',
     '    // Plugin panel routes and the plugin quota API are only served on the v0 mux.\n'
     '    if let Some(rest) = path.strip_prefix("v0/") {\n'
     '        return Ok(format!("{origin}/v0/{rest}"));\n'
     '    }\n'
     '    Ok(format!("{origin}/v8/management/{path}"))\n}'),
])

replace('src/services/quotaService.ts', [
    (
        "export type QuotaProvider = 'claude' | 'codex' | 'kimi' | 'xai' | 'antigravity' | 'devin';",
        "export type QuotaProvider =\n"
        "  | 'claude'\n"
        "  | 'codex'\n"
        "  | 'kimi'\n"
        "  | 'xai'\n"
        "  | 'antigravity'\n"
        "  | 'devin'\n"
        "  | 'plugin';",
    ),
    (
        "  antigravity: 'https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary',\n};",
        "  antigravity: 'https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary',\n"
        "  // Plugin providers are answered by the plugin management API; there is no upstream endpoint.\n"
        "  plugin: '',\n"
        "};",
    ),
    (
        "  antigravity: {\n"
        "    Authorization: 'Bearer $TOKEN$',\n"
        "    'Content-Type': 'application/json',\n"
        "    'User-Agent': 'antigravity/cli/1.0.13 (aidev_client; os_type=darwin; arch=arm64)',\n"
        "  },\n};",
        "  antigravity: {\n"
        "    Authorization: 'Bearer $TOKEN$',\n"
        "    'Content-Type': 'application/json',\n"
        "    'User-Agent': 'antigravity/cli/1.0.13 (aidev_client; os_type=darwin; arch=arm64)',\n"
        "  },\n"
        "  // The plugin API injects the credential server-side; the client only sends the auth index.\n"
        "  plugin: {},\n"
        "};",
    ),
    (
        "export const providerForFile = (file: AuthFile): QuotaProvider | null => {\n"
        "  const value = readString(file, 'provider', 'type', 'account_type').toLowerCase().replace(/_/g, '-');\n"
        "  if (value === 'x-ai' || value === 'grok') return 'xai';",
        "// cpa-multi-plugins providers that expose a quota summary through their plugin API.\n"
        "const PLUGIN_QUOTA_PROVIDERS = ['workbuddy', 'trae', 'qoder', 'zcode', 'mimo'];\n"
        "\n"
        "export const providerForFile = (file: AuthFile): QuotaProvider | null => {\n"
        "  const value = readString(file, 'provider', 'type', 'account_type').toLowerCase().replace(/_/g, '-');\n"
        "  if (PLUGIN_QUOTA_PROVIDERS.includes(value)) return 'plugin';\n"
        "  if (value === 'x-ai' || value === 'grok') return 'xai';",
    ),
    (
        "  try {\n"
        "    if (booleanValue(file.disabled) === true) throw new Error(quotaText('quota.fileDisabled'));\n"
        "    const codexMetadata = provider === 'codex' ? codexMetadataFor(file) : undefined;",
        "  try {\n"
        "    if (booleanValue(file.disabled) === true) throw new Error(quotaText('quota.fileDisabled'));\n"
        "    if (provider === 'plugin') return await loadPluginQuota(file);\n"
        "    const codexMetadata = provider === 'codex' ? codexMetadataFor(file) : undefined;",
    ),
    (
        "async function loadQuotaSnapshot(file: AuthFile): Promise<QuotaState> {",
        "const pluginNumber = (value: unknown): number | null =>\n"
        "  (typeof value === 'number' && Number.isFinite(value) ? value : null);\n"
        "\n"
        "// Plugin quota is resolved by the plugin's own management API. The bundled\n"
        "// cpa-multi-plugins providers share one payload shape: `summary` carries the\n"
        "// per-region and total pack numbers, `accounts[].checkin` the sign-in credits.\n"
        "async function loadPluginQuota(file: AuthFile): Promise<QuotaState> {\n"
        "  const pluginId = readString(file, 'provider', 'type', 'account_type').toLowerCase().replace(/_/g, '-');\n"
        "  if (!/^[a-z0-9-]+$/.test(pluginId)) throw new Error(quotaText('quota.service.error.unrecognized'));\n"
        "  const payload = await managementApi.post<Record<string, unknown>>(\n"
        "    `/v0/management/plugins/${pluginId}/refresh`,\n"
        "    undefined,\n"
        "    { timeoutMs: 30_000 },\n"
        "  );\n"
        "  if (!isRecord(payload)) throw new Error(quotaText('quota.service.error.noResponse'));\n"
        "  const summary = isRecord(payload.summary) ? payload.summary : {};\n"
        "  const totalSize = pluginNumber(summary.total_size) ?? 0;\n"
        "  const packCount = pluginNumber(summary.pack_count) ?? 0;\n"
        "  const rows: QuotaRow[] = [];\n"
        "  if (totalSize > 0) {\n"
        "    const totalRemain = pluginNumber(summary.total_remain) ?? 0;\n"
        "    rows.push({\n"
        "      label: quotaText('quota.plugin.packages'),\n"
        "      remainingPercent: Math.max(0, Math.min(100, (totalRemain / totalSize) * 100)),\n"
        "      detail: quotaText('quota.plugin.packagesDetail', {\n"
        "        remain: totalRemain, size: totalSize, count: packCount,\n"
        "      }),\n"
        "    });\n"
        "    // Only spell out the region split when more than one region holds quota.\n"
        "    const regions = Object.keys(summary)\n"
        "      .filter((key) => key.endsWith('_size') && key !== 'total_size')\n"
        "      .map((key) => {\n"
        "        const region = key.slice(0, -'_size'.length);\n"
        "        return {\n"
        "          region,\n"
        "          size: pluginNumber(summary[key]) ?? 0,\n"
        "          remain: pluginNumber(summary[`${region}_remain`]) ?? 0,\n"
        "        };\n"
        "      })\n"
        "      .filter((entry) => entry.size > 0);\n"
        "    if (regions.length > 1) {\n"
        "      regions.forEach((entry) => {\n"
        "        rows.push({\n"
        "          label: entry.region.toUpperCase(),\n"
        "          remainingPercent: Math.max(0, Math.min(100, (entry.remain / entry.size) * 100)),\n"
        "          detail: quotaText('quota.plugin.regionDetail', { remain: entry.remain, size: entry.size }),\n"
        "        });\n"
        "      });\n"
        "    }\n"
        "  }\n"
        "  const accounts = Array.isArray(payload.accounts) ? payload.accounts.filter(isRecord) : [];\n"
        "  const checkin = accounts\n"
        "    .map((account) => (isRecord(account.checkin) ? account.checkin : null))\n"
        "    .find((entry) => entry !== null);\n"
        "  if (checkin) {\n"
        "    const totalCredits = pluginNumber(checkin.total_credits) ?? 0;\n"
        "    if (totalCredits > 0) {\n"
        "      rows.push({\n"
        "        label: quotaText('quota.plugin.checkin'),\n"
        "        remainingPercent: null,\n"
        "        detail: quotaText('quota.plugin.checkinDetail', {\n"
        "          today: pluginNumber(checkin.today_credit) ?? 0,\n"
        "          total: totalCredits,\n"
        "          streak: pluginNumber(checkin.streak_days) ?? 0,\n"
        "        }),\n"
        "      });\n"
        "    }\n"
        "  }\n"
        "  if (rows.length === 0) throw new Error(quotaText('quota.service.error.unrecognized'));\n"
        "  return {\n"
        "    status: 'success',\n"
        "    rows,\n"
        "    plan: packCount > 0 ? quotaText('quota.plugin.packCount', { count: packCount }) : undefined,\n"
        "    fetchedAt: Date.now(),\n"
        "  };\n"
        "}\n"
        "\n"
        "async function loadQuotaSnapshot(file: AuthFile): Promise<QuotaState> {",
    ),
])

replace('src/pages/QuotaPage.tsx', [
    ("import kimiIcon from '../assets/icons/kimi-light.svg';",
     "import kimiIcon from '../assets/icons/kimi-light.svg';\n"
     "import pluginIcon from '../assets/icons/plugin.svg';\n"
     "import workbuddyIcon from '../assets/icons/workbuddy.png';\n"
     "import traeIcon from '../assets/icons/trae.png';\n"
     "import qoderIcon from '../assets/icons/qoder.png';\n"
     "import zcodeIcon from '../assets/icons/zcode.png';\n"
     "import mimoIcon from '../assets/icons/mimo.png';"),
    ("import { managementApi, readBoolean, responseList } from '../services/managementApi';",
     "import { managementApi, readBoolean, readString, responseList } from '../services/managementApi';"),
    ("const providerMeta: Record<QuotaProvider, { label: string; icon: string }> = {",
     "// Every bundled plugin shares the single `plugin` quota provider, so the group icon\n"
     "// (a generic puzzle) says nothing about which provider a credential belongs to. Show\n"
     "// the credential's own plugin logo, and keep the group icon only as a fallback for\n"
     "// plugins that ship no bundled logo.\n"
     "const PLUGIN_CARD_ICONS: Record<string, string> = {\n"
     "  workbuddy: workbuddyIcon,\n"
     "  trae: traeIcon,\n"
     "  qoder: qoderIcon,\n"
     "  zcode: zcodeIcon,\n"
     "  mimo: mimoIcon,\n"
     "};\n"
     "\n"
     "const cardIcon = (provider: QuotaProvider | null, file: AuthFile): string => {\n"
     "  if (provider === 'plugin') {\n"
     "    const pluginId = readString(file, 'provider', 'type', 'account_type').toLowerCase().replace(/_/g, '-');\n"
     "    const own = PLUGIN_CARD_ICONS[pluginId];\n"
     "    if (own) return own;\n"
     "  }\n"
     "  return provider ? providerMeta[provider].icon : '';\n"
     "};\n"
     "\n"
     "const providerMeta: Record<QuotaProvider, { label: string; icon: string }> = {"),
    ("          <img src={provider ? providerMeta[provider].icon : ''} alt=\"\" className=\"quota-account-icon\" />",
     "          <img src={cardIcon(provider, file)} alt=\"\" className=\"quota-account-icon\" />"),
    ("  antigravity: { label: 'Antigravity', icon: antigravityIcon },\n};",
     "  antigravity: { label: 'Antigravity', icon: antigravityIcon },\n"
     "  plugin: { label: 'Plugins', icon: pluginIcon },\n};"),
    ("const providerOrder: QuotaProvider[] = ['claude', 'antigravity', 'codex', 'xai', 'kimi', 'devin'];",
     "const providerOrder: QuotaProvider[] = ['claude', 'antigravity', 'codex', 'xai', 'kimi', 'devin', 'plugin'];"),
])

QUOTA_MESSAGES = {
    'src/i18n/locales/zh-CN.ts': [
        ("'quota.plugin.packages': '套餐额度',"),
        ("'quota.plugin.packagesDetail': '剩余 {remain} / 共 {size} · {count} 个套餐包',"),
        ("'quota.plugin.regionDetail': '剩余 {remain} / 共 {size}',"),
        ("'quota.plugin.packCount': '{count} 个套餐包',"),
        ("'quota.plugin.checkin': '签到积分',"),
        ("'quota.plugin.checkinDetail': '今日 +{today} · 累计 {total} · 连续 {streak} 天',"),
        ("'quota.plugin.rateLimited': '查询过于频繁，请稍后再试',"),
    ],
    'src/i18n/locales/en.ts': [
        ("'quota.plugin.packages': 'Package quota',"),
        ("'quota.plugin.packagesDetail': '{remain} of {size} left · {count} packages',"),
        ("'quota.plugin.regionDetail': '{remain} of {size} left',"),
        ("'quota.plugin.packCount': '{count} packages',"),
        ("'quota.plugin.checkin': 'Check-in credits',"),
        ("'quota.plugin.checkinDetail': '+{today} today · {total} total · {streak} day streak',"),
        ("'quota.plugin.rateLimited': 'Too many quota lookups at once, please try again in a moment',"),
    ],
    'src/i18n/ja.ts': [
        ("'quota.plugin.packages': 'パッケージ枠',"),
        ("'quota.plugin.packagesDetail': '残り {remain} / {size} · {count} パッケージ',"),
        ("'quota.plugin.regionDetail': '残り {remain} / {size}',"),
        ("'quota.plugin.packCount': '{count} パッケージ',"),
        ("'quota.plugin.checkin': 'チェックイン積分',"),
        ("'quota.plugin.checkinDetail': '本日 +{today} · 累計 {total} · {streak} 日連続',"),
        ("'quota.plugin.rateLimited': '照会が頻繁すぎます。少し待ってから再試行してください',"),
    ],
}

# The anchor must be matched as a whole line: the key also occurs mid-line inside
# the message values, and replacing there would split the entry in half.
ANCHOR = "'quota.service.error.missingConsumeAuthIndex'"


def write_new(path, content):
    """Create a file the fork adds (upstream has no such file to patch)."""
    full = os.path.join(ROOT, path)
    if os.path.exists(full):
        print('  already exists %s' % path)
        return
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(content)
    print('created %s' % path)

def append_messages(path, lines):
    full = os.path.join(ROOT, path)
    with open(full, 'r', encoding='utf-8', newline='') as handle:
        text = handle.read()
    if lines[0] in text:
        print('  already applied in %s' % path)
        return
    matches = [line for line in text.splitlines() if line.strip().startswith(ANCHOR)]
    if len(matches) != 1:
        raise SystemExit('AMBIGUOUS ANCHOR in %s (%d matches)' % (path, len(matches)))
    addendum = ''.join('  ' + line + '\n' for line in lines).rstrip('\n')
    text = text.replace(matches[0], matches[0] + '\n' + addendum, 1)
    with open(full, 'w', encoding='utf-8', newline='') as handle:
        handle.write(text)
    print('patched %s (messages)' % path)


for path, lines in QUOTA_MESSAGES.items():
    append_messages(path, lines)

# --- Per-account plugin quota ------------------------------------------------
# `POST /plugins/<id>/refresh` returns every account of that plugin, so the first
# version showed the pooled total on every credential. Match the credential back to
# its account entry and render that account's own numbers instead.

replace('src/services/quotaService.ts', [
    (
        "  const summary = isRecord(payload.summary) ? payload.summary : {};\n"
        "  const totalSize = pluginNumber(summary.total_size) ?? 0;\n"
        "  const packCount = pluginNumber(summary.pack_count) ?? 0;\n"
        "  const rows: QuotaRow[] = [];\n"
        "  if (totalSize > 0) {\n"
        "    const totalRemain = pluginNumber(summary.total_remain) ?? 0;\n"
        "    rows.push({\n"
        "      label: quotaText('quota.plugin.packages'),\n"
        "      remainingPercent: Math.max(0, Math.min(100, (totalRemain / totalSize) * 100)),\n"
        "      detail: quotaText('quota.plugin.packagesDetail', {\n"
        "        remain: totalRemain, size: totalSize, count: packCount,\n"
        "      }),\n"
        "    });\n"
        "    // Only spell out the region split when more than one region holds quota.\n"
        "    const regions = Object.keys(summary)\n"
        "      .filter((key) => key.endsWith('_size') && key !== 'total_size')\n"
        "      .map((key) => {\n"
        "        const region = key.slice(0, -'_size'.length);\n"
        "        return {\n"
        "          region,\n"
        "          size: pluginNumber(summary[key]) ?? 0,\n"
        "          remain: pluginNumber(summary[`${region}_remain`]) ?? 0,\n"
        "        };\n"
        "      })\n"
        "      .filter((entry) => entry.size > 0);\n"
        "    if (regions.length > 1) {\n"
        "      regions.forEach((entry) => {\n"
        "        rows.push({\n"
        "          label: entry.region.toUpperCase(),\n"
        "          remainingPercent: Math.max(0, Math.min(100, (entry.remain / entry.size) * 100)),\n"
        "          detail: quotaText('quota.plugin.regionDetail', { remain: entry.remain, size: entry.size }),\n"
        "        });\n"
        "      });\n"
        "    }\n"
        "  }\n"
        "  const accounts = Array.isArray(payload.accounts) ? payload.accounts.filter(isRecord) : [];\n"
        "  const checkin = accounts\n"
        "    .map((account) => (isRecord(account.checkin) ? account.checkin : null))\n"
        "    .find((entry) => entry !== null);\n"
        "  if (checkin) {\n"
        "    const totalCredits = pluginNumber(checkin.total_credits) ?? 0;\n"
        "    if (totalCredits > 0) {\n"
        "      rows.push({\n"
        "        label: quotaText('quota.plugin.checkin'),\n"
        "        remainingPercent: null,\n"
        "        detail: quotaText('quota.plugin.checkinDetail', {\n"
        "          today: pluginNumber(checkin.today_credit) ?? 0,\n"
        "          total: totalCredits,\n"
        "          streak: pluginNumber(checkin.streak_days) ?? 0,\n"
        "        }),\n"
        "      });\n"
        "    }\n"
        "  }\n"
        "  if (rows.length === 0) throw new Error(quotaText('quota.service.error.unrecognized'));\n"
        "  return {\n"
        "    status: 'success',\n"
        "    rows,\n"
        "    plan: packCount > 0 ? quotaText('quota.plugin.packCount', { count: packCount }) : undefined,\n"
        "    fetchedAt: Date.now(),\n"
        "  };\n"
        "}",
        "  const summary = isRecord(payload.summary) ? payload.summary : {};\n"
        "  const accounts = Array.isArray(payload.accounts) ? payload.accounts.filter(isRecord) : [];\n"
        "  const authIndex = normalizeAuthIndex(file.auth_index ?? file.authIndex);\n"
        "  const credentialName = readString(file, 'name', 'auth_id');\n"
        "  const own = accounts.find((account) => {\n"
        "    const index = normalizeAuthIndex(account.auth_index ?? account.authIndex);\n"
        "    if (authIndex && index) return index === authIndex;\n"
        "    const id = readString(account, 'auth_id', 'name');\n"
        "    return Boolean(credentialName && id && id === credentialName);\n"
        "  }) ?? (accounts.length === 1 ? accounts[0] : null);\n"
        "  const credits = isRecord(own?.credits) ? (own?.credits as Record<string, unknown>) : null;\n"
        "  const totalSize = pluginNumber(credits?.total_size) ?? 0;\n"
        "  const totalRemain = pluginNumber(credits?.total_remain) ?? 0;\n"
        "  const packCount = pluginNumber(credits?.pack_count) ?? 0;\n"
        "  const rows: QuotaRow[] = [];\n"
        "  if (totalSize > 0) {\n"
        "    rows.push({\n"
        "      label: quotaText('quota.plugin.packages'),\n"
        "      remainingPercent: Math.max(0, Math.min(100, (totalRemain / totalSize) * 100)),\n"
        "      detail: quotaText('quota.plugin.packagesDetail', {\n"
        "        remain: totalRemain, size: totalSize, count: packCount,\n"
        "      }),\n"
        "    });\n"
        "  }\n"
        "  const checkin = isRecord(own?.checkin) ? (own?.checkin as Record<string, unknown>) : null;\n"
        "  if (checkin) {\n"
        "    const totalCredits = pluginNumber(checkin.total_credits) ?? 0;\n"
        "    if (totalCredits > 0) {\n"
        "      rows.push({\n"
        "        label: quotaText('quota.plugin.checkin'),\n"
        "        remainingPercent: null,\n"
        "        detail: quotaText('quota.plugin.checkinDetail', {\n"
        "          today: pluginNumber(checkin.today_credit) ?? 0,\n"
        "          total: totalCredits,\n"
        "          streak: pluginNumber(checkin.streak_days) ?? 0,\n"
        "        }),\n"
        "      });\n"
        "    }\n"
        "  }\n"
        "  // The plugin answers with every account it owns; keep the pooled totals as a\n"
        "  // trailing row so a multi-account pool stays visible from any credential.\n"
        "  const poolSize = pluginNumber(summary.total_size) ?? 0;\n"
        "  if (poolSize > 0 && accounts.length > 1) {\n"
        "    const poolRemain = pluginNumber(summary.total_remain) ?? 0;\n"
        "    rows.push({\n"
        "      label: quotaText('quota.plugin.pool'),\n"
        "      remainingPercent: Math.max(0, Math.min(100, (poolRemain / poolSize) * 100)),\n"
        "      detail: quotaText('quota.plugin.poolDetail', {\n"
        "        count: accounts.length, remain: poolRemain, size: poolSize,\n"
        "      }),\n"
        "    });\n"
        "  }\n"
        "  if (rows.length === 0) throw new Error(quotaText('quota.service.error.unrecognized'));\n"
        "  return {\n"
        "    status: 'success',\n"
        "    rows,\n"
        "    plan: own && readString(own, 'nickname')\n"
        "      ? readString(own, 'nickname')\n"
        "      : packCount > 0\n"
        "        ? quotaText('quota.plugin.packCount', { count: packCount })\n"
        "        : undefined,\n"
        "    fetchedAt: Date.now(),\n"
        "  };\n"
        "}",
    ),
])

# --- Rate-limited plugin quota: wait a second and ask again --------------------
# Refreshing several credentials at once trips the plugin request limiter and the
# core answers 429 "rate limit exceeded". Retry after a short pause instead of
# showing that message to the user.

replace('src/services/quotaService.ts', [
    (
        "const pluginNumber = (value: unknown): number | null =>\n"
        "  (typeof value === 'number' && Number.isFinite(value) ? value : null);",
        "const pluginNumber = (value: unknown): number | null =>\n"
        "  (typeof value === 'number' && Number.isFinite(value) ? value : null);\n"
        "\n"
        "const isRateLimitedError = (error: unknown): boolean => {\n"
        "  const message = error instanceof Error ? error.message : String(error ?? '');\n"
        "  return /\\(429\\)|\\b429\\b|rate limit|rate limited|too many requests/i.test(message);\n"
        "};\n"
        "\n"
        "// A plugin refresh already reports every account that plugin owns, so the\n"
        "// credentials page and the quota page asking at the same moment only need one\n"
        "// request between them. Sharing it is what keeps us under the limiter; the\n"
        "// retries below only cover the case where something else got there first.\n"
        "const pluginQuotaInFlight = new Map<string, Promise<Record<string, unknown>>>();\n"
        "\n"
        "const PLUGIN_QUOTA_RETRIES = 5;\n"
        "\n"
        "async function refreshPluginQuota(pluginId: string): Promise<Record<string, unknown>> {\n"
        "  const shared = pluginQuotaInFlight.get(pluginId);\n"
        "  if (shared) return shared;\n"
        "  const pending = (async () => {\n"
        "    let lastError: unknown;\n"
        "    for (let attempt = 0; attempt <= PLUGIN_QUOTA_RETRIES; attempt += 1) {\n"
        "      try {\n"
        "        return await managementApi.post<Record<string, unknown>>(\n"
        "          `/v0/management/plugins/${pluginId}/refresh`,\n"
        "          undefined,\n"
        "          { timeoutMs: 30_000 },\n"
        "        );\n"
        "      } catch (error) {\n"
        "        lastError = error;\n"
        "        // Bail out on anything that is not the limiter, and stop once the\n"
        "        // retries are used up so the caller can report the failure.\n"
        "        if (!isRateLimitedError(error) || attempt === PLUGIN_QUOTA_RETRIES) break;\n"
        "        await new Promise<void>((resolve) => {\n"
        "          window.setTimeout(resolve, 1000 * (attempt + 1));\n"
        "        });\n"
        "      }\n"
        "    }\n"
        "    throw lastError instanceof Error ? lastError : new Error(String(lastError ?? ''));\n"
        "  })();\n"
        "  pluginQuotaInFlight.set(pluginId, pending);\n"
        "  try {\n"
        "    return await pending;\n"
        "  } finally {\n"
        "    pluginQuotaInFlight.delete(pluginId);\n"
        "  }\n"
        "}",
    ),
    (
        "  const payload = await managementApi.post<Record<string, unknown>>(\n"
        "    `/v0/management/plugins/${pluginId}/refresh`,\n"
        "    undefined,\n"
        "    { timeoutMs: 30_000 },\n"
        "  );\n"
        "  if (!isRecord(payload)) throw new Error(quotaText('quota.service.error.noResponse'));\n",
        "  let payload: Record<string, unknown> | null = null;\n"
        "  try {\n"
        "    payload = await refreshPluginQuota(pluginId);\n"
        "  } catch (error) {\n"
        "    if (isRateLimitedError(error)) throw new Error(quotaText('quota.plugin.rateLimited'));\n"
        "    throw error;\n"
        "  }\n"
        "  if (!isRecord(payload)) throw new Error(quotaText('quota.service.error.noResponse'));\n",
    ),
])

# --- One OAuth card per upstream ------------------------------------------------
# zcode (zai / bigmodel) and workbuddy (cn / intl) each reach two upstreams. The
# plugin config field only decides which upstream the NEXT login uses, and the
# plugin's own description says existing accounts keep the upstream they were
# logged in with - so the two coexist and deserve one card each. The region is
# written immediately before starting that login: start_oauth_login takes no
# region argument, so the order matters.

write_new('src/services/pluginOAuthRegions.ts', """import type { PluginListEntry } from './plugins';

export type PluginOAuthRegion = {
  key: string;
  field: string;
  value: string;
  label: string;
};

type RegionDefinition = {
  field: string;
  values: { value: string; label: string }[];
};

// CN entries come first: they are the ones used most.
const REGION_DEFINITIONS: Record<string, RegionDefinition> = {
  zcode: {
    field: 'login_provider',
    values: [
      { value: 'bigmodel', label: '智谱' },
      { value: 'zai', label: 'Z.AI' },
    ],
  },
  workbuddy: {
    field: 'login_region',
    values: [
      { value: 'cn', label: '国内' },
      { value: 'intl', label: '国际' },
    ],
  },
};

/** Regions to offer for a plugin, or [] to keep the plain single card. */
export function pluginOAuthRegions(plugin: PluginListEntry): PluginOAuthRegion[] {
  const definition = REGION_DEFINITIONS[plugin.id];
  if (!definition) return [];
  // Only split when the running plugin really declares that field, so a plugin
  // that drops it keeps working as one card.
  const declared = plugin.configFields.some(
    field => field.name === definition.field && field.enumValues.length > 0,
  );
  if (!declared) return [];
  return definition.values.map(entry => ({
    key: `${plugin.id}:${entry.value}`,
    field: definition.field,
    value: entry.value,
    label: entry.label,
  }));
}
""")

replace('src/pages/PluginOAuthDialog.tsx', [
    (
        "import { pluginOAuthText, type PluginOAuthMessage } from '../i18n/pluginOAuth';",
        "import { pluginOAuthText, type PluginOAuthMessage } from '../i18n/pluginOAuth';\n"
        "import { pluginsApi } from '../services/plugins';\n"
        "import type { PluginOAuthRegion } from '../services/pluginOAuthRegions';",
    ),
    (
        "export function PluginOAuthDialog({ plugin, browser = 'default', onClose, onCompleted }: {\n"
        "  plugin: PluginListEntry;\n"
        "  browser?: string;\n"
        "  onClose: () => void;\n"
        "  onCompleted: () => void;\n"
        "}) {",
        "export function PluginOAuthDialog({ plugin, region, browser = 'default', onClose, onCompleted }: {\n"
        "  plugin: PluginListEntry;\n"
        "  region?: PluginOAuthRegion | null;\n"
        "  browser?: string;\n"
        "  onClose: () => void;\n"
        "  onCompleted: () => void;\n"
        "}) {\n"
        "  // The dialog owns the region write: the login must not start until the\n"
        "  // plugin config already points at this card's upstream.\n"
        "  const [regionReady, setRegionReady] = useState(!region);\n"
        "  const [regionFailed, setRegionFailed] = useState(false);\n"
        "  useEffect(() => {\n"
        "    if (!region) return;\n"
        "    let active = true;\n"
        "    void pluginsApi.patchConfig(plugin.id, { [region.field]: region.value })\n"
        "      .then(() => { if (active) setRegionReady(true); })\n"
        "      .catch(() => { if (active) setRegionFailed(true); });\n"
        "    return () => { active = false; };\n"
        "  }, [plugin.id, region]);",
    ),
    (
        "    if (!plugin.supportsOAuth || !plugin.effectiveEnabled || !provider) {\n"
        "      fail(translate('unavailable'));\n"
        "      return stop;\n"
        "    }\n",
        "    if (!plugin.supportsOAuth || !plugin.effectiveEnabled || !provider) {\n"
        "      fail(translate('unavailable'));\n"
        "      return stop;\n"
        "    }\n"
        "    // A region card must not log in before its upstream reached the plugin\n"
        "    // config, otherwise the token would come from the other region.\n"
        "    if (regionFailed) { fail(translate('failed')); return stop; }\n"
        "    if (!regionReady) { return stop; }\n",
    ),
    (
        "  }, [provider, plugin.supportsOAuth, plugin.effectiveEnabled, attempt]);",
        "  }, [provider, plugin.supportsOAuth, plugin.effectiveEnabled, attempt, regionReady, regionFailed]);",
    ),
])

replace('src/pages/PluginOAuthProviders.tsx', [
    (
        "import { collectPluginOAuthProviders } from '../services/pluginOAuthProviders';",
        "import { collectPluginOAuthProviders } from '../services/pluginOAuthProviders';\n"
        "import { pluginOAuthRegions, type PluginOAuthRegion } from '../services/pluginOAuthRegions';",
    ),
    (
        "  const selectedPlugin = plugins.find(plugin => plugin.oauthProvider === selectedProvider);",
        "  // One card per upstream for multi-region plugins (zcode, workbuddy); other\n"
        "  // plugins keep their single card. CN regions are listed first.\n"
        "  const cards = plugins.flatMap(plugin => {\n"
        "    const regions = pluginOAuthRegions(plugin);\n"
        "    if (!regions.length) return [{ plugin, region: null as PluginOAuthRegion | null, key: plugin.id }];\n"
        "    return regions.map(region => ({ plugin, region, key: region.key }));\n"
        "  });\n"
        "  const selectedCard = cards.find(card => card.key === selectedProvider);\n"
        "  const selectedPlugin = selectedCard?.plugin;",
    ),
    (
        "        setSelectedProvider(previous => next.some(plugin => plugin.oauthProvider === previous) ? previous : null);",
        "        setSelectedProvider(previous => previous && next.some(plugin =>\n"
        "          plugin.id === previous || pluginOAuthRegions(plugin).some(region => region.key === previous)\n"
        "        ) ? previous : null);",
    ),
    (
        "    {plugins.map(plugin => {\n"
        "      const provider = plugin.oauthProvider!;\n"
        "      const authorized = completed.has(provider);\n"
        "      return <section className=\"panel oauth-card\" key={provider}>\n",
        "    {cards.map(({ plugin, region, key }) => {\n"
        "      const provider = plugin.oauthProvider!;\n"
        "      const authorized = completed.has(key);\n"
        "      return <section className=\"panel oauth-card\" key={key}>\n",
    ),
    (
        "            <h2>{pluginOAuthText('providerTitle', locale).replace('{name}', getPluginTitle(plugin))}</h2>\n"
        "            {authorized && <span className=\"state-pill success\">{t('oauth.status.completed')}</span>}",
        "            <h2>{pluginOAuthText('providerTitle', locale).replace('{name}', getPluginTitle(plugin))}</h2>\n"
        "            {region && <p className=\"oauth-card-region\">{region.label}</p>}\n"
        "            {authorized && <span className=\"state-pill success\">{t('oauth.status.completed')}</span>}",
    ),
    (
        "          <button type=\"button\" className=\"primary-button\" onClick={() => setSelectedProvider(provider)}>",
        "          <button type=\"button\" className=\"primary-button\" onClick={() => setSelectedProvider(key)}>",
    ),
    (
        "    {selectedPlugin && <PluginOAuthDialog\n"
        "      key={selectedPlugin.oauthProvider}\n"
        "      plugin={selectedPlugin}\n"
        "      browser={browser}\n"
        "      onClose={() => setSelectedProvider(null)}\n"
        "      onCompleted={() => setCompleted(previous => new Set(previous).add(selectedPlugin.oauthProvider!))}\n"
        "    />}",
        "    {selectedCard && <PluginOAuthDialog\n"
        "      key={selectedCard.key}\n"
        "      plugin={selectedCard.plugin}\n"
        "      region={selectedCard.region}\n"
        "      browser={browser}\n"
        "      onClose={() => setSelectedProvider(null)}\n"
        "      onCompleted={() => setCompleted(previous => new Set(previous).add(selectedCard.key))}\n"
        "    />}",
    ),
])

replace('src/pages/PluginOAuthProviders.css', [
    (
        ".plugin-oauth-provider-status {",
        ".oauth-card-region {\n"
        "  margin: 2px 0 0;\n"
        "  color: var(--text-secondary);\n"
        "  font-size: var(--font-size-meta);\n"
        "}\n"
        "\n"
        ".plugin-oauth-provider-status {",
    ),
])


# --- Plugin OAuth cards: use the plugin's own logo ------------------------------
# Upstream renders a generic puzzle glyph for every plugin card. Prefer the local
# brand icon, then the plugin's `logo` metadata, and only fall back to the puzzle.

replace('src/pages/PluginOAuthProviders.tsx', [
    (
        "import { LogIn, Puzzle, RefreshCw } from 'lucide-react';",
        "import { LogIn, Puzzle, RefreshCw } from 'lucide-react';\n"
        "import workbuddyIcon from '../assets/icons/workbuddy.png';\n"
        "import traeIcon from '../assets/icons/trae.png';\n"
        "import qoderIcon from '../assets/icons/qoder.png';\n"
        "import zcodeIcon from '../assets/icons/zcode.png';\n"
        "import mimoIcon from '../assets/icons/mimo.png';",
    ),
    (
        "export function PluginOAuthProviders(",
        "const PLUGIN_ICON_BY_PROVIDER: Record<string, string> = {\n"
        "  workbuddy: workbuddyIcon,\n"
        "  trae: traeIcon,\n"
        "  qoder: qoderIcon,\n"
        "  zcode: zcodeIcon,\n"
        "  mimo: mimoIcon,\n"
        "};\n"
        "\n"
        "const pluginLogo = (plugin: PluginListEntry): string => {\n"
        "  const provider = plugin.oauthProvider ?? '';\n"
        "  const local = PLUGIN_ICON_BY_PROVIDER[provider] ?? '';\n"
        "  if (local) return local;\n"
        "  const remote = typeof plugin.logo === 'string' ? plugin.logo.trim() : '';\n"
        "  return remote;\n"
        "};\n"
        "\n"
        "export function PluginOAuthProviders(",
    ),
    (
        "          <Puzzle className=\"provider-logo\" size={40} aria-hidden=\"true\" />",
        "          {pluginLogo(plugin)\n"
        "            ? <img className=\"provider-logo\" src={pluginLogo(plugin)} alt=\"\" />\n"
        "            : <Puzzle className=\"provider-logo\" size={40} aria-hidden=\"true\" />}",
    ),
])

# --- Credential import: accept third-party exports, and export a credential ----

replace('src/services/managementApi.ts', [
    (
        "  uploadAuthFile: async (file: File) => {\n"
        "    const data = Array.from(new Uint8Array(await file.arrayBuffer()));\n"
        "    return invoke<ManagementJson>('upload_auth_file', {\n"
        "      name: file.name,\n"
        "      data,\n"
        "    });\n"
        "  },",
        "  uploadAuthFile: async (file: File) => {\n"
        "    const data = Array.from(new Uint8Array(await file.arrayBuffer()));\n"
        "    return invoke<ManagementJson>('upload_auth_file', {\n"
        "      name: file.name,\n"
        "      data,\n"
        "    });\n"
        "  },\n"
        "  uploadAuthFileContent: async (name: string, content: string) => {\n"
        "    const data = Array.from(new TextEncoder().encode(content));\n"
        "    return invoke<ManagementJson>('upload_auth_file', { name, data });\n"
        "  },\n"
        "  exportAuthFile: (source: string, target: string) =>\n"
        "    invoke<void>('export_auth_file', { source, target }),",
    ),
])

replace('src-tauri/src/management_api.rs', [
    (
        "use std::{\n"
        "    collections::HashMap,\n"
        "    error::Error,\n"
        "    fs,\n"
        "    path::Path,\n"
        "    process::{Command, Stdio},\n"
        "    sync::LazyLock,\n"
        "    time::Duration,\n"
        "};",
        "use std::{\n"
        "    collections::HashMap,\n"
        "    error::Error,\n"
        "    fs,\n"
        "    path::{Path, PathBuf},\n"
        "    process::{Command, Stdio},\n"
        "    sync::LazyLock,\n"
        "    time::Duration,\n"
        "};",
    ),
    (
        "#[tauri::command]\npub(crate) fn open_auth_files_directory(",
        "#[tauri::command]\n"
        "pub(crate) fn export_auth_file(source: String, target: String) -> Result<(), String> {\n"
        "    let install_dir = core_install_dir()?;\n"
        "    let candidate = PathBuf::from(source.trim());\n"
        "    // The credentials list reports paths relative to the core install directory.\n"
        "    let source_path = if candidate.is_absolute() {\n"
        "        candidate\n"
        "    } else {\n"
        "        install_dir.join(candidate)\n"
        "    };\n"
        "    if !source_path.is_file() {\n"
        "        return Err(format!(\n"
        "            \"Credential file not found: {}\",\n"
        "            path_to_string(&source_path)\n"
        "        ));\n"
        "    }\n"
        "    let target_path = PathBuf::from(target.trim());\n"
        "    if target_path.as_os_str().is_empty() {\n"
        "        return Err(\"Credential export target is empty\".to_string());\n"
        "    }\n"
        "    fs::copy(&source_path, &target_path).map_err(|error| {\n"
        "        format!(\n"
        "            \"Failed to copy {} to {}: {error}\",\n"
        "            path_to_string(&source_path),\n"
        "            path_to_string(&target_path)\n"
        "        )\n"
        "    })?;\n"
        "    Ok(())\n"
        "}\n"
        "\n"
        "#[tauri::command]\npub(crate) fn open_auth_files_directory(",
    ),
])

replace('src-tauri/src/main.rs', [
    (
        "            management_api::upload_auth_file,",
        "            management_api::upload_auth_file,\n            management_api::export_auth_file,",
    ),
])

replace('src/pages/AuthFileManagementPage.tsx', [
    (
        "import {\n"
        "  formatDate,\n"
        "  managementApi,\n"
        "  readBoolean,\n"
        "  readNumber,\n"
        "  readString,\n"
        "  responseList,\n"
        "} from '../services/managementApi';",
        "import {\n"
        "  formatDate,\n"
        "  isRecord,\n"
        "  managementApi,\n"
        "  readBoolean,\n"
        "  readNumber,\n"
        "  readString,\n"
        "  responseList,\n"
        "} from '../services/managementApi';",
    ),
    (
        "  mimo: mimoIcon,\n};",
        "  mimo: mimoIcon,\n};\n"
        "\n"
        "// Third-party exports (for example cockpit-style `workbuddy_accounts_*.json`) ship a\n"
        "// JSON array of flat snake_case accounts, while CPA stores one nested camelCase file\n"
        "// per credential. Split the array and reshape every entry before uploading it.\n"
        "const REGION_BY_DOMAIN: Record<string, string> = {\n"
        "  'copilot.tencent.com': 'cn',\n"
        "  'codebuddy.cn': 'cn',\n"
        "  'www.codebuddy.cn': 'cn',\n"
        "  'workbuddy.ai': 'global',\n"
        "  'www.workbuddy.ai': 'global',\n"
        "  'codebuddy.ai': 'intl',\n"
        "  'www.codebuddy.ai': 'intl',\n"
        "};\n"
        "\n"
        "const normalizeImportedCredential = (\n"
        "  value: Record<string, unknown>,\n"
        "  fallbackProvider: string,\n"
        "): Record<string, unknown> => {\n"
        "  if (isRecord(value.auth) || isRecord(value.account)) return value;\n"
        "  const accessToken = readString(value, 'accessToken', 'access_token');\n"
        "  if (!accessToken) return value;\n"
        "  const domain = readString(value, 'domain') || 'www.codebuddy.cn';\n"
        "  const provider = readString(value, 'provider', 'type', 'account_type') || fallbackProvider;\n"
        "  const rawExpiry = value.expiresAt ?? value.expires_at;\n"
        "  let expiresAt = 0;\n"
        "  if (typeof rawExpiry === 'number' && Number.isFinite(rawExpiry)) {\n"
        "    expiresAt = rawExpiry > 10 ** 11 ? Math.floor(rawExpiry / 1000) : Math.floor(rawExpiry);\n"
        "  }\n"
        "  return {\n"
        "    account: {\n"
        "      enterpriseId: '',\n"
        "      nickname: readString(value, 'nickname', 'name'),\n"
        "      uid: readString(value, 'uid', 'user_id'),\n"
        "    },\n"
        "    auth: {\n"
        "      accessToken,\n"
        "      refreshToken: readString(value, 'refreshToken', 'refresh_token'),\n"
        "      expiresAt,\n"
        "      domain,\n"
        "      region: readString(value, 'region') || REGION_BY_DOMAIN[domain] || 'cn',\n"
        "    },\n"
        "    auth_kind: 'oauth',\n"
        "    disabled: false,\n"
        "    provider,\n"
        "    type: provider,\n"
        "  };\n"
        "};\n"
        "\n"
        "const importCredentialFile = async (file: File): Promise<number> => {\n"
        "  let parsed: unknown = null;\n"
        "  try {\n"
        "    parsed = JSON.parse(await file.text());\n"
        "  } catch {\n"
        "    parsed = null;\n"
        "  }\n"
        "  const entries = (Array.isArray(parsed) ? parsed : [parsed]).filter(isRecord);\n"
        "  const alreadyCredential =\n"
        "    entries.length === 1 && (isRecord(entries[0].auth) || isRecord(entries[0].account));\n"
        "  if (parsed === null || entries.length === 0 || alreadyCredential) {\n"
        "    await managementApi.uploadAuthFile(file);\n"
        "    return 1;\n"
        "  }\n"
        "  const fallbackProvider = file.name.split(/[_.-]/)[0].toLowerCase();\n"
        "  let uploaded = 0;\n"
        "  for (const entry of entries) {\n"
        "    const normalized = normalizeImportedCredential(entry, fallbackProvider);\n"
        "    const provider =\n"
        "      readString(normalized, 'provider', 'type', 'account_type') || fallbackProvider || 'credential';\n"
        "    const uid = isRecord(normalized.account) ? readString(normalized.account, 'uid') : '';\n"
        "    const name = uid ? `${provider}-${uid}.json` : file.name;\n"
        "    await managementApi.uploadAuthFileContent(name, JSON.stringify(normalized));\n"
        "    uploaded += 1;\n"
        "  }\n"
        "  return uploaded;\n"
        "};",
    ),
    (
        "    for (const file of selected) {\n"
        "      try {\n"
        "        await managementApi.uploadAuthFile(file);\n"
        "        uploaded += 1;\n"
        "      } catch (requestError) {\n"
        "        failures.push(`${file.name}：${String(requestError)}`);\n"
        "      }\n"
        "    }",
        "    for (const file of selected) {\n"
        "      try {\n"
        "        uploaded += await importCredentialFile(file);\n"
        "      } catch (requestError) {\n"
        "        failures.push(`${file.name}：${String(requestError)}`);\n"
        "      }\n"
        "    }",
    ),
    (
        "  const toggleStatus = async (file: AuthFile) => {",
        "  const exportFile = async (file: AuthFile) => {\n"
        "    feedback.clearNotice();\n"
        "    setError('');\n"
        "    const name = fileName(file);\n"
        "    const source = readString(file, 'path');\n"
        "    if (!source) {\n"
        "      setError(t('authFiles.exportFailed', { error: t('authFiles.fileOnly') }));\n"
        "      return;\n"
        "    }\n"
        "    setBusy(true);\n"
        "    try {\n"
        "      const target = await save({\n"
        "        defaultPath: name,\n"
        "        filters: [{ name: 'JSON', extensions: ['json'] }],\n"
        "      });\n"
        "      if (!target) return;\n"
        "      await managementApi.exportAuthFile(source, target);\n"
        "      showNotice({ key: 'authFiles.exported', variables: { name } });\n"
        "    } catch (requestError) {\n"
        "      setError(t('authFiles.exportFailed', { error: String(requestError) }));\n"
        "    } finally {\n"
        "      setBusy(false);\n"
        "    }\n"
        "  };\n"
        "\n"
        "  const toggleStatus = async (file: AuthFile) => {",
    ),
    (
        "                      <button type=\"button\" className=\"auth-list-action danger\" onClick={() => void deleteFile(file)}",
        "                      <button type=\"button\" className=\"auth-list-action\" onClick={() => void exportFile(file)} disabled={busy || !readString(file, 'path')} title={t('authFiles.export')} aria-label={t('authFiles.export')}><FileDown size={15} aria-hidden=\"true\" /></button>\n"
        "                      <button type=\"button\" className=\"auth-list-action danger\" onClick={() => void deleteFile(file)}",
    ),
    (
        "import { useConfirmation } from '../components/ConfirmationDialog';",
        "import { save } from '@tauri-apps/plugin-dialog';\n"
        "import { useConfirmation } from '../components/ConfirmationDialog';",
    ),
])

AUTH_FILE_MESSAGES = {
    'src/i18n/locales/zh-CN.ts': [
        ("'authFiles.export': '导出',"),
        ("'authFiles.exported': '已导出 {name}',"),
        ("'authFiles.exportFailed': '导出失败：{error}',"),
        ("'quota.plugin.pool': '账号池合计',"),
        ("'quota.plugin.poolDetail': '{count} 个账号 · 剩余 {remain} / 共 {size}',"),
    ],
    'src/i18n/locales/en.ts': [
        ("'authFiles.export': 'Export',"),
        ("'authFiles.exported': 'Exported {name}',"),
        ("'authFiles.exportFailed': 'Export failed: {error}',"),
        ("'quota.plugin.pool': 'All accounts',"),
        ("'quota.plugin.poolDetail': '{count} accounts · {remain} of {size} left',"),
    ],
    'src/i18n/ja.ts': [
        ("'authFiles.export': 'エクスポート',"),
        ("'authFiles.exported': '{name} をエクスポートしました',"),
        ("'authFiles.exportFailed': 'エクスポートに失敗: {error}',"),
        ("'quota.plugin.pool': '全アカウント合計',"),
        ("'quota.plugin.poolDetail': '{count} アカウント · 残り {remain} / {size}',"),
    ],
}

for path, lines in AUTH_FILE_MESSAGES.items():
    append_messages(path, lines)

SVG_TITLE = '<svg fill="currentColor" fill-rule="evenodd" height="1em" style="flex:none;line-height:1" viewBox="0 0 24 24" width="1em" xmlns="http://www.w3.org/2000/svg"><title>%s</title>%s</svg>\n'

# Per-provider icons for the credential list and the plugin OAuth cards.
# The PNGs are the real brand logos (64px) taken from each plugin's `logo`
# metadata, embedded here so regenerating the patch stays offline.
PLUGIN_LOGOS = {
    'trae.png': (
        'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABVUlEQVR42mPk4ub9zzCEARPDEAejHhj1wKgHRj0w'
        '6oFRD4x6YCABCyEF/GEGA+rAj6suUOYByX7/Qe2B0Tww6gFaZ2J08GXnTYaX9Tto4hixBg8GXg912nrg78cfDL8f'
        'f6CJB/59+jGaByg3kI+DKmoGxAOssgIMirvSGUSK7fE6Xm5NPNXqFxZqOl5udTwDq6wAg0iRAwMDAwPDm96DWB3P'
        'oS3BwKEtwcDAwMDwvHDjwMcAsuNhQKTIASUmkB2P3EyhNCZom4mRRpwYoXhQZuLfjz8wPApdiFK8vuk9wPCmD5GE'
        '/n76wfAoZCHDz6svUNo5gyIJoXsC3fHYPEENx1M1E8M8cd9tJt4KCeaJv2RUWnTJA8TUptRy/GhNPCRaozekGzG6'
        'mBpP60djYNQDI7ZH9vvxB4aPqy4OGg8wjs6RjXpg1AOjHhj1wKgHRj0w6oER7AEAEeV5RSJorpwAAAAASUVORK5C'
        'YII='
    ),
    'qoder.png': (
        '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'
    ),
    'mimo.png': (
        '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'
    ),
}

for name, chunks in PLUGIN_LOGOS.items():
    target_path = os.path.join(ROOT, 'src', 'assets', 'icons', name)
    logo_bytes = base64.b64decode(''.join(chunks))
    with open(target_path, 'wb') as handle:
        handle.write(logo_bytes)
    print('wrote', name)

PLUGIN_GROUP_ICON = '<svg fill="currentColor" fill-rule="evenodd" height="1em" style="flex:none;line-height:1" viewBox="0 0 24 24" width="1em" xmlns="http://www.w3.org/2000/svg"><title>Plugins</title><path d="M20.5 11H19V7c0-1.1-.9-2-2-2h-4V3.5C13 2.12 11.88 1 10.5 1S8 2.12 8 3.5V5H4c-1.1 0-2 .9-2 2v3.8h1.5c1.49 0 2.7 1.21 2.7 2.7s-1.21 2.7-2.7 2.7H2V20c0 1.1.9 2 2 2h3.8v-1.5c0-1.49 1.21-2.7 2.7-2.7s2.7 1.21 2.7 2.7V22H17c1.1 0 2-.9 2-2v-4h1.5c1.38 0 2.5-1.12 2.5-2.5S21.88 11 20.5 11z"/></svg>\n'
with open(os.path.join(ROOT, 'src', 'assets', 'icons', 'plugin.svg'), 'w', encoding='utf-8', newline='') as handle:
    handle.write(PLUGIN_GROUP_ICON)
print('wrote plugin.svg')
