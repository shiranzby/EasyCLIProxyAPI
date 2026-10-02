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

replace('src/pages/ManagementPages.tsx', [
    ("type OAuthProviderId = 'codex' | 'claude' | 'antigravity' | 'kimi' | 'xai' | 'devin';",
     "type OAuthProviderId =\n"
     "  | 'codex'\n"
     "  | 'claude'\n"
     "  | 'antigravity'\n"
     "  | 'kimi'\n"
     "  | 'xai'\n"
     "  | 'devin'\n"
     "  | 'workbuddy'\n"
     "  | 'trae'\n"
     "  | 'qoder'\n"
     "  | 'zcode'\n"
     "  | 'mimo';"),
    ("import kimiIcon from '../assets/icons/kimi-light.svg';",
     "import kimiIcon from '../assets/icons/kimi-light.svg';\n"
     "import workbuddyIcon from '../assets/icons/workbuddy.png';\n"
     "import traeIcon from '../assets/icons/trae.svg';\n"
     "import qoderIcon from '../assets/icons/qoder.svg';\n"
     "import zcodeIcon from '../assets/icons/zcode.png';\n"
     "import mimoIcon from '../assets/icons/mimo.svg';"),
    ("  { id: 'devin' as const, name: 'Devin OAuth', icon: devinIcon },\n];",
     "  { id: 'devin' as const, name: 'Devin OAuth', icon: devinIcon },\n"
     "  { id: 'workbuddy' as const, name: 'WorkBuddy OAuth', icon: workbuddyIcon },\n"
     "  { id: 'trae' as const, name: 'Trae OAuth', icon: traeIcon },\n"
     "  { id: 'qoder' as const, name: 'Qoder OAuth', icon: qoderIcon },\n"
     "  { id: 'zcode' as const, name: 'ZCode OAuth', icon: zcodeIcon },\n"
     "  { id: 'mimo' as const, name: 'MiMo OAuth', icon: mimoIcon },\n"
     "];"),
])

PLUGIN_ICON_IMPORTS = (
    "import workbuddyIcon from '../assets/icons/workbuddy.png';\n"
    "import traeIcon from '../assets/icons/trae.svg';\n"
    "import qoderIcon from '../assets/icons/qoder.svg';\n"
    "import zcodeIcon from '../assets/icons/zcode.png';\n"
    "import mimoIcon from '../assets/icons/mimo.svg';"
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
     "import pluginIcon from '../assets/icons/plugin.svg';"),
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
    ],
    'src/i18n/locales/en.ts': [
        ("'quota.plugin.packages': 'Package quota',"),
        ("'quota.plugin.packagesDetail': '{remain} of {size} left · {count} packages',"),
        ("'quota.plugin.regionDetail': '{remain} of {size} left',"),
        ("'quota.plugin.packCount': '{count} packages',"),
        ("'quota.plugin.checkin': 'Check-in credits',"),
        ("'quota.plugin.checkinDetail': '+{today} today · {total} total · {streak} day streak',"),
    ],
    'src/i18n/ja.ts': [
        ("'quota.plugin.packages': 'パッケージ枠',"),
        ("'quota.plugin.packagesDetail': '残り {remain} / {size} · {count} パッケージ',"),
        ("'quota.plugin.regionDetail': '残り {remain} / {size}',"),
        ("'quota.plugin.packCount': '{count} パッケージ',"),
        ("'quota.plugin.checkin': 'チェックイン積分',"),
        ("'quota.plugin.checkinDetail': '本日 +{today} · 累計 {total} · {streak} 日連続',"),
    ],
}

ANCHOR = "'quota.service.error.missingConsumeAuthIndex'"
for path, lines in QUOTA_MESSAGES.items():
    full = os.path.join(ROOT, path)
    with open(full, 'r', encoding='utf-8', newline='') as handle:
        text = handle.read()
    if lines[0] in text:
        print('  already applied in %s' % path)
        continue
    anchor_lines = [line for line in text.splitlines() if line.strip().startswith(ANCHOR)]
    if len(anchor_lines) != 1:
        raise SystemExit('AMBIGUOUS ANCHOR in %s (%d matches)' % (path, len(anchor_lines)))
    anchor = anchor_lines[0]
    addendum = ''.join('  ' + line + '\n' for line in lines)
    text = text.replace(anchor, anchor + '\n' + addendum.rstrip('\n'), 1)
    with open(full, 'w', encoding='utf-8', newline='') as handle:
        handle.write(text)
    print('patched %s (messages)' % path)

SVG_TITLE = '<svg fill="currentColor" fill-rule="evenodd" height="1em" style="flex:none;line-height:1" viewBox="0 0 24 24" width="1em" xmlns="http://www.w3.org/2000/svg"><title>%s</title>%s</svg>\n'

ICONS = {
    'trae.svg': ('Trae', '<path d="M7 6h10v2.2H7V6zm3.9 0h2.2v12h-2.2V6z"/>'),
    'qoder.svg': ('Qoder', '<path d="M12 3a9 9 0 100 18 9 9 0 000-18zm0 3.4a5.6 5.6 0 110 11.2 5.6 5.6 0 010-11.2zM15.2 15.2l4.3 4.3-1.9 1.9-4.3-4.3 1.9-1.9z"/>'),
    'mimo.svg': ('MiMo', '<path d="M12 3a9 9 0 100 18 9 9 0 000-18zm0 3.2a5.8 5.8 0 110 11.6 5.8 5.8 0 010-11.6z" /><path d="M12 9.6a2.4 2.4 0 100 4.8 2.4 2.4 0 000-4.8z"/>'),
    'plugin.svg': ('Plugins', '<path d="M20.5 11H19V7c0-1.1-.9-2-2-2h-4V3.5C13 2.12 11.88 1 10.5 1S8 2.12 8 3.5V5H4c-1.1 0-2 .9-2 2v3.8h1.5c1.49 0 2.7 1.21 2.7 2.7s-1.21 2.7-2.7 2.7H2V20c0 1.1.9 2 2 2h3.8v-1.5c0-1.49 1.21-2.7 2.7-2.7s2.7 1.21 2.7 2.7V22H17c1.1 0 2-.9 2-2v-4h1.5c1.38 0 2.5-1.12 2.5-2.5S21.88 11 20.5 11z"/>'),
}

for name, (title, body) in ICONS.items():
    full = os.path.join(ROOT, 'src', 'assets', 'icons', name)
    with open(full, 'w', encoding='utf-8', newline='') as handle:
        handle.write(SVG_TITLE % (title, body))
    print('wrote', name)
