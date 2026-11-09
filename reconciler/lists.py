"""Parse the address lists out of Anticapture's indexer ``constants.ts``.

This is a line-based parser, not a TypeScript parser. It understands the shapes used
in that file (``Label: "0x..."``, ``"Label":`` followed by the address on the next
line) and skips commented-out lines, which it reports separately.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

LIST_NAMES = [
    "TreasuryAddresses",
    "CEXAddresses",
    "DEXAddresses",
    "LendingAddresses",
    "BurningAddresses",
    "NonCirculatingAddresses",
]

# list name -> DAO enum -> [(label, address, line number)]
AddressLists = dict[str, dict[str, list[tuple[str, str, int]]]]


@dataclass(frozen=True)
class CommentedAddress:
    list_name: str
    dao: str | None
    line: int


def parse_lists(source: str) -> tuple[AddressLists, list[CommentedAddress]]:
    lines = source.split("\n")
    starts = {}
    for i, line in enumerate(lines):
        m = re.match(r"export const (\w+)", line)
        if m:
            starts[m.group(1)] = i
    ends = sorted(starts.values())
    out: AddressLists = {}
    commented: list[CommentedAddress] = []
    for name in LIST_NAMES:
        if name not in starts:
            out[name] = {}
            continue
        a = starts[name]
        b = min([s for s in ends if s > a] + [len(lines)])
        dao = None
        per_dao: dict[str, list[tuple[str, str, int]]] = {}
        pending = None
        for i in range(a, b):
            s = lines[i].strip()
            if s.startswith("//"):
                if re.search(r'"0x[0-9a-fA-F]{40}"', s):
                    commented.append(CommentedAddress(name, dao, i + 1))
                continue
            s = re.sub(r"//.*$", "", s)
            m = re.match(r"\[DaoIdEnum\.(\w+)\]", s)
            if m:
                dao = m.group(1)
                per_dao.setdefault(dao, [])
            m = re.match(r'"?([^":\[\]]+?)"?\s*:\s*"(0x[0-9a-fA-F]{40})"', s)
            if m and dao:
                per_dao[dao].append((m.group(1), m.group(2), i + 1))
                continue
            m = re.match(r'"?([^":\[\]]+?)"?\s*:\s*$', s)
            if m and dao:
                pending = (m.group(1), i + 1)
                continue
            m = re.match(r'"(0x[0-9a-fA-F]{40})"', s)
            if m and pending and dao:
                per_dao[dao].append((pending[0], m.group(1), pending[1]))
                pending = None
        out[name] = per_dao
    return out, commented


def load_constants(path: str | None, url: str, timeout: float = 60.0) -> str:
    """Read constants.ts from a local path if given, otherwise download it."""
    if path:
        with open(path) as f:
            return f.read()
    import urllib.request

    from .http import HEADERS

    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=timeout) as r:
        return r.read().decode()
