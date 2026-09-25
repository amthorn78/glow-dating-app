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

**M02-I1**, 24 September 2026. A manual implementation session in the `Glow app` environment, running as root (uid 0). Branch `claude/eager-goodall-1zjgey`. The start gate ran `git fetch origin claude/fervent-darwin-idyko3` and `git merge --ff-only 9280bdc4666f48c0e89ae8b03e09818faec4419e` from main `07b3b10`, and `git rev-parse HEAD` printed `9280bdc4666f48c0e89ae8b03e09818faec4419e`.

Commits: `999bebc` (script), `d90ac9c` (pin-drift test), `16a6473` (documentation) and `fe26041` (mobile installer correction), followed by the commit that adds this section.

### Environment (names only)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | Present; values not read |
| `command -v node npm npx python3.12` | `/root/.local/bin/{node,npm,npx,python3.12}` |
| Versions | `node` v24.19.0, `npm` 11.9.0, `python3.12` Python 3.12.14 |
| Proxy and CA names | `HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS` and `SSL_CERT_FILE` are present. They were compared, without printing, to the loopback proxy and `/root/.ccr/ca-bundle.crt` described in the container's `/root/.ccr/README.md`, and matched |

The container's Setup-script toolchain showed the same ownership as App Manager 2 recorded: 3401 of 5672 Node-tree entries were uid:gid 1000:1000 (`ubuntu`), and the Python tree had no non-root entries.

Other observations:

- `/root` is mode 700, so in this container uid 1000 cannot reach the tree through `/root`.
- `/root/.local/bin/uv` and `uvx` are owned by 1001:117. They are part of the container image, not installed by the script, and are outside M02.

### Archive and script review

- **Archives.** `node-v24.19.0-linux-x64.tar.xz` records all 5779 entries as `iojs/iojs`, numerically 1000/1000. `Python-3.12.14.tgz` records 0/0. Neither archive has a group- or world-writable entry or a setuid or setgid bit. GNU tar 1.35 running as root restores recorded owners by default. That is the source of the uid-1000 Node tree.
- **Fast path.** The old fast path ran `bin/node --version` from an existing tree before any ownership check, and then kept the tree.
- **`--version` without a standard library.** `PYTHONHOME=/nonexistent python3.12 --version` printed `Python 3.12.14` and exited 0. The old Python fast path, which checked only `--version`, therefore accepted an install whose standard library was incomplete.
- **npm version check.** The old check ran `npm` through `PATH`. If the tree's `bin/npm` was missing, it could have run another npm; this container also has `/opt/node22/bin/npm` and `/usr/local/bin/npm`.

**Change (`999bebc`):**

- Both archives are extracted with `tar --no-same-owner --no-same-permissions` under `umask 022`.
- `trusted_tree` requires every entry to be owned by the running uid and no non-link entry to be group- or world-writable. It runs before anything in an existing tree executes. A failing tree is replaced from the hash-verified archive, not repaired in place, and the check is asserted again after installation.
- The Python fast path also imports `bz2, ctypes, lzma, sqlite3, ssl, zlib`.
- npm is checked through the tree's own `bin/npm`.
- Pins, hashes, URLs and linking are unchanged. The Setup script must be pasted again.

### Script checks

All runs used `env -i HOME=<temporary> PATH=/usr/bin:/bin LANG=C.UTF-8`, with no proxy or CA variables. The unmodified script (`9280bdc`) was run from a scratch copy.

| Test | Result |
|---|---|
| `bash -n scripts/bootstrap-toolchain.sh` | Exit 0 before and after the change |
| Fresh run, unmodified script | Exit 0 in 125 s. Node tree: 3401 entries 1000:1000 and 2271 entries 0:0. The 0:0 entries are the 2269 in `lib/node_modules/npm` plus the `bin/npm` and `bin/npx` links. Python tree: 4164 entries 0:0 |
| Fresh run, changed script | Exit 0 in 128 s. Node tree 5672 entries 0:0; Python tree 4164 entries 0:0. No group- or world-writable non-link entries and no setuid or setgid bits. Prefix, `.local`, `.local/bin` and the four links are 0:0. Linked versions: v24.19.0 / 11.9.0 / 11.9.0 (`npx`) / Python 3.12.14, OpenSSL 3.0.13 |
| Rerun (file) and rerun (`bash -s <` script, as a pasted Setup script) | Both exit 0, in 0.43 s and 0.50 s, reporting both components already installed. Inode and mtime of all 9837 prefix entries were unchanged |
| Unknown option `--bogus` | Exit 1 with usage |
| Scratch copy, wrong `NODE_SHA256` | Exit 1 in 0 s: `Node archive SHA-256 mismatch`. Nothing extracted; no links |
| Scratch copy, wrong `NPM_INTEGRITY` | Exit 1 in 4 s: `npm tarball SHA-512 mismatch`. The verified Node tree was extracted, still with its bundled npm (5779 entries); npm was not installed; no links. The next run rejects that tree through the npm version check |
| Scratch copy, wrong `PYTHON_SHA256` | Exit 1 in 9 s: `Python source SHA-256 mismatch`. No Python entries; no links |
| Temporary directories after the failures | None left under `/tmp` |
| Changed script on the unmodified script's output (uid-1000 Node tree) | Exit 0 in 10.8 s. Logged `replacing …/node-v24.19.0-linux-x64: it has entries owned by another account or writable by group or others`, re-extracted Node and kept Python (same `bin/python3.12` inode). Node 5672 entries 0:0. The next run was a no-op |
| uid-1000 Node tree with a planted `bin/node` wrapper that creates a marker file | Unmodified script: kept the tree and executed the planted binary as root (marker created). Changed script: replaced the tree without executing it (no marker); 0 non-root entries afterwards |
| One group-writable file (`lib/node_modules/npm/package.json`) in a root-owned Node tree | Changed script: replaced the tree; 0 group- or world-writable entries afterwards |
| `lib/python3.12/encodings` removed (simulated interrupted `make install`) | Unmodified script: exit 0 in 0 s, "Python 3.12.14 already installed", after which `python3.12 -c 'import ssl'` failed (`ModuleNotFoundError: No module named 'encodings'`). Changed script: rebuilt Python in 118 s; standard library usable; 4164 entries 0:0 |
| Changed script on this container's actual Setup-script toolchain (`env -i HOME=/root PATH=/usr/bin:/bin`) | Exit 0 in 10.0 s. The Node tree (3401 non-root entries) was replaced and Python kept (same inode). Afterwards both trees were entirely 0:0, versions v24.19.0 / 11.9.0 / 3.12.14, and a rerun was a no-op. The later checks below ran on this repaired toolchain |

### Pin-drift test

`services/api/tests/test_toolchain_pins.py` has three tests (Python, Node, npm). It reads the files and executes nothing. With `GLOW_ENV=test .venv/bin/python manage.py test tests.test_toolchain_pins` from `services/api`, three tests passed.

Temporary edits, each reverted, with `git status` confirming the revert:

| Edit | Result |
|---|---|
| `Dockerfile` tag 3.12.14 → 3.12.15 | FAILED (failures=1): `Python pins disagree (diverging files first): 3.12.15 in Dockerfile; 3.12.14 in scripts/bootstrap-toolchain.sh, services/api/.python-version, .github/workflows/foundation.yml` |
| `apps/mobile/package.json` `engines.npm` → 11.9.1 | FAILED: `npm pins disagree (diverging files first): 11.9.1 in apps/mobile/package.json engines.npm; 11.9.0 in scripts/bootstrap-toolchain.sh, apps/mobile/package.json packageManager, packages/contracts/package.json engines.npm, packages/contracts/package.json packageManager, .github/workflows/foundation.yml` |
| Script `NODE_VERSION` → 24.19.1 | FAILED: `Node pins disagree (diverging files first): 24.19.1 in scripts/bootstrap-toolchain.sh; 24.19.0 in apps/mobile/package.json engines.node, packages/contracts/package.json engines.node, .github/workflows/foundation.yml` |

All three messages come from the committed test (`d90ac9c`).

### Full suite on the pinned toolchain

Every command ran with `env -i HOME=/root PATH=/root/.local/bin:/usr/bin:/bin LANG=C.UTF-8` plus the variables shown.

| Command | Result |
|---|---|
| `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v` | Exit 0; 9 tests OK |
| `python3.12 -m venv services/api/.venv`; `pip install --require-hashes -r requirements-dev.lock` | Exit 0 in 11 s. pip 25.0.1 printed a newer-release notice |
| `pip check` | "No broken requirements found." |
| `GLOW_ENV=test manage.py check` | No issues |
| `GLOW_ENV=test manage.py test tests --verbosity 2` | Exit 0; **253 tests OK** (250 before + 3) in 9.8 s |
| `ruff check .` / `ruff format --check .` / `mypy` | All checks passed / 58 files already formatted / no issues in 29 source files |
| `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` | 38 tests OK |
| `GLOW_ENV=test python -m glow_persistence.static_check` | 32 app models; migrations 0001/0002; no SQL or connection |
| `GLOW_ENV=test python smoke.py` | live 200, ready 503, recommendations 200 |
| `npm ci --ignore-scripts --prefix apps/mobile` and `--prefix packages/contracts`, bare `env -i` | **Failed**: exit 1 after 72 s and 71 s. The debug logs show `http fetch GET https://registry.npmjs.org/… attempt 3 failed with SELF_SIGNED_CERT_IN_CHAIN`, then npm's `Exit handler never called!` |
| The same installs with `HTTPS_PROXY="$HTTPS_PROXY" NODE_EXTRA_CA_CERTS="$NODE_EXTRA_CA_CERTS"` added (values passed by reference, not printed) | Exit 0. Mobile: 670 packages in 28 s, 14 moderate advisories (pre-existing). Contracts: 20 packages in 2 s, 0 vulnerabilities |
| `npm run check --prefix packages/contracts` | Exit 0; 373/373 |
| `npm run check --prefix apps/mobile` | Exit 0 in 22 s; typecheck, lint, 516/516 |
| `EXPO_OFFLINE=1 npm run check:expo` | Exit 0; "Dependencies are up to date", with the offline-mode caveat |
| `EXPO_OFFLINE=1 npm run export:development` | Exit 0 in 29 s; iOS (1326 modules) and Android (1467 modules) development bundles in `.work/native-export` |
| `GLOW_SMOKE_PYTHON=… node scripts/smoke.mjs` | PASS (live 200, ready 503, writes 405) |
| `GLOW_SMOKE_PYTHON=… node --test scripts/smoke.test.mjs` | 1/1 |

**npm under `env -i`.** The environment re-terminates outbound TLS at its proxy (`/root/.ccr/README.md`). curl and pip use the system trust store, which holds the proxy CA, so the script's downloads and `pip install` succeeded without CA variables. Node uses its bundled CA store and needs `NODE_EXTRA_CA_CERTS`. App Manager 2's observation that direct HTTPS worked under `env -i` used curl; it does not extend to npm. The local-development guide now records the pass-through.

**Rendered suite (informational only).** `npx playwright test` ran through an uncommitted scratch configuration in the ignored `apps/mobile/.work/`. It extended `playwright.config.ts` with `launchOptions.executablePath` set to the preinstalled `/opt/pw-browsers/chromium` (revision 1194), under a clean process environment. Result: exit 0, 83 passed in 4.7 minutes, including both `state-corrections.spec.ts:45` cases ("… obsolete unsaved birth draft" in 2.9 s). This is not the pinned browser, and one local pass says nothing about the intermittent hosted failure. The scratch configuration was deleted afterwards. The web server printed an Electron `Running as root without --no-sandbox` fatal line; it did not affect the run.

### Documentation checks

- Relative-link check over every changed Markdown file, using a scratch checker for file targets and heading anchors that skips code: 11 files, 85 relative links, 0 broken. Before the change, all 21 relative links in `docs/continuity/history/p05-2-handoff.md` were broken, and all 21 now resolve. The rewrite changed only link targets: the file is identical to its previous version once link targets are masked.
- `git diff --check`: clean.
- **Expo installer.** In `apps/mobile`, `EXPO_OFFLINE=1 CI=1 npx expo install --check` without the wrapper exited 1: `app.config.ts` threw from `getConfig`. `EXPO_OFFLINE=1 CI=1 node scripts/development.mjs install --check` exited 0 ("Dependencies are up to date"). `apps/mobile/AGENTS.md` therefore runs Expo's installer through the wrapper, adding `npm_config_ignore_scripts=true`. `@expo/package-manager` spawns npm with the inherited process environment (`BasePackageManager`), which is why that setting reaches npm. This was established by reading the code; no package install was run.

### Classification

The trusted policy is `main`'s `scripts/change_scope.py`, extracted to a temporary directory and run with `python3 -I … --base 07b3b10720ddd333ada807a56595f369263714fe --head <head> --merge-base`. On head `16a6473` the result was `{"full": true, "reason": "behavior-or-empty"}` with 24 paths, including `scripts/bootstrap-toolchain.sh` and `services/api/tests/test_toolchain_pins.py`. The final head, which adds only Markdown on top of `16a6473`, was classified the same way before the push; that result is in the M02-I1 report.

### Limits

- No hosted CI result is recorded here. Pushing the session branch starts a Foundation push run on its head; its result is in the M02-I1 report, and a PR run follows only when the manager integrates. The Setup script has not yet run with the changed file as an actual environment Setup script; the closest test is the manual run on this container's Setup-script toolchain above.
- It is not known whether pasting a changed Setup script rebuilds the environment's cached filesystem. If a cache from the earlier script is reused, the changed script replaces the uid-1000 Node tree when it runs. If the Setup script does not run at all on a cached container, the tree stays as it is until the script runs.
- The script does not validate a pre-existing custom `--prefix` directory or `$HOME/.local/bin`. It creates the default prefix itself under the running account's `HOME`.
- The ownership check trusts files owned by the running account. It detects foreign ownership and group or world write access, not content changed by that same account.

## App Manager 2 — M02-I1 verification and integration (24 September 2026)

Nathan relayed the M02-I1 report: branch `claude/eager-goodall-1zjgey`, head `3a0726d`. App Manager 2 checked it against the pushed branch in the same `Glow app` environment. No HDE variable names were present, the three `STREAM_*` names were present, and the toolchain was v24.19.0 / 11.9.0 / 3.12.14.

| Check | Result |
|---|---|
| Remote head | `origin/claude/eager-goodall-1zjgey` is `3a0726d47248e40d9462d0dbb5ffc34f08ab4c5f`, tree `5892e40c196386106d796fd6483e93bd1597f87d`, as reported |
| Ancestry | The start SHA `9280bdc4666f48c0e89ae8b03e09818faec4419e` is an ancestor. There are five commits: `999bebc`, `d90ac9c`, `16a6473`, `fe26041`, `3a0726d` |
| Changed paths | 13 files, +366/−60. All are within the brief's owned paths except `apps/mobile/README.md`: a one-line comment, disclosed in the report and accepted. No manager-owned file, application code, dependency manifest or lock, workflow, `.env.example`, classifier or `Dockerfile` changed. The script stays mode 100755 and the new test is 100644 |
| Diff read | Complete. **Script:** both archives are extracted without their recorded owners or permissions under `umask 022`; `trusted_tree` runs before anything in an existing tree executes; a failing tree is re-extracted rather than repaired; the Python fast path imports the required modules; npm is checked through the tree's own `bin/npm`; the trust check is asserted after installation. **Test:** reads files only and names the diverging file. **Documentation:** as briefed |
| Evidence section | A single hunk, confined to "Implementation session" |
| `docs/continuity/history/p05-2-handoff.md` | Identical to its previous version once link targets are masked. 21 of 39 targets changed, and all of them resolve |
| Manager re-runs | `bash -n` exit 0. Pin test: 3 tests OK (`python3.12 -m unittest tests.test_toolchain_pins` from `services/api`, clean process environment). Classifier tests: 9 OK (`python3.12 -I`). `git diff --check` clean. A first pin-test attempt with `python3.12 -I` could not import `tests`, because isolated mode leaves the working directory off `sys.path`. That was the manager's invocation, not a test defect |
| Classification | `main`'s policy, run with `python3 -I … --merge-base` on head `3a0726d`: `{"full": true, "reason": "behavior-or-empty"}`, 24 paths |
| Hosted CI | Push run [36030512434](https://github.com/amthorn78/glow-dating-app/actions/runs/36030512434) on `3a0726d` succeeded on all six jobs, read job by job. The implementer's report quotes 253 API tests and 83/83 rendered cases from its logs |

**Integration.** `git merge --ff-only 3a0726d47248e40d9462d0dbb5ffc34f08ab4c5f` on `claude/fervent-darwin-idyko3`. No manager push had moved the branch since the start SHA. The manager commit that adds this section also updates the brief, the manager workflow and the current handoff, and adds the review prompt.

**Corrections to the M02-I1 prompt, accepted from the implementer:**

1. The prompt's `npx expo install` guidance fails as written, because `app.config.ts` rejects a bare Expo CLI run. The wrapper form is used instead.
2. App Manager 2's statement that direct HTTPS works under `env -i` came from curl probes only. In this environment npm also needs `NODE_EXTRA_CA_CERTS` and the proxy variable.

**PR18 CI before integration (head `9280bdc`):**

- [PR run 36025924316](https://github.com/amthorn78/glow-dating-app/actions/runs/36025924316) succeeded on all six jobs.
- [Push run 36025919795](https://github.com/amthorn78/glow-dating-app/actions/runs/36025919795) failed Mobile checks at 82/83 rendered cases. The failing case was `rendered/onboarding.spec.ts:103` ("private birth journey validates input, preserves uncertainty and stops before profile discovery"): after `birth-submit`, `screen-remaining` did not appear within 10 s (line 113). The gate failed as a consequence.
- `9280bdc` changed only Markdown.
- A failed-jobs-only re-run requested through the manager's GitHub integration returned `403 Resource not accessible by integration`. This is stated on [PR18](https://github.com/amthorn78/glow-dating-app/pull/18#issuecomment-5817984693).
- This is the third intermittent rendered failure of one kind: a form submit that does not advance to the next screen.

**Reasoning-level tracking.** At Nathan's direction, the manager scores each prompt with the TypeSafe effort scorer v4 beside its own call. The method is PE37's frozen v4, and the uses are in the Notion page *TypeSafe effort scorer — Glow app usage log*.

- The first v4 request, for M02-I1, returned 403 `authentication_error`.
- After Nathan added the API credential, the identical request returned HTTP 200 in the already-running session. The result: Score 2.55, P(high) 0.41, P(extra high) 0.57, which reads as extra high. The manager's call was high.
- Nathan ran extra high. The recorded outcome is adequate, and the better call is TypeSafe.

## App Manager 2 — exact-head review relay (24 September 2026)

**Review.** Nathan ran the review session at the extra-high level on `ccebd1bf5eb23155fec17ef7670164e5431d3849`.

- Its start gate, merge base (`07b3b10`) and trusted-base classification (full scope, 25 paths) matched the manager's.
- Verdict: approve for merge, with nothing blocking.
- Findings: six should-fix, one residual risk and several nits.
- The session reports it changed nothing in the repository or on GitHub.

**Hosted CI on `ccebd1b`.** [Push run 36037425892](https://github.com/amthorn78/glow-dating-app/actions/runs/36037425892) and [PR run 36037435481](https://github.com/amthorn78/glow-dating-app/actions/runs/36037435481) both succeeded on all six jobs. Read job by job, all four application jobs ran, including the rendered step, and the gate succeeded.

**Manager verification of the findings:**

| Finding | Manager check | Result |
|---|---|---|
| 1. Symlinks bypass `trusted_tree` | Read the code: `find` runs in its default mode, a symlink is judged by its own owner and its target is never examined | Confirmed |
| 2. CI's ruff reads Markdown | In a scratch venv installed from `requirements-dev.lock` (ruff 0.16.8), in `services/api`: `ruff format --check README.md` printed "1 file already formatted"; `ruff format --check .` printed 58 files; with `--extend-exclude '*.md'` it printed 57 | Confirmed. `pyproject.toml` holds only `[tool.ruff]`, `[tool.ruff.lint]` and `[tool.mypy]` settings |
| 3. A single merge base | Read the code: `git merge-base` without `--all` | Confirmed by reading; the reviewer's criss-cross repository was not rebuilt |
| 4. Push-run cancellation | `foundation.yml`: concurrency group `foundation-${{ github.ref }}` with `cancel-in-progress: true`; a push compares from `github.event.before`; the gate prints `Application checks passed` or `Ordinary documentation: application jobs intentionally skipped` | Confirmed from the workflow text |
| 5. Stale lines | `docs/planning/manager-workflow.md:108` and `docs/ephemeral/README.md:5` at `ccebd1b` | Confirmed |
| 6. Pin-test false passes | Read the patterns: single quotes only, and the exact `npm install --global` spelling | Confirmed by reading |
| 8. Missing `-I` | Read the code | Confirmed |
| 11. Mobile Expo command | `apps/mobile/scripts/development.mjs` passes every argument to the Expo CLI with the fixture environment | Confirmed; the wrapper form works |
| 13. PF01 table | A blank line separated the D08 and D09 rows | Confirmed |

**Facts gathered for the corrections:**

- The toolchain trees in this container have 12 symlinks in the Node tree and 8 in the Python tree. All are relative and resolve inside their tree.
- `/root` is mode 700. `/root/.local`, `/root/.local/bin`, `/root/.local/share` and the prefix are root-owned with mode 755.

**Correction to an earlier observation.** App Manager 1's search, in the section above, found nothing that reads Markdown. That missed ruff: the API job's `ruff format --check .` formats Markdown files, as finding 2 shows.

**Decisions:**

- **Nathan, 24 September:** Markdown under `.claude/` stays full scope, chosen when asked.
- **Nathan's policy:** one work item at a time, with the correction round belonging to M02.
- **The manager:** fix every finding except a workflow change inside M02, as correction round M02-C1, before merge. The Setup script is then pasted once.

The disposition table is in the brief.

## Correction session M02-C1

**M02-C1**, 24 September 2026. A manual implementation session in the `Glow app` environment, running as root (uid 0). Branch `claude/vigilant-einstein-i95w78`, created from main `07b3b10`. The start gate ran `git fetch origin claude/fervent-darwin-idyko3` and `git merge --ff-only 485756128bbd5bff2e6238bbbab5f11bde050c3a`, and `git rev-parse HEAD` printed `485756128bbd5bff2e6238bbbab5f11bde050c3a`.

Commits: `e9e5ac0` (classifier), `52a1ea9` (pin-drift test), `b3e3b20` (ruff exclusion), `435b31e` (mobile instructions), `f8c17db` (script), `c5893a5` (Setup-script bullets), followed by the commit that adds this section.

"Old" below means the file at `4857561`; "new" means this session's file. Old runs used a scratch copy of the old script.

### Environment (names only)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | Present; values not read |
| `command -v node npm npx python3.12` | `/root/.local/bin/{node,npm,npx,python3.12}` |
| Versions | `node` v24.19.0, `npm` 11.9.0, `python3.12` Python 3.12.14 |
| This container's Setup-script toolchain | Node tree: 3401 of 5672 entries `ubuntu:ubuntu` (uid 1000), 2271 root. Python tree: 4164 entries, all root. The environment still runs the Setup script from before M02-I1. The new script would replace that Node tree, so it was run only on a copy, and `/root/.local` was left as found |
| Tools used by the script | GNU bash 5.2.21, util-linux `setsid` 2.39.3, curl 8.5.0, GNU tar 1.35, GNU coreutils 9.4 |

### Script changes

| Finding | Change |
|---|---|
| 1. Symlinks | `trusted_tree` rejects a tree whose root is not a real directory (a symlink or a dangling link). Every symlink in the tree must have relative text that never climbs above the tree root, component by component, and must resolve (`realpath -e`) to a regular file inside the tree's real path. A dangling link fails `realpath -e`. The check runs before anything in the tree executes, as before |
| 8. Isolated Python | Both standard-library checks (the already-installed check and the post-build check) run `python3.12 -I` |
| 9. Directories | `safe_dir` stops the script unless the prefix directory and the link directory (`$HOME/.local/bin`) are owned by the running account and not writable by group or others. Every parent of each, up to `/`, must belong to root or the running account and must not be writable by group or others unless it has the sticky bit (`/tmp`). The prefix is resolved to its physical path once, and only that path is used afterwards, including in the links. The link directory is found again through `PATH` at every lookup, so its path may not contain a symlink (its logical and physical paths must agree). Both checks run before any tree is inspected or executed |
| 10. Robustness | `unset CDPATH` at the top, and the prefix is resolved with `cd -P -- … && pwd -P`. `curl -q` is the first option (ignores `~/.curlrc`), with `--connect-timeout 30` and stall protection `--speed-limit 1024 --speed-time 60`, and no total time limit. curl documents a stall abort as a timeout, which `--retry 3` retries; this was not exercised here. Downloads, both extractions, the npm install and the three Python build steps run through `run`: a background `setsid` step in its own process group that the script waits for. `SIGINT` and `SIGTERM` stop that whole group (TERM, up to 5 s, then KILL), remove the temporary directory, print a message and re-raise the signal. npm is installed through the tree's own `bin/npm`. `set +m` keeps background steps from being process-group leaders, so `setsid` does not fork |
| 13. Timing text | The header and the build log line say about two minutes |
| Not in the review | `export NODE_DISABLE_COMPILE_CACHE=1`; see "Node compile cache" below |

Pins, hashes and URLs are unchanged. The script remains mode 100755.

### Script checks

All runs used `env -i HOME=<temporary> PATH=/usr/bin:/bin LANG=C.UTF-8`, plus the variables named, with no proxy or CA variables. The final battery ran on the committed script (`git hash-object` `450b3cf6504dd0ab13ae2932d8da5a5346319c81`). Old-script results come from earlier runs in this session.

| Test | Result |
|---|---|
| `bash -n` | Exit 0 |
| Fresh run into an empty temporary `HOME` (mode 700, 0:0) | Exit 0 in 98.7 s. Node tree 5672 entries and Python tree 4164 entries, all 0:0, with 12 and 8 symlinks. No group- or world-writable non-link entries and no setuid or setgid bits. `.local`, `.local/bin`, `.local/share` and the prefix are 0:0 with mode 755, and the four links are 0:0. Linked versions: v24.19.0 / 11.9.0 / 11.9.0 (`npx`) / Python 3.12.14, OpenSSL 3.0.13. `python3` was unchanged (`/usr/bin/python3`, 3.11.15) |
| Rerun from the file, and from `bash -s <` the file | Both exit 0 in 0.6 s, reporting both components already installed. Inode and mtime of all 9837 prefix entries were unchanged |

**Adversarial cases.** A "stand-in" is a `bin/node` shell script that appends a line to a marker file and prints the pinned versions. The old script's run counts come from its own runs.

| Case | Old script | New script |
|---|---|---|
| A. Node tree root is a root-owned symlink to a copy whose `bin/node` is a stand-in | Exit 0 in 0.1 s; kept the tree; stand-in ran 4 times | Exit 0 in 7.8 s: "replacing … it breaks the ownership, permission or symlink rules", re-extracted. Stand-in not run. The root is a directory, and the symlink's former target was left in place |
| B1. `bin/node` is a root-owned absolute symlink to a uid-1000 stand-in outside the tree | Stand-in ran 4 times; kept | Replaced in 11.0 s; not run. 5672 entries, 0 non-root, 12 symlinks |
| B2. `bin/node` is `../../../../../../<outside>/evil-node` (relative, climbs out) | Stand-in ran 4 times; kept | Replaced in 11.7 s; not run |
| B3. `bin/corepack` dangles | Kept | Replaced in 11.8 s |
| B4. `bin/node` leaves the tree to a hop that points back to the real binary | Kept (ran the real binary) | Replaced in 11.6 s |
| C1. Prefix owned by uid 1000, holding a trusted-looking tree with a stand-in | Stand-in ran 4 times | Exit 1 in 0.0 s: "prefix directory … is not owned by the running account (uid 0)". Not run |
| C2 and C3. Prefix mode 775 and 757 | Stand-in ran 4 times each | Exit 1: "… is writable by group or others". Not run |
| C4. Prefix parent mode 777 | Stand-in ran 4 times | Exit 1: "… has an unsafe parent …: it must belong to root or the running account and must not be writable by group or others unless sticky". Not run |
| C6. Prefix parent owned by uid 1000 (755) | Stand-in ran 4 times | Exit 1, unsafe parent. Not run |
| C5. Prefix parent mode 1777, root-owned (sticky) | Not run | Exit 0 in 0.6 s; accepted |
| C7. `--prefix` is a symlink to a root-owned 755 directory | Not run | Exit 0 in 0.7 s; the reported paths use the physical directory |
| D1. `.local/bin` owned by uid 1000 (prefix elsewhere, with a stand-in) | Stand-in ran 4 times; links created there | Exit 1 in 0.0 s: "link directory … is not owned by the running account (uid 0)". Not run; no links |
| D2. `.local/bin` mode 777 | Same as D1 | Exit 1: "… is writable by group or others" |
| D3. `.local/bin` is a symlink to a root-owned 755 directory | Same as D1 | Exit 1: "link directory … must not be or pass through a symlink" |
| D4. `.local` is a symlink to a real directory | Same as D1 | Exit 1: same message as D3 |
| D5. `.local` mode 777 | Same as D1 | Exit 1: unsafe parent `.local` |
| E1. Python tree without the standard-library `ssl.py`; fake `ssl.py` on `PYTHONPATH` | Exit 0 in 0.4 s: "Python 3.12.14 already installed". Fake imported once; afterwards `python3.12 -I -c 'import ssl'` failed | Exit 0 in 149.2 s: rebuilt Python. Fake not imported. `ssl` works (OpenSSL 3.0.13); 4164 entries 0:0 |
| E2. Complete Python; fake `ssl.py` on `PYTHONPATH` | Fake imported once | Not imported; already installed |
| F1. Complete Python; `ssl.py` in the working directory | Fake imported once | Not imported; already installed |
| F3. Python without `ssl.py`; fake `ssl.py` in `~/.local/lib/python3.12/site-packages` | Fake imported once; the broken tree was kept | Rebuilt in 148.1 s; not imported |
| G. `--prefix tc --no-link` from `work/`, with `CDPATH` set to a directory that also holds `tc/` with a stand-in | Exit 2 in 0.7 s. The prefix became that other `tc` path twice, joined by a newline, and `tar` failed: "Cannot open: No such file or directory" | Exit 0 in 0.6 s; `work/tc` used; stand-in not run |

E1 and F3 ran in parallel, so each rebuild shared the 4 CPUs with the other. A first attempt at the E and F cases wrote a malformed fake module (a `printf` error in the test helper); those runs were discarded and repeated as above.

**Wrong hashes** (scratch copies of the new script, each with its own `TMPDIR`):

| Copy | Result |
|---|---|
| Wrong `NODE_SHA256` | Exit 1 in 0.6 s: "Node archive SHA-256 mismatch". Nothing extracted; no links; `TMPDIR` empty |
| Wrong `NPM_INTEGRITY` | Exit 1 in 5.2 s: "npm tarball SHA-512 mismatch". The verified Node tree was extracted with its bundled npm (5779 entries); npm was not installed; no links; `TMPDIR` empty |
| Wrong `PYTHON_SHA256` (Node already present) | Exit 1 in 0.8 s: "Python source SHA-256 mismatch". No Python entries; no links; `TMPDIR` empty |
| Unknown option `--bogus` | Exit 1 with usage |

**Interruption during the Python build.** Each run had the Node tree pre-copied, its own `TMPDIR` and its own session. It was started by a launcher that restores the default `SIGINT` disposition, because background jobs start with it ignored. The signal was sent to the script's pid once the `configure` and `make` logs existed and a compiler was running in the build directory.

| | Old, `SIGTERM` | New, `SIGTERM` | New, `SIGINT` |
|---|---|---|---|
| Live processes working under `TMPDIR` at the signal | 9 | 10 | 7 |
| Script exit | 143 after 0.10 s | 143 after 0.27 s | 130 after 0.19 s |
| Live processes under `TMPDIR` 2 s later | 4: `make`, `sh`, `gcc`, `cc1` | 0 | 0 |
| Processes left in the run's session | 4 | 0 | 0 |
| `TMPDIR` entries left | 2: a compiler temporary `cc01bRin.s` and `node-compile-cache`. The work directory itself was gone; bash ran the old `EXIT` trap on `SIGTERM`, while the build kept running in the deleted directory | 0 | 0 |
| Message | None | "stopped by SIGTERM; temporary files removed" | "stopped by SIGINT; temporary files removed" |

After both new-script interruptions the prefix held the complete Node tree, no Python directory (the script removes it before `configure`) and no links. The leftover old-script processes were killed after the observation.

An earlier version of the new script ran the Python steps as `run … >log 2>&1`. The handler then ran with its standard error in that step log, which it deleted, so the message was lost. The redirection now happens inside the step's own subshell. The result above is from the final script.

**Copy of this container's Setup-script toolchain.** `cp -a` of `/root/.local/share/glow-app-toolchain` into a temporary prefix. Before: Node tree 5672 entries, 3401 non-root, 12 symlinks; Python tree 4164 entries, 0 non-root, 8 symlinks. `--prefix <copy> --no-link` exited 0 in 9.1 s: it replaced the Node tree and kept Python. Afterwards both trees had 0 non-root entries, and a rerun was a no-op in 0.7 s. The real prefix (9837 entries: inode, mtime and owner) and `/root/.local/bin` (27 entries) were unchanged.

### Node compile cache (not in the review)

A run of the wrong-`PYTHON_SHA256` copy with its own `TMPDIR` left one entry there, `node-compile-cache`. npm 11 enables Node's compile cache in `$TMPDIR/node-compile-cache` when it starts, for example on `npm --version`.

- With a `node-compile-cache` directory pre-created in `TMPDIR`, owned by uid 1000 with mode 777, root's `npm --version` wrote 73 entries into it. That is compiled code read back from outside the checked trees.
- With `NODE_DISABLE_COMPILE_CACHE=1`, `npm --version` left 0 entries in `TMPDIR`.
- This container already has a root-owned `/tmp/node-compile-cache`, created at 16:02 by its Setup-script run.

The script now exports `NODE_DISABLE_COMPILE_CACHE=1` for every Node and npm process it starts. Afterwards the wrong-hash copy left 0 entries in `TMPDIR`.

### Classifier

- `env -i … python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v` on Python 3.12.14: **13 tests OK** (9 before). The same command with the system `python3` (3.11.15): 13 OK.
- New tests:
  - A criss-cross history with increasing commit dates. `git merge-base --all` returns two bases, the code commit and the documentation commit. From one base the diff is documentation only, and from the other it includes `app.py`. The result is `{"full": true, "reason": "multiple-merge-bases"}`.
  - Unrelated histories give `comparison-unavailable`.
  - `.claude/agents/helper.md`, `.claude/skills/x/SKILL.md`, `.claude/commands/deploy.md`, `docs/.claude/x.md`, `apps/mobile/.claude/rules/r.md`, `.CLAUDE/agents/helper.md`, `.Claude/skills/x/SKILL.md`, and `.claude/agents/helper.md` with `docs/planning/brief.md` are full scope.
  - `CLAUDE.md`, `AGENTS.md`, `apps/mobile/CLAUDE.md`, `docs/continuity/claude-code-handoff.md`, `docs/claude/notes.md`, `.claude.md`, `docs/.claude-notes/x.md` and `docs/claude.md/x.md` stay `ordinary-docs-only`.
  - The single-base test now also asserts one merge base and the reason.
- The committed tests run against the old classifier: 13 run, **9 failures**. There are 8 `.claude` subtests, plus the criss-cross test (`False is not true`), where the old classifier's single `git merge-base` picked the newest base, the code commit, and classified the history as ordinary documentation. The fixture's dates make git pick that base. The assertions do not depend on which base git picks.
- `ruff check` with the API configuration on both files: 7 E501 and 2 I001, the same counts as the old files (`scripts/` is not in CI's lint scope).

### Pin-drift test

`python3.12 -m unittest tests.test_toolchain_pins -v` from `services/api` in a clean process environment: 3 tests OK.

Each edit below was made to `.github/workflows/foundation.yml` and reverted with `git checkout`, and `git diff --quiet` confirmed the revert. The old test ran from its `4857561` source with `ROOT` pointed at this checkout.

| Edit | Old test | New test |
|---|---|---|
| Line 66 `python-version: 3.13.1` (unquoted) | OK (false pass) | FAILED: `Python pins disagree (diverging files first): 3.13.1 in .github/workflows/foundation.yml:66; 3.12.14 in scripts/bootstrap-toolchain.sh:46, services/api/.python-version, .github/workflows/foundation.yml:134, Dockerfile:3` |
| Line 95 `node-version: "24.20.0"` | OK (false pass) | FAILED: `Node pins disagree (diverging files first): 24.20.0 in .github/workflows/foundation.yml:95; 24.19.0 in scripts/bootstrap-toolchain.sh:42, apps/mobile/package.json engines.node, packages/contracts/package.json engines.node, .github/workflows/foundation.yml:137` |
| Line 97 `npm i -g npm@11.10.0` | OK (false pass) | FAILED: `npm pins disagree (diverging files first): 11.10.0 in .github/workflows/foundation.yml:97; 11.9.0 in scripts/bootstrap-toolchain.sh:44, apps/mobile/package.json engines.npm, apps/mobile/package.json packageManager, packages/contracts/package.json engines.npm, packages/contracts/package.json packageManager, .github/workflows/foundation.yml:140` |
| Line 97 `npm install npm@11.10.0 --global` (flag after) | OK (false pass) | FAILED: `.github/workflows/foundation.yml: 1 npm install pins recognized for 2 'actions/setup-node@' matches` |
| Line 134 `python-version-file: services/api/.python-version` | OK (false pass) | FAILED: `.github/workflows/foundation.yml: 1 python-version pins recognized for 2 'actions/setup-python@' matches` |
| Line 140 npm install replaced by `echo skipped` | OK (false pass) | FAILED: `.github/workflows/foundation.yml: 1 npm install pins recognized for 2 'actions/setup-node@' matches` |

The npm count invariant: Node 24.19.0 bundles npm 11.17.0, so every job that sets up Node must install the pinned npm once. The recognized npm installs must therefore equal both the `actions/setup-node@` uses and the `npm@` references in the workflow. A spelling the pattern does not parse then changes a count instead of passing unseen.

### Ruff

In `services/api`, with ruff 0.16.8 from `requirements-dev.lock`:

| Command | Result |
|---|---|
| `ruff format --check .` (new configuration) | 57 files already formatted, exit 0 |
| `ruff check .` | All checks passed |
| `ruff format --check --config <old pyproject.toml> .` | 58 files already formatted |
| With a temporary `TEMP-ruff-markdown-check.md` containing an unformatted Python block, old configuration | exit 1: 1 file would be reformatted, 58 files already formatted |
| The same file, new configuration | 57 files already formatted, exit 0; `ruff check .` passed |

The temporary file was deleted, and `git status` showed only the intended changes.

### Mobile instruction

`apps/mobile/scripts/development.mjs` runs `node_modules/expo/bin/cli` with all its arguments, with `GLOW_APP_ENV=development` and `EXPO_PUBLIC_GLOW_MODE=fixture`, and refuses other values. After `npm ci --ignore-scripts` (exit 0 in 24 s, with `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` passed by reference), `CI=1 EXPO_OFFLINE=1 node scripts/development.mjs run:ios --help` and `… run:android --help` each exited 0 with Expo's usage for that command. A bare `npx expo run:android --help` also printed help, because help does not load `app.config.ts`. This shows forwarding only. No native build or device run was performed.

### API suite on the pinned toolchain

Every command ran with `env -i HOME=/root PATH=/root/.local/bin:/usr/bin:/bin LANG=C.UTF-8` plus the variables shown.

| Command | Result |
|---|---|
| `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock` | Exit 0 in 61 s. pip 25.0.1 printed a newer-release notice |
| `pip check` | "No broken requirements found." |
| `GLOW_ENV=test manage.py check` | No issues |
| `GLOW_ENV=test manage.py test tests --verbosity 2` | Exit 0; **253 tests OK** in 7.7 s |
| `ruff check .` / `ruff format --check .` / `mypy` | All checks passed / 57 files already formatted / no issues in 29 source files |
| `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` | 38 tests OK |

### Documentation checks

- Relative-link check over the three changed Markdown files (`apps/mobile/AGENTS.md`, `docs/operations/local-development.md`, this record), using a scratch checker for file targets and heading anchors that skips code: 3 files, 9 relative links, 0 broken.
- `git diff --check 4857561 HEAD`: clean.
- Changed paths against `4857561`: the seven owned files above and this record. The script stays mode 100755; the Python files stay 100644.
- **Trusted-base classification.** `main`'s `scripts/change_scope.py` (`07b3b10`) was extracted to a temporary directory and run with `python3 -I … --base 07b3b10720ddd333ada807a56595f369263714fe --head c5893a5cb2abbc463314eb7fc1ea84b3be4a79cf --merge-base`. The result was `{"full": true, "reason": "behavior-or-empty"}` with 29 paths, including all three scripts, `services/api/pyproject.toml` and the pin test. `git merge-base --all` returned one base. The final head adds only this Markdown section; its classification is in the M02-C1 report.

### Limits

- **The Setup script changed and must be pasted once after M02 merges.** The script has not run as an actual environment Setup script. The closest test is the run on a copy of this container's Setup-script toolchain above. This container's Node tree stays uid-1000-owned until the new script runs here.
- **Parent directories:** the check runs up to `/`. It trusts root-owned parents and sticky directories. `TMPDIR`, where `mktemp -d` creates the private work directory (mode 700), is not checked.
- **Unchanged scope:** the ownership check still trusts content owned by the running account. Files inside the link directory are not checked. `/root/.local/bin/uv` and `uvx` are owned by 1001:117 here; they come from the container image and are outside M02.
- **Signals:**
  - Only `SIGINT` and `SIGTERM` are handled; `SIGKILL` cannot be, and `SIGHUP` was not tested.
  - A signal that arrives during a short foreground command (`find`, `sha256sum`, `rm`, a `--version` check) takes effect when that command ends.
  - One gap is not covered: a signal between starting a step and recording its pid.
  - An interruption during `make install` was not tested in this session. It leaves a partial Python tree, which the next run's import check rejects; the M02-I1 section tests that state with `encodings` removed.
  - Without `ps` or `awk`, the handler sends `KILL` right after `TERM`. This was established by reading the code, not tested.
- **`.claude` matching:** it ignores case only. Other filesystem aliases, such as HFS+ ignorable Unicode characters or Windows 8.3 short names, are not detected.
- **CI:** it loads the classifier from `main`, so the new classifier rules apply to later PRs only after M02 merges. No hosted CI result is recorded here. Pushing the session branch starts a Foundation push run.
- **Not run:** mobile checks beyond `npm ci` and the two help commands, and the rendered suite. The intermittent rendered cases were not touched.

## App Manager 2 — M02-C1 verification and integration (24 September 2026)

Nathan relayed the M02-C1 report: branch `claude/vigilant-einstein-i95w78`, head `9be8228`, run at the extra-high level. App Manager 2 checked it against the pushed branch in the `Glow app` environment. No HDE variable names were present, the three `STREAM_*` names were present, and the toolchain was v24.19.0 / 11.9.0 / 3.12.14.

| Check | Result |
|---|---|
| Remote head | `9be82285ca70668f427d0adb23ae68ae6b2faa2b`, tree `d7cdf41ed1e8662ee5c58e2b2bcdd2dea9e6feb7`, as reported |
| Ancestry | The start SHA `485756128bbd5bff2e6238bbbab5f11bde050c3a` is an ancestor. There are seven commits: `e9e5ac0`, `52a1ea9`, `b3e3b20`, `435b31e`, `f8c17db`, `c5893a5`, `9be8228` |
| Changed paths | 8 files, +489/−50, all within M02-C1's owned paths. The script stays mode 100755. `pyproject.toml` gained only `extend-exclude = ["*.md"]`. The `apps/mobile/AGENTS.md` change is the development-build line in "Rules", and the `local-development.md` change is the Setup-script bullets. The evidence change is one appended hunk |
| Script, read in full | `CDPATH` is unset and the Node compile cache disabled. The prefix and link directories are checked with their parents; the link directory's path may not contain a symlink. `trusted_tree` requires a real root directory, ownership by the running account, no group or other write, and relative symlinks that never climb above the root and resolve to regular files inside it; a `find` or link failure rejects the tree through `pipefail`. Nothing in an untrusted tree runs. The standard-library checks use `-I`. Long steps run in their own process group, and SIGINT and SIGTERM stop the group and remove the temporary directory. `curl -q` has a connection timeout and stall abort. npm is installed through the tree's own `bin/npm` |
| Classifier | A path component equal to `.claude`, ignoring case, is full scope. `git merge-base --all` returning anything other than exactly one base is full scope, reason `multiple-merge-bases`. Unrelated histories fail closed as `comparison-unavailable` |
| Manager re-runs, detached worktree at `9be8228` | `bash -n` exit 0. Classifier tests: 13 OK (`python3.12 -I`). Pin test: 3 OK. `ruff format --check .` in `services/api`: 57 files; `ruff check .` passed. `git diff --check 4857561 9be8228` clean |
| Regression direction (manager) | The new `scripts/test_change_scope.py`, copied beside `ccebd1b`'s `change_scope.py` in a temporary directory and run with `python3.12 -I -m unittest discover`: 13 tests, `FAILED (failures=9)`. The failures are the eight `.claude` subtests and the criss-cross test, so the new tests catch the old behavior |
| Pin-test demonstrations (manager) | The first `python-version` made unquoted `3.13.1` failed, naming `.github/workflows/foundation.yml:66`. The first npm install made `npm i -g npm@11.10.0` failed, naming `.github/workflows/foundation.yml:97`. Both edits were reverted and the worktree was clean |
| Classification | `main`'s policy, `python3 -I … --merge-base`: `{"full": true, "reason": "behavior-or-empty"}`, 29 paths, one merge base |
| Hosted CI | Push run [36049068606](https://github.com/amthorn78/glow-dating-app/actions/runs/36049068606) on `9be8228` succeeded on all six jobs, read job by job, including the rendered step. The gate log says `Application checks passed`, so under the push-run evidence rule it counts as evidence for code |

**Deviations accepted:**

- `NODE_DISABLE_COMPILE_CACHE=1`. npm 11 otherwise wrote compiled code into a `$TMPDIR` cache directory another account had created.
- The stricter symlink rule: relative links, never climbing above the root, and regular-file targets. All 20 real links pass.
- `.claude` matching ignores case.
- A symlinked `--prefix` is resolved to its physical path, while a symlinked link directory is refused.
- npm install output goes to a log that is printed on failure.
- Pin-test messages carry line numbers, and there are extra classifier tests for unrelated histories and the single-base reason.

**Limits carried forward:**

- `TMPDIR` is not checked; `mktemp -d` creates a directory only the running account can open.
- `.claude` aliases other than case are not detected, such as invisible Unicode characters or Windows short names.
- Files inside the link directory are not checked. In this container, `/root/.local/bin/uv` and `uvx` are owned by uid 1001 and come from the image; `/root` is mode 700.
- Only SIGINT and SIGTERM are handled.
- The new classifier rules apply to later PRs only after M02 merges.
- This container's own toolchain still has the uid-1000 Node tree from the pre-M02 Setup script, until the final script is pasted after merge.

**Integration.** `git merge --ff-only 9be82285ca70668f427d0adb23ae68ae6b2faa2b` on `claude/fervent-darwin-idyko3`; no manager push had moved the branch since the start SHA. A delta review of the final head against `ccebd1b` follows.

## M02 merge receipt — App Manager 2 (24–25 September 2026)

### Delta review relay

Nathan ran the delta review at the extra-high level on head `5e3fb2f3940486284822f398a39d4f233833eedd` and relayed its report. The report said it changed nothing in the repository or on GitHub.

- **Start gate and classification:** `ccebd1b` is an ancestor, and the only merge base is `07b3b10`. Main's classifier returned `{"full": true, "reason": "behavior-or-empty"}` over 30 paths.
- **Verdict:** approve for merge. All 13 findings of the `ccebd1b` review are resolved, and all six M02-C1 deviations are acceptable. It raised six new findings, all nits (N1–N6); the brief records their disposition.
- **Its checks:**
  - `bash -n`: exit 0. `shellcheck` 0.11.0 gave informational SC2015 notes only.
  - A fresh clean-environment run exited 0 in 98.7 s. Both trees were root-owned, with 12 and 8 relative links.
  - Reruns took 0.63 s and 0.60 s, with all 9837 prefix entries unchanged. The wrong Node and Python hashes exited 1 without extracting anything.
  - Adversarial cases A, B1–B5, C1–C7, D1–D5, E1, E2, F1, F2, G and J1 behaved as intended: refused, or replaced the tree without running the stand-in.
  - `SIGTERM` to the script or its process group left 0 processes and 0 temporary entries.
  - The classifier tests passed 13 of 13. Against `ccebd1b`'s classifier the same file gave `FAILED (failures=9)`.
  - The pin test passed 3 of 3, and three false-pass edits in a `git archive` copy failed as intended.
  - Pinned ruff 0.16.8 reported 57 files, and `ruff check` passed.
  - `git diff --check` was clean. The link check found 70 links and 0 broken. The secret scan was clean, and `STREAM_API_SECRET` appears by name only.
- **Its limits:**
  - Hosted CI was left to the manager.
  - `SIGINT`, curl's stall-and-retry path and a real environment Setup run were not exercised.
  - `.claude` look-alike names were reasoned about only.
  - In E1, a long temporary path hit the Unix socket path limit, so the rebuilt tree was smaller (2156 entries instead of 4164). The report attributes this to the test setup, not the script.

**Manager check of the relay.** App Manager 2 read each nit's cited lines at `5e3fb2f` and confirmed its premise. It did not re-run the adversarial cases.

- N1: `run()` starts every step with `setsid`.
- N2: the pin patterns also match inside YAML comments.
- N3: the inventory row stated usage as if it were a limit.
- N4: the M02-C1 "Signals" limit states that the import check rejects a partial install.
- N5: `AGENTS.md` line 13 lacked the `.claude` exception.
- N6: `extend-exclude = ["*.md"]` is a path glob.

**Corrections to earlier sections.** The earlier sections are left unchanged; these notes correct them.

- The M02-C1 "Signals" limit says an interrupted `make install` "leaves a partial Python tree, which the next run's import check rejects". The delta review found otherwise. A tree without `bin/python3`, the other `*3` links, pip and the man pages passed the fast path as "Python 3.12.14 already installed", although `python3.12 -m venv` still worked. The import check catches a missing standard-library module, not every partial install.
- The same limit says only that `SIGKILL` cannot be handled. Because each step runs in its own session, a `SIGKILL` sent to the script's process group also leaves the running step alive. The review counted 13 build processes and 5 temporary entries 2 s later; the pre-C1 script left no process running. `SIGHUP` to the group left nothing behind but printed no message.

### Hosted CI on the reviewed head

On `5e3fb2f`, [push run 36071229369](https://github.com/amthorn78/glow-dating-app/actions/runs/36071229369) and [PR run 36071232840](https://github.com/amthorn78/glow-dating-app/actions/runs/36071232840) succeeded on all six jobs. App Manager 2 read them job by job, and every step ran, including "Render and exercise account onboarding". Both gate logs say `Application checks passed`. The head had no other check runs.

### Merge and main verification

- **Merge:** App Manager 2 marked PR18 ready and merged it with a merge commit at 2026-09-24T23:59:26Z, with the expected head pinned to `5e3fb2f3940486284822f398a39d4f233833eedd`.
- **Merge commit:** `2b6c7dfdd10114407c610cce9f38a88ec35cd3ff`, with parents `07b3b10720ddd333ada807a56595f369263714fe` and `5e3fb2f3940486284822f398a39d4f233833eedd`.
- **Tree:** `e3032d54b2732abd9a59a9710f6e38652763e3b7`, the reviewed head's tree. `git diff 5e3fb2f origin/main` is empty.
- **Setup script on main:** `scripts/bootstrap-toolchain.sh` is blob `450b3cf6504dd0ab13ae2932d8da5a5346319c81`, mode 100755. This is the script Nathan pastes.
- **Main CI:** [push run 36075413521](https://github.com/amthorn78/glow-dating-app/actions/runs/36075413521) on `2b6c7df` succeeded on all six jobs. The rendered step ran from 00:01:39 to 00:05:25 UTC, and the gate log says `Application checks passed`.

### After the merge

- **The classifier is live.** CI now loads the M02-C1 classifier from `main`. This close-out changes only Markdown, outside any `.claude` directory, and is the first PR that classifier judges.
- **Pending owner action.** Nathan pastes `scripts/bootstrap-toolchain.sh` from `main` into the `Glow app` environment's Setup script once, unchanged. Until then, this container's toolchain keeps the uid-1000 Node tree: on 25 September, `find /root/.local/share/glow-app-toolchain ! -user 0 | wc -l` printed 3401. After the paste, the next session's Setup run should bring it to 0.
- **Reasoning levels.** For the delta review, the manager and TypeSafe both said extra high. TypeSafe's rule also flagged ultracode for the first time, with P(`single_session`) at 0.43. Nathan ran extra high without ultracode. The outcome was adequate and the better call was "both"; the ultracode flag was not tested.
- **Close-out edits:** N3 and N5 are fixed, N6 is noted in the CI policy, and the N1 and N4 corrections are above. The manager workflow now says the classifier rules are live. The brief and the current handoff record M02 as done, with the queued follow-ups. The M02 prompts and the App Manager 2 start prompt are pruned: their results are in this record and the brief, and Git history keeps their text. A short start prompt for the next manager replaces them.
- **Notion:**
  - The 47 Work Register Plan References that pointed to Drive now point to the repository: 46 to PF01, and AP1-DBA-001 to its preserved assignment in `docs/planning/sources/`. A re-query found none left.
  - A03 is Done, resolved by P01.1.
  - An M01 row now exists.
