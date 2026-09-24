# Environment inventory

The complete verified inventory is maintained in the [Claude handoff — environment-variable inventory](../continuity/claude-code-handoff.md#environment-variable-inventory), including exact code names, purpose, local/CI/deployment requirements, provisioning location and secret classification. This page is a stable entry point, not a duplicate table.

Safe local templates: [`services/api/.env.example`](../../services/api/.env.example) and [`apps/mobile/.env.example`](../../apps/mobile/.env.example). See [local setup](local-development.md) for their different loading behavior. The [configuration catalog](configuration.md) retains the detailed validator contract. Future provider slots are not active environment loaders; do not populate them until separately reviewed integration work introduces that behavior.

## Claude cloud environment `Glow app` (Nathan's settings, 24 September 2026)

This is the dedicated environment for every Glow app manager, implementation and review session. A session's environment is fixed when it starts; switching environments requires a new session, and variable changes reach only sessions started afterwards. Any command in any session in this environment can read its variables, so values that are secret are recorded here by name only.

| Setting | Value |
|---|---|
| Network access | Custom, with "Also include default list of common package managers" checked. Allowed domains: `www.python.org`, `docs.expo.dev`, `*.stream-io-api.com`, `getstream.io` |
| Setup script | `scripts/bootstrap-toolchain.sh`, pasted unchanged. Installs Node 24.19.0, npm 11.9.0 and CPython 3.12.14, linked in `$HOME/.local/bin`. Paste again whenever the file changes, not only its pins. See [local setup](local-development.md#claude-code-cloud-sessions) |
| HDE variables | None. `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` belong only to the HDE environment |

### Stream development application (getstream.io)

| Variable | Value | Classification |
|---|---|---|
| `STREAM_APP_ID` | `1729640` | Nonsecret application identity |
| `STREAM_API_KEY` | `qdstwyevnyea` | Client-safe identifier; not sufficient to authenticate a user |
| `STREAM_API_SECRET` | Held only in the environment settings; never recorded | **Secret.** Server-side signing/administration credential. Never print, copy or log it, and never expose it to mobile code or `EXPO_PUBLIC_*` |

- This is Nathan's **development** Stream application. It is for sandbox testing with synthetic users only. Production needs its own Stream application and secret, stored separately.
- **No code reads these names yet.** P06.1 will adopt them in the app's loader: they are the environment names for the future `GLOW_CHAT_API_SECRET` slot and the Stream API key and app ID.
- The fixture API does not reject `STREAM_*` names, so existing checks are unaffected. Plan, region, pricing and permission behavior are unverified until the P06.1 proof records them.
