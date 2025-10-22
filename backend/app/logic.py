# backend/app/logic.py
# ------------------------------------------------------------
# Binary CPMM with virtual liquidity (Uniswap-style x*y = k).
# - Monetary units in DB are *cents* (integers).
# - Returned share amounts are in *points* (floats), where
#     1.0 share pays exactly 1.0 point (=100 cents) on win.
# - YES/NO prices move continuously; virtual liquidity provides
#   initial depth and keeps prices well-defined at launch.
# ------------------------------------------------------------

from __future__ import annotations
from typing import Dict, Literal, Tuple

Side = Literal["YES", "NO"]
EPS = 1e-12  # numeric guard for division

# --------------- Effective pools (real + virtual) ---------------

def effective_pools(
    yes_real_cents: int,
    no_real_cents: int,
    virt_yes_cents: int,
    virt_no_cents: int,
) -> Tuple[float, float]:
    """Return effective YES/NO pools in *cents* including virtual depth."""
    y = float(yes_real_cents + virt_yes_cents)
    n = float(no_real_cents + virt_no_cents)
    # Keep strictly positive
    if y < EPS: y = EPS
    if n < EPS: n = EPS
    return y, n


# --------------- Prices & odds (spot) ---------------

def spot_price_yes(yes_eff_cents: float, no_eff_cents: float) -> float:
    """Spot price for a YES share (in points per share, i.e. [0..1])."""
    return no_eff_cents / (yes_eff_cents + no_eff_cents)

def spot_price_no(yes_eff_cents: float, no_eff_cents: float) -> float:
    """Spot price for a NO share (in points per share, i.e. [0..1])."""
    return yes_eff_cents / (yes_eff_cents + no_eff_cents)

def odds_from_pools(yes_eff_cents: float, no_eff_cents: float) -> Dict[str, float]:
    """Return odds (YES/NO) from current effective pools."""
    total = yes_eff_cents + no_eff_cents
    if total < EPS:
        return {"yes": 0.5, "no": 0.5}
    return {"yes": yes_eff_cents / total, "no": no_eff_cents / total}

def implied_payout_per1_spot(yes_eff_cents: float, no_eff_cents: float) -> Dict[str, float]:
    """
    Convenience: 'payout per 1 point' at the *spot* price.
    If price_yes = p, naive payout multiple shown = 1/p; similarly for NO.
    (This is just for UI display; actual profit depends on average fill.)
    """
    p_yes = spot_price_yes(yes_eff_cents, no_eff_cents)
    p_no  = spot_price_no(yes_eff_cents, no_eff_cents)
    return {
        "yes": (1.0 / max(p_yes, EPS)),
        "no":  (1.0 / max(p_no,  EPS)),
    }


# --------------- CPMM math (buy integrals) ---------------

def _shares_for_spend_yes(yes_eff: float, no_eff: float, spend_cents: float) -> float:
    """
    Continuous buy YES: integrate price curve.
    Initial price p0 = no_eff / (yes_eff + no_eff).
    New k must remain constant: (yes_eff + Δy) * (no_eff - Δn) = k, but
    for the x*y=k invariant with prices defined as above, the integral
    amount of YES shares issued for spend S (in cents/points*100) is:

    shares_yes = (S / 100) * (1 / p_avg)  where p_avg is the average fill price.
    In closed-form for x*y=k, this reduces to:
        shares_yes = ( (no_eff + yes_eff) * ln( (yes_eff + no_eff) / (yes_eff + no_eff - S) ) - S ) / 100
    BUT that expression mixes units; instead we use the standard
    differential relation:
        price_yes = no / (yes + no)
        dYES_shares = (dSpend / 100) / price_yes
    and integrate numerically in a few steps for stability.
    """
    # To keep this robust and easy to reason about, do a small-step integration.
    steps = max(1, min(100, int(spend_cents // 50) + 1))  # ~50¢ per step
    remaining = spend_cents
    shares = 0.0
    y, n = yes_eff, no_eff
    for _ in range(steps):
        if remaining <= 0:
            break
        dS = remaining / (steps - _)  # split remainder evenly across remaining steps
        price = spot_price_yes(y, n)  # points/share
        # shares bought this sub-step:
        dShares = (dS / 100.0) / max(price, EPS)
        shares += dShares
        # pools move: buying YES pushes YES up and NO down in effective space
        # Spend dS adds to YES effective pool and removes from NO effective pool to preserve x*y
        y += dS
        n = max(n - dS, EPS)
        remaining -= dS
    return shares

def _shares_for_spend_no(yes_eff: float, no_eff: float, spend_cents: float) -> float:
    """Symmetric to _shares_for_spend_yes."""
    steps = max(1, min(100, int(spend_cents // 50) + 1))
    remaining = spend_cents
    shares = 0.0
    y, n = yes_eff, no_eff
    for _ in range(steps):
        if remaining <= 0:
            break
        dS = remaining / (steps - _)
        price = spot_price_no(y, n)
        dShares = (dS / 100.0) / max(price, EPS)
        shares += dShares
        # Buying NO adds to NO pool and removes from YES pool
        n += dS
        y = max(y - dS, EPS)
        remaining -= dS
    return shares


# --------------- Public helpers for router code ---------------

def preview_buy(
    side: Side,
    spend_cents: int,
    yes_real_cents: int,
    no_real_cents: int,
    virt_yes_cents: int,
    virt_no_cents: int,
) -> Dict[str, float]:
    """
    Compute preview without mutating state:
    - shares_points_issued
    - price_yes_after
    - odds after
    - implied spot payout multiples
    """
    if spend_cents <= 0:
        return {
            "shares_points_issued": 0.0,
            "price_yes_after": spot_price_yes(*effective_pools(yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)),
            "odds": odds_from_pools(*effective_pools(yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)),
            "implied_payout_per1_spot": implied_payout_per1_spot(*effective_pools(yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)),
        }

    y, n = effective_pools(yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)

    if side == "YES":
        shares = _shares_for_spend_yes(y, n, float(spend_cents))
        # after move (effective):
        y_after = y + spend_cents
        n_after = max(n - spend_cents, EPS)
    else:
        shares = _shares_for_spend_no(y, n, float(spend_cents))
        n_after = n + spend_cents
        y_after = max(y - spend_cents, EPS)

    price_after = spot_price_yes(y_after, n_after)
    odds_after = odds_from_pools(y_after, n_after)
    mult_after = implied_payout_per1_spot(y_after, n_after)

    return {
        "shares_points_issued": shares,
        "price_yes_after": price_after,
        "odds": odds_after,
        "implied_payout_per1_spot": mult_after,
    }


def apply_buy(
    side: Side,
    spend_cents: int,
    yes_real_cents: int,
    no_real_cents: int,
    virt_yes_cents: int,
    virt_no_cents: int,
) -> Dict[str, float]:
    """
    Apply a buy to REAL pools, returning:
      - new_yes_real_cents / new_no_real_cents (ints)
      - shares_points_issued (float)
      - price_yes_after, odds, implied_payout_per1_spot
    NOTE: virtual pools are *not* mutated here (they're fixed depth).
    """
    if spend_cents <= 0:
        return {
            "new_yes_real_cents": yes_real_cents,
            "new_no_real_cents": no_real_cents,
            "shares_points_issued": 0.0,
            "price_yes_after": spot_price_yes(*effective_pools(yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)),
            "odds": odds_from_pools(*effective_pools(yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)),
            "implied_payout_per1_spot": implied_payout_per1_spot(*effective_pools(yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)),
        }

    y_eff, n_eff = effective_pools(yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)

    if side == "YES":
        shares = _shares_for_spend_yes(y_eff, n_eff, float(spend_cents))
        # Real pools change: we *add* spend to YES real, and conceptually
        # remove the same from NO effective — but since virtual is fixed,
        # we only mutate the REAL side we added to.
        new_yes_real = yes_real_cents + spend_cents
        new_no_real  = no_real_cents
        y_after, n_after = effective_pools(new_yes_real, new_no_real, virt_yes_cents, virt_no_cents)
    else:
        shares = _shares_for_spend_no(y_eff, n_eff, float(spend_cents))
        new_no_real  = no_real_cents + spend_cents
        new_yes_real = yes_real_cents
        y_after, n_after = effective_pools(new_yes_real, new_no_real, virt_yes_cents, virt_no_cents)

    return {
        "new_yes_real_cents": int(round(new_yes_real)),
        "new_no_real_cents":  int(round(new_no_real)),
        "shares_points_issued": float(shares),
        "price_yes_after": spot_price_yes(y_after, n_after),
        "odds": odds_from_pools(y_after, n_after),
        "implied_payout_per1_spot": implied_payout_per1_spot(y_after, n_after),
    }