import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Magic Collection & Deck Matcher", layout="wide", page_icon="🃏")
st.title("🃏 Magic Collection & Deck Matcher mit Moxfield")

collection_file = st.file_uploader("Deine Kartensammlung hochladen (CSV mit 'Name' Spalte)", type=["csv"])

MOXFIELD_DECKS_URL = "https://www.moxfield.com/decks"

@st.cache_data(ttl=3600)
def get_deck_links():
    r = requests.get(MOXFIELD_DECKS_URL)
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    deck_links = []
    # Die Deck-Links auf der Moxfield Seite finden (kann sich ändern!)
    for a in soup.select("a.deck-link")[:5]:
        name = a.get("title", "Unbekannt")
        href = a.get("href")
        if href:
            deck_links.append((name, "https://www.moxfield.com" + href))
    return deck_links

@st.cache_data(ttl=3600)
def get_deck_cards(deck_url):
    r = requests.get(deck_url)
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    cards = []
    for card in soup.select(".deck-card-name"):
        cards.append(card.text.strip())
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
        st.markdown("## Top 5 Decks von Moxfield")

        decks = get_deck_links()
        if not decks:
            st.error("Konnte keine Decks von Moxfield laden. Versuche es später nochmal.")
        else:
            for deck_name, deck_url in decks:
                cards = get_deck_cards(deck_url)
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
