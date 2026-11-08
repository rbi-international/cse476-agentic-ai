"""Settings, read from the environment so no secret ever lives in the code."""

import os

MODEL = os.environ.get("HELPDESK_MODEL", "openai/gpt-oss-20b")
API_KEY = os.environ.get("HELPDESK_API_KEY", "")
