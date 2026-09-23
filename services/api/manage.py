#!/usr/bin/env python
"""Django management entrypoint. No environment is silently selected."""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "glow_api.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
