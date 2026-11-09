from reconciler import compare
from reconciler.lists import CommentedAddress, parse_lists
from tests.test_lists import SOURCE

GOV = "0x9D4C63565D5618310271bF3F3c01b2954C1D1639"
CHARLIE = "0xef41CbD211076E8b1901e214Bf751d404cf06638"
TIMELOCK = "0x57a8865cfB1eCEf7253c27da6B4BC3dAEE5Be518"
ZERO = "0x" + "0" * 40


def types(alerts):
    return sorted(a.type for a in alerts)


def test_list_issues_finds_duplicate_and_commented_line():
    lists, commented = parse_lists(SOURCE)
    alerts = compare.list_issues("gtc", "GTC", lists, commented)
    assert types(alerts) == ["list_commented_line", "list_duplicate"]


def test_list_issues_flags_address_in_two_categories():
    addr = "0x1111111111111111111111111111111111111111"
    lists = {
        "TreasuryAddresses": {"X": [("a", addr, 1)]},
        "CEXAddresses": {"X": [("b", addr, 2)]},
        "BurningAddresses": {"X": [("c", addr, 3)]},
    }
    alerts = compare.list_issues("x", "X", lists, [CommentedAddress("CEXAddresses", "Y", 9)])
    assert types(alerts) == ["list_category_conflict"]
    assert alerts[0].evidence["categories"] == ["BurningAddresses", "CEXAddresses", "TreasuryAddresses"]


def test_governance_detects_new_admin_and_pending_admin():
    alerts = compare.governance_issues("gtc", TIMELOCK, GOV, admin=CHARLIE, pending_admin=GOV)
    assert types(alerts) == ["governance_migration_pending", "governor_not_indexed"]
    assert alerts[0].severity == "critical"


def test_governance_quiet_when_config_matches_chain():
    assert (
        compare.governance_issues(
            "gtc", TIMELOCK, GOV, admin=GOV.lower(), pending_admin=ZERO, governor_timelock=TIMELOCK
        )
        == []
    )


def test_governance_timelock_mismatch_and_lost_role():
    alerts = compare.governance_issues("ens", TIMELOCK, GOV, proposer_role_ok=False, governor_timelock=CHARLIE)
    assert types(alerts) == ["governor_not_indexed", "timelock_mismatch"]


def test_latest_api_activity_uses_proposal_queue_time():
    health = {"indexer": {"lastEventTimestamp": 1000}}
    proposals = [{"timestamp": 900, "queuedTimestamp": 1500, "executedTimestamp": None}]
    assert compare.latest_api_activity(health, proposals) == 1500
    assert compare.latest_api_activity({}, []) is None


def test_freshness_stalled_vs_quiet_vs_ok():
    stalled, lag = compare.freshness_issues("nouns", 1_000, 1_000 + 7_200, "degraded", 1800)
    assert types(stalled) == ["indexer_stalled"] and lag == 7200
    quiet, _ = compare.freshness_issues("ens", 1_000, 1_000, "degraded", 1800)
    assert types(quiet) == ["health_false_positive"]
    ok, _ = compare.freshness_issues("ens", 1_000, 1_100, "ok", 1800)
    assert ok == []
    nodata, lag = compare.freshness_issues("ens", None, 1_100, "ok", 1800)
    assert types(nodata) == ["freshness_no_data"] and lag is None


def test_lil_nouns_false_positive_is_gone():
    """Health feed is 16 h behind, but the newest chain log is a queue the API already shows."""
    health = {"status": "degraded", "indexer": {"lastEventTimestamp": 1_794_163_667}}
    proposals = [{"timestamp": 1_793_646_047, "queuedTimestamp": 1_794_221_675}]
    api_last = compare.latest_api_activity(health, proposals)
    alerts, _ = compare.freshness_issues("lil_nouns", api_last, 1_794_221_675, "degraded", 1800)
    assert types(alerts) == ["health_false_positive"]


def test_pct_diff():
    assert compare.pct_diff(101, 100) == 1.0
    assert compare.pct_diff(0, 0) == 0.0
    assert compare.pct_diff(5, 0) == 100.0


def test_supply_issues_threshold_and_zero_skip():
    api = {"totalSupply": "1000", "treasury": "1002", "cexSupply": "0"}
    expected = {"totalSupply": 1000, "treasury": 1000, "cexSupply": 0}
    alerts = compare.supply_issues("gtc", api, expected, 0.1)
    assert len(alerts) == 1 and "treasury" in alerts[0].message
    assert compare.supply_issues("gtc", api, expected, 1.0) == []


def test_nft_supply():
    assert compare.nft_supply_issues("nouns", 2043, 2043) == []
    assert compare.nft_supply_issues("nouns", 2052, 2043)[0].severity == "high"


def test_voting_power_ignores_failed_calls():
    rows = [("0xa", 5, 9), ("0xb", 3, 3), ("0xc", 1, None)]
    alerts = compare.voting_power_issues("nouns", rows)
    assert len(alerts) == 1 and alerts[0].evidence == {"address": "0xa", "api": "5", "chain": "9"}


def test_decode_proposal_votes_per_kind():
    w = list(range(12))
    assert compare.decode_proposal_votes("oz", [30, 70, 5]) == {"for": 70, "against": 30, "abstain": 5}
    assert compare.decode_proposal_votes("bravo", w) == {"for": 5, "against": 6, "abstain": 7}
    assert compare.decode_proposal_votes("alpha", w) == {"for": 5, "against": 6, "abstain": 0}
    assert compare.decode_proposal_votes("nouns", w) == {"for": 7, "against": 8, "abstain": 9}
    assert compare.decode_proposal_votes("oz", []) is None


def test_proposal_votes_mismatch_abstain_counted_as_for():
    proposal = {"id": "42", "title": "t", "forVotes": "150", "againstVotes": "10", "abstainVotes": "0"}
    chain = {"for": 100, "against": 10, "abstain": 50}
    alerts = compare.proposal_vote_issues("gtc", proposal, chain, GOV)
    assert types(alerts) == ["proposal_votes_mismatch"]
    assert compare.proposal_vote_issues("gtc", {**proposal, "forVotes": "100", "abstainVotes": "50"}, chain, GOV) == []


def test_unlabeled_holders():
    holders = [
        {"address": "0x14d7cee42d4643f0c767a1d504d9ca24c890f86c", "share": 20.25, "balance": 2e25},
        {"address": TIMELOCK.lower(), "share": 10.0, "balance": 1e25},
        {"address": "0x1111111111111111111111111111111111111111", "share": 0.5, "balance": 1e23},
    ]
    alerts = compare.unlabeled_holder_issues("gtc", holders, {TIMELOCK}, 1.0)
    assert len(alerts) == 1
    assert alerts[0].evidence == {"address": "0x14D7Cee42D4643f0C767A1D504d9cA24C890f86c", "balance": 20_000_000}
