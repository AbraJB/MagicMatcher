import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Magic Collection & Deck Matcher", layout="wide")
st.title("🃏 Magic Collection & Deck Matcher mit MTGJSON")

# Upload der Kartensammlung
collection_file = st.file_uploader("Upload your card collection CSV (mit 'Name' Spalte)", type=["csv"])

DECKS_URL = "https://mtgjson.com/api/v5/AllDecks.json"

@st.cache_data(ttl=3600)
def get_decks():
    r = requests.get(DECKS_URL)
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get("data", {}).get("decks", [])

if collection_file:
    df = pd.read_csv(collection_file)
    if "Name" not in df.columns:
        st.error("Die CSV-Datei braucht eine Spalte namens 'Name'.")
    else:
        user_cards = set(df['Name'].dropna().str.strip())
        st.markdown("### Deine Sammlung")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("## Decks aus MTGJSON (Top 5)")

        decks = get_decks()
        if not decks:
            st.error("Konnte Deckdaten nicht laden.")
        else:
            for deck in decks[:5]:
                deck_name = deck.get("name", "Unbekannt")
                cards = [c.get("name") for c in deck.get("cards", [])]
                have = len(set(cards) & user_cards)
                total = len(cards)
                percent = round(have / total * 100, 1) if total else 0

                with st.expander(f"**{deck_name}** – {have}/{total} Karten vorhanden ({percent}%)"):
                    st.write("### Karten im Deck:")
                    cols = st.columns(4)
                    for i, card in enumerate(cards):
                        col = cols[i % 4]
                        if card in user_cards:
                            col.markdown(f"✅ **{card}**")
                        else:
                            col.markdown(f"❌ {card}")

else:
    st.info("Bitte lade eine CSV-Datei mit einer 'Name' Spalte hoch, um deine Sammlung zu analysieren.")
