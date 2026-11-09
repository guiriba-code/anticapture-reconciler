"""Pure comparison logic. No network access here, so it is fully unit-tested."""

from __future__ import annotations

from dataclasses import dataclass, field

from eth_utils import to_checksum_address

from .lists import AddressLists, CommentedAddress

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


@dataclass
class Alert:
    dao: str
    type: str
    severity: str
    message: str
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "dao": self.dao,
            "type": self.type,
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
        }


# ---------- address lists ----------


def list_issues(dao: str, enum: str, lists: AddressLists, commented: list[CommentedAddress]) -> list[Alert]:
    """Duplicate labels for one address, addresses in two categories, commented-out addresses."""
    alerts: list[Alert] = []
    categories: dict[str, set[str]] = {}
    for name, per_dao in lists.items():
        by_address: dict[str, list[tuple[str, int]]] = {}
        for label, address, line in per_dao.get(enum, []):
            by_address.setdefault(address.lower(), []).append((label, line))
            categories.setdefault(address.lower(), set()).add(name)
        for address, labels in by_address.items():
            if len(labels) > 1:
                alerts.append(
                    Alert(
                        dao,
                        "list_duplicate",
                        "medium",
                        f"{name}: the same address appears with {len(labels)} labels",
                        {"address": to_checksum_address(address), "labels": labels},
                    )
                )
    for address, cats in categories.items():
        if len(cats - {"BurningAddresses"}) > 1:
            alerts.append(
                Alert(
                    dao,
                    "list_category_conflict",
                    "medium",
                    "address is in more than one category",
                    {"address": to_checksum_address(address), "categories": sorted(cats)},
                )
            )
    for c in commented:
        if c.dao == enum:
            alerts.append(
                Alert(
                    dao,
                    "list_commented_line",
                    "info",
                    f"{c.list_name}: commented-out address on line {c.line} (not counted in any metric)",
                    {"line": c.line},
                )
            )
    return alerts


# ---------- governance ----------


def governance_issues(
    dao: str,
    timelock: str,
    configured_governor: str,
    admin: str | None = None,
    pending_admin: str | None = None,
    proposer_role_ok: bool | None = None,
    governor_timelock: str | None = None,
) -> list[Alert]:
    alerts: list[Alert] = []
    zero = "0x" + "0" * 40
    if admin is not None and admin.lower() != configured_governor.lower():
        alerts.append(
            Alert(
                dao,
                "governor_not_indexed",
                "critical",
                "timelock admin() points to a governor that is not configured",
                {
                    "timelock": timelock,
                    "onchain_admin": to_checksum_address(admin),
                    "configured_governor": configured_governor,
                },
            )
        )
    if pending_admin is not None and pending_admin.lower() != zero:
        alerts.append(
            Alert(
                dao,
                "governance_migration_pending",
                "high",
                "timelock has a pendingAdmin set (governor change in progress?)",
                {"timelock": timelock, "pending_admin": to_checksum_address(pending_admin)},
            )
        )
    if proposer_role_ok is False:
        alerts.append(
            Alert(
                dao,
                "governor_not_indexed",
                "critical",
                "configured governor no longer has PROPOSER_ROLE on the timelock",
                {"timelock": timelock, "governor": configured_governor},
            )
        )
    if governor_timelock is not None and governor_timelock.lower() != timelock.lower():
        alerts.append(
            Alert(
                dao,
                "timelock_mismatch",
                "medium",
                "governor.timelock() differs from the configured timelock",
                {"configured": timelock, "onchain": to_checksum_address(governor_timelock)},
            )
        )
    return alerts


# ---------- freshness ----------


def latest_api_activity(health: dict, proposals: list[dict]) -> int | None:
    """Latest indexed activity the API exposes.

    ``/health`` only reports the newest ``feed_event`` row, which does not include
    proposal queue/execute events. Taking the max with the proposal timestamps avoids
    the false "stalled" alert seen on Lil Nouns, where the newest chain log was a
    ``ProposalQueued`` that the API had already indexed.
    """
    candidates = []
    last = (health.get("indexer") or {}).get("lastEventTimestamp")
    if last:
        candidates.append(int(last))
    for p in proposals:
        for key in ("timestamp", "queuedTimestamp", "executedTimestamp"):
            v = p.get(key)
            if v:
                candidates.append(int(v))
    return max(candidates) if candidates else None


def freshness_issues(
    dao: str,
    api_last: int | None,
    chain_last: int | None,
    health_status: str | None,
    max_lag: int,
    fmt=lambda ts: str(ts),
    chain_block: int | None = None,
) -> tuple[list[Alert], int | None]:
    if api_last is None or chain_last is None:
        return [
            Alert(
                dao,
                "freshness_no_data",
                "info",
                "could not measure indexer lag (no recent log or no API timestamp)",
                {"api_last_activity": api_last},
            )
        ], None
    lag = chain_last - api_last
    if lag > max_lag:
        return [
            Alert(
                dao,
                "indexer_stalled",
                "high",
                f"the chain has an event {lag // 3600} h after the API's latest indexed activity",
                {"api_last_activity": fmt(api_last), "chain_last_event": fmt(chain_last), "chain_block": chain_block},
            )
        ], lag
    if health_status == "degraded":
        return [
            Alert(
                dao,
                "health_false_positive",
                "low",
                "/health says 'degraded' but the indexer is caught up with the chain (the DAO is just quiet)",
                {"api_last_activity": fmt(api_last), "chain_last_event": fmt(chain_last)},
            )
        ], lag
    return [], lag


# ---------- supply ----------

SUPPLY_FIELDS = {
    "TreasuryAddresses": "treasury",
    "CEXAddresses": "cexSupply",
    "DEXAddresses": "dexSupply",
    "LendingAddresses": "lendingSupply",
    "NonCirculatingAddresses": "nonCirculatingSupply",
}


def pct_diff(api_value: int, chain_value: int) -> float:
    if chain_value == 0:
        return 0.0 if api_value == 0 else 100.0
    return 100 * (api_value - chain_value) / chain_value


def supply_issues(dao: str, api_token: dict, expected: dict[str, int], max_pct: float) -> list[Alert]:
    alerts = []
    for f, chain_value in expected.items():
        api_value = int(api_token.get(f) or 0)
        if api_value == 0 and chain_value == 0:
            continue
        pct = pct_diff(api_value, chain_value)
        if abs(pct) > max_pct:
            alerts.append(
                Alert(
                    dao,
                    "supply_mismatch",
                    "medium",
                    f"{f}: API differs from the on-chain sum of the lists by {pct:.3f}%",
                    {"api": str(api_value), "chain": str(chain_value)},
                )
            )
    return alerts


def nft_supply_issues(dao: str, api_total: int, chain_total: int) -> list[Alert]:
    if api_total == chain_total:
        return []
    return [
        Alert(
            dao,
            "supply_mismatch",
            "high",
            "API TOTAL_SUPPLY differs from the NFT totalSupply() (burns or lag)",
            {"api": str(api_total), "chain": str(chain_total)},
        )
    ]


# ---------- voting power ----------


def voting_power_issues(dao: str, rows: list[tuple[str, int, int | None]]) -> list[Alert]:
    """rows: (account, api value, chain value or None when the call failed)."""
    return [
        Alert(
            dao,
            "voting_power_mismatch",
            "high",
            "API voting power differs from the token contract",
            {"address": a, "api": str(api), "chain": str(chain)},
        )
        for a, api, chain in rows
        if chain is not None and int(api) != chain
    ]


# ---------- proposals ----------


def decode_proposal_votes(kind: str, w: list[int]) -> dict[str, int] | None:
    """Turn governor return words into for/against/abstain.

    oz:    proposalVotes(id) -> (against, for, abstain)
    bravo: proposals(id) -> (id, proposer, eta, startBlock, endBlock, for, against, abstain, ...)
    alpha: proposals(id) -> (id, proposer, eta, startBlock, endBlock, for, against, ...), no abstain
    nouns: proposals(id) -> (..., for at index 7, against 8, abstain 9, ...)
    """
    if not w:
        return None
    if kind == "oz":
        return {"for": w[1], "against": w[0], "abstain": w[2]}
    if kind == "bravo":
        return {"for": w[5], "against": w[6], "abstain": w[7]}
    if kind == "alpha":
        return {"for": w[5], "against": w[6], "abstain": 0}
    if kind == "nouns":
        return {"for": w[7], "against": w[8], "abstain": w[9]}
    raise ValueError(f"unknown governor kind: {kind}")


def proposal_vote_issues(dao: str, proposal: dict, chain_votes: dict[str, int], governor: str) -> list[Alert]:
    api_votes = {
        "for": int(proposal["forVotes"]),
        "against": int(proposal["againstVotes"]),
        "abstain": int(proposal["abstainVotes"]),
    }
    if api_votes == chain_votes:
        return []
    return [
        Alert(
            dao,
            "proposal_votes_mismatch",
            "high",
            f"proposal {str(proposal['id'])[:20]}: API totals differ from the governor",
            {
                "title": (proposal.get("title") or "")[:60],
                "api": {k: str(v) for k, v in api_votes.items()},
                "chain": {k: str(v) for k, v in chain_votes.items()},
                "governor": governor,
            },
        )
    ]


# ---------- top holders ----------


def unlabeled_holder_issues(
    dao: str, holders: list[dict], labeled: set[str], min_share: float, decimals: int = 18
) -> list[Alert]:
    labeled = {a.lower() for a in labeled}
    return [
        Alert(
            dao,
            "unlabeled_holder",
            "medium",
            f"holder with {h['share']:.2f}% of supply is not in any list",
            {"address": to_checksum_address(h["address"]), "balance": round(float(h["balance"]) / 10**decimals)},
        )
        for h in holders
        if float(h.get("share", 0)) >= min_share and h["address"].lower() not in labeled
    ]
