"""ABI encoding helpers and contract reads (eth_call, Multicall3)."""

from __future__ import annotations

from eth_abi import decode, encode
from eth_utils import keccak, to_checksum_address

from .config import MULTICALL3
from .http import RpcClient


def selector(signature: str) -> str:
    return "0x" + keccak(text=signature).hex()[:8]


def topic(signature: str) -> str:
    return "0x" + keccak(text=signature).hex()


def enc_address(address: str) -> str:
    return address.lower()[2:].rjust(64, "0")


def enc_uint(n: int) -> str:
    return hex(int(n))[2:].rjust(64, "0")


def words(hex_data: str | None) -> list[int]:
    """Split ABI return data into 32-byte unsigned words."""
    h = (hex_data or "0x")[2:]
    return [int(h[i : i + 64], 16) for i in range(0, len(h), 64)]


def word_address(hex_data: str) -> str:
    return to_checksum_address("0x" + hex_data[-40:])


class Chain:
    def __init__(self, rpc: RpcClient):
        self.rpc = rpc

    def call(self, to: str, data: str, chain: int = 1, block: str = "latest") -> str:
        return self.rpc.request("eth_call", [{"to": to, "data": data}, block], chain)

    def multicall(self, calls: list[tuple[str, str]], chain: int = 1, block: str = "latest") -> list[str | None]:
        """Run (target, calldata) pairs through Multicall3.tryAggregate; failed calls are None."""
        out: list[str | None] = []
        for i in range(0, len(calls), 150):
            part = calls[i : i + 150]
            payload = encode(
                ["bool", "(address,bytes)[]"],
                [False, [(to_checksum_address(t), bytes.fromhex(d[2:])) for t, d in part]],
            ).hex()
            r = self.call(MULTICALL3, selector("tryAggregate(bool,(address,bytes)[])") + payload, chain, block)
            results = decode(["(bool,bytes)[]"], bytes.fromhex(r[2:]))[0]
            out += ["0x" + b.hex() if ok else None for ok, b in results]
        return out

    def head(self, chain: int) -> int:
        return int(self.rpc.request("eth_blockNumber", [], chain), 16)

    def block_timestamp(self, number: int, chain: int) -> int:
        return int(self.rpc.request("eth_getBlockByNumber", [hex(number), False], chain)["timestamp"], 16)

    def get_logs(self, address: str, from_block: int, to_block: int, chain: int) -> list[dict]:
        return self.rpc.request(
            "eth_getLogs", [{"address": address, "fromBlock": hex(from_block), "toBlock": hex(to_block)}], chain
        )
