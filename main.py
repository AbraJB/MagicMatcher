import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Magic Deck Matcher (Moxfield Scraper)", layout="wide")
st.title("🧙 Magic Deck Matcher")
st.markdown("Compare your card collection with decks from [Moxfield](https://www.moxfield.com).")

# --- Load or upload card collection ---
st.sidebar.header("1. Upload your card collection")
collection_file = st.sidebar.file_uploader("CSV with a column: Name", type=["csv"])
collection_set = set()

if collection_file:
    collection_df = pd.read_csv(collection_file)
    st.write("Uploaded collection preview:")
    st.write(collection_df.head())
    collection_set = set(collection_df['Name'].dropna().str.strip())
else:
    use_sample = st.sidebar.checkbox("Use sample collection instead (if no file uploaded)")
    if use_sample:
        sample_cards = [
            "Lightning Bolt", "Boros Charm", "Goblin Guide", "Serra Angel",
            "Rift Bolt", "Skewer the Critics", "Lava Spike", "Monastery Swiftspear"
        ]
        collection_set = set(sample_cards)
        st.write("Using sample collection:")
        st.write(sample_cards)

# --- Moxfield deck input ---
st.sidebar.header("2. Enter Moxfield Deck URLs")
deck_urls_input = st.sidebar.text_area("One URL per line", height=150)

def extract_deck_id(url):
    if "/decks/" in url:
        return url.split("/decks/")[-1].split("/")[0]
    return None

def load_moxfield_deck(deck_id):
    url = f"https://www.moxfield.com/decks/{deck_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        mainboard_section = soup.select_one(".deck-mainboard")
        if not mainboard_section:
            st.error("Could not find mainboard section on Moxfield page.")
            return []
        card_elements = mainboard_section.select(".card-name")
        cards = [card_elem.get_text(strip=True) for card_elem in card_elements]
        return cards
    except Exception as e:
        st.error(f"Failed to load deck {deck_id} by scraping: {e}")
        return []

# --- Matching logic ---
st.header("🔍 Match Results")
if collection_set and deck_urls_input.strip():
    urls = [u.strip() for u in deck_urls_input.strip().splitlines()]
    for url in urls:
        deck_id = extract_deck_id(url)
        if not deck_id:
            st.error(f"❌ Invalid Moxfield URL: {url}")
            continue

        card_list = load_moxfield_deck(deck_id)
        if not card_list:
            st.error(f"❌ Could not load deck from: {url}")
            continue

        total = len(card_list)
        owned = sum(1 for card in card_list if card in collection_set)
        missing = [card for card in card_list if card not in collection_set]
        percent = round((owned / total) * 100, 1)

        with st.expander(f"🔹 {deck_id} – {percent}% match"):
            st.write(f"**Owned:** {owned} / {total} cards")
            if missing:
                st.warning("Missing Cards:")
                st.write(", ".join(missing))
            else:
                st.success("✅ You can build this deck completely!")
elif not collection_set:
    st.info("Please upload your collection or use the sample collection.")
elif not deck_urls_input.strip():
    st.info("Please enter at least one Moxfield deck URL to begin.")
