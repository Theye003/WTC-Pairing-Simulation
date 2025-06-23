import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import itertools

# --------- Hilfsfunktionen ---------

def parse_cell(value):
    if isinstance(value, str) and "-" in value:
        try:
            low, high = map(float, value.strip().split("-"))
            return (low + high) / 2
        except:
            return float('nan')
    try:
        return float(value)
    except:
        return float('nan')

def parse_matrix(raw_df):
    return raw_df.applymap(parse_cell)

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

# --------- Streamlit App ---------

st.set_page_config(page_title="WTC Pairing Simulator", layout="wide")
st.title("🔮 WTC Pairing Simulator")

st.markdown("""
Wähle die Teamgröße und gib die Matchup-Matrix ein (als Werte oder Spannweiten wie `9-12`).  
Spaltennamen (Enemy1 …) und Zeilennamen (Army1 …) dürfen nicht geändert werden.
""")

# Teamgröße
team_size = st.radio("Teamgröße auswählen:", [3, 5, 8], horizontal=True)
army_names = [f"Army{i+1}" for i in range(team_size)]
enemy_names = [f"Enemy{i+1}" for i in range(team_size)]

# Datei-Upload oder manueller Editor
uploaded_file = st.file_uploader("📤 CSV-Datei hochladen (optional)", type="csv")

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file, index_col=0)
    matrix = parse_matrix(raw_df)
    st.subheader("📊 Matrix aus Datei:")
    st.dataframe(raw_df)
else:
    st.subheader("📝 Matrix-Eingabe (manuell)")
    default_matrix = pd.DataFrame(
        [["" for _ in range(team_size)] for _ in range(team_size)],
        index=army_names,
        columns=enemy_names
    )
    edited_matrix = st.data_editor(default_matrix, use_container_width=True)
    matrix = parse_matrix(edited_matrix)

    # Validierung
    if not all(name in matrix.index for name in army_names) or not all(name in matrix.columns for name in enemy_names):
        st.error("❌ Fehler: Bitte verwende die automatischen Namen für Zeilen (Army1…) und Spalten (Enemy1…).")
        st.stop()

# Matrix-Visualisierung
st.subheader("🎨 Erwartungswert-Matrix mit Farbcodierung")
styled = matrix.style.background_gradient(axis=None, cmap="RdYlGn", low=0.2, high=0.8)
st.dataframe(styled, use_container_width=True)

top_n = st.slider("Wie viele Top-Pairings anzeigen?", 1, 50, min(10, team_size * 5))

# Simulation
if st.button("🚀 Simulation starten"):
    with st.spinner("Berechne alle legitimen WTC-Pairings..."):
        results = simulate_wtc_pairings(matrix)

    if not results:
        st.error("⚠️ Keine gültigen Pairings gefunden. Bitte überprüfe die Matrix.")
    else:
        st.success(f"{len(results)} mögliche Pairings simuliert.")

        top = results[:top_n]
        st.subheader(f"🏅 Top {top_n} Pairings")

        for i, (pairing, score) in enumerate(top, start=1):
            st.markdown(f"### 🧩 Pairing #{i} – Gesamtpunktzahl: `{score:.1f}`")
            for o, t in pairing:
                st.markdown(f"- **{o}** vs **{t}** → `{matrix.loc[o, t]:.1f}`")

        st.subheader("📈 Balkendiagramm der Top Pairings")
        fig, ax = plt.subplots(figsize=(12, 6))
        labels = [" | ".join([f"{o} vs {t}" for o, t in p]) for p, _ in top]
        scores = [s for _, s in top]
        ax.barh(range(len(scores)), scores, tick_label=labels)
        ax.set_xlabel("Gesamtpunktzahl")
        ax.set_ylabel("Pairing")
        ax.set_title("Top-Pairings nach Score")
        ax.invert_yaxis()
        st.pyplot(fig)
