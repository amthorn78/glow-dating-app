import os
import socket
import unittest

import tests  # noqa: F401  (installs the network guard)


class OfflineEnvironmentTest(unittest.TestCase):
    def test_no_stream_variables(self) -> None:
        present = sorted(name for name in os.environ if name.startswith("STREAM_"))
        self.assertEqual(present, [], "run the offline tests with env -i (see README)")

    def test_network_is_refused(self) -> None:
        with self.assertRaises(OSError):
            socket.create_connection(("chat.stream-io-api.com", 443), timeout=1)


if __name__ == "__main__":
    unittest.main()
