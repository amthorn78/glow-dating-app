"""Exercise the actual built image without publishing ports or enabling a network.

Run from the repository root: python scripts/container_smoke.py glow-api:ci
Requires Docker; builds and images are local to the CI runner. No registry push.
"""

import json
import subprocess
import sys
import time


def docker(*args, timeout=30, input_text=None):
    return subprocess.run(
        ["docker", *args],
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True,
    ).stdout.strip()


def main():
    image = sys.argv[1]
    metadata = json.loads(docker("image", "inspect", image))[0]
    config = metadata["Config"]
    assert config["User"] == "10001:10001"
    assert config["WorkingDir"] == "/opt/glow/api"
    assert config["Entrypoint"] == ["python", "-m", "glow_api.runtime"]
    assert config["StopSignal"] == "SIGTERM"
    security = (
        "--network", "none", "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,size=16m",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--pids-limit", "64",
    )
    marker = "synthetic-container-secret-marker"
    for values in (
        (),
        ("GLOW_ENV=staging",),
        ("GLOW_ENV=production",),
        ("GLOW_ENV=test", f"DATABASE_URL={marker}"),
        ("GLOW_ENV=test", f"HDE_API_TOKEN={marker}"),
        ("GLOW_ENV=test", f"CELERY_BROKER_URL={marker}"),
    ):
        flags = [item for value in values for item in ("-e", value)]
        result = subprocess.run(
            ["docker", "run", "--rm", *security, *flags, image],
            capture_output=True, text=True, timeout=15, check=False,
        )
        assert result.returncode == 78, "Unsafe image mode did not refuse startup."
        assert '"event": "runtime_refused"' in result.stdout
        assert marker not in result.stdout + result.stderr

    container = docker("run", "--detach", *security, "-e", "GLOW_ENV=test", "-e", "PORT=8123", image)
    try:
        # Probe inside this container's network namespace. No -p/-P, host network,
        # live provider, database, broker, external proxy or shared volume exists.
        probe = r'''
import json, os, socket, sys, time, urllib.request, urllib.error
assert sys.version_info[:3] == (3, 12, 14)
assert os.getuid() == 10001
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
deadline = time.monotonic() + 10
while True:
    try:
        with opener.open("http://127.0.0.1:8123/health/live", timeout=.3) as response:
            assert response.status == 200
        break
    except (urllib.error.URLError, TimeoutError):
        if time.monotonic() >= deadline:
            raise AssertionError("Liveness startup budget exceeded.") from None
        time.sleep(.05)
try:
    opener.open("http://127.0.0.1:8123/health/ready", timeout=1)
    raise AssertionError("Fixtures incorrectly declared ready.")
except urllib.error.HTTPError as response:
    assert response.code == 503
    assert json.load(response)["status"] == "not_ready"
    response.close()
with opener.open("http://127.0.0.1:8123/api/v1/development/recommendations", timeout=1) as response:
    assert response.status == 200
with open("/proc/net/tcp", encoding="ascii") as entries:
    listeners = [line.split()[1] for line in entries.readlines()[1:] if line.split()[3] == "0A"]
assert listeners == ["0100007F:1FBB"], "Artifact listener escaped its fixed loopback boundary."
assert not os.path.exists("glow_persistence")
assert not os.path.exists("manage.py")
assert not os.path.exists(".git")
print("built-image loopback smoke passed")
'''
        print(docker("exec", "-i", container, "python", "-", input_text=probe, timeout=15))
        started = time.monotonic()
        docker("stop", "--time", "7", container, timeout=10)
        state = json.loads(docker("inspect", container))[0]["State"]
        assert not state["Running"] and state["ExitCode"] == 0
        assert not state["OOMKilled"]
        assert time.monotonic() - started < 9
        print(json.dumps({"event": "container_validation_passed", "image_id": metadata["Id"]}))
    finally:
        docker("rm", "--force", container)


if __name__ == "__main__":
    main()
