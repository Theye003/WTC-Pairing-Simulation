import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import itertools

# ------------------ Hilfsfunktionen ------------------

def simulate_wtc_pairings(matrix):
    results = []
    our_armies = list(matrix.index)
    their_armies = list(matrix.columns)

    for our_defender in our_armies:
        for their_defender in their_armies:
            our_rest = [a for a in our_armies if a != our_defender]
            their_rest = [e for e in their_armies if e != their_defender]

            our_offers = list(itertools.combinations(our_rest, 2))
            their_offers = list(itertools.combinations(their_rest, 2))

            for our_pair in our_offers:
                for their_pair in their_offers:
                    for our_choice in our_pair:
                        for their_choice in their_pair:
                            pairs = [
                                (our_defender, their_choice),
                                (their_defender, our_choice)
                            ]
                            o_used = {our_defender, our_choice}
                            t_used = {their_defender, their_choice}
                            our_left = [a for a in our_rest if a not in o_used]
                            their_left = [e for e in their_rest if e not in t_used]

                            for perm in itertools.permutations(their_left):
                                rest_pairs = list(zip(our_left, perm))
                                full_pairing = pairs + rest_pairs
                                try:
                                    score = sum(matrix.loc[o, t] for o, t in full_pairing)
                                except KeyError:
                                    continue
                                results.append((full_pairing, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results

# ------------------ Streamlit App ------------------

st.set_page_config(page_title="WTC Pairing Simulator", layout="wide")
st.title("✅ WTC Pairing Simulator – Testmatrix Version")

st.markdown("""
Diese Version verwendet eine fest eingebettete 3x3 Matrix.  
Keine Eingabe nötig. Du musst nur auf **"Simulation starten"** klicken.
""")

# Feste, funktionierende Testmatrix
matrix = pd.DataFrame(
    {
        "Enemy1": [12, 10, 15],
        "Enemy2": [9, 12, 13],
        "Enemy3": [13, 14, 11]
    },
    index=["Army1", "Army2", "Army3"]
)

st.subheader("📊 Eingesetzte Matrix:")
st.dataframe(matrix)

top_n = st.slider("Wie viele Top-Pairings anzeigen?", 1, 20, 5)

if st.button("🚀 Simulation starten"):
    with st.spinner("Berechne alle legitimen WTC-Pairings..."):
        results = simulate_wtc_pairings(matrix)

    if not results:
        st.error("❌ Keine gültigen Pairings gefunden. Matrix möglicherweise fehlerhaft.")
    else:
        st.success(f"✅ {len(results)} mögliche Pairings simuliert.")

        top = results[:top_n]
        st.subheader(f"🏅 Top {top_n} Pairings")

        for i, (pairing, score) in enumerate(top, start=1):
            st.markdown(f"### 🧩 Pairing #{i} – Gesamtpunktzahl: `{score:.1f}`")
            for o, t in pairing:
                st.markdown(f"- **{o}** vs **{t}** → `{matrix.loc[o, t]:.1f}`")

        st.subheader("📈 Balkendiagramm der Top Pairings")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 6))
        labels = [" | ".join([f"{o} vs {t}" for o, t in p]) for p, _ in top]
        scores = [s for _, s in top]
        ax.barh(range(len(scores)), scores, tick_label=labels)
        ax.set_xlabel("Gesamtpunktzahl")
        ax.set_ylabel("Pairing")
        ax.set_title("Top-Pairings nach Score")
        ax.invert_yaxis()
        st.pyplot(fig)
