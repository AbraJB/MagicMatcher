import streamlit as st
import pandas as pd
import requests

st.title("🧙‍♂️ Magic: The Gathering – Deck Checker mit Moxfield")

# Beispiel-Moxfield-Decks (Name → Deck-ID)
moxfield_decks = {
    "Yuriko Ninjas (EDH)": "WR0WxU44U0OgLAsyOKFw",
    "Chulane Value (EDH)": "kBh9kF5DHEKwOlvVXkOY",
    "Talion Faerie Combo": "N5gy9Sn4Z0mgc1DchYkg"
}

# Funktion: Lade ein Deck von Moxfield über die API
def load_moxfield_deck(deck_id):
    url = f"https://api.moxfield.com/v2/decks/{deck_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    card_dict = data["mainboard"]
    cards = []
    for card_name, info in card_dict.items():
        quantity = info.get("quantity", 1)
        cards.extend([card_name] * quantity)
    return cards

# Funktion: Vergleiche Sammlung mit Deck
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

# Datei-Upload
collection_file = st.file_uploader("📤 Lade deine Kartensammlung hoch (CSV mit Spalte 'Name')", type=["csv"])

if collection_file:
    df = pd.read_csv(collection_file)
    if "Name" not in df.columns:
        st.error("Fehlende Spalte 'Name' in der CSV.")
    else:
        user_cards = df["Name"].dropna().str.strip().tolist()
        st.subheader("🃏 Deine Sammlung:")
        st.dataframe(df)

        st.subheader("📚 Abgleich mit Moxfield-Decks")

        full_decks = []
        partial_decks = []

        for deck_name, deck_id in moxfield_decks.items():
            st.markdown(f"#### 🔍 Prüfe Deck: *{deck_name}*")
            deck_cards = load_moxfield_deck(deck_id)
            if not deck_cards:
                st.warning(f"❌ Konnte Deck **{deck_name}** nicht laden.")
                continue

            coverage, missing_cards = compare_deck(deck_cards, user_cards)

            if coverage == 100:
                full_decks.append(deck_name)
                st.success(f"✅ Du kannst das Deck **{deck_name}** vollständig bauen!")
            elif coverage >= 75:
                partial_decks.append(deck_name)
                st.info(f"🟡 Du besitzt {coverage}% des Decks **{deck_name}**.")
                st.write("Fehlende Karten:")
                for card, count in missing_cards.items():
                    st.write(f"- {card} x{count}")
            else:
                st.write(f"🔴 Du besitzt nur {coverage}% des Decks **{deck_name}**.")
                st.write("Fehlende Karten:")
                for card, count in list(missing_cards.items())[:5]:  # Zeige max. 5 an
                    st.write(f"- {card} x{count}")
                st.caption("...mehr fehlen.")

        st.markdown("---")
        st.subheader("📈 Zusammenfassung:")
        st.write(f"✅ Vollständige Decks baubar: {len(full_decks)}")
        st.write(f"🟡 Teilweise baubare Decks (≥75%): {len(partial_decks)}")
else:
    st.info("Bitte lade eine CSV-Datei mit deiner Sammlung hoch. Beispiel:")
    st.code("Name\nLightning Bolt\nIsland\nSnapcaster Mage", language="csv")
