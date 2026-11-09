"""Checks that read the API and the chain, then delegate to ``compare``."""

from __future__ import annotations

import datetime
import time

from . import compare
from .chain import Chain, enc_address, enc_uint, selector, topic, word_address, words
from .config import THRESHOLDS, Settings
from .http import ApiClient, get_json
from .lists import AddressLists, CommentedAddress


def fmt_ts(ts: int) -> str:
    t = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
    return f"{t:%Y-%m-%d %H:%M} UTC"


class Checker:
    def __init__(
        self, settings: Settings, api: ApiClient, chain: Chain, lists: AddressLists, commented: list[CommentedAddress]
    ):
        self.settings = settings
        self.api = api
        self.chain = chain
        self.lists = lists
        self.commented = commented
        self.alerts: list[compare.Alert] = []
        self._proposals: dict[str, list[dict]] = {}

    def _add(self, alerts):
        self.alerts.extend(alerts)

    def _recent_proposals(self, dao: str) -> list[dict] | None:
        if dao not in self._proposals:
            r = self.api.get(f"{dao}/proposals", {"limit": THRESHOLDS["recent_proposals"], "skip": 0, "lean": "true"})
            self._proposals[dao] = None if "__error__" in r else r.get("items", [])
        return self._proposals[dao]

    # ----- lists -----
    def lists_check(self, dao: str, cfg: dict):
        found = compare.list_issues(dao, cfg["enum"], self.lists, self.commented)
        self._add(found)
        return {"alerts": len(found)}

    # ----- governance -----
    def governance_check(self, dao: str, cfg: dict):
        if not cfg.get("timelock"):
            return {"skipped": "no timelock configured"}
        tl, kind = cfg["timelock"]
        ch = cfg["chain"]
        gov = cfg["governors"][0][0]
        kw = {}
        if kind == "compound":
            kw["admin"] = word_address(self.chain.call(tl, selector("admin()"), ch))
            kw["pending_admin"] = word_address(self.chain.call(tl, selector("pendingAdmin()"), ch))
        else:
            data = selector("hasRole(bytes32,address)") + topic("PROPOSER_ROLE")[2:] + enc_address(gov)
            kw["proposer_role_ok"] = words(self.chain.call(tl, data, ch))[0] == 1
        real = self.chain.call(gov, selector("timelock()"), ch)
        if real and len(real) >= 42:
            kw["governor_timelock"] = word_address(real)
        found = compare.governance_issues(dao, tl, gov, **kw)
        self._add(found)
        return {"alerts": len(found)}

    # ----- freshness -----
    def freshness_check(self, dao: str, cfg: dict):
        health = self.api.get(f"{dao}/health")
        if "__error__" in health:
            self._add(
                [
                    compare.Alert(
                        dao, "api_error", "medium", f"/{dao}/health returned an error", {"error": health["__error__"]}
                    )
                ]
            )
            return None
        ch = cfg["chain"]
        head = self.chain.head(ch)
        window = 1800 if ch == 1 else 9000
        chain_block = None
        for address in [cfg["token"]] + [g for g, _ in cfg["governors"]]:
            b = head
            for _ in range(8):  # walk back up to 8 windows until a log shows up
                try:
                    logs = self.chain.get_logs(address, b - window, b, ch)
                except Exception:
                    logs = []
                if logs:
                    bn = max(int(x["blockNumber"], 16) for x in logs)
                    chain_block = bn if chain_block is None else max(chain_block, bn)
                    break
                b -= window
        chain_last = self.chain.block_timestamp(chain_block, ch) if chain_block else None
        api_last = compare.latest_api_activity(health, self._recent_proposals(dao) or [])
        found, lag = compare.freshness_issues(
            dao,
            api_last,
            chain_last,
            health.get("status"),
            THRESHOLDS["indexer_lag_seconds"],
            fmt=fmt_ts,
            chain_block=chain_block,
        )
        self._add(found)
        return {"lag_seconds": lag, "health_status": health.get("status")}

    # ----- supply -----
    def supply_check(self, dao: str, cfg: dict):
        token = self.api.get(f"{dao}/token")
        ch, t, enum = cfg["chain"], cfg["token"], cfg["enum"]
        if "__error__" in token:
            self._add([compare.Alert(dao, "api_error", "high", f"/{dao}/token returned error {token['__error__']}")])
            token = None
        total = words(self.chain.call(t, selector("totalSupply()"), ch))[0]
        if cfg.get("nft"):
            if token:
                self._add(compare.nft_supply_issues(dao, int(token["totalSupply"]), total))
            return {"chain_total_supply": total}
        if not token:
            return None
        burn = {a.lower() for _, a, _ in self.lists["BurningAddresses"].get(enum, []) if int(a, 16) != 0}
        balances = self.chain.multicall([(t, selector("balanceOf(address)") + enc_address(a)) for a in burn], ch)
        expected = {"totalSupply": total - sum(words(x)[0] for x in balances if x)}
        for list_name, field in compare.SUPPLY_FIELDS.items():
            addrs = list({a.lower() for _, a, _ in self.lists[list_name].get(enum, [])})
            r = (
                self.chain.multicall([(t, selector("balanceOf(address)") + enc_address(a)) for a in addrs], ch)
                if addrs
                else []
            )
            expected[field] = sum(words(x)[0] for x in r if x)
        found = compare.supply_issues(dao, token, expected, THRESHOLDS["supply_diff_pct"])
        self._add(found)
        return {"fields_checked": len(expected), "alerts": len(found)}

    # ----- voting power -----
    def voting_power_check(self, dao: str, cfg: dict):
        r = self.api.get(f"{dao}/voting-powers", {"limit": THRESHOLDS["voting_power_sample"], "skip": 0})
        if "__error__" in r:
            self._add([compare.Alert(dao, "api_error", "medium", "/voting-powers returned an error")])
            return None
        items = r["items"]
        onchain = self.chain.multicall(
            [(cfg["token"], selector(cfg["vp_fn"]) + enc_address(x["accountId"])) for x in items], cfg["chain"]
        )
        rows = [
            (x["accountId"], int(x["votingPower"]), words(c)[0] if c else None)
            for x, c in zip(items, onchain, strict=True)
        ]
        found = compare.voting_power_issues(dao, rows)
        self._add(found)
        return {"sampled": len(items), "mismatches": len(found)}

    # ----- proposals -----
    def proposals_check(self, dao: str, cfg: dict):
        if not cfg["governors"]:
            return {"skipped": "no governor configured"}
        items = self._recent_proposals(dao)
        if items is None:
            self._add([compare.Alert(dao, "api_error", "medium", "/proposals returned an error")])
            return None
        n = 0
        for p in items:
            pid = int(p["id"])
            gov, kind = cfg["governors"][0]
            if pid < cfg.get("legacy_id_below", 0):
                gov, kind = cfg["governors"][-1]
            if kind == "oz":
                w = words(self.chain.call(gov, selector("proposalVotes(uint256)") + enc_uint(pid), cfg["chain"]))
            else:
                w = words(self.chain.call(gov, selector("proposals(uint256)") + enc_uint(pid), cfg["chain"]))
            chain_votes = compare.decode_proposal_votes(kind, w)
            if chain_votes is None:
                continue
            n += 1
            self._add(compare.proposal_vote_issues(dao, p, chain_votes, gov))
        return {"compared": n}

    # ----- top holders -----
    def holders_check(self, dao: str, cfg: dict):
        """Large holders that are in no list. Mainnet ERC-20 only (Ethplorer public API)."""
        if cfg["chain"] != 1 or cfg.get("nft"):
            return {"skipped": "not a mainnet ERC-20"}
        s = self.settings
        url = f"{s.ethplorer_url}/getTopTokenHolders/{cfg['token']}?apiKey={s.ethplorer_key}&limit=50"
        try:
            holders = get_json(url, s.http_timeout_s).get("holders", [])
        except Exception as e:
            self._add([compare.Alert(dao, "holders_unavailable", "info", f"could not read top holders: {e}")])
            return None
        enum = cfg["enum"]
        labeled = {a for name in self.lists for _, a, _ in self.lists[name].get(enum, [])}
        labeled |= {g for g, _ in cfg["governors"]}
        found = compare.unlabeled_holder_issues(dao, holders, labeled, THRESHOLDS["unlabeled_holder_pct"])
        self._add(found)
        time.sleep(2)  # Ethplorer free tier
        return {"holders": len(holders), "unlabeled": len(found)}

    def run_dao(self, dao: str, cfg: dict) -> dict:
        summary = {}
        for name, fn in [
            ("lists", self.lists_check),
            ("governance", self.governance_check),
            ("freshness", self.freshness_check),
            ("supply", self.supply_check),
            ("voting_power", self.voting_power_check),
            ("proposals", self.proposals_check),
            ("holders", self.holders_check),
        ]:
            try:
                summary[name] = fn(dao, cfg)
            except Exception as e:
                summary[name] = f"error: {e}"
                self._add([compare.Alert(dao, "check_failed", "info", f"{name}: {e}")])
        return summary
