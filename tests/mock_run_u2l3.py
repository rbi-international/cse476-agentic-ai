"""
Prove the API wrapper hides all the mess and handles every network fault,
offline. No real network, ever: the Transport seam is a fake.
"""

import sys

sys.path.insert(0, "src")

from cse476.api import (  # noqa: E402
    ApiError,
    FakeTransport,
    HttpClient,
    weather_api_tool,
    weather_tool_schema,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


def make(**kw):
    t = FakeTransport(**kw)
    c = HttpClient(transport=t, base_url="https://api.example.com", api_key="secret")
    return t, c


print("\n1. the happy path returns a clean sentence, not a raw payload")
_, c = make()
tool = weather_api_tool(c)
out = tool("Delhi")
chk("has the city", "Delhi" in out)
chk("temperature is in Celsius, not Kelvin", "38C" in out)
chk("condition code was translated to words", "haze" in out)
chk("no raw field names leaked", "tmp_k" not in out and "cond_cd" not in out)

print("\n2. the messy shape never reaches the caller")
chk("no Kelvin number leaked", "311" not in out)
chk("no nested keys leaked", "cur" not in out and "loc" not in out)

print("\n3. the api key travels in a header, not the url")
t, c = make()
weather_api_tool(c)("Mumbai")
chk("key not in the requested url", all("secret" not in u for u in t.calls))

print("\n4. a timeout becomes a readable sentence, not a crash")
_, c = make(raise_timeout=True)
out = weather_api_tool(c)("Delhi")
chk("did not raise", isinstance(out, str))
chk("says it could not get weather", "could not get weather" in out.lower())
chk("mentions the timeout", "timed out" in out.lower())

print("\n5. status codes are distinguished, not collapsed")
for status, needle in ((401, "401"), (429, "429"), (503, "503")):
    _, c = make(status=status)
    try:
        c.get_json("weather", params={"q": "delhi"})
        chk(f"{status} should have raised", False)
    except ApiError as e:
        chk(f"{status} raised a specific ApiError", needle in str(e))

print("\n6. 401 tells you it is your key, 429 tells you to back off")
_, c = make(status=401)
try:
    c.get_json("weather")
except ApiError as e:
    chk("401 mentions the key", "key" in str(e).lower())
_, c = make(status=429)
try:
    c.get_json("weather")
except ApiError as e:
    chk("429 mentions backing off", "back off" in str(e).lower())

print("\n7. a 200 with a broken body is caught (the network 'lie')")
_, c = make(bad_json=True)
out = weather_api_tool(c)("Delhi")
chk("did not crash on non-json", isinstance(out, str))
chk("reported the problem readably", "could not get weather" in out.lower())

print("\n8. an unexpected payload shape fails readably")
# a 200 with valid JSON but the wrong shape
from cse476.api import Response  # noqa: E402

class WrongShape(FakeTransport):
    def get(self, url, headers, timeout):
        import json as _j
        return Response(200, _j.dumps({"totally": "different"}))

c = HttpClient(transport=WrongShape(), base_url="https://x", api_key="k")
out = weather_api_tool(c)("Delhi")
chk("did not crash on a shape change", isinstance(out, str))
chk("said the shape was unexpected", "unexpected shape" in out.lower())

print("\n9. the schema the model sees hides the mess")
sch = weather_tool_schema()
text = str(sch)
chk("schema mentions the city", "city" in text)
chk("schema says nothing about kelvin or codes",
    "kelvin" not in text.lower() and "cond_cd" not in text)

print("\n10. the same tool works through the real seam with a swapped transport")
# swapping the transport changes nothing above it: the point of the seam
_, c1 = make()
_, c2 = make()
chk("two independent clients give the same clean answer",
    weather_api_tool(c1)("Jammu") == weather_api_tool(c2)("Jammu"))

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
