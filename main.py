import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Magic Deck Matcher", layout="wide")
st.title("🧙 Magic Deck Matcher")
st.markdown("Vergleiche deine Kartensammlung mit Beispiel-Decks aus Commander & Modern.")

# --- Load or upload card collection ---
st.sidebar.header("1. Kartensammlung hochladen")
collection_file = st.sidebar.file_uploader("CSV mit Spalten: Name,Anzahl", type=["csv"])

if collection_file:
    collection_df = pd.read_csv(collection_file)
else:
    st.sidebar.markdown("*Keine Datei hochgeladen. Beispiel-Sammlung wird verwendet.*")
    collection_df = pd.read_csv("sample_collection.csv")

collection_dict = dict(zip(collection_df['Name'], collection_df['Anzahl']))

# --- Load example decks ---
st.sidebar.header("2. Deckformat wählen")
deck_format = st.sidebar.selectbox("Format", ["Commander", "Modern"])
deck_folder = f"decks/{deck_format.lower()}"
deck_files = [f for f in os.listdir(deck_folder) if f.endswith(".json")]

def load_deck(path):
    with open(path, "r") as f:
        return json.load(f)

deck_data = [(f[:-5], load_deck(os.path.join(deck_folder, f))) for f in deck_files]

# --- Matching logic ---
st.header("🔍 Ergebnisse")
results = []

for deck_name, cards in deck_data:
    total = len(cards)
    owned = sum(1 for card in cards if collection_dict.get(card, 0) > 0)
    missing = [card for card in cards if collection_dict.get(card, 0) == 0]
    percent = round((owned / total) * 100, 1)
    results.append({
        "Deck": deck_name,
        "Übereinstimmung": percent,
        "Fehlende Karten": missing
    })

results = sorted(results, key=lambda x: -x["Übereinstimmung"])

for res in results:
    with st.expander(f"{res['Deck']} – {res['Übereinstimmung']}% passend"):
        if res["Fehlende Karten"]:
            st.write("**Fehlende Karten:**")
            st.write(", ".join(res["Fehlende Karten"]))
        else:
            st.success("✅ Du kannst dieses Deck vollständig bauen!")
