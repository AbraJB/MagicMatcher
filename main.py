import streamlit as st
import pandas as pd
from pyrchidekt.api import getDeckById

st.set_page_config(page_title="Archidekt Deck Checker", layout="wide")
st.title("📚 Magic: The Gathering – Archidekt Deck Matcher")

# Öffentliche Archidekt-Decks mit realen IDs (Beispiele)
archidekt_decks = {
    "Mono Green Stompy": 423111,
    "Azorius Control": 428776,
    "Rakdos Aggro": 427345,
    "Izzet Spells": 430012,
    "Selesnya Tokens": 421998,
}

def load_archidekt_deck(deck_id):
    try:
        deck = getDeckById(deck_id)
    except Exception:
        return None
    cards = []
    for category in deck.categories:
        for card in category.cards:
            cards.extend([card.card.oracle_card.name] * card.quantity)
    return cards

def compare_deck(deck_cards, collection_cards):
    collection_count = pd.Series(collection_cards).value_counts()
    deck_count = pd.Series(deck_cards).value_counts()
    missing = {}
    have = 0
    total = len(deck_cards)
    for card in deck_count.index:
        needed = deck_count[card]
        owned = collection_count.get(card, 0)
        have += min(needed, owned)
        if owned < needed:
            missing[card] = needed - owned
    coverage = round((have / total) * 100, 1)
    return coverage, missing

collection_file = st.file_uploader("📁 Lade deine Kartensammlung (CSV mit Spalte 'Name')", type=["csv"])

if collection_file:
    df = pd.read_csv(collection_file)
    if "Name" not in df.columns:
        st.error("Die CSV braucht eine Spalte namens `Name`.")
    else:
        user_cards = df["Name"].dropna().str.strip().tolist()
        st.subheader("🃏 Deine Sammlung")
        st.dataframe(df, height=200)

        st.markdown("---")
        st.subheader("🔍 Abgleich mit Archidekt-Decks")

        full_matches = []
        partial_matches = []

        for deck_name, deck_id in archidekt_decks.items():
            with st.spinner(f"Prüfe Deck: {deck_name}"):
                deck_cards = load_archidekt_deck(deck_id)
                if not deck_cards:
                    st.warning(f"Konnte Deck **{deck_name}** (ID {deck_id}) nicht laden.")
                    continue
                coverage, missing_cards = compare_deck(deck_cards, user_cards)
                with st.expander(f"{deck_name} – {coverage}% Karten vorhanden"):
                    if coverage == 100:
                        st.success("✅ Vollständig baubar")
                        full_matches.append(deck_name)
                    elif coverage >= 75:
                        st.info("🟡 Teilweise baubar")
                        partial_matches.append(deck_name)
                        st.write("Fehlende Karten:")
                        for card, count in missing_cards.items():
                            st.write(f"- {card} x{count}")
                    else:
                        st.warning("🔴 Unter 75 %")
                        st.write("Einige fehlende Karten:")
                        for c, cnt in list(missing_cards.items())[:10]:
                            st.write(f"- {c} x{cnt}")

        st.markdown("---")
        st.subheader("📈 Übersicht")
        st.success(f"✅ Vollständig: {len(full_matches)}")
        st.info(f"🟡 Teilweise (≥75 %): {len(partial_matches)}")
        st.warning(f"🔴 Nicht genug: {len(archidekt_decks) - len(full_matches) - len(partial_matches)}")

else:
    st.info("Bitte lade zuerst deine Kartensammlung hoch.")
