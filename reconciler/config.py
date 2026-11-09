"""Runtime settings (environment variables) and the per-DAO contract map.

Every setting has a public default, so the tool runs with no configuration.
Nothing here needs an API key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_API_URL = "https://www.anticapture.com/api/gateful"
DEFAULT_CONSTANTS_URL = "https://raw.githubusercontent.com/blockful/anticapture/dev/apps/indexer/src/lib/constants.ts"
DEFAULT_RPC_URLS = "https://rpc.mevblocker.io,https://eth.drpc.org,https://eth-mainnet.public.blastapi.io"
DEFAULT_SCROLL_RPC_URLS = "https://rpc.scroll.io,https://scroll.drpc.org"
DEFAULT_ETHPLORER_URL = "https://api.ethplorer.io"
MULTICALL3 = "0xcA11bde05977b3631167028862bE2a173976CA11"

ETHEREUM = 1
SCROLL = 534352


def load_dotenv(path: str | os.PathLike = ".env") -> None:
    """Load KEY=VALUE lines from a .env file without overriding the real environment."""
    p = Path(path)
    if not p.is_file():
        return
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


def _split(value: str) -> list[str]:
    return [u.strip() for u in value.split(",") if u.strip()]


@dataclass
class Settings:
    api_url: str = DEFAULT_API_URL
    constants_url: str = DEFAULT_CONSTANTS_URL
    constants_path: str | None = None
    rpc_urls: dict[int, list[str]] = field(default_factory=dict)
    ethplorer_url: str = DEFAULT_ETHPLORER_URL
    ethplorer_key: str = "freekey"
    api_min_interval_s: float = 0.6
    http_timeout_s: float = 60.0

    @classmethod
    def from_env(cls) -> Settings:
        env = os.environ
        return cls(
            api_url=env.get("ANTICAPTURE_API_URL", DEFAULT_API_URL).rstrip("/"),
            constants_url=env.get("ANTICAPTURE_CONSTANTS_URL", DEFAULT_CONSTANTS_URL),
            constants_path=env.get("ANTICAPTURE_CONSTANTS_PATH") or None,
            rpc_urls={
                ETHEREUM: _split(env.get("RPC_URL", DEFAULT_RPC_URLS)),
                SCROLL: _split(env.get("SCROLL_RPC_URL", DEFAULT_SCROLL_RPC_URLS)),
            },
            ethplorer_url=env.get("ETHPLORER_API_URL", DEFAULT_ETHPLORER_URL).rstrip("/"),
            ethplorer_key=env.get("ETHPLORER_API_KEY", "freekey"),
            api_min_interval_s=float(env.get("API_MIN_INTERVAL_SECONDS", "0.6")),
            http_timeout_s=float(env.get("HTTP_TIMEOUT_SECONDS", "60")),
        )


# Alert thresholds.
THRESHOLDS = {
    "indexer_lag_seconds": 1800,  # chain event newer than the API's latest activity by more than this
    "supply_diff_pct": 0.1,  # API vs on-chain list sum
    "unlabeled_holder_pct": 1.0,  # top holder share that should be in some list
    "voting_power_sample": 20,  # top N delegates compared
    "recent_proposals": 10,  # latest N proposals compared
}

# Governor kinds: "oz" (proposalVotes), "bravo"/"alpha"/"nouns" (proposals() struct).
# Timelock kinds: "compound" (admin/pendingAdmin) or "oz" (AccessControl PROPOSER_ROLE).
# These mirror what Anticapture is configured to index (apps/indexer/src/lib/constants.ts
# and the dashboard dao-config). They are NOT necessarily the live governors: the point of
# the governance check is to notice when the chain has moved on.
DAOS: dict[str, dict] = {
    "uni": dict(
        enum="UNI",
        chain=ETHEREUM,
        token="0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        vp_fn="getCurrentVotes(address)",
        governors=[("0x408ED6354d4973f66138C91495F2f2FCbd8724C3", "bravo")],
        timelock=("0x1a9C8182C09F50C8318d769245beA52c32BE35BC", "compound"),
    ),
    "ens": dict(
        enum="ENS",
        chain=ETHEREUM,
        token="0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72",
        vp_fn="getVotes(address)",
        governors=[("0x323A76393544d5ecca80cd6ef2A560C6a395b7E3", "oz")],
        timelock=("0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7", "oz"),
    ),
    "gtc": dict(
        enum="GTC",
        chain=ETHEREUM,
        token="0xDe30da39c46104798bB5aA3fe8B9e0e1F348163F",
        vp_fn="getCurrentVotes(address)",
        governors=[
            ("0x9D4C63565D5618310271bF3F3c01b2954C1D1639", "oz"),
            ("0xDbD27635A534A3d3169Ef0498beB56Fb9c937489", "alpha"),
        ],
        timelock=("0x57a8865cfB1eCEf7253c27da6B4BC3dAEE5Be518", "compound"),
        # Proposal ids below this belong to the last governor in the list (GovernorAlpha).
        legacy_id_below=1000,
    ),
    "comp": dict(
        enum="COMP",
        chain=ETHEREUM,
        token="0xc00e94Cb662C3520282E6f5717214004A7f26888",
        vp_fn="getCurrentVotes(address)",
        governors=[("0x309a862bbC1A00e45506cB8A802D1ff10004c8C0", "oz")],
        timelock=("0x6d903f6003cca6255D85CcA4D3B5E5146dC33925", "compound"),
    ),
    "obol": dict(
        enum="OBOL",
        chain=ETHEREUM,
        token="0x0B010000b7624eb9B3DfBC279673C76E9D29D5F7",
        vp_fn="getVotes(address)",
        governors=[("0xcB1622185A0c62A80494bEde05Ba95ef29Fbf85c", "oz")],
        timelock=("0xCdBf527842Ab04Da548d33EB09d03DB831381Fb0", "oz"),
    ),
    "fluid": dict(
        enum="FLUID",
        chain=ETHEREUM,
        token="0x6f40d4A6237C257fff2dB00FA0510DeEECd303eb",
        vp_fn="getCurrentVotes(address)",
        governors=[("0x0204Cd037B2ec03605CFdFe482D8e257C765fA1B", "bravo")],
        timelock=("0xC7Cb1dE2721BFC0E0DA1b9D526bCdC54eF1C0eFC", "compound"),
    ),
    "nouns": dict(
        enum="NOUNS",
        chain=ETHEREUM,
        nft=True,
        token="0x9C8fF314C9Bc7F6e59A9d9225Fb22946427eDC03",
        vp_fn="getCurrentVotes(address)",
        governors=[("0x6f3E6272A167e8AcCb32072d08E0957F9c79223d", "nouns")],
        timelock=("0xb1a32FC9F9D8b2cf86C068Cae13108809547ef71", "compound"),
    ),
    "lil_nouns": dict(
        enum="LIL_NOUNS",
        chain=ETHEREUM,
        nft=True,
        token="0x4b10701Bfd7BFEdc47d50562b76b436fbB5BdB3B",
        vp_fn="getCurrentVotes(address)",
        governors=[("0x5d2C31ce16924C2a71D317e5BbFd5ce387854039", "nouns")],
        timelock=("0xd5f279ff9EB21c6D40C8f345a66f2751C4eeA1fB", "compound"),
    ),
    "shu": dict(
        enum="SHU",
        chain=ETHEREUM,
        token="0xe485E2f1bab389C08721B291f6b59780feC83Fd7",
        vp_fn="getVotes(address)",
        governors=[],
        timelock=None,
    ),
    "scr": dict(
        enum="SCR",
        chain=SCROLL,
        token="0xd29687c813D741E2F938F4aC377128810E217b1b",
        vp_fn="getVotes(address)",
        governors=[("0x2f3F2054776bd3C2fc30d750734A8F539Bb214f0", "oz")],
        timelock=("0x79D83D1518e2eAA64cdc0631df01b06e2762CC14", "oz"),
    ),
}
