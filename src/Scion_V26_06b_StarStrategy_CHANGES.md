# MLB Scion — V26.06b play-strategy implementation (PDF §9)

Implements the two-tier flag state machine (§9.2) and the 1/3/5/7-star decision
table (§9.3/§9.4). Only `MLB_Scion.py` and `MLB_Scion_Globals.py` changed —
**no changes to `MLB_Scion_Preds.py`** (all required getters/setters already
existed).

## MLB_Scion_Globals.py

- **New constants:** `PROB_STRONG_VOTE_THRESHOLD = 0.93`; ensemble-state labels
  `ENS_STATE_SILENT / ENS_STATE_FLAG / ENS_STATE_STRONG` (+ `ENS_FLAGGED_STATES`);
  home-dog price-tier bounds `HOMEDOG_PRICE_TIER_LOW = 100`,
  `HOMEDOG_PRICE_TIER_HIGH = 119`.
- **`getNumStars()` fixed** to return 6 and 7 (previously anything above FIVESTAR
  silently returned 0 — the 7★ tier would have been lost).
- **New messages:** per-ensemble state comments (STRONG-FLAG / FLAG / SILENT-dog
  / SILENT-gate for both ensembles) and per-decision comments (consensus 7★/5★,
  single home-fave override 3★, single visitor-fave no-override 1★, default
  visitor-dog 1★, default home-dog tiered), plus null-SP "allowed" notes.

## MLB_Scion.py

- **`deriveBookProbabilities()` (new helper).** Computes `book_close(home)` (devig
  of the closing implied probs — sets the FAVE side) and `book_mid(home)` (devig
  of the mean of opening+closing implied probs — used for the gap), per §9.1. If
  the opening line is missing/invalid, `book_mid` falls back to `book_close`.
- **`validateEnsemblePosition()` rewritten** into the §9.2 state machine. It now
  returns `(ensState, predsObj)` where `ensState ∈ {SILENT, FLAG, STRONG-FLAG}`:
  an ensemble is flagged only when it backs the FAVE side, its gap over
  `book_mid` clears the edge threshold, and its side-vote share clears 0.83
  (FLAG) or 0.93 (STRONG). `_addEnsStateComment()` records the state/reason.
- **`determineScionSidePosition()` rewritten** to apply the §9.4 decision table:
  both flagged → FAVE (7★ if both STRONG else 5★); exactly one flagged → HF 3★ if
  the fave is home, else HOME DOG 1★ (single visitor-fave flag does **not**
  override); none flagged → the DOG, with the visitor dog flat 1★ and the home
  dog closing-price tiered 5★/3★/5★ on `hom_clml`.
- **`getDefaultDogPlay()` simplified** to return the dog side from the bookie
  prices with the old win-loss-price gate removed (every in-scope game is now
  played).
- `getB1Position()`, `getPriceVoteMatchStatus()`, `applySideStrategy()` and
  `evaluateModelResponse()` are unchanged. (`getPriceVoteMatchStatus()` is now
  unused by the play path but retained.)

## Behaviour changes to be aware of (intended, per §9)

1. **VF (visitor-favourite) plays are now made** (both ensembles flag a visitor
   favourite → 7★/5★). The old "VF disallowed" rule is gone.
2. **Null starting-pitcher games are now played** (previously NoPlay). They are
   still noted in the comments for awareness.
3. **Every in-scope game gets a play** — the old bookie-range and model-price-range
   gates no longer suppress games to NoPlay. NoPlay now occurs **only** when a
   valid team price cannot be computed (|price| < 100). This assumes the ±150
   scoping is enforced upstream (the pm150 matchup set); if some out-of-scope
   games can reach this stage, add a scope guard before the decision.
4. **The gap is now measured against `book_mid`** (mean of open+close), not the
   closing line as before. The FAVE side is still set by the closing line.

## Validation performed

- Both files compile (`py_compile`).
- The state machine and all rows of the §9.3 table were unit-tested (22 cases).
- The **actual** rewritten functions were run end-to-end against mock config/preds
  objects across 12 representative games (every table row, null-SP, invalid
  price) — all correct.
- Not run against the live pipeline (needs the full module set + model outputs);
  recommend a smoke run on one slate, and per §9.5 deploy with **all stars forced
  to 1 (flat)** in the forward test first, switching star weights on only once the
  ladder ordering holds.
