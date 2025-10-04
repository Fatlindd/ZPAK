# d_hondt_calculator.py
from __future__ import annotations

from typing import Dict, List, Tuple


def allocate_dhondt(
    votes: Dict[str, int],
    total_seats: int,
    threshold_pct: float = 0.0,
) -> Dict[str, int]:
    """
    Ndarja e ulëseve me metodën D'Hondt.
    - votes: {emri_i_partise: vota}
    - total_seats: numri total i ulëseve
    - threshold_pct: prag elektoral në % (p.sh. 5.0 për 5%)

    Kthen: {parti: ulëse}
    """
    if total_seats <= 0:
        return {}

    # Filtrim me prag
    total_votes = sum(max(0, v) for v in votes.values())
    if total_votes <= 0:
        return {}

    thr = max(0.0, float(threshold_pct)) / 100.0
    filtered = {p: int(v) for p, v in votes.items() if total_votes and (v / total_votes) >= thr}

    if not filtered:
        return {}

    # Gjenero kuota D'Hondt: V / k, k = 1..total_seats
    # Do të mbledhim të gjitha kuotat e mundshme dhe do të marrim top-N (N=total_seats)
    quotients: List[Tuple[float, str]] = []
    for party, v in filtered.items():
        for k in range(1, total_seats + 1):
            quotients.append((v / k, party))

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
