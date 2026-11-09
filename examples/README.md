# Example run

`latest-run/` is a real run of `python -m reconciler` against the production Anticapture API and public RPCs, finished on 2026-11-09 at 15:19 UTC (12:19 BRT). It covered all 10 DAOs in 121 s and produced 88 alerts:

- 1 critical;
- 12 high;
- 69 medium;
- 5 low;
- 1 info.

The address lists came from `constants.ts` on the `dev` branch of `blockful/anticapture`.

The findings in it are real at that time. They include:
- GTC's timelock now owned by Governor Charlie `0xef41CbD211076E8b1901e214Bf751d404cf06638`;
- the stalled Nouns indexer;
- abstain votes counted as "for" on GTC;
- a Scroll proposal whose `VoteCastWithParams` votes were not indexed;
- `/lil_nouns/token` returning HTTP 500.

They will change as Anticapture ships fixes.
