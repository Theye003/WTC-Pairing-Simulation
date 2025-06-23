import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import itertools

# ------------------ Neue WTC Simulation für Teamgröße 5 ------------------

def simulate_wtc_pairings_team5(matrix):
    results = []
    our_armies = list(matrix.index)
    their_armies = list(matrix.columns)

    for our_defender in our_armies:
        for their_defender in their_armies:
            our_rest = [a for a in our_armies if a != our_defender]
            their_rest = [e for e in their_armies if e != their_defender]

            our_offer_pairs = list(itertools.combinations(our_rest, 2))
            their_offer_pairs = list(itertools.combinations(their_rest, 2))

            for our_offer in our_offer_pairs:
                for their_offer in their_offer_pairs:
                    for their_chosen in their_offer:
                        for our_chosen in our_offer:
                            pairs = [
                                (our_defender, their_chosen),
                                (our_chosen, their_defender)
                            ]

                            used_our = {our_defender, our_chosen}
                            used_their = {their_defender, their_chosen}

                            our_remaining = [o for o in our_armies if o not in used_our]
                            their_remaining = [t for t in their_armies if t not in used_their]

                            if len(our_remaining) != 3 or len(their_remaining) != 3:
                                continue

                            for perm in itertools.permutations(their_remaining):
                                rest_pairs = list(zip(our_remaining, perm))
                                full_pairing = pairs + rest_pairs
                                try:
                                    score = sum(matrix.loc[o, t] for o, t in full_pairing)
                                    results.append((full_pairing, score))
                                except KeyError:
                                    continue

    results.sort(key=lambda x: x[1], reverse=True)
    return results

# ------------------ Streamlit App ------------------

st.set_page_config(page_title="WTC Pairing Simulator", layout="wide")
st.title("✅ WTC Pairing Simulator – Teamgröße 5 (fest)")

st.markdown("""
Diese Version simuliert alle möglichen Pairings für zwei 5er-Teams im WTC-System.  
Matrix und Teamgröße sind fest eingebaut – einfach auf „Simulation starten“ klicken!
""")

# Feste Matrix (gültig)
matrix = pd.DataFrame(
    {
        "Enemy1": [12, 10, 15, 13, 9],
        "Enemy2": [9, 12, 13, 11, 10],
        "Enemy3": [13, 14, 11, 12, 13],
        "Enemy4": [11, 13, 12, 14, 10],
        "Enemy5": [10, 11, 13, 9, 12]
    },
    index=["Army1", "Army2", "Army3", "Army4", "Army5"]
)

st.subheader("📊 Eingesetzte Matrix (Erwartungswerte):")
st.dataframe(matrix.style.background_gradient(axis=None, cmap="RdYlGn", low=0.2, high=0.8))

top_n = st.slider("Wie viele Top-Pairings anzeigen?", 1, 50, 10)

if st.button("🚀 Simulation starten"):
    with st.spinner("Berechne alle legitimen Pairings nach WTC-System..."):
        results = simulate_wtc_pairings_team5(matrix)

    if not results:
        st.error("❌ Keine gültigen Pairings gefunden.")
    else:
        st.success(f"✅ {len(results)} gültige Pairings gefunden.")

        top = results[:top_n]
        st.subheader(f"🏅 Top {top_n} Pairings")

        for i, (pairing, score) in enumerate(top, start=1):
            st.markdown(f"### 🧩 Pairing #{i} – Gesamtpunktzahl: `{score:.1f}`")
            for o, t in pairing:
                st.markdown(f"- **{o}** vs **{t}** → `{matrix.loc[o, t]:.1f}`")

        st.subheader("📈 Balkendiagramm der Top Pairings")
        labels = [" | ".join([f"{o} vs {t}" for o, t in p]) for p, _ in top]
        scores = [s for _, s in top]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(range(len(scores)), scores, tick_label=labels)
        ax.set_xlabel("Gesamtpunktzahl")
        ax.set_ylabel("Pairing")
        ax.set_title("Top-Pairings nach Score")
        ax.invert_yaxis()
        st.pyplot(fig)
