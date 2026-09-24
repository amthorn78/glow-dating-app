# Local development for the Claude handoff

Use a real clone of `amthorn78/glow-dating-app`, not a reconstructed snapshot's Git history. Verify `git remote -v`, `git status --short`, `git fetch origin`, current main and open PRs before editing. Preserve unrelated changes. Repository access is the only credential needed for the current fixture baseline.

## Pinned tools and installs

Use Python **3.12.14**, Node **24.19.0**, npm **11.9.0** (see `.python-version`, `.node-version`, package `engines` and CI). Install the tools using your environment's normal trusted tool manager. Do not upgrade pins during this migration.

From repository root, in a clean shell without inherited database/provider configuration:

```bash
python3 --version
node --version
npm --version
python3 -m venv services/api/.venv
services/api/.venv/bin/python -m pip install --require-hashes -r services/api/requirements-dev.lock
services/api/.venv/bin/python -m pip check
npm ci --ignore-scripts --prefix apps/mobile
npm ci --ignore-scripts --prefix packages/contracts
```

Do not dump your environment to diagnose a configuration refusal. The API rejects even empty reserved secret/connection variables by presence. Use a dedicated process environment instead of copying HDE/Railway configuration. The full inventory is in [the handoff](../continuity/claude-code-handoff.md#environment-variable-inventory).

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
python3 -m unittest discover -s scripts -p 'test_change_scope.py' -v
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
npx playwright install --with-deps chromium
npm run test:rendered
```

Docker is optional locally and used by the hosted artifact gate. See [build-and-deploy](build-and-deploy.md) for the existing image build/isolated smoke commands. No image is deployed by CI. Browser rendering and development JavaScript exports do not prove signed native builds or device accessibility. See [CI/review policy](ci-and-branch-policy.md) before spending time on checks for ordinary documentation.
