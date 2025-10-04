# sainte_lague_calculator.py
from __future__ import annotations

from typing import Dict, List, Tuple


def allocate_sainte_lague(
    votes: Dict[str, int],
    total_seats: int,
    threshold_pct: float = 0.0,
    *,
    first_divisor: float = 1.0,  # 1.0 standard; p.sh. 1.4 për 'modified'
) -> Dict[str, int]:
    """
    Ndarja e ulëseve me metodën Sainte-Laguë (standard ose 'modified').
    - votes: {emri_i_partise: vota}
    - total_seats: numri total i ulëseve
    - threshold_pct: prag elektoral në % (p.sh. 5.0 për 5%)
    - first_divisor: ndarësi i parë (1.0 standard; 1.4 modified)

    Kthen: {parti: ulëse}
    """
    if total_seats <= 0:
        return {}

    total_votes = sum(max(0, v) for v in votes.values())
    if total_votes <= 0:
        return {}

    thr = max(0.0, float(threshold_pct)) / 100.0
    filtered = {p: int(v) for p, v in votes.items() if total_votes and (v / total_votes) >= thr}

    if not filtered:
        return {}

    # Ndarësit: first_divisor, pastaj shto 2 (1,3,5,...) → 1, 3, 5, ...
    def divisor_at(idx: int) -> float:
        return first_divisor + idx * 2.0

    # Gjenero kuota — mjafton deri në total_seats për parti
    quotients: List[Tuple[float, str]] = []
    for party, v in filtered.items():
        for i in range(total_seats):
            d = divisor_at(i)
            quotients.append((v / d, party))

    # Renditje: vlera zbritëse; në barazi → parti me më shumë vota; pastaj emër alfabetik
    quotients.sort(
        key=lambda x: (x[0], filtered[x[1]], -ord(x[1][0]) if x[1] else 0),
        reverse=True,
    )

    top = quotients[:total_seats]
    seats = {p: 0 for p in filtered}
    for _, party in top:
        seats[party] += 1
    return seats
