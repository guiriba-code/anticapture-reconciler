# anticapture-reconciler

A read-only tool that checks the numbers published by the public [Anticapture](https://www.anticapture.com) API against the blockchain and reports where they disagree.

It never writes to any service, needs no API key, and uses only public endpoints by default. It started as a prototype for an external data-integrity review of Anticapture in November 2026.

## What it does

For each DAO, the tool reads the Anticapture API and the chain at the latest block and runs seven checks:

| Check | What it compares | Alert types |
|---|---|---|
| **Lists** | The address lists in Anticapture's indexer `constants.ts`: the same address with two labels, an address in two categories, commented-out addresses | `list_duplicate`, `list_category_conflict`, `list_commented_line` |
| **Governance** | Compound-style timelock `admin()` / `pendingAdmin()`, or OZ timelock `hasRole(PROPOSER_ROLE, governor)`, against the configured governor. Also `governor.timelock()` against the configured timelock. | `governor_not_indexed` (critical), `governance_migration_pending`, `timelock_mismatch` |
| **Freshness** | The newest token or governor log on chain (`eth_getLogs`) against the newest activity the API shows: `/health` `lastEventTimestamp`, plus the created/queued/executed timestamps of recent proposals | `indexer_stalled`, `health_false_positive`, `freshness_no_data` |
| **Supply** | `/{dao}/token` against `totalSupply()` minus burn addresses and against the sum of `balanceOf` over each list (treasury, CEX, DEX, lending, non-circulating). NFT DAOs: `totalSupply()`. | `supply_mismatch`, `api_error` |
| **Voting power** | The top 20 of `/{dao}/voting-powers` against `getVotes` / `getCurrentVotes` | `voting_power_mismatch` |
| **Proposals** | The 10 newest proposals: API for/against/abstain against `proposalVotes()` (OZ) or `proposals()` (Bravo, Alpha, Nouns) | `proposal_votes_mismatch` |
| **Top holders** | The top 50 holders (Ethplorer) with ≥ 1% of supply that are in no list | `unlabeled_holder` |

Other alert types: `check_failed` and `holders_unavailable` (info) mean a check could not run. Severities are `critical`, `high`, `medium`, `low` and `info`.

DAOs covered: `uni`, `ens`, `gtc`, `comp`, `obol`, `fluid`, `nouns`, `lil_nouns`, `shu` and `scr` (Scroll chain).

The contract map in [`reconciler/config.py`](reconciler/config.py) mirrors what Anticapture is **configured** to index, not necessarily the live contracts. That is how the governance check notices when a DAO moves to a new governor. When Anticapture updates its config, update this map too.

## Install and run

Requires Python 3.10+.

```bash
git clone https://github.com/guiriba-code/anticapture-reconciler.git
cd anticapture-reconciler
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

python -m reconciler                                  # all DAOs, writes ./output/
python -m reconciler --daos gtc,nouns --output out    # some DAOs, custom directory
python -m reconciler --fail-on high                   # exit code 2 if any high/critical alert
```

A full run takes about 2–6 minutes, depending on RPC speed. Much of that is the deliberate spacing between API calls.

### Configuration

All settings are optional environment variables. A `.env` file in the working directory is read if present. See [`.env.example`](.env.example).

| Variable | Default | Purpose |
|---|---|---|
| `ANTICAPTURE_API_URL` | `https://www.anticapture.com/api/gateful` | API under test |
| `ANTICAPTURE_CONSTANTS_URL` | `constants.ts` on the `dev` branch of `blockful/anticapture` | Source of the address lists |
| `ANTICAPTURE_CONSTANTS_PATH` | unset | Local `constants.ts` (wins over the URL), useful to test a branch |
| `RPC_URL` | `https://rpc.mevblocker.io,https://eth.drpc.org,https://eth-mainnet.public.blastapi.io` | Ethereum JSON-RPC endpoints, tried in order |
| `SCROLL_RPC_URL` | `https://rpc.scroll.io,https://scroll.drpc.org` | Scroll JSON-RPC endpoints |
| `ETHPLORER_API_URL` / `ETHPLORER_API_KEY` | `https://api.ethplorer.io` / `freekey` | Top holders (`freekey` is Ethplorer's public key) |
| `API_MIN_INTERVAL_SECONDS` | `0.6` | Minimum spacing between Anticapture API calls |
| `HTTP_TIMEOUT_SECONDS` | `60` | Per-request timeout |

The RPC endpoints must answer `eth_call` and `eth_getLogs` over ranges of a few thousand blocks. If you use a private RPC whose URL contains a key, keep it in your local `.env` or in a CI secret. Never commit it.

## Outputs

Each run writes three files to the output directory:

- `alerts.json`: run metadata, a per-DAO summary of each check, and every alert with its evidence;
- `alerts.md`: the same alerts as a table, most severe first;
- `metrics.prom`: Prometheus text format, ready for a node-exporter textfile collector:

```
anticapture_reconciliation_alerts{dao="gtc",type="governor_not_indexed",severity="critical"} 1
anticapture_reconciliation_last_run_timestamp_seconds 1794236400
anticapture_reconciliation_duration_seconds 287
```

### Example output

[`examples/latest-run/`](examples/latest-run/) holds a real run. Its first lines:

> Run finished at 2026-11-09 15:19 UTC, took 121 s. DAOs: uni, ens, gtc, comp, obol, fluid, nouns, lil_nouns, shu, scr. Total: 88 alerts.

| Severity | DAO | Type | Message | Evidence |
|---|---|---|---|---|
| critical | gtc | governor_not_indexed | timelock admin() points to a governor that is not configured | `{"timelock": "0x57a8865cfB1eCEf7253c27da6B4BC3dAEE5Be518", "onchain_admin": "0xef41CbD211076E8b1901e214Bf751d404cf06638", "configured_governor": "0x9D4C63565D5618310271bF3F3c01b2954C1D1639"}` |
| high | fluid | governance_migration_pending | timelock has a pendingAdmin set (governor change in progress?) | `{"timelock": "0xC7Cb1dE2721BFC0E0DA1b9D526bCdC54eF1C0eFC", "pending_admin": "0x4F6F977aCDD1177DCD81aB83074855EcB9C2D49e"}` |
| high | gtc | proposal_votes_mismatch | proposal 75248911656791723576: API totals differ from the governor | `{"title": "REVOTE: Gitcoin DAO 2026 Budget Request [First Tranche]", "api": {"for": "4168863373892326077510548", "against": "236112752690344884", "abstain": "0"}, "chain": {"for": "3168028180370528751607167", "against": "236112752690344884", "abstain": "1000835193521797325903381"}, "governor": "0x9D4C63565D5618310271bF3F3c01b2954C1D1639"}` |
| high | gtc | proposal_votes_mismatch | proposal 12758623331512311890: API totals differ from the governor | `{"title": "REPOST [SGTM 004]: Generating Yield on DAO Treasury Assets t", "api": {"for": "2863707982783256336902361", "against": "8473769915973229288", "abstain": "0"}, "chain": {"for": "2863706706350447958226379", "against": "8473769915973229288", "abstain": "1276432808378675982"}, "governor": "0x9D4C63565D5618310271bF3F3c01b2954C1D1639"}` |
| high | gtc | proposal_votes_mismatch | proposal 42131400951029541481: API totals differ from the governor | `{"title": "[SGTM 004]: Generating Yield on DAO Treasury Assets to Suppo", "api": {"for": "1830165077578630063350375", "against": "400457369337789710168865", "abstain": "0"}, "chain": {"for": "1830162181084274302303222", "against": "400457369337789710168865", "abstain": "2896494355761047153"}, "governor": "0x9D4C63565D5618310271bF3F3c01b2954C1D1639"}` |
| high | gtc | proposal_votes_mismatch | proposal 17479554285430824235: API totals differ from the governor | `{"title": "[REPOST] Revoke Wonderland Vesting Contract - Contract Termi", "api": {"for": "2815176816420051837061940", "against": "5691302190133969644", "abstain": "0"}, "chain": {"for": "2815174400769086137065999", "against": "5691302190133969644", "abstain": "2415650965699995941"}, "governor": "0x9D4C63565D5618310271bF3F3c01b2954C1D1639"}` |
| high | gtc | proposal_votes_mismatch | proposal 10898830780403431523: API totals differ from the governor | `{"title": "Revoke Wonderland Vesting Contract - Contract Termination", "api": {"for": "1274933142954770859880186", "against": "31239427034689563006", "abstain": "0"}, "chain": {"for": "1274916560815280659534563", "against": "31239427034689563006", "abstain": "16582139490200345623"}, "governor": "0x9D4C63565D5618310271bF3F3c01b2954C1D1639"}` |
| high | gtc | proposal_votes_mismatch | proposal 54395366128290939379: API totals differ from the governor | `{"title": "[PROPOSAL] 2025 Budget - Allo", "api": {"for": "3150460781013397502333389", "against": "3406679754006315334985", "abstain": "0"}, "chain": {"for": "2758226498925896552919654", "against": "3406679754006315334985", "abstain": "392234282087500949413735"}, "governor": "0x9D4C63565D5618310271bF3F3c01b2954C1D1639"}` |
| high | lil_nouns | api_error | /lil_nouns/token returned error 500 | `{}` |
| high | nouns | indexer_stalled | the chain has an event 501 h after the API's latest indexed activity | `{"api_last_activity": "2026-10-19 16:49 UTC", "chain_last_event": "2026-11-09 14:12 UTC", "chain_block": 26377852}` |
| high | nouns | supply_mismatch | API TOTAL_SUPPLY differs from the NFT totalSupply() (burns or lag) | `{"api": "2052", "chain": "2044"}` |
| high | nouns | voting_power_mismatch | API voting power differs from the token contract | `{"address": "0xb1a32FC9F9D8b2cf86C068Cae13108809547ef71", "api": "665", "chain": "683"}` |
| high | scr | proposal_votes_mismatch | proposal 17736716284166632362: API totals differ from the governor | `{"title": "DAO Treasury Management RFP", "api": {"for": "0", "against": "0", "abstain": "614918476319895673775190"}, "chain": {"for": "1806873994978754561328164", "against": "0", "abstain": "614918476319895673775190"}, "governor": "0x2f3F2054776bd3C2fc30d750734A8F539Bb214f0"}` |

The full list (including medium, low and info alerts) is in [`alerts.md`](examples/latest-run/alerts.md).

## How it works

1. Load settings from the environment, and `.env` if present.
2. Download `constants.ts` and parse the six address lists. Commented-out lines are skipped and recorded.
3. For each DAO, run the seven checks in order. Each check reads the API (rate limited, with retries) and the chain (Multicall3 for batches, falling back across RPC endpoints). It then hands both sides to a pure comparison function in [`reconciler/compare.py`](reconciler/compare.py).
4. A check that fails becomes a `check_failed` alert, and the run continues.
5. Write `alerts.json`, `alerts.md` and `metrics.prom`.

## Limitations

- **Not covered:** AAVE (voting power from three tokens with a 1e10 scale), TORN (locked governance balance, no `DelegateVotesChanged`), and SHU proposals (Azorius module).
- **API and chain are not read at the same block.** The API does not expose the block it reflects, so a transfer that lands between the two reads can cause a small one-off difference. Treat a single supply or voting-power alert as a prompt to re-run, not as proof.
- **Freshness is heuristic.** The API's own `/health` only tracks one event table. This tool also uses proposal timestamps, which removes the known Lil Nouns false positive (a `ProposalQueued` the API had already indexed). An event type the API does not expose at all could still look like a lag. The real fix is to compare against the indexer's sync cursor, which the API does not publish today.
- Only the 10 newest proposals and the top 20 delegates are compared each run.
- `unlabeled_holder` lists candidates only. Deciding whether an address is an exchange, a person or a contract needs a human (or a labelling service).
- The contract map is hand-maintained (see above).

## Running it in production

A suggested setup for the Anticapture team:

1. **Hourly run.** Use a cron job, a Railway/Kubernetes cron, or the included [`hourly.yml`](ci/workflows/hourly.yml) GitHub Actions workflow. To activate it, see [`ci/README.md`](ci/README.md). That workflow is **off by default**. Set the repository variable `RECONCILER_SCHEDULE_ENABLED=true` to enable the hourly schedule. "Run workflow" always works by hand. Each run uploads the three files as an artifact and adds `alerts.md` to the job summary.
2. **Prometheus.** Write `metrics.prom` into a node-exporter textfile collector directory, or push it to a Pushgateway. Example Alertmanager rules:

```yaml
groups:
  - name: anticapture-reconciler
    rules:
      - alert: AnticaptureGovernorNotIndexed
        expr: anticapture_reconciliation_alerts{type="governor_not_indexed"} > 0
        labels: { severity: critical }
      - alert: AnticaptureIndexerStalled
        expr: anticapture_reconciliation_alerts{type="indexer_stalled"} > 0
        for: 2h
        labels: { severity: high }
      - alert: AnticaptureDataMismatch
        expr: sum by (dao, type) (anticapture_reconciliation_alerts{type=~"supply_mismatch|voting_power_mismatch|proposal_votes_mismatch"}) > 0
        for: 3h
        labels: { severity: warning }
      - alert: AnticaptureReconcilerNotRunning
        expr: time() - anticapture_reconciliation_last_run_timestamp_seconds > 3 * 3600
        labels: { severity: warning }
```

3. **Timelock owner watcher.** An hourly poll catches a governor migration within an hour. To hear about it as it happens, also subscribe to `NewAdmin`, `NewPendingAdmin` (Compound timelocks), `RoleGranted` / `RoleRevoked` (OZ timelocks) and `TimelockChange` on each configured timelock and governor, for example with a Tenderly alert or a small log subscriber.
4. **Better freshness.** If the API exposes the indexer's sync block (Ponder's `ponder_sync`), compare against that instead of event timestamps.

## Development

```bash
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
pytest -q          # unit tests, no network
```

A ready-made CI workflow ([`ci/workflows/ci.yml`](ci/workflows/ci.yml)) runs lint and tests on every push and pull request, without network calls. It is not active yet; [`ci/README.md`](ci/README.md) explains how to turn it on.

## License

MIT. See [LICENSE](LICENSE).
