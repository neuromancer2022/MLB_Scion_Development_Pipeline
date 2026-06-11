# MLB Scion — What Actually Happened to the Season

*V25.08b2SE, balance sheet to 11 Jun 2026. A read-over-coffee summary.*

---

## The headline: there was no June collapse, and no cliff

The story we'd been telling — "$110k down to $20k, probably model and data drift from
the dGEN clean-up, hitting around 5 June" — doesn't survive contact with the numbers.

- The equity curve **peaked at $117,560 on 11 May**, not in June.
- It then bled down in a high-variance sawtooth through late May and into June,
  briefly going **negative (−$8,320 on 8 June)** before recovering to **+$8,120** today.
- **5 June was a +$7,680 day.** There is no discontinuity there. The earlier
  hypothesis that the dGEN feature fix caused a train-serve cliff is off the table.

So the season didn't crash. It turned over $2.01m to finish at **+0.40% ROI** —
essentially break-even — and the question worth answering isn't "what broke in June"
but "why is a system that should be making 8% sitting at zero."

## The answer is almost a single cell

Breaking the book down by side, price band and stake size, nearly all the damage
lands in one place:

| Favourite price band | Bets | Win % | P/L | ROI |
|---|---|---|---|---|
| −100 to −110 | 29 | 58.6% | **+$11,355** | +8.7% |
| **−111 to −130** | 28 | **39.3%** | **−$61,800** | **−42.5%** |
| −131 to −150 | 15 | 60.0% | −$8,685 | −11.8% |

And within that −111/−130 band, the bleed is concentrated entirely in the
**top $6,000 stake tier: 21 bets, 33.3% win rate, −$61,140, −48.5% ROI.**

That one cell is **96% of the entire −$63,780 favourite loss**. It is not a bad month —
it loses in *every* month (Apr −$15,600, May −$33,450, Jun −$12,750). Strip those
21 bets and the EX book goes from +$6,090 to roughly **+$67,000**.

## Everything else is working

This is the part that matters for morale and direction: the rest of the book is fine.

- **Dogs: +6.0% ROI** (+$69,870 on the EX side) — the engine is healthy.
- **Small favourites (−100 to −110): +8.7%** — favourites aren't all bad, just the juicy ones.
- **The $3,000 stake tier: +14.9% (+$61,830)** — the lower-confidence bets are the *best* bets.

Which exposes the actual fault. The biggest stakes sit on the worst bets:
**$6,000 favourites are −32%, while $6,000 dogs are a perfectly healthy +6.4%.**
The confidence signal is inverted *on the favourite side* — the ensemble stakes
hardest exactly where it is least right. Laying −120 juice and winning a third of
the time is arithmetic, not bad luck: that price needs ~55% to break even.

## Being honest about the statistics

Twenty-one bets is a small number, and I've sliced the data four ways to isolate
this, which is precisely how you manufacture a pattern that isn't there. Three things
keep it credible: it's negative in all three months (variance doesn't repeat that
cleanly), it has a structural mechanism (the breakeven arithmetic above), and the
action it implies isn't a significance claim. "Don't put your maximum stake on your
empirically worst, most-vig-exposed bet type until you understand why" is just risk
management — it holds even if the true number is merely mediocre rather than −48%.

## Leading hypothesis for the inversion

I can't see the stake-sizing logic from the accounting, so this needs checking in the
code. The most likely mechanism, given the two-ensemble design: a −120 favourite falls
inside **both** the ±150 and the ±210 ensembles, collects agreement from two ensembles
rather than one, clears the top-stake threshold, and gets the $6,000 ticket. In other
words, overlapping price bands manufacture false confidence on exactly the favourites
that lose. If that's the cause, the fix lives in the staking rule, not the models.

## What to do, in order

1. **Before Ivan resumes — cap or kill the favourite side.** Minimum-regret: drop the
   top stake tier on −111 to −130 favourites. Cleaner: stop betting favourites entirely
   until proven otherwise. No retraining required; it roughly triples the season
   retrospectively.

2. **Diagnose the confidence-to-stake inversion** — the real bug. Check whether stake is
   driven by cross-ensemble agreement and whether agreement runs higher on the losing
   favourites (the double-counting hypothesis above).

3. **Do not retrain in response to this.** It's a bet-selection and staking failure on
   top of the models, not a training-data fault. Retraining would bury it.

4. **Make the evaluation pipeline surface this automatically.** Extend the sports_roi
   bucket report with a side × price-band × stake-tier panel, so an −$85k favourite book
   can never again hide behind a +$93k dog book. Run the new V119 / V123 candidates
   through it to confirm they don't repeat the over-bet-favourites behaviour.

5. **On the ±150 / ±210 split and a possible 150–210 band:** the data argues against
   carving a dedicated band — favourites above −150 are barely bet, and the dogs that
   carried the 151–170 slice (+$55,800 on 20 bets) look like an unrepeatable hot streak.
   The favourite damage is in the *moderate* zone the ±150 ensemble already owns.

6. **This sharpens the V123 / dog-first direction.** The live edge is unambiguously the
   dog side — which is what the V119 "10% on dogs" backtest already said. When testing
   V123, look explicitly at whether removing the current line tames the favourite
   overconfidence; if it does, that's a strong independent reason to weight V123 up.

---

**Bottom line:** the binding problem was never V113-vs-V123 model counts, and it wasn't
the data fix. It's that the legacy system stakes hardest on a bet type it can't beat.
That's a one-line risk fix today and a staking-logic diagnosis this week — both upstream
of any retraining decision.
