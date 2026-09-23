"""Fixed logging policy for the P03 loopback artifact server."""

from copy import deepcopy

from .telemetry import LOGGING

# Request paths, query strings, headers and exception text never enter routine
# server logs. The same allowlisted formatter is installed before WSGI preload.
accesslog = None
errorlog = "-"
loglevel = "info"
logconfig_dict = deepcopy(LOGGING)
