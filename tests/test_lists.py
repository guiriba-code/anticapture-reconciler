from reconciler.lists import parse_lists

SOURCE = """
export const TreasuryAddresses: Record<DaoIdEnum, Record<string, Address>> = {
  [DaoIdEnum.GTC]: {
    Timelock: "0x57a8865cfB1eCEf7253c27da6B4BC3dAEE5Be518",
    "Long label":
      "0x1111111111111111111111111111111111111111",
    // Old: "0x2222222222222222222222222222222222222222",
  },
};
export const CEXAddresses: Record<DaoIdEnum, Record<string, Address>> = {
  [DaoIdEnum.GTC]: {
    Bithumb: "0x74be0CF1c9972C00ed4EF290e0E5BCFd18873f13",
    Upbit: "0x74be0CF1c9972C00ed4EF290e0E5BCFd18873f13", // duplicate
  },
};
"""


def test_parses_inline_and_wrapped_entries():
    lists, _ = parse_lists(SOURCE)
    treasury = lists["TreasuryAddresses"]["GTC"]
    assert [(label, addr) for label, addr, _ in treasury] == [
        ("Timelock", "0x57a8865cfB1eCEf7253c27da6B4BC3dAEE5Be518"),
        ("Long label", "0x1111111111111111111111111111111111111111"),
    ]


def test_commented_addresses_are_reported_not_parsed():
    lists, commented = parse_lists(SOURCE)
    addrs = {a for _, a, _ in lists["TreasuryAddresses"]["GTC"]}
    assert "0x2222222222222222222222222222222222222222" not in addrs
    assert len(commented) == 1
    assert commented[0].list_name == "TreasuryAddresses"
    assert commented[0].dao == "GTC"


def test_missing_lists_are_empty():
    lists, _ = parse_lists(SOURCE)
    assert lists["DEXAddresses"] == {}
    assert len(lists["CEXAddresses"]["GTC"]) == 2
