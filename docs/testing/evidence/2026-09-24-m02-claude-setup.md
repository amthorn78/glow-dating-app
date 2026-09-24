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
