# M02 evidence — Claude setup and workflow optimization

Evidence record for [M02](../../planning/claude-setup-optimization.md). This file records observations only. It is not an instruction source.

## Manager baseline — 24 September 2026

**Source:** main `07b3b10720ddd333ada807a56595f369263714fe`, tree `fda515b624c4916dbb7d037beec8e276a62b2e3b`, clean worktree. There were no open PRs; the latest merged PR was PR16.

**Host:** a Claude Code cloud session (Claude Code 2.1.281) in the environment shared with HDE work. Ubuntu, x86_64, 4 CPUs.

### Container toolchain as provided

| Tool | Observed |
|---|---|
| `python3` | 3.11.15 |
| `python3.12` | 3.12.3 |
| `node` / `npm` | 22.22.2 / 10.9.7 |
| Docker | Daemon unavailable (`/var/run/docker.sock` missing) |
| Playwright Chromium | Preinstalled revision 1194. Playwright 1.62.1 expects revision 1234 (Chrome 151.0.7922.34) |

`/root/.local/bin` is first on `PATH`. The `claude` binary is a native ELF executable.

### Inherited environment

Names were checked with a prefix filter; no values were read or printed. The environment injects `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT`. `PORT` has a 4–5 digit shape.

`GLOW_ENV=test .venv/bin/python manage.py check` run in that environment exited 1 with:

```text
ImproperlyConfigured: contradictory: inherited_connection (DATABASE_URL, GEO_API_KEY, HD_API_KEY)
```

`node scripts/smoke.mjs` exited 1. Both are the intended fail-closed behavior. On 24 September Nathan first reported that environments could not be separated, then confirmed that switching requires only a new session.

### Pinned toolchain sources

| Artifact | Verification | SHA-256 |
|---|---|---|
| `node-v24.19.0-linux-x64.tar.xz` from nodejs.org | Matches `SHASUMS256.txt`. That file's signature verified with key `5BE8A3F6C8A5C01D106C0AD820B1A390B168D356` (Antoine du Hamel), fetched from keys.openpgp.org and listed in the nodejs/node README release keys | `14b342e71204f811bde6153be8e04b62aef63c236fef92b55f9c83154b409647` |
| `Python-3.12.14.tgz` from www.python.org | GPG signature verified with key `7169605F62C751356D054A26A821E680E5FA6305` (Thomas Wouters), fetched from keys.openpgp.org | `6c6df908d2c3fd24e6d76869e92542abd0f33aec9dfc18df8875f89660286d43` |

- Python was built with `./configure --prefix=<scratch> --with-ensurepip=install`, `make -j4` and `make install`. The build took about 3 minutes from configure to install. `ssl`, `sqlite3`, `ctypes`, `lzma`, `bz2` and `zlib` imported (OpenSSL 3.0.13).
- Node 24.19.0 bundles npm 11.17.0. With it, `npm ci --ignore-scripts` on a copy of `apps/mobile` failed: `EBADENGINE`, Required `{"node":"24.19.0","npm":"11.9.0"}`, Actual npm `11.17.0`. After `npm install --global npm@11.9.0`, the install succeeded.
- Network observations: `nodejs.org`, `www.python.org`, `registry.npmjs.org` and `pypi.org` returned 200 from this environment. The python-build-standalone GitHub releases page returned 403. The official cloud-environment documentation read the same day lists `nodejs.org`, npm, PyPI and conda hosts in the Trusted defaults, but not `www.python.org` or a Playwright browser CDN.

### Checks on the pinned toolchain

The pinned toolchain was Python 3.12.14, Node 24.19.0 and npm 11.9.0. Python and smoke commands ran in a clean process environment: `env -i HOME=... PATH=<toolchain>:/usr/bin:/bin LANG=C.UTF-8`.

| Command | Result |
|---|---|
| `npm ci --ignore-scripts --prefix apps/mobile` | Exit 0; 670 packages; npm audit reported 14 moderate advisories (pre-existing) |
| `npm ci --ignore-scripts --prefix packages/contracts` | Exit 0; 20 packages; 0 vulnerabilities |
| `npm run check --prefix packages/contracts` | Exit 0; 373/373 |
| `npm run check --prefix apps/mobile` | Exit 0; typecheck, lint, 516/516 |
| `EXPO_OFFLINE=1 npm run check:expo` | Exit 0; dependencies up to date (offline-mode caveat printed) |
| `EXPO_OFFLINE=1 npm run export:development` | Exit 0; iOS/Android development bundles in `.work/native-export` |
| `python3 -m venv services/api/.venv` + `pip install --require-hashes -r requirements-dev.lock` + `pip check` | Exit 0; no broken requirements |
| `GLOW_ENV=test manage.py check` | No issues |
| `GLOW_ENV=test manage.py test tests --verbosity 2` | 250 tests OK |
| `ruff check .` / `ruff format --check .` / `mypy` | All passed / 57 files formatted / no issues in 29 files |
| `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests` | 38 tests OK |
| `GLOW_ENV=test python -m glow_persistence.static_check` | 32 app models; migrations 0001/0002 agree; no SQL/connection |
| `GLOW_ENV=test python smoke.py` | live 200, ready 503, recommendations 200 |
| `python3 -I -m unittest discover -s scripts -p 'test_change_scope.py'` | 8 tests OK (system Python 3.11.15) |
| `node scripts/smoke.mjs` | PASS (spawned loopback API; live 200, ready 503, writes 405) |
| `node --test scripts/smoke.test.mjs` | 1/1 |

**Rendered suite (informational only):** `npx playwright test` ran through an uncommitted scratch config that set `launchOptions.executablePath` to the preinstalled Chromium (revision 1194). Result: 83 passed in 4.0 minutes. This is not the pinned browser, so hosted CI remains the rendered-acceptance evidence. The scratch config was removed and the worktree was clean afterwards.

### Environment templates

- **`services/api/.env.example`** was copied to a temporary `.env` and loaded with `set -a; . .env; set +a` in a clean environment. With `glow_api.devserver --port 0`: live 200, ready 503, recommendations 200. With `PORT=8000` added, `glow_api.runtime.runtime_command` bound `127.0.0.1:8000`.
- **`apps/mobile/.env.example`** was tested with `expo config --type public` in a clean environment. Without `.env`, it refused with "development-only". With the template, the config resolved (`Glow Development`). With the optional API origin uncommented, it also resolved. The temporary `.env` was removed.

### Documentation and instruction observations

- Relative-link check over 73 tracked Markdown files found 21 broken targets, all in `docs/continuity/history/p05-2-handoff.md`. That file moved into `history/` without its relative paths being updated.
- `docs/operations/local-development.md` cites `.python-version` and `.node-version` as pin sources. Only `services/api/.python-version` exists; the Node pins live in package `engines` and the workflow. The guide also omits the npm 11.9.0 installation step.
- `apps/mobile/AGENTS.md` is Expo template guidance that recommends EAS build/submit/update. The repository blocks release builds, and store release is outside current authorization.
- Official Claude Code documentation (read 24 September) states the following. Subagents receive project `CLAUDE.md`. Imports resolve relative to the importing file. A cloud Setup script runs before Claude Code launches and its filesystem result is cached for about seven days. SessionStart hooks run on every session start and resume.
- The Notion Work Register (62 rows) was queried read-only. 47 rows cite the historical Drive plan as their Plan Reference. There is no D09, M01 or M02 row, and A03 shows Ready.

## Implementation session

*Reserved for M02-I1 results.*
