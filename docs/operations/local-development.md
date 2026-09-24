# Local development for the Claude handoff

Use a real clone of `amthorn78/glow-dating-app`, not a reconstructed snapshot's Git history. Verify `git remote -v`, `git status --short`, `git fetch origin`, current main and open PRs before editing. Preserve unrelated changes. Repository access is the only credential needed for the current fixture baseline.

## Pinned tools and installs

Use Python **3.12.14**, Node **24.19.0** and npm **11.9.0**. The pins live in:

- `services/api/.python-version`;
- the `engines` and `packageManager` fields of `apps/mobile/package.json` and `packages/contracts/package.json`;
- `.github/workflows/foundation.yml` (`python-version`, `node-version`, `npm@…`);
- the `Dockerfile` Python tag.

There is no `.node-version` file. `scripts/bootstrap-toolchain.sh` carries the same pins, and `services/api/tests/test_toolchain_pins.py` fails, naming the diverging file, when any of them disagree. Do not upgrade pins during this migration.

Install the tools with your environment's normal trusted tool manager. On Linux x86_64 you can instead run `bash scripts/bootstrap-toolchain.sh`, which installs all three from hash-verified downloads (see [Claude Code cloud sessions](#claude-code-cloud-sessions)).

**npm must be exactly 11.9.0.** Node 24.19.0 bundles npm 11.17.0. `apps/mobile/.npmrc` sets `engine-strict`, so `npm ci` for the mobile app fails with `EBADENGINE` (Required `{"node":"24.19.0","npm":"11.9.0"}`) until the pinned npm is installed; `packages/contracts` only warns. Install it into your Node installation first, as CI does (the bootstrap script already does this from a verified tarball):

```bash
npm install --global npm@11.9.0
```

From repository root, in a clean shell without inherited database/provider configuration, check the versions, then create the API virtual environment with `python3.12`. `python3` may be a different version; the Claude cloud container's is 3.11.

```bash
python3.12 --version   # Python 3.12.14
node --version         # v24.19.0
npm --version          # 11.9.0
python3.12 -m venv services/api/.venv
services/api/.venv/bin/python -m pip install --require-hashes -r services/api/requirements-dev.lock
services/api/.venv/bin/python -m pip check
npm ci --ignore-scripts --prefix apps/mobile
npm ci --ignore-scripts --prefix packages/contracts
```

Do not dump your environment to diagnose a configuration refusal. The API rejects even empty reserved secret/connection variables by presence. Use a dedicated process environment instead of copying HDE/Railway configuration. The full inventory is in [the handoff](../continuity/claude-code-handoff.md#environment-variable-inventory); the Claude cloud environment's settings are in the [environment inventory](environment-inventory.md).

## API

```bash
cd services/api
cp .env.example .env
set -a
. ./.env
set +a
.venv/bin/python -m glow_api.devserver --port 8000
```

The standard-library loopback server performs no migration checks. Python/Django does **not** automatically read `.env`; the explicit shell loading above supplies the safe local example. `.env` files are ignored. `GET /health/live` returns 200, `/health/ready` deliberately returns 503, and `/api/v1/development/recommendations` serves synthetic smoke records. There are no real account/token/provider mutation routes. Stop with Ctrl-C. Do not run `migrate`.

## Mobile

In a separate shell:

```bash
cd apps/mobile
cp .env.example .env
npm start
```

The development wrapper defaults to `GLOW_APP_ENV=development` and `EXPO_PUBLIC_GLOW_MODE=fixture`. Expo loads mobile dotenv using its own tooling; the wrapper/runtime guards still reject release modes. Leave `EXPO_PUBLIC_GLOW_API_BASE_URL` unset for the bundled fixture experience. A simulator smoke connection may use the example loopback origin; physical-device reachability is unproven, and the API still binds only loopback. The public-origin parser accepting private HTTP does not make that server reachable over a LAN.

## Checks

From repository root:

```bash
python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v
npm run check --prefix packages/contracts
npm run check --prefix apps/mobile
GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node scripts/smoke.mjs
GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node --test scripts/smoke.test.mjs
```

From `services/api/`:

```bash
GLOW_ENV=test .venv/bin/python manage.py check
GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
PYTHONPATH=. .venv/bin/python -m unittest discover -s ../../packages/contracts/tests -v
GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check
```

From `apps/mobile/` when the assignment needs rendering/export proof:

```bash
EXPO_OFFLINE=1 npm run check:expo
EXPO_OFFLINE=1 npm run export:development
npx playwright install --with-deps chromium   # workstation only; never in a Claude cloud container
npm run test:rendered
```

Docker is optional locally and used by the hosted artifact gate. See [build-and-deploy](build-and-deploy.md) for the existing image build/isolated smoke commands. No image is deployed by CI. Browser rendering and development JavaScript exports do not prove signed native builds or device accessibility. See [CI/review policy](ci-and-branch-policy.md) before spending time on checks for ordinary documentation.

## Claude Code cloud sessions

Glow app manager, implementation and review sessions run in the dedicated `Glow app` cloud environment. Its settings are recorded in the [environment inventory](environment-inventory.md#claude-cloud-environment-glow-app-nathans-settings-24-september-2026): the network allowlist, the Setup script, the Stream development variables and the absence of HDE variables. The owner steps are in the [M02 brief](../planning/claude-setup-optimization.md#owner-action--dedicated-environment-settings). A session's environment is fixed when it starts; switching environments needs a new session.

**Setup script.** The environment's Setup script is the whole of `scripts/bootstrap-toolchain.sh`, pasted unchanged.

- It runs before Claude Code starts, as the session account (root in the observed containers). It installs Node 24.19.0, npm 11.9.0 and CPython 3.12.14 from hash-verified downloads into `$HOME/.local/share/glow-app-toolchain`.
- It links `node`, `npm`, `npx` and `python3.12` into `$HOME/.local/bin`, which is first on `PATH`. It never replaces `python3` or `python`.
- Trust rules, all checked before anything in a tree runs:
  - Installed files belong to the account running the script and are not writable by group or others.
  - Symlinks may not leave their tree. Each one is relative, stays inside the tree at every step and resolves to a regular file there. A tree whose root is a symlink fails the check.
  - The prefix directory and the link directory (`$HOME/.local/bin`) must belong to the running account and must not be writable by group or others. Their parent directories must belong to that account or root and must not be writable by group or others unless sticky, like `/tmp`. The link directory's path may not contain a symlink.
  - A tree that breaks a rule is replaced from the verified archive. An unsafe prefix or link directory stops the script with an error; correct its owner or mode and rerun.
- A rerun with the toolchain present changes nothing and takes under a second. The first run takes about two minutes, mostly building Python.
- When a merged PR changes the file, Nathan pastes it into the environment again.

**First-session verification** (names only; never print values):

```bash
for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done
command -v node npm npx python3.12                     # each in $HOME/.local/bin
node --version; npm --version; python3.12 --version    # v24.19.0, 11.9.0, Python 3.12.14
```

If a tool is missing or has the wrong version, the Setup script did not produce the toolchain. Tell Nathan, then run `bash scripts/bootstrap-toolchain.sh` in the session.

**Per-branch installs.** Each session starts from a fresh clone. The Setup script provides only the toolchain, so install `apps/mobile/node_modules`, `packages/contracts/node_modules` and `services/api/.venv` with the commands above in every session and branch. They are ignored and never committed.

**Wrong environment.** `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` present means the session is in the HDE-shared environment.

- Tell Nathan. Never read, print or use the values, and never dump the environment (`env`, `printenv`, `set`) to diagnose it.
- The API refuses to start there (`ImproperlyConfigured: contradictory: inherited_connection (…)`) and `node scripts/smoke.mjs` fails. That refusal is correct behavior, not a defect to work around.
- Run app commands only in a clean process environment that starts empty and names each variable it passes, for example from `services/api/`:

  ```bash
  env -i HOME="$HOME" PATH="$PATH" LANG=C.UTF-8 GLOW_ENV=test .venv/bin/python manage.py check
  ```

- Network installs in such a clean environment also need the session's proxy and CA variables, passed through by reference and never printed: add `HTTPS_PROXY="$HTTPS_PROXY" NODE_EXTRA_CA_CERTS="$NODE_EXTRA_CA_CERTS"` for `npm ci`. Without them, npm failed with `SELF_SIGNED_CERT_IN_CHAIN` in the `Glow app` environment on 24 September 2026. curl and pip use the system trust store and worked. These are infrastructure settings, not application or provider credentials.

**Rendered tests.** The container's preinstalled Chromium is revision 1194, while `@playwright/test` 1.62.1 expects revision 1234, and the Playwright download host is not on the allowlist. Never run `playwright install` in the cloud container. Rendered acceptance comes from hosted CI (Foundation, Mobile checks). A local run against the preinstalled browser, through an uncommitted configuration, is informational only.

**Other limits.** The container has no Docker daemon, so the API artifact checks also rely on hosted CI.
