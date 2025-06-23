import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import numpy as np

# ------------------ WTC Simulation für 5 Spieler ------------------

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
st.title("🎯 WTC Pairing Simulator – Teamgröße 5 mit Namen")

st.markdown("""
Gib deine 5 Armeenamen und die 5 gegnerischen Armeen ein.  
Fülle dann die Matrix manuell oder lasse Testwerte automatisch generieren.
""")

# Eingabe der Namen
st.subheader("🔤 Namen eingeben")

col1, col2 = st.columns(2)
with col1:
    our_names = [st.text_input(f"Unsere Armee {i+1}", f"Army{i+1}") for i in range(5)]
with col2:
    their_names = [st.text_input(f"Gegner {i+1}", f"Enemy{i+1}") for i in range(5)]

# Matrix bearbeiten
st.subheader("📊 Erwartungswert-Matrix")

use_random = st.checkbox("✅ Testwerte automatisch füllen")

if use_random:
    np.random.seed(42)
    matrix = pd.DataFrame(
        np.random.randint(4, 16, size=(5, 5)),
        index=our_names,
        columns=their_names
    )
    st.success("Zufallsmatrix generiert")
else:
    empty_matrix = pd.DataFrame(
        [["" for _ in range(5)] for _ in range(5)],
        index=our_names,
        columns=their_names
    )
    matrix = st.data_editor(empty_matrix, use_container_width=True)
    try:
        matrix = matrix.applymap(lambda x: float(x) if x != "" else None)
    except:
        st.error("Fehler beim Parsen der Matrix – bitte nur Zahlen eingeben.")
        st.stop()

# Matrix anzeigen
st.dataframe(matrix.style.background_gradient(axis=None, cmap="RdYlGn", low=0.2, high=0.8))

# Check auf Lücken
if matrix.isnull().values.any():
    st.warning("❗ Bitte alle Felder in der Matrix ausfüllen.")
    st.stop()

# Simulation starten
top_n = st.slider("Wie viele einzigartige Top-Pairings anzeigen?", 1, 50, 10)

if st.button("🚀 Simulation starten"):
    with st.spinner("Berechne alle legitimen Pairings..."):
        results = simulate_wtc_pairings_team5(matrix)

    if not results:
        st.error("❌ Keine gültigen Pairings gefunden.")
    else:
        # Nur inhaltlich unterschiedliche Pairings durch Set
        seen = set()
        unique_results = []

        for pairing, score in results:
            key = tuple(sorted((o, t) for o, t in pairing))
            if key not in seen:
                seen.add(key)
                unique_results.append((pairing, score))
            if len(unique_results) >= top_n:
                break

        st.success(f"✅ {len(unique_results)} eindeutige Pairings gefunden.")

        st.subheader(f"🏅 Top {len(unique_results)} einzigartige Pairings")

        for i, (pairing, score) in enumerate(unique_results, start=1):
            st.markdown(f"### 🧩 Pairing #{i} – Gesamtpunktzahl: `{score:.1f}`")
            for o, t in pairing:
                st.markdown(f"- **{o}** vs **{t}** → `{matrix.loc[o, t]:.1f}`")

        st.subheader("📈 Balkendiagramm der Top Pairings")
        labels = [" | ".join([f"{o} vs {t}" for o, t in p]) for p, _ in unique_results]
        scores = [s for _, s in unique_results]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(range(len(scores)), scores, tick_label=labels)
        ax.set_xlabel("Gesamtpunktzahl")
        ax.set_ylabel("Pairing")
        ax.set_title("Top-Pairings nach Score")
        ax.invert_yaxis()
        st.pyplot(fig)
