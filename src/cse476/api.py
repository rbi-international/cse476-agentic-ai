"""
Turning a real API into a tool an agent can trust.

Unit 2 Lecture 3. In the last lecture the tools were functions on your own
machine. Now they reach a real service over the network, which is where every
failure mode from Lecture 2 stops being a teaching example and becomes an
ordinary Tuesday. This module is about the wrapper: the thin, careful layer
between a messy external API and the clean tool the model sees.

    HttpClient        a tiny transport with a timeout, injected so we can test
    fetch_json        one request, with the network faults handled in one place
    weather_api_tool  a raw, messy API wrapped into a clean tool
    the anti-corruption layer, in miniature

The lesson: never let the shape of an external API leak into your agent. Wrap
it, translate it, and hand the model a clean sentence, not a raw payload.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Protocol


# ---------------------------------------------------------------- the transport

class Response:
    """A minimal HTTP response, enough to teach the pattern without a real net."""

    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body

    def json(self) -> Any:
        return json.loads(self.body)


class Transport(Protocol):
    """
    The seam. Real code puts requests here. Tests put a fake here. Because the
    agent code depends on this Protocol and not on a concrete network library,
    every network fault can be reproduced offline, on purpose, in a test.
    """

    def get(self, url: str, headers: dict[str, str], timeout: float) -> Response:
        ...


class ApiError(Exception):
    """A network or API failure the tool layer is expected to translate."""


@dataclass
class HttpClient:
    """
    A thin client with the two things every real request needs and beginners
    forget: a timeout, and a single place that turns transport faults into one
    error type the rest of the code can handle.
    """

    transport: Transport
    base_url: str
    api_key: str = ""
    timeout: float = 5.0

    def get_json(self, path: str, params: dict[str, str] | None = None) -> Any:
        """
        One GET request, returning parsed JSON, with the messy parts contained.

        Every failure a real request can suffer is turned into an ApiError with
        a readable message here, so nothing above this line has to know how HTTP
        breaks. This is the same 'contain the mess in one function' idea as
        call_tool in Lecture 2, one layer lower.
        """
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"

        headers = {"Accept": "application/json"}
        if self.api_key:
            # WHY the key goes in a header and never in the URL: a URL ends up in
            # logs, browser history and error messages. A header does not. This
            # is a security habit worth forming now, cheaply.
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            resp = self.transport.get(url, headers=headers, timeout=self.timeout)
        except TimeoutError as e:
            raise ApiError(f"Request to {path} timed out after {self.timeout}s.") from e
        except Exception as e:  # noqa: BLE001
            raise ApiError(f"Request to {path} failed: {e}") from e

        return self._handle(path, resp)

    def _handle(self, path: str, resp: Response) -> Any:
        """Turn a status code into either data or a clear, typed error."""
        if resp.status == 200:
            try:
                return resp.json()
            except json.JSONDecodeError as e:
                # a 200 with unparseable body is the 'it lies' failure from L2,
                # arriving over the network this time
                raise ApiError(
                    f"{path} returned status 200 but the body was not valid JSON."
                ) from e

        # WHY these three are named separately: they call for different action.
        # 401 is your problem (fix the key). 429 is a timing problem (back off).
        # 5xx is their problem (retry or give up). Collapsing them into one
        # 'error' throws away the information you need to respond correctly.
        if resp.status == 401:
            raise ApiError(f"{path} returned 401 Unauthorized. Check the API key.")
        if resp.status == 429:
            raise ApiError(f"{path} returned 429 Too Many Requests. Back off and retry.")
        if 500 <= resp.status < 600:
            raise ApiError(f"{path} returned {resp.status}, a server error. Retry later.")
        raise ApiError(f"{path} returned an unexpected status {resp.status}.")


# ---------------------------------------------------------------- the raw API

# This is what a real third-party API hands you: nested, abbreviated, full of
# fields you do not want, in units you did not ask for. The point of the wrapper
# is that NONE of this shape reaches the model.
def _raw_weather_payload(city: str) -> dict[str, Any]:
    data = {
        "mumbai": {"loc": {"n": "Mumbai", "cc": "IN"},
                   "cur": {"tmp_k": 304.15, "hum_pct": 84, "cond_cd": 500}},
        "delhi": {"loc": {"n": "Delhi", "cc": "IN"},
                  "cur": {"tmp_k": 311.15, "hum_pct": 30, "cond_cd": 721}},
        "jammu": {"loc": {"n": "Jammu", "cc": "IN"},
                  "cur": {"tmp_k": 302.15, "hum_pct": 40, "cond_cd": 800}},
    }
    return data[city.strip().lower()]


COND = {500: "light rain", 721: "haze", 800: "clear sky"}


# ---------------------------------------------------------------- the wrapper

def weather_api_tool(client: HttpClient) -> Callable[[str], str]:
    """
    Wrap the raw weather API into a clean tool the model can use.

    This closure captures the http client and returns a plain function with the
    tidy signature the model expects: city in, one readable sentence out. All
    the ugliness, the nested payload, the Kelvin temperatures, the condition
    codes, the network errors, is translated here and never leaks upward. This
    thin translating layer is the whole lesson of the lecture.
    """

    def get_weather(city: str) -> str:
        try:
            payload = client.get_json("weather", params={"q": city})
        except ApiError as e:
            # the tool speaks the model's language, not HTTP's. A network fault
            # becomes a sentence the model can read and act on, exactly like
            # call_tool did in Lecture 2.
            return f"Could not get weather for {city}: {e}"

        try:
            loc = payload["loc"]["n"]
            kelvin = payload["cur"]["tmp_k"]
            humidity = payload["cur"]["hum_pct"]
            condition = COND.get(payload["cur"]["cond_cd"], "unknown conditions")
        except (KeyError, TypeError):
            # the API changed shape on us, a real and common event. Fail
            # readably rather than crashing three layers up.
            return f"Weather data for {city} arrived in an unexpected shape."

        celsius = round(kelvin - 273.15)
        return f"{loc}: {celsius}C, {humidity}% humidity, {condition}."

    return get_weather


def weather_tool_schema() -> dict[str, Any]:
    """The schema the model sees. Note it says nothing about Kelvin or codes."""
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get current weather for one city as a short readable summary. "
                "Known cities: Mumbai, Delhi, Jammu."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. 'Delhi'."}
                },
                "required": ["city"],
            },
        },
    }


# ---------------------------------------------------------------- a usable fake

class FakeTransport:
    """
    A scriptable transport so the whole chain runs offline and every fault is
    reproducible. Real code swaps this for a real HTTP library; nothing else
    changes, which is the entire reason the Transport seam exists.
    """

    def __init__(
        self,
        status: int = 200,
        raise_timeout: bool = False,
        bad_json: bool = False,
    ):
        self.status = status
        self.raise_timeout = raise_timeout
        self.bad_json = bad_json
        self.calls: list[str] = []

    def get(self, url: str, headers: dict[str, str], timeout: float) -> Response:
        self.calls.append(url)
        if self.raise_timeout:
            raise TimeoutError("simulated timeout")
        if self.status != 200:
            return Response(self.status, "{}")
        if self.bad_json:
            return Response(200, "<html>not json</html>")
        # pull the city out of the query and return the raw, messy payload
        city = url.split("q=", 1)[1] if "q=" in url else "mumbai"
        try:
            payload = _raw_weather_payload(city)
        except KeyError:
            return Response(200, json.dumps({"error": "unknown city"}))
        return Response(200, json.dumps(payload))
