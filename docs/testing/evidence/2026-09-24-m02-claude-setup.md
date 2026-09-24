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

## App Manager 1 — publication, Setup script and handover

**Proposal commit.** `6b476941e569006638077b1b0333473dfd4f4f5d` (tree `f32f204974547e996edd7d5bb1c2218e8ddcaca2`) was pushed to `claude/ecstatic-goodall-qajdh4`, and [draft PR17](https://github.com/amthorn78/glow-dating-app/pull/17) was opened. Both hosted runs for that head passed all six jobs. `Change scope` classified the head as full scope, and all four application jobs ran.

| Run | Event | Jobs |
|---|---|---|
| [36019083905](https://github.com/amthorn78/glow-dating-app/actions/runs/36019083905) | push | 6/6 success |
| [36019116522](https://github.com/amthorn78/glow-dating-app/actions/runs/36019116522) | pull request | 6/6 success |

These runs cover the proposal head only, not later heads.

**`scripts/bootstrap-toolchain.sh`.** The npm tarball pin (`sha512-BBZoU926…YdNaA==`) is the `dist.integrity` value from registry metadata for `npm@11.9.0`. All runs used `env -i HOME=<temporary> PATH=/usr/bin:/bin LANG=C.UTF-8`, with no proxy or CA variables.

| Test | Result |
|---|---|
| `bash -n` | Syntax OK |
| Fresh run (default prefix and links) | Exit 0 in 96 s: Node 24.19.0, npm 11.9.0 (offline install of the verified tarball), CPython 3.12.14 (`--with-ensurepip=install --disable-test-modules`, `make -j4`) |
| Rerun | Exit 0 in 0 s; reported both components already installed |
| Links | `node`, `npm`, `npx`, `python3.12` → versions v24.19.0 / 11.9.0 / 11.9.0 / 3.12.14. `python3` unchanged (3.11.15). `ssl` reported OpenSSL 3.0.13 |
| Scratch copy with a wrong `NODE_SHA256` | Exit 1, `Node archive SHA-256 mismatch`; 0 toolchain entries extracted |
| Script supplied on stdin (`bash -s < script`, as a pasted Setup script) | Exit 0 |
| Unknown option | Exit 1 with usage |
| API suite on a venv from this Python build, `requirements-dev.lock` installed with hashes | 250 tests OK |

Direct HTTPS to nodejs.org without `HTTPS_PROXY` returned 200 in this environment. The script has not yet run as an actual environment Setup script; App Manager 2 verifies that result.

**Superseded subagent attempt.** App Manager 1 first commissioned M02-I1 as an Agent-tool subagent with worktree isolation. The harness created its worktree from `main` (`07b3b10`), not from the manager branch head (`6b47694`). The subagent stopped at its start gate. It made no edits or commits, and the worktree was removed. Nathan then fixed the manual relay, recorded verbatim in `docs/planning/manager-workflow.md`: the manager never starts implementation or review work itself, and implementation sessions may use any tools they need.

**Documentation exemption change.** At Nathan's direction, `scripts/change_scope.py` treats any change made only of regular Markdown files as ordinary documentation. Before the change, only the inert evidence allowlist was exempt; proposal head `6b47694`, which touched only `docs/`, ran all six jobs.

- `env -i ... python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v` on Python 3.12.14 ran 9 tests OK. The two new tests are Markdown anywhere → ordinary, and scripts/configuration/non-Markdown/uppercase `.MD`/mixed → full. The existing symlink/executable, renamed-code, hidden-code, trusted-policy substitution, fail-closed and merge-base cases are kept.
- `ruff check` on both files reported 9 findings, the same count as `main`'s versions: pre-existing line-length/import style. `scripts/` is not in CI's lint scope.
- A search of tests, application source, scripts, the workflow and the Dockerfile found nothing that reads Markdown. The only match is a code comment in `glow_persistence/models.py`.

## App Manager 2 — start verification (24 September 2026)

**Host:** a Claude Code cloud session in the dedicated `Glow app` environment. It is the first session there and runs as root (uid 0). Its working branch is `claude/fervent-darwin-idyko3`.

### Environment (names only)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `PORT` | Not set |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | Set and non-empty. The first two compared equal to the inventory's documented nonsecret values without being printed. For the secret, only presence was tested |
| Proxy and CA names present | `HTTPS_PROXY`, `https_proxy`, `NO_PROXY`, `SSL_CERT_FILE`, `NODE_EXTRA_CA_CERTS`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`. Values not read |

### Setup script — first real run

The toolchain directories were created at 16:02–16:03 UTC, just before this session started, so the environment's Setup script ran for this container.

| Check | Result |
|---|---|
| `command -v node npm npx python3.12` | All in `/root/.local/bin` |
| Link targets | Under `/root/.local/share/glow-app-toolchain/`: `node` → `node-v24.19.0-linux-x64/bin/node`; `npm` and `npx` → that tree's `lib/node_modules/npm/bin/npm-cli.js` and `npx-cli.js`; `python3.12` → `python-3.12.14/bin/python3.12` |
| Versions | `node` v24.19.0, `npm` 11.9.0, `python3.12` Python 3.12.14 |
| `python3` | `/usr/local/bin/python3`, Python 3.11.15 (unchanged) |
| Standard library | `bz2`, `ctypes`, `lzma`, `sqlite3`, `ssl`, `zlib` import. OpenSSL 3.0.13 |
| Ownership: Node tree | uid:gid 1000:1000 (`ubuntu:ubuntu`; that account exists in this container) on 3401 entries. They include the tree root, `bin/`, `bin/node` (mode 755), `bin/corepack`, `include/`, `lib/`, `lib/node_modules/` and `share/` |
| Ownership: npm | The reinstalled npm is root-owned on 2271 entries, including the `bin/npm` and `bin/npx` links and `lib/node_modules/npm` |
| Ownership: Python tree | No entries with a non-root owner |

**Ownership observation.** `tar` running as root keeps the archive's numeric owners, so the extracted Node tree belongs to a non-root account while root executes its binaries. The npm install and the Python `make install` run as root, so their files are root-owned. npm's files, however, sit in directories uid 1000 can write (`bin/`, `lib/node_modules/`), so that account can replace them as well. This was passed to M02-I1 to evaluate and fix.

### Network

Status codes only, for `https://nodejs.org/dist/v24.19.0/SHASUMS256.txt`, `https://www.python.org/ftp/python/3.12.14/` and `https://registry.npmjs.org/npm/11.9.0`:

- through the session's proxy configuration: each returned 200;
- directly, under `env -i HOME=/tmp PATH=/usr/bin:/bin`: each returned 200.

### Repository, classification and replacement PR

- **Remote state.** main was `07b3b10720ddd333ada807a56595f369263714fe` (PR16). The only open PR was draft PR17, head `a335c4fa621bcb3b756dc8ed44289a1dddda7eb1`, five commits ahead of main.
- **Trusted-base classification.** `main`'s `scripts/change_scope.py` was extracted to a temporary directory outside the worktree and run with `python3 -I … --base 07b3b10… --head a335c4f… --merge-base`. Result: `{"full": true, "reason": "behavior-or-empty"}` with 17 paths. That set includes `scripts/bootstrap-toolchain.sh`, `scripts/change_scope.py` and `scripts/test_change_scope.py`, and no `.github/` path. The complete classifier diff was read.
- **Branch and PRs.**
  - `claude/fervent-darwin-idyko3` was fast-forwarded from `07b3b10` to `a335c4f` with no changes and pushed.
  - [Draft PR18](https://github.com/amthorn78/glow-dating-app/pull/18) was opened as the replacement.
  - PR17 was closed with a [link comment](https://github.com/amthorn78/glow-dating-app/pull/17#issuecomment-5817767473).

### PR17 hosted runs

The workflow's concurrency group is per ref with `cancel-in-progress: true`.

| Head | Push run | PR run |
|---|---|---|
| `6b47694` | [36019083905](https://github.com/amthorn78/glow-dating-app/actions/runs/36019083905) success | [36019116522](https://github.com/amthorn78/glow-dating-app/actions/runs/36019116522) success |
| `c68b7b2` | [36020655609](https://github.com/amthorn78/glow-dating-app/actions/runs/36020655609) cancelled | [36020662524](https://github.com/amthorn78/glow-dating-app/actions/runs/36020662524) cancelled |
| `022929d` | [36020824519](https://github.com/amthorn78/glow-dating-app/actions/runs/36020824519) success | [36020836838](https://github.com/amthorn78/glow-dating-app/actions/runs/36020836838) **failure** |
| `6c45bd4` | [36022580663](https://github.com/amthorn78/glow-dating-app/actions/runs/36022580663) success | [36022589152](https://github.com/amthorn78/glow-dating-app/actions/runs/36022589152) success |
| `a335c4f` | [36024345357](https://github.com/amthorn78/glow-dating-app/actions/runs/36024345357) success | [36024353198](https://github.com/amthorn78/glow-dating-app/actions/runs/36024353198) success: all six jobs, including the rendered step (16:03:13–16:06:58 UTC) and the gate, read job by job |

**Failure preserved: PR run 36020836838 on `022929d`.**

- API checks, API mobile smoke and API artifact checks passed.
- Mobile [job 107706842358](https://github.com/amthorn78/glow-dating-app/actions/runs/36020836838/job/107706842358) failed at step "Render and exercise account onboarding": 82 passed, 1 failed, in 3.1 minutes. The Foundation gate failed as a consequence.
- **Failing case:** `rendered/state-corrections.spec.ts:45:7 › eligibility correction replaces an obsolete unsaved birth draft`. After `adult-date` was filled with `1992-07-16` and `eligibility-submit` was clicked, `expect(getByTestId('screen-birth').filter({ visible: true })).toBeVisible()` timed out after 10000 ms at line 57.
- **Logged diagnostics:** the visible screen was `screen-eligibility`. The birth-control diagnostics were `submitCount: 0`, no date or place fields, and `visibleAlertPresent: true`.
- The alert text is not in the log. The workflow uploads only the two layout screenshots, not Playwright's `error-context.md`.
- `022929d` changed no mobile files, and the push run for the same head passed.
- The same case failed with the same symptom on PR14's first PR attempt (run 35991614536). There, too, the parallel push run passed; see [AB1-R012](../../continuity/history/AB1-R012.md).
- Root cause unknown. It is not relabeled as an infrastructure failure.

## Implementation session

*Reserved for M02-I1 results.*
