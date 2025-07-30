import streamlit as st
import pandas as pd
import requests

st.title("Magic Collection Checker with Scryfall")

# Upload CSV
collection_file = st.file_uploader("Upload your card collection CSV (with 'Name' column)", type=["csv"])
if collection_file:
    df = pd.read_csv(collection_file)
    st.write("Uploaded collection:")
    st.dataframe(df)

    card_names = df['Name'].dropna().unique()

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
    for _, row in res_df.iterrows():
        if row["Image"] != "N/A":
            st
