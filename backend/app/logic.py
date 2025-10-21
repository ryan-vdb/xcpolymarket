# backend/app/logic.py
from typing import Dict, Tuple

# -------- Display helpers (compat with existing routes/UI) --------
def odds(pool_yes_cents: int, pool_no_cents: int) -> Dict[str, float]:
    total = max(pool_yes_cents + pool_no_cents, 1)
    return {"yes": pool_yes_cents / total, "no": pool_no_cents / total}

def implied_payout_per1(pool_yes_cents: int, pool_no_cents: int) -> Dict[str, float]:
    """
    Back-compat for your Markets page. In CPMM this isn't the true 'payout multiple',
    but it's still a useful display: total/pool_side (converted from cents to points).
    """
    total = pool_yes_cents + pool_no_cents
    yes = total / max(pool_yes_cents, 1)
    no  = total / max(pool_no_cents, 1)
    return {"yes": yes / 100.0, "no": no / 100.0}

# --------------------- CPMM core (Polymarket-like) ---------------------
def cpmm_price_yes(pool_yes: int, pool_no: int) -> float:
    total = pool_yes + pool_no
    return pool_yes / total if total > 0 else 0.5

def cpmm_buy_yes(pool_yes: int, pool_no: int, cash_in: int) -> Tuple[int, int, int]:
    """
    User pays `cash_in` cents; receives YES shares (in cents of par).
      shares = (pool_no * cash_in) / (pool_yes + cash_in)
      pool_yes' = pool_yes + cash_in
      pool_no'  = pool_no  - shares
    Returns: (shares_out_cents, new_pool_yes, new_pool_no)
    """
    if cash_in <= 0:
        return 0, pool_yes, pool_no
    denom = pool_yes + cash_in
    if denom <= 0:
        return 0, pool_yes, pool_no
    shares = (pool_no * cash_in) // denom
    new_py = pool_yes + cash_in
    new_pn = pool_no - shares
    if new_pn < 0:
        shares += new_pn  # clamp
        new_pn = 0
    return shares, new_py, new_pn

def cpmm_buy_no(pool_yes: int, pool_no: int, cash_in: int) -> Tuple[int, int, int]:
    """
    Symmetric for NO:
      shares = (pool_yes * cash_in) / (pool_no + cash_in)
      pool_no'  = pool_no  + cash_in
      pool_yes' = pool_yes - shares
    """
    if cash_in <= 0:
        return 0, pool_yes, pool_no
    denom = pool_no + cash_in
    if denom <= 0:
        return 0, pool_yes, pool_no
    shares = (pool_yes * cash_in) // denom
    new_pn = pool_no + cash_in
    new_py = pool_yes - shares
    if new_py < 0:
        shares += new_py
        new_py = 0
    return shares, new_py, new_pn