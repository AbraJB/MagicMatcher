import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Moxfield Deck Checker", layout="wide")
st.title("🧙‍♂️ Magic: The Gathering – Moxfield Deck Checker")

# 🔗 Vordefinierte öffentliche Moxfield-Decks
moxfield_decks = {
    "Atraxa Infect (EDH)": "8lTuB-BqH0O6mb7jj1aCeQ",
    "Mono Red Burn": "jFahKLROUEC9z14tRc7K7g",
    "Yuriko Ninjas": "WR0WxU44U0OgLAsyOKFw",
    "Chulane Value": "kBh9kF5DHEKwOlvVXkOY",
    "Golgari Elfball": "1bmDZHeXYU-tYO8MLYOFTA",
}

# 📥 Deck laden von Moxfield
def load_moxfield_deck(deck_id):
    url = f"https://api.moxfield.com/v2/decks/{deck_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    card_dict = data.get("mainboard", {})
    cards = []
    for card_name, info in card_dict.items():
        quantity = info.get("quantity", 1)
        cards.extend([card_name] * quantity)
    return cards

# 🔍 Vergleich Sammlung vs Deck
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

# 📤 Sammlung hochladen
collection_file = st.file_uploader("📁 Lade deine Kartensammlung hoch (CSV mit Spalte 'Name')", type=["csv"])

if collection_file:
    df = pd.read_csv(collection_file)
    if "Name" not in df.columns:
        st.error("❌ Deine CSV-Datei benötigt eine Spalte namens `Name`.")
    else:
        user_cards = df["Name"].dropna().str.strip().tolist()

        st.subheader("📚 Deine Sammlung")
        st.dataframe(df, height=250)

        st.markdown("---")
        st.subheader("📊 Deck-Abgleich mit Moxfield")

        full_matches = []
        partial_matches = []

        for deck_name, deck_id in moxfield_decks.items():
            with st.spinner(f"🔍 Prüfe Deck: {deck_name}"):
                deck_cards = load_moxfield_deck(deck_id)
                if not deck_cards:
                    st.warning(f"❌ Konnte Deck **{deck_name}** nicht laden.")
                    continue

                coverage, missing_cards = compare_deck(deck_cards, user_cards)

                with st.expander(f"📘 {deck_name} – {coverage}% Karten vorhanden"):
                    if coverage == 100:
                        st.success("✅ Du kannst dieses Deck vollständig bauen!")
                        full_matches.append(deck_name)
                    elif coverage >= 75:
                        st.info("🟡 Teilweise baubar.")
                        partial_matches.append(deck_name)
                        st.write("Fehlende Karten:")
                        for card, count in missing_cards.items():
                            st.write(f"- {card} x{count}")
                    else:
                        st.warning("🔴 Weniger als 75 % vorhanden.")
                        st.write("Fehlende Karten (Beispiel):")
                        for card, count in list(missing_cards.items())[:10]:
                            st.write(f"- {card} x{count}")

        # ✅ Zusammenfassung
        st.markdown("---")
        st.subheader("📈 Ergebnis-Übersicht")
        st.success(f"✅ Vollständige Decks: {len(full_matches)}")
        st.info(f"🟡 Teilweise baubare Decks: {len(partial_matches)}")
        st.warning(f"🔴 Andere Decks: {len(moxfield_decks) - len(full_matches) - len(partial_matches)}")

else:
    st.info("⬆️ Bitte lade zuerst deine Sammlung als CSV-Datei hoch (Spalte: `Name`).")
