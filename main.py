import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Magic Deck Matcher", layout="wide")
st.title("🧙 Magic Deck Matcher")
st.markdown("Compare your card collection with sample decks from Commander & Modern.")

# --- Load or upload card collection ---
st.sidebar.header("1. Upload your card collection")
collection_file = st.sidebar.file_uploader("CSV with columns: Name,Quantity", type=["csv"])

if collection_file:
    collection_df = pd.read_csv(collection_file)
else:
    st.sidebar.markdown("*No file uploaded. Using sample collection.*")
    collection_df = pd.read_csv("sample_collection.csv")

collection_dict = dict(zip(collection_df['Name'], collection_df['Quantity']))

# --- Load example decks ---
st.sidebar.header("2. Choose deck format")
deck_format = st.sidebar.selectbox("Format", ["Commander", "Modern"])
deck_folder = f"decks/{deck_format.lower()}"
deck_files = [f for f in os.listdir(deck_folder) if f.endswith(".json")]

def load_deck(path):
    with open(path, "r") as f:
        return json.load(f)

deck_data = [(f[:-5], load_deck(os.path.join(deck_folder, f))) for f in deck_files]

# --- Matching logic ---
st.header("🔍 Results")
results = []

for deck_name, cards in deck_data:
    total = len(cards)
    owned = sum(1 for card in cards if collection_dict.get(card, 0) > 0)
    missing = [card for card in cards if collection_dict.get(card, 0) == 0]
    percent = round((owned / total) * 100, 1)
    results.append({
        "Deck": deck_name,
        "Match Percentage": percent,
        "Missing Cards": missing
    })

results = sorted(results, key=lambda x: -x["Match Percentage"])

for res in results:
    with st.expander(f"{res['Deck']} – {res['Match Percentage']}% match"):
        if res["Missing Cards"]:
            st.write("**Missing Cards:**")
            st.write(", ".join(res["Missing Cards"]))
        else:
            st.success("✅ You can build this deck completely!")
