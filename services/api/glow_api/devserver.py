"""Loopback-only smoke server, without Django migration checks or database access."""

import argparse
import json
import os
from wsgiref.simple_server import make_server


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ready-json", action="store_true", help="Emit a bound-port handshake.")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535; 0 selects an available port")

    from .wsgi import application

    with make_server("127.0.0.1", args.port, application) as server:
        if args.ready_json:
            print(
                json.dumps(
                    {
                        "event": "glow_fixture_ready",
                        "pid": os.getpid(),
                        "host": "127.0.0.1",
                        "port": server.server_port,
                    }
                ),
                flush=True,
            )
        else:
            print(
                f"Synthetic fixture API at http://127.0.0.1:{server.server_port}; "
                "no live integrations.",
                flush=True,
            )
        server.serve_forever()


if __name__ == "__main__":
    main()
