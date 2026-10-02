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

# The anchor must be matched as a whole line: the key also occurs mid-line inside
# the message values, and replacing there would split the entry in half.
ANCHOR = "'quota.service.error.missingConsumeAuthIndex'"


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

replace('src-tauri/capabilities/default.json', [
    ('    "dialog:allow-open"', '    "dialog:allow-open",\n    "dialog:allow-save"'),
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
        "                    <button type=\"button\" className=\"icon-button danger\" onClick={() => void deleteFile(file)}",
        "                    <button type=\"button\" className=\"icon-button quiet\" onClick={() => void exportFile(file)} disabled={busy || !readString(file, 'path')} title={t('authFiles.export')} aria-label={t('authFiles.export')}><FileDown size={15} aria-hidden=\"true\" /></button>\n"
        "                    <button type=\"button\" className=\"icon-button danger\" onClick={() => void deleteFile(file)}",
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
