# main.py
from __future__ import annotations

import random
from typing import Dict, List

import streamlit as st
from streamlit_option_menu import option_menu

from d_hondt_calculator import allocate_dhondt
from sainte_lague_calculator import allocate_sainte_lague


# ========================
# Page & CSS
# ========================

def setup_page() -> None:
    st.set_page_config(page_title="Ndarja e Ulëseve", page_icon="🗳️", layout="wide")
    # Spacing i lehtë që titulli të mos ngjitet lart
    st.markdown("<div style='margin-top:25px'></div>", unsafe_allow_html=True)
    st.markdown("### 🗳️ Ndarja Proporcionale e Ulëseve")
    st.caption("Zgjidh metodën, fut të dhënat dhe llogarit shpërndarjen e ulëseve.")
    st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)


def inject_css() -> None:
    """Stile për navbar, inpute, karta, spacing dhe NO inner scrolling në rezultatet."""
    st.markdown(
        """
        <style>
        /* -------- Kontejneri kryesor -------- */
        .block-container { 
            padding-top: 1.4rem !important; 
            padding-bottom: 0.8rem !important;
        }

        /* ====== DISABLE inner scrolling on results/columns (desktop & mobile) ====== */
        /* Kjo shmang 'nested scroll' dhe lejon faqen (body) të përdoret për scroll */
        .results-left, .results-right {
          overflow: visible !important;
          max-height: none !important;
          -webkit-overflow-scrolling: auto !important;
        }
        /* Disa kontejnerë të brendshëm të Streamlit-it marrin overflow:auto;
           këto i detyrojmë të jenë visible në seksionin e rezultateve */
        .results-left [data-testid="stVerticalBlock"],
        .results-right [data-testid="stVerticalBlock"],
        .results-left [data-testid="stVerticalBlock"] > div,
        .results-right [data-testid="stVerticalBlock"] > div,
        .results-left [data-testid="column"],
        .results-right [data-testid="column"] {
          overflow: visible !important;
          max-height: none !important;
        }

        @media (max-width: 640px) {
          html, body {
            overflow-x: hidden;
            overflow-y: auto;
          }
        }

        /* -------- Navbar -------- */
        .nav-link.active, .nav-link.active i { color: #FFFFFF !important; }

        /* Desktop defaults: kompakte */
        div[data-testid="stHorizontalBlock"] .nav-link { padding: 6px 12px !important; }
        div[data-testid="stHorizontalBlock"] .nav-link-selected { padding: 8px 16px !important; }
        div[data-testid="stHorizontalBlock"] .nav-link, 
        div[data-testid="stHorizontalBlock"] .nav-link-selected { 
            font-size: 14px !important; 
            margin: 0 4px !important; 
            border-radius: 10px !important;
            line-height: 1.05;
        }
        div[data-testid="stHorizontalBlock"] .icon { font-size: 14px !important; }

        /* Mobile navbar: “pills” me padding të moderuar.
           ↓ Linku i selektuar s’ka padding të tepruar (jo “shumë e kuqe”). */
        @media (max-width: 640px) {
          div[data-testid="stHorizontalBlock"] > div {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            padding: 2px 0;
            margin: 0;
          }
          div[data-testid="stHorizontalBlock"] .nav-link {
            padding: 8px 12px !important;
            margin: 2px 4px !important;
            font-size: 15px !important;
            border-radius: 999px !important;
            white-space: nowrap;
          }
          div[data-testid="stHorizontalBlock"] .nav-link-selected {
            padding: 8px 12px !important;   /* i njëjtë me nav-link */
            margin: 2px 4px !important;
            font-size: 15px !important;
            border-radius: 999px !important;
            white-space: nowrap;
          }
        }

        /* -------- Panel input (etiketa mobile) -------- */
        .desktop-headers { display: block; margin-bottom: 4px; }
        .mobile-label { display: none; font-weight: 600; margin-bottom: 4px; }
        @media (max-width: 640px) {
          .desktop-headers { display: none; }
          .mobile-label { display: block; }
        }

        /* Ul pak spacing-un e elementeve tekstualë default */
        h4, .stMarkdown p { margin-top: 0.2rem; margin-bottom: 0.2rem; }

        /* -------- HR e hollë me margjina minimale -------- */
        .thin-hr {
          border: 0; border-top: 1px solid #e6e8ed;
          margin: 6px 0;
        }

        /* -------- Karta rezultati -------- */
        .result-card {
            border-radius: 14px;
            padding: 14px 16px;
            color: #ffffff;
            display: grid;
            grid-template-columns: 44px 1fr;
            gap: 12px;
            align-items: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }
        .result-card .icon-wrap {
            width: 44px; height: 44px; border-radius: 10px;
            background: rgba(255,255,255,0.18);
            display: flex; align-items: center; justify-content: center;
        }
        .result-card .icon-wrap svg {
            width: 20px; height: 20px; stroke: #ffffff; fill: none; stroke-width: 2;
        }
        .result-card .meta { display: flex; flex-direction: column; line-height: 1.25; }
        .result-card .primary { font-size: 18px; font-weight: 800; padding: 4px 0; }
        .result-card .secondary { opacity: 0.95; font-size: 12px; }

        /* Hapësira të vogla mes rreshtave dhe kartave */
        .row-spacer { height: 6px; }

        /* Mobile tweaks për kartat */
        @media (max-width: 640px) {
          .result-card { padding: 12px 12px; grid-template-columns: 36px 1fr; gap: 10px; }
          .result-card .icon-wrap { width: 36px; height: 36px; border-radius: 9px; }
          .result-card .icon-wrap svg { width: 18px; height: 18px; }
          .result-card .primary { font-size: 16px; padding: 2px 0; }
          .result-card .secondary { font-size: 12px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ========================
# Navbar
# ========================

def navbar_methods() -> str:
    selected = option_menu(
        menu_title=None,
        options=["Metoda D’Hondt", "Metoda Sainte-Laguë"],
        icons=["bar-chart-line", "pie-chart"],
        orientation="horizontal",
        default_index=0,
        styles={
            "container": {
                "padding": "6px 8px",
                "background-color": "#F3F5F9",
                "border-radius": "12px",
            },
            "nav-link": {
                "font-size": "14px",
                "padding": "6px 12px",
                "margin": "0 4px",
                "border-radius": "10px",
                "font-weight": "500",
                "color": "#2B2F36",
            },
            "nav-link-selected": {
                "background-color": "#E8564F",
                "color": "#FFFFFF",
                "padding": "8px 16px",
                "border-radius": "10px",
                "font-weight": "600",
                "box-shadow": "0 2px 4px rgba(0,0,0,0.06)",
            },
        },
    )
    return selected


# ========================
# Session & Inputs
# ========================

def _ensure_state() -> None:
    if "parties" not in st.session_state:
        random.seed(42)
        st.session_state.parties = [
            {"name": f"Partia {chr(65+i)}", "votes": random.randint(500, 10000)}
            for i in range(5)
        ]
    st.session_state.setdefault("party_count", 5)
    st.session_state.setdefault("total_seats", 30)
    st.session_state.setdefault("threshold_pct", 0.0)
    st.session_state.setdefault("seat_results", {})
    st.session_state.setdefault("current_method", "Metoda D’Hondt")


def resize_parties() -> None:
    target = int(st.session_state.get("party_count", 0))
    cur = len(st.session_state.parties)
    if target > cur:
        for i in range(cur, target):
            st.session_state.parties.append({"name": f"Partia {chr(65 + i)}", "votes": 0})
    elif target < cur:
        st.session_state.parties = st.session_state.parties[:target]


def _remove_party(idx: int) -> None:
    if 0 <= idx < len(st.session_state.parties):
        st.session_state.parties.pop(idx)
        st.session_state.party_count = max(0, st.session_state.party_count - 1)


def render_input_expander() -> None:
    with st.expander("⚙️ Parametrat & të dhënat", expanded=True):
        top = st.columns([1.0, 1.0, 1.0])
        with top[0]:
            st.number_input("Numri total i ulëseve", min_value=1, step=1, key="total_seats")
        with top[1]:
            st.number_input("Pragu elektoral (%)", min_value=0.0, max_value=100.0, step=1.0, key="threshold_pct")
        with top[2]:
            st.number_input("Numri i partive", min_value=0, step=1, key="party_count", on_change=resize_parties)

        st.markdown('<hr class="thin-hr">', unsafe_allow_html=True)

        if st.session_state.party_count > 0:
            h1, h2, h3 = st.columns([2.2, 1.0, 0.7])
            with h1:
                st.markdown('<div class="desktop-headers">Emri i partisë</div>', unsafe_allow_html=True)
            with h2:
                st.markdown('<div class="desktop-headers">Vota</div>', unsafe_allow_html=True)
            with h3:
                st.markdown('<div class="desktop-headers">Fshij</div>', unsafe_allow_html=True)

            for i, row in enumerate(st.session_state.parties):
                c1, c2, c3 = st.columns([2.2, 1.0, 0.7])
                with c1:
                    st.markdown('<div class="mobile-label">Emri i partisë</div>', unsafe_allow_html=True)
                    row["name"] = st.text_input("Emri i partisë", value=row.get("name", ""), key=f"name_{i}", label_visibility="collapsed")
                with c2:
                    st.markdown('<div class="mobile-label">Vota</div>', unsafe_allow_html=True)
                    row["votes"] = st.number_input("Vota", min_value=0, step=100, value=int(row.get("votes", 0)), key=f"votes_{i}", label_visibility="collapsed")
                with c3:
                    st.button("Fshij", key=f"del_{i}", type="primary", use_container_width=True, on_click=_remove_party, args=(i,))

        st.markdown('<hr class="thin-hr">', unsafe_allow_html=True)
        if st.button("Calculate", type="primary", use_container_width=True):
            run_calculation(st.session_state.current_method)


# ========================
# Calculation + Results
# ========================

def run_calculation(method_label: str) -> None:
    votes = {p["name"]: int(p["votes"]) for p in st.session_state.parties if p["name"].strip()}
    total = st.session_state.total_seats
    thr = st.session_state.threshold_pct

    if not votes or total <= 0:
        st.session_state.seat_results = {}
        return

    if method_label == "Metoda D’Hondt":
        st.session_state.seat_results = allocate_dhondt(votes=votes, total_seats=total, threshold_pct=thr)
    else:
        st.session_state.seat_results = allocate_sainte_lague(votes=votes, total_seats=total, threshold_pct=thr, first_divisor=1.0)


PALETTE = ["#E8743B", "#19A0AA", "#4C78A8", "#F2C14E", "#6AB04A", "#9B59B6", "#E67E22", "#D35400", "#16A085", "#C0392B"]

def people_svg() -> str:
    return """<svg viewBox='0 0 24 24'><path d='M16 11c1.66 0 3-1.79 3-4s-1.34-4-3-4-3 1.79-3 4 1.34 4 3 4zM8 11c1.66 0 3-1.79 3-4S9.66 3 8 3 5 4.79 5 7s1.34 4 3 4z'/><path d='M8 13c-3.33 0-6 1.34-6 3v2h12v-2c0-1.66-2.67-3-6-3zm8 0c-.29 0-.57.02-.84.05 1.84.73 3.16 1.95 3.16 3.45v2h6v-2c0-1.66-2.67-3-6-3z'/></svg>"""

def render_results_panel() -> None:
    # Shto kontejnerët që çaktivizojnë inner scroll
    left_col, right_col = st.columns([1.2, 1.0])

    # ------ MAJTAS: Rezultatet (karta) ------
    with left_col:
        st.markdown('<div class="results-left">', unsafe_allow_html=True)
        st.markdown("#### Rezultatet")
        st.markdown('<hr class="thin-hr">', unsafe_allow_html=True)

        parties = st.session_state.parties
        seat_map = st.session_state.seat_results

        def _card(name, votes, seats, bg):
            return f"""
            <div class='result-card' style='background:{bg};'>
              <div class='icon-wrap'>{people_svg()}</div>
              <div class='meta'>
                <div class='primary'>{name} | {votes:,} voters</div>
                <div class='secondary'>{seats} seats</div>
              </div>
            </div>
            """

        for i, p in enumerate(parties):
            bg = PALETTE[i % len(PALETTE)]
            st.markdown(_card(p["name"], int(p["votes"]), int(seat_map.get(p["name"], 0)), bg), unsafe_allow_html=True)
            st.markdown("<div class='row-spacer'></div>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ------ DJATHTAS: Grafiku ------
    with right_col:
        st.markdown('<div class="results-right">', unsafe_allow_html=True)
        st.markdown("#### Votat sipas partive")
        st.markdown('<hr class="thin-hr">', unsafe_allow_html=True)

        import pandas as pd
        df = pd.DataFrame(st.session_state.parties)
        if not df.empty:
            df_chart = df.set_index("name")[["votes"]]
            df_chart.columns = ["Vota"]
            st.bar_chart(df_chart, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ========================
# Main
# ========================

def main() -> None:
    setup_page()
    inject_css()
    _ensure_state()
    selection = navbar_methods()
    st.session_state.current_method = selection
    render_input_expander()
    render_results_panel()


if __name__ == "__main__":
    main()
