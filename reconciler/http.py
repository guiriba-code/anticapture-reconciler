"""Small HTTP helpers: the Anticapture API (rate limited) and JSON-RPC with fallback."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "anticapture-reconciler/0.2 (read-only; +https://github.com/guiriba-code/anticapture-reconciler)"
HEADERS = {"User-Agent": USER_AGENT, "content-type": "application/json"}


def get_json(url: str, timeout: float = 60.0):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class ApiClient:
    """GET client for the public Anticapture API.

    Requests are spaced by ``min_interval`` seconds and retried with exponential
    backoff on 429/5xx. A cache-busting parameter bypasses the 1 h CDN cache.
    Errors are returned as ``{"__error__": <status or message>}`` instead of raised.
    """

    def __init__(self, base_url: str, min_interval: float = 0.6, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.min_interval = min_interval
        self.timeout = timeout
        self._last = 0.0

    def get(self, path: str, params: dict | None = None):
        params = dict(params or {})
        params["_rc"] = int(time.time())
        url = f"{self.base_url}/{path}?" + urllib.parse.urlencode(params)
        delay = 1.0
        for attempt in range(5):
            wait = self.min_interval - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                return get_json(url, self.timeout)
            except urllib.error.HTTPError as e:
                if e.code in (429, 502, 503, 504) and attempt < 4:
                    time.sleep(delay)
                    delay *= 2
                    continue
                return {"__error__": e.code}
            except Exception as e:  # network error, bad JSON
                if attempt < 4:
                    time.sleep(delay)
                    delay *= 2
                    continue
                return {"__error__": str(e)}
        return {"__error__": "retries exhausted"}


class RpcClient:
    """JSON-RPC client that tries each configured endpoint in turn."""

    def __init__(self, urls_by_chain: dict[int, list[str]], timeout: float = 60.0):
        self.urls = urls_by_chain
        self.timeout = timeout

    def request(self, method: str, params: list, chain: int = 1):
        urls = self.urls.get(chain) or []
        if not urls:
            raise RuntimeError(f"no RPC URL configured for chain {chain}")
        err = None
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        for attempt in range(4):
            for url in urls:
                try:
                    req = urllib.request.Request(url, data=body, headers=HEADERS)
                    with urllib.request.urlopen(req, timeout=self.timeout) as r:
                        j = json.loads(r.read().decode())
                    if "result" in j:
                        return j["result"]
                    err = j.get("error")
                except Exception as e:
                    err = str(e)
            time.sleep(1 + attempt)
        raise RuntimeError(f"RPC failed: {method}: {err}")
