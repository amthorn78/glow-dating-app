# Official Python tag and index resolved through Docker Hub's tag API 2026-09-23.
# P03 artifact only: its entrypoint refuses staging/production and binds loopback.
FROM python:3.12.14-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=UTC
WORKDIR /opt/glow/api
COPY services/api/requirements.lock ./requirements.lock
RUN python -m pip install --no-cache-dir --require-hashes --only-binary=:all: -r requirements.lock \
    && python -m pip check
COPY services/api/glow_api ./glow_api
COPY services/api/glow_domain ./glow_domain
USER 10001:10001
STOPSIGNAL SIGTERM
ENTRYPOINT ["python", "-m", "glow_api.runtime"]
