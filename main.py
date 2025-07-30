import streamlit as st
import pandas as pd
import requests

st.title("Magic Collection Checker with Scryfall & Deck Builder")

# Beispiel-Deck-Datenbank (Deckname -> Liste von Karten)
deck_database = {
    "Aggro Deck": ["Lightning Bolt", "Goblin Guide", "Mountain", "Monastery Swiftspear"],
    "Control Deck": ["Counterspell", "Island", "Snapcaster Mage", "Serum Visions"],
    "Midrange Deck": ["Tarmogoyf", "Thoughtseize", "Forest", "Llanowar Elves"]
}

def can_build_deck(collection_cards, deck_cards):
    # Prüft, ob alle Karten im Deck in der Sammlung sind
    return all(card in collection_cards for card in deck_cards)

collection_file = st.file_uploader("Upload your card collection CSV (with 'Name' column)", type=["csv"])

if collection_file:
    df = pd.read_csv(collection_file)
    if 'Name' not in df.columns:
        st.error("Die CSV-Datei benötigt eine Spalte 'Name' mit Kartennamen.")
    else:
        st.write("Uploaded collection:")
        st.dataframe(df)

        card_names = df['Name'].dropna().str.strip().unique()
        collection_cards = set(card_names)

        st.header("Check cards against Scryfall")

        results = []
        for card_name in card_names:
            url = f"https://api.scryfall.com/cards/named?exact={card_name}"
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                results.append({
                    "Name": card_name,
                    "Scryfall ID": data.get("id"),
                    "Set": data.get("set_name"),
                    "Type": data.get("type_line"),
                    "Rarity": data.get("rarity"),
                    "Image": data["image_uris"]["normal"] if "image_uris" in data else "N/A"
                })
            else:
                results.append({
                    "Name": card_name,
                    "Scryfall ID": None,
                    "Set": None,
                    "Type": None,
                    "Rarity": None,
                    "Image": "N/A"
                })

        res_df = pd.DataFrame(results)
        st.write("Scryfall lookup results:")
        st.dataframe(res_df)

        st.header("Card Images")

        cols = st.columns(4)  # 4 Spalten für die Bilder
        i = 0

        for _, row in res_df.iterrows():
            if row["Image"] != "N/A":
                with cols[i % 4]:
                    st.image(row["Image"], width=150, caption=f"{row['Name']} ({row['Set']})")
                i += 1

        st.header("Passende Decks basierend auf deiner Sammlung")

        matching_decks = []
        for deck_name, deck_cards in deck_database.items():
            if can_build_deck(collection_cards, deck_cards):
                matching_decks.append(deck_name)

        if matching_decks:
            for deck in matching_decks:
                st.success(f"Du kannst das Deck bauen: **{deck}**")
                st.write("Karten in diesem Deck:")
                st.write(deck_database[deck])
        else:
            st.warning("Kein Deck passt komplett zu deiner Sammlung. Versuche weitere Karten hinzuzufügen.")

else:
    st.info("Bitte lade eine CSV-Datei mit einer 'Name'-Spalte hoch.")
