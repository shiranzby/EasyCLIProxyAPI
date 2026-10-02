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

SVG_TITLE = '<svg fill="currentColor" fill-rule="evenodd" height="1em" style="flex:none;line-height:1" viewBox="0 0 24 24" width="1em" xmlns="http://www.w3.org/2000/svg"><title>%s</title>%s</svg>\n'

ICONS = {
    'trae.svg': ('Trae', '<path d="M7 6h10v2.2H7V6zm3.9 0h2.2v12h-2.2V6z"/>'),
    'qoder.svg': ('Qoder', '<path d="M12 3a9 9 0 100 18 9 9 0 000-18zm0 3.4a5.6 5.6 0 110 11.2 5.6 5.6 0 010-11.2zM15.2 15.2l4.3 4.3-1.9 1.9-4.3-4.3 1.9-1.9z"/>'),
    'mimo.svg': ('MiMo', '<path d="M12 3a9 9 0 100 18 9 9 0 000-18zm0 3.2a5.8 5.8 0 110 11.6 5.8 5.8 0 010-11.6z" /><path d="M12 9.6a2.4 2.4 0 100 4.8 2.4 2.4 0 000-4.8z"/>'),
}

for name, (title, body) in ICONS.items():
    full = os.path.join(ROOT, 'src', 'assets', 'icons', name)
    with open(full, 'w', encoding='utf-8', newline='') as handle:
        handle.write(SVG_TITLE % (title, body))
    print('wrote', name)
