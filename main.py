import streamlit as st
import pandas as pd
import requests
import re

st.title("🧙‍♂️ Magic: The Gathering – Moxfield Deck Checker")

# Funktion: Extrahiere Moxfield-Deck-ID aus URL
def extract_deck_id(url):
    match = re.search(r"/decks/([\w\-]+)", url)
    return match.group(1) if match else None

# Funktion: Lade ein Deck von Moxfield
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

# Funktion: Vergleiche Deck mit Sammlung
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

# Benutzer lädt Sammlung hoch
collection_file = st.file_uploader("📤 Lade deine Kartensammlung hoch (CSV mit Spalte 'Name')", type=["csv"])

# Benutzer gibt Deck-URL ein
deck_url = st.text_input("🔗 Gib die URL eines öffentlichen Moxfield-Decks ein:")

if collection_file and deck_url:
    df = pd.read_csv(collection_file)
    if "Name" not in df.columns:
        st.error("Die CSV-Datei benötigt eine Spalte 'Name'.")
    else:
        user_cards = df["Name"].dropna().str.strip().tolist()
        st.subheader("🃏 Deine Sammlung:")
        st.dataframe(df)

        # Deck-ID extrahieren
        deck_id = extract_deck_id(deck_url)
        if not deck_id:
            st.error("❌ Konnte die Deck-ID aus der URL nicht extrahieren.")
        else:
            st.markdown("---")
            st.subheader("📚 Deckprüfung")

            deck_cards = load_moxfield_deck(deck_id)
            if not deck_cards:
                st.error("❌ Konnte das Deck von Moxfield nicht laden. Stelle sicher, dass es öffentlich ist.")
            else:
                coverage, missing_cards = compare_deck(deck_cards, user_cards)

                if coverage == 100:
                    st.success("✅ Du kannst dieses Deck **vollständig** bauen!")
                elif coverage >= 75:
                    st.info(f"🟡 Du kannst {coverage}% des Decks bauen.")
                    st.write("Fehlende Karten:")
                    for card, count in missing_cards.items():
                        st.write(f"- {card} x{count}")
                else:
                    st.warning(f"🔴 Nur {coverage}% der Karten vorhanden – das reicht nicht.")
                    st.write("Einige fehlende Karten:")
                    for card, count in list(missing_cards.items())[:10]:
                        st.write(f"- {card} x{count}")
else:
    st.info("👉 Bitte lade deine Sammlung hoch **und** gib eine Moxfield-Deck-URL ein.")
