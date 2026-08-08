# Diagnostic: shows what endpoint your code actually resolves to.
# Run this on YOUR machine: python /tmp/diag.py  (with your .env present)
import os
from dotenv import load_dotenv
load_dotenv()

ep  = os.getenv("AZURE_OPENAI_ENDPOINT", "")
key = os.getenv("AZURE_OPENAI_API_KEY", "")
prov = os.getenv("PROVIDER", "")

print("PROVIDER        :", prov)
print("ENDPOINT (raw)  :", repr(ep))
print("KEY looks like  :", "URL (WRONG)" if key.startswith("http") else
                           f"key, {len(key)} chars" if key else "EMPTY (WRONG)")

# replicate lanes.py normalisation
base = ep.strip()
for suf in ("/responses", "/chat/completions", "/completions"):
    if base.rstrip("/").endswith(suf):
        base = base.rstrip("/")[:-len(suf)]
if not base.rstrip("/").endswith("/openai/v1"):
    base = base.rstrip("/") + "/openai/v1"
base = base.rstrip("/") + "/"
print("base_url used   :", base)

# host check
from urllib.parse import urlparse
host = urlparse(base).hostname or ""
print("host            :", host)
if "your-resource" in host:
    print("  >>> PROBLEM: still the PLACEHOLDER host. A duplicate .env line is winning.")
if not host.endswith("azure.com"):
    print("  >>> PROBLEM: host does not look like an Azure endpoint.")
