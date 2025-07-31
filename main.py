import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Magic Collection & Deck Matcher", layout="wide", page_icon="🃏")
st.title("🃏 Magic Collection & Deck Matcher mit TappedOut")

collection_file = st.file_uploader("Deine Kartensammlung hochladen (CSV mit 'Name' Spalte)", type=["csv"])

# Beispielhafte TappedOut-Deck URLs (kannst du nach Belieben anpassen)
TAPPEDOUT_DECKS = {
    "Mono Red Aggro": "https://tappedout.net/mtg-decks/mono-red-aggro/",
    "Simic Ramp": "https://tappedout.net/mtg-decks/simic-ramp-2023/",
    "Golgari Midrange": "https://tappedout.net/mtg-decks/golgari-midrange-2023/",
}

@st.cache_data(ttl=3600)
def get_tappedout_deck_cards(deck_url):
    r = requests.get(deck_url)
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    cards = []

    # Karten im TappedOut-Deck sind in <a> Tags mit "deck-view-card-name" Klasse
    for card_tag in soup.select("a.deck-view-card-name"):
        card_name = card_tag.text.strip()
        cards.append(card_name)

    return cards

if collection_file:
    df = pd.read_csv(collection_file)
    if "Name" not in df.columns:
        st.error("Die CSV-Datei benötigt eine Spalte namens 'Name'.")
    else:
        user_cards = set(df['Name'].dropna().str.strip())
        st.markdown("### Deine Sammlung")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("## Beispielhafte Top Decks von TappedOut")

        for deck_name, deck_url in TAPPEDOUT_DECKS.items():
            st.write(f"🔍 Prüfe Deck: **{deck_name}**")
            cards = get_tappedout_deck_cards(deck_url)
            if not cards:
                st.error(f"Konnte Deck {deck_name} nicht laden.")
                continue

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
