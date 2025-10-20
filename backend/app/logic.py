from typing import Dict

def odds(s_yes: int, s_no: int) -> Dict[str, float]:
    total = max(s_yes + s_no, 1)
    return {"yes": s_yes / total, "no": s_no / total}

def implied_payout_per1(s_yes: int, s_no: int) -> Dict[str, float]:
    total = s_yes + s_no
    yes = total / max(s_yes, 1)
    no = total / max(s_no, 1)
    return {"yes": yes / 100.0, "no": no / 100.0}  # convert from cents → points per 1 point

def preview_after_add(s_yes: int, s_no: int, side: str, add_cents: int):
    if side == "YES":
        s_yes += add_cents
    else:
        s_no += add_cents
    return {
        "odds": odds(s_yes, s_no),
        "implied_payout_per1": implied_payout_per1(s_yes, s_no),
        "totals": {"s_yes_cents": s_yes, "s_no_cents": s_no}
    }