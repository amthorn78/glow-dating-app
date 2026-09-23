"""Exercise the WSGI API over loopback HTTP, then stop the temporary server.

Requires explicit GLOW_ENV=development or test. Never connects to any provider.
"""

import json
import threading
import urllib.error
import urllib.request
from wsgiref.simple_server import make_server

from glow_api.devserver import SafeRequestHandler, SafeWSGIServer
from glow_api.wsgi import application


def main() -> None:
    # The OS selects an available loopback port; no fixed-port collision or
    # external proxy is part of this isolated fixture smoke check.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with make_server(
        "127.0.0.1",
        0,
        application,
        server_class=SafeWSGIServer,
        handler_class=SafeRequestHandler,
    ) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            cases = (
                ("/health/live", 200, "alive"),
                ("/health/ready", 503, "not_ready"),
                ("/api/v1/development/recommendations", 200, None),
            )
            for path, expected_status, expected_body_status in cases:
                try:
                    response = opener.open(
                        f"http://127.0.0.1:{server.server_port}{path}", timeout=5
                    )
                except urllib.error.HTTPError as exc:
                    response = exc
                with response:
                    body = json.load(response)
                    if response.status != expected_status:
                        raise RuntimeError(f"Unexpected HTTP status for {path}")
                    if expected_body_status and body.get("status") != expected_body_status:
                        raise RuntimeError(f"Unexpected health response for {path}")
                    if expected_body_status is None:
                        if body.get("mode") != "fixture":
                            raise RuntimeError("Fixture marker missing")
                        if body.get("contract_version") != "gapp-dev-v1" or not body.get("items"):
                            raise RuntimeError("Unexpected recommendation envelope")
                        if any(
                            item.get("compatibility") != {"status": "pending", "source": "fixture"}
                            for item in body["items"]
                        ):
                            raise RuntimeError("Unexpected compatibility claim in smoke fixture")
                    print(f"PASS {path}: HTTP {response.status}")
        finally:
            server.shutdown()
            thread.join(timeout=5)


if __name__ == "__main__":
    main()
