# Reconciler alerts

Run finished at 2026-11-09 15:19 UTC, took 121 s. DAOs: uni, ens, gtc, comp, obol, fluid, nouns, lil_nouns, shu, scr. Total: 88 alerts.

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
| medium | comp | list_category_conflict | address is in more than one category | `{"address": "0x3Afdc9BCA9213A35503b077a6072F3D0d5AB0840", "categories": ["LendingAddresses", "TreasuryAddresses"]}` |
| medium | comp | list_category_conflict | address is in more than one category | `{"address": "0xc3d688B66703497DAA19211EEdff47f25384cdc3", "categories": ["LendingAddresses", "TreasuryAddresses"]}` |
| medium | comp | list_duplicate | TreasuryAddresses: the same address appears with 2 labels | `{"address": "0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf", "labels": [["manUSDbC", 381], ["arbUSDC", 388]]}` |
| medium | comp | list_duplicate | CEXAddresses: the same address appears with 2 labels | `{"address": "0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503", "labels": [["Binance 2", 594], ["Upbit", 600]]}` |
| medium | comp | unlabeled_holder | holder with 18.21% of supply is not in any list | `{"address": "0x91d14789071e5E195FFC9F745348736677De3292", "balance": 1820531}` |
| medium | comp | unlabeled_holder | holder with 12.78% of supply is not in any list | `{"address": "0x1d48963DD8FAdA6aB5C2C7b92Eba81ECC5030270", "balance": 1277641}` |
| medium | comp | unlabeled_holder | holder with 2.90% of supply is not in any list | `{"address": "0x5a52E96BAcdaBb82fd05763E25335261B270Efcb", "balance": 290386}` |
| medium | comp | unlabeled_holder | holder with 2.87% of supply is not in any list | `{"address": "0x27944bC193AF572136b0f370Ca738514D52f7c80", "balance": 287024}` |
| medium | comp | unlabeled_holder | holder with 1.92% of supply is not in any list | `{"address": "0x8BacCcA3e83843555867b3865d7689D099406567", "balance": 192200}` |
| medium | comp | unlabeled_holder | holder with 1.19% of supply is not in any list | `{"address": "0xaa58d64f9Ca0d6436F903A4d590AD8e5982c8030", "balance": 119214}` |
| medium | comp | unlabeled_holder | holder with 1.01% of supply is not in any list | `{"address": "0x3E0f52239518B540a06f81d51AC4ea7FfdEce329", "balance": 101000}` |
| medium | ens | unlabeled_holder | holder with 3.56% of supply is not in any list | `{"address": "0x690F0581eCecCf8389c223170778cD9D029606F2", "balance": 3564590}` |
| medium | ens | unlabeled_holder | holder with 3.00% of supply is not in any list | `{"address": "0x2Cd5BB500066B913d320Fc9AC52a72422915c422", "balance": 3000738}` |
| medium | ens | unlabeled_holder | holder with 2.67% of supply is not in any list | `{"address": "0xF977814e90dA44bFA03b6295A0616a897441aceC", "balance": 2666476}` |
| medium | ens | unlabeled_holder | holder with 1.00% of supply is not in any list | `{"address": "0x9C7dB6B1085ec4D07f75c0BD91AD3FcD368fA19E", "balance": 1000000}` |
| medium | fluid | timelock_mismatch | governor.timelock() differs from the configured timelock | `{"configured": "0xC7Cb1dE2721BFC0E0DA1b9D526bCdC54eF1C0eFC", "onchain": "0x2386DC45AdDed673317eF068992F19421B481F4c"}` |
| medium | fluid | unlabeled_holder | holder with 5.81% of supply is not in any list | `{"address": "0x8675f6d434818BB3Ee99B7E3FD0acC5c9737DFFA", "balance": 5808211}` |
| medium | fluid | unlabeled_holder | holder with 5.78% of supply is not in any list | `{"address": "0xEeDaE08F92235AeE591993bb9108aCF35C6B1505", "balance": 5775021}` |
| medium | fluid | unlabeled_holder | holder with 5.00% of supply is not in any list | `{"address": "0xB671e841a8e6DB528358Ed385983892552EF422f", "balance": 5000000}` |
| medium | fluid | unlabeled_holder | holder with 5.00% of supply is not in any list | `{"address": "0xCaBebC7f76D53582a4be7d9972A2b4F531753fd7", "balance": 5000000}` |
| medium | fluid | unlabeled_holder | holder with 4.11% of supply is not in any list | `{"address": "0xd21fdB989c5897Be42A21e8D0C09599CBD87CcF6", "balance": 4107493}` |
| medium | fluid | unlabeled_holder | holder with 4.04% of supply is not in any list | `{"address": "0xa5978bcc0DeFdfFB50f5aFe763edfdcF5063Ac80", "balance": 4042620}` |
| medium | fluid | unlabeled_holder | holder with 3.41% of supply is not in any list | `{"address": "0x2C1cc9Ec0b727b08db1a468445eF84dA16cD80c7", "balance": 3414001}` |
| medium | fluid | unlabeled_holder | holder with 3.19% of supply is not in any list | `{"address": "0xa338ac3eF9ba403F3732755fE1cc1A184415B5b8", "balance": 3187500}` |
| medium | fluid | unlabeled_holder | holder with 2.50% of supply is not in any list | `{"address": "0x1716f0C19CbDe6644356a79fBE19361B0790f152", "balance": 2500000}` |
| medium | fluid | unlabeled_holder | holder with 2.10% of supply is not in any list | `{"address": "0x2079C29Be9c8095042edB95f293B5b510203d6cE", "balance": 2102468}` |
| medium | fluid | unlabeled_holder | holder with 1.50% of supply is not in any list | `{"address": "0xB0319779F1714C5AB393d79cDCE9eb05A603bDdf", "balance": 1500000}` |
| medium | fluid | unlabeled_holder | holder with 1.13% of supply is not in any list | `{"address": "0x6D05031b5E7514656232C37f7a237c6c3A4DdeeA", "balance": 1134845}` |
| medium | fluid | unlabeled_holder | holder with 1.02% of supply is not in any list | `{"address": "0x40b9fcc4afC60BcE840d8A1Fbce086067118B81a", "balance": 1016626}` |
| medium | fluid | unlabeled_holder | holder with 1.00% of supply is not in any list | `{"address": "0x2f5E5a67D55FD117b83049d05a48F6f678432100", "balance": 1000001}` |
| medium | fluid | unlabeled_holder | holder with 1.00% of supply is not in any list | `{"address": "0x5AAB0630aaCa6d0bf1c310aF6C2BB3826A951cFb", "balance": 1000001}` |
| medium | fluid | unlabeled_holder | holder with 1.00% of supply is not in any list | `{"address": "0x4b950048068b7acbe574d1Bf1Ed36c43C8Cba468", "balance": 1000000}` |
| medium | gtc | list_duplicate | CEXAddresses: the same address appears with 2 labels | `{"address": "0x74be0CF1c9972C00ed4EF290e0E5BCFd18873f13", "labels": [["Bithumb", 550], ["Upbit", 551]]}` |
| medium | gtc | unlabeled_holder | holder with 20.25% of supply is not in any list | `{"address": "0x14D7Cee42D4643f0C767A1D504d9cA24C890f86c", "balance": 20253987}` |
| medium | gtc | unlabeled_holder | holder with 6.04% of supply is not in any list | `{"address": "0x4Da8853217d0D5B59e8FCDE36D1BeBB0a1932A14", "balance": 6039329}` |
| medium | gtc | unlabeled_holder | holder with 4.80% of supply is not in any list | `{"address": "0x41fbBa5CB38D22B2D80606406944cEdd7c97f6F9", "balance": 4796933}` |
| medium | gtc | unlabeled_holder | holder with 3.34% of supply is not in any list | `{"address": "0x15Da7556D5ED888306839bed06f868AeaeDCb0d7", "balance": 3336048}` |
| medium | gtc | unlabeled_holder | holder with 1.56% of supply is not in any list | `{"address": "0x00eBF4F968A507a4404e643EeCB35449262861A1", "balance": 1564592}` |
| medium | gtc | unlabeled_holder | holder with 1.49% of supply is not in any list | `{"address": "0x2340Fc21b654a72DBBAF8aC6D4d3F39ed96C394E", "balance": 1491751}` |
| medium | gtc | unlabeled_holder | holder with 1.24% of supply is not in any list | `{"address": "0x900a248296691385357551cC7D5FAe9E256dce8E", "balance": 1243247}` |
| medium | gtc | unlabeled_holder | holder with 1.06% of supply is not in any list | `{"address": "0x42C7DF3f6BFe02EB61c0C2Bd2d73C69eeC6023cd", "balance": 1059739}` |
| medium | obol | unlabeled_holder | holder with 12.30% of supply is not in any list | `{"address": "0xAEfd0B68212ddca96D9cF69128C6f47351feF5FB", "balance": 61484761}` |
| medium | obol | unlabeled_holder | holder with 5.34% of supply is not in any list | `{"address": "0xc2B2fbAfb17E5Bc59AB0CEa2B811529303b9bD83", "balance": 26712528}` |
| medium | obol | unlabeled_holder | holder with 3.65% of supply is not in any list | `{"address": "0x6e8aA1C7Fe95F049232DeD6369963751d3E18E97", "balance": 18250000}` |
| medium | obol | unlabeled_holder | holder with 3.43% of supply is not in any list | `{"address": "0x2CDE9919e81b20B4B33DD562a48a84b54C48F00C", "balance": 17129896}` |
| medium | obol | unlabeled_holder | holder with 2.80% of supply is not in any list | `{"address": "0x872a45DB44F9e9f4341F2f738Eefc84b1F6eb205", "balance": 14005033}` |
| medium | obol | unlabeled_holder | holder with 2.61% of supply is not in any list | `{"address": "0x1bb64AF7FE05fc69c740609267d2AbE3e119Ef82", "balance": 13060987}` |
| medium | obol | unlabeled_holder | holder with 2.20% of supply is not in any list | `{"address": "0xf15a9265b7f3783b0b9B21de23F02F46794d4305", "balance": 10999996}` |
| medium | obol | unlabeled_holder | holder with 2.20% of supply is not in any list | `{"address": "0x94b0a3f9102BB4690e78aA543B24Fe316e43A0bA", "balance": 10999996}` |
| medium | obol | unlabeled_holder | holder with 2.10% of supply is not in any list | `{"address": "0x4Bee16dA02971Da5A75ee7F79602Ab8c0cfF432C", "balance": 10521958}` |
| medium | obol | unlabeled_holder | holder with 2.03% of supply is not in any list | `{"address": "0x543714F349970cD3b02d6Dc6A85ac8641f2BB3A3", "balance": 10136622}` |
| medium | obol | unlabeled_holder | holder with 1.58% of supply is not in any list | `{"address": "0x13cae86c7ae26DBaDe71C3ce16f7Cad00B97201e", "balance": 7912559}` |
| medium | obol | unlabeled_holder | holder with 1.39% of supply is not in any list | `{"address": "0xa8bF0cD4D76D92Cb345e81999029f3174A219305", "balance": 6953274}` |
| medium | obol | unlabeled_holder | holder with 1.00% of supply is not in any list | `{"address": "0xA44f2f0B5CBDc5895d3Db8A81334bcD8F62cefd2", "balance": 4999996}` |
| medium | scr | list_duplicate | DEXAddresses: the same address appears with 2 labels | `{"address": "0x7761786afAB6E496e6Bf3EBe56fc2ea71cd02d7D", "labels": [["Honeypop", 691], ["DEX", 692]]}` |
| medium | shu | unlabeled_holder | holder with 7.08% of supply is not in any list | `{"address": "0x05a886B980654a3da2E424A6725265b43773a6a1", "balance": 70794021}` |
| medium | shu | unlabeled_holder | holder with 6.00% of supply is not in any list | `{"address": "0x2379bD87Dc1Ae99C478811Eb546e1E61C3F14f7D", "balance": 60000000}` |
| medium | shu | unlabeled_holder | holder with 1.90% of supply is not in any list | `{"address": "0x88ad09518695c6c3712AC10a214bE5109a655671", "balance": 19016571}` |
| medium | shu | unlabeled_holder | holder with 1.33% of supply is not in any list | `{"address": "0xBF1a121A3ddd82b34f15aaE3Fa1F53E4D29dBF7B", "balance": 13250001}` |
| medium | shu | unlabeled_holder | holder with 1.32% of supply is not in any list | `{"address": "0xB476Ee7D610DAe7B23B671EBC7Bd6112E9772969", "balance": 13221073}` |
| medium | shu | unlabeled_holder | holder with 1.28% of supply is not in any list | `{"address": "0x4E0882D6D8d8fb911a1ece4a1ED1A915d1620ADF", "balance": 12811926}` |
| medium | shu | unlabeled_holder | holder with 1.28% of supply is not in any list | `{"address": "0x563c784005222cebbD49E66BD5A1cB63dFe622a2", "balance": 12767045}` |
| medium | shu | unlabeled_holder | holder with 1.08% of supply is not in any list | `{"address": "0x11A48030Ff922a40Cef987Eb93b8f14b5cEB3360", "balance": 10796357}` |
| medium | shu | unlabeled_holder | holder with 1.04% of supply is not in any list | `{"address": "0x925De0307879CD9d96043B37f61671529Ff6C42E", "balance": 10370958}` |
| medium | uni | unlabeled_holder | holder with 2.30% of supply is not in any list | `{"address": "0x61CB39BecE033c5bdA281747db1c15CceD2096eB", "balance": 23047481}` |
| medium | uni | unlabeled_holder | holder with 1.64% of supply is not in any list | `{"address": "0x611f7bF868a6212f871e89F7e44684045DdFB09d", "balance": 16366631}` |
| medium | uni | unlabeled_holder | holder with 1.33% of supply is not in any list | `{"address": "0x5069A64BC6616dEC1584eE0500B7813A9B680F7E", "balance": 13314112}` |
| medium | uni | unlabeled_holder | holder with 1.26% of supply is not in any list | `{"address": "0x36CA0ABDF3852f00AEE7798C7DFb5eaD5D3FEc2A", "balance": 12611331}` |
| medium | uni | unlabeled_holder | holder with 1.03% of supply is not in any list | `{"address": "0x6D278351f4A973D1349Ef1e54ED37DAEd0799e19", "balance": 10286054}` |
| low | fluid | health_false_positive | /health says 'degraded' but the indexer is caught up with the chain (the DAO is just quiet) | `{"api_last_activity": "2026-11-09 15:11 UTC", "chain_last_event": "2026-11-09 15:11 UTC"}` |
| low | gtc | health_false_positive | /health says 'degraded' but the indexer is caught up with the chain (the DAO is just quiet) | `{"api_last_activity": "2026-11-09 15:12 UTC", "chain_last_event": "2026-11-09 15:12 UTC"}` |
| low | lil_nouns | health_false_positive | /health says 'degraded' but the indexer is caught up with the chain (the DAO is just quiet) | `{"api_last_activity": "2026-11-09 10:54 UTC", "chain_last_event": "2026-11-09 10:54 UTC"}` |
| low | obol | health_false_positive | /health says 'degraded' but the indexer is caught up with the chain (the DAO is just quiet) | `{"api_last_activity": "2026-11-09 15:09 UTC", "chain_last_event": "2026-11-09 15:09 UTC"}` |
| low | shu | health_false_positive | /health says 'degraded' but the indexer is caught up with the chain (the DAO is just quiet) | `{"api_last_activity": "2026-11-08 20:08 UTC", "chain_last_event": "2026-11-08 20:08 UTC"}` |
| info | uni | list_commented_line | DEXAddresses: commented-out address on line 647 (not counted in any metric) | `{"line": 647}` |
