import streamlit as st
import pandas as pd
import json
import os

# --------------------------------------------------
# Load Paper Catalog
# --------------------------------------------------
catalog_path = os.path.join("papers", "paper_catalog.json")

try:
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    papers = catalog.get("papers", [])
except Exception as e:
    st.error(f"Error reading paper catalog: {e}")
    papers = []

# --------------------------------------------------
# Build DataFrame
# --------------------------------------------------
if not papers:
    st.warning("No papers available for analytics.")
    st.stop()

df = pd.DataFrame(papers)

st.title("📊 Analytics Dashboard")

st.write("### Visibility of Collection Metadata")
st.dataframe(df)

# --------------------------------------------------
# Topics Distribution
# --------------------------------------------------
st.write("### 📈 Topic Distribution")

# If the 'topics' column doesn't exist, create it with empty lists
if "topics" not in df.columns:
    df["topics"] = [[] for _ in range(len(df))]
else:
    # Ensure every row has a list (not None or string)
    df["topics"] = df["topics"].apply(lambda x: x if isinstance(x, list) else [])

# Explode topics into rows
topics_expanded = df.explode("topics")

# Show chart only if there are any non-empty topic values
valid_topics = topics_expanded["topics"].dropna()
if not valid_topics.empty:
    st.bar_chart(valid_topics.value_counts())
else:
    st.info("No topic entries available to chart.")

# --------------------------------------------------
# Authors Distribution
# --------------------------------------------------
st.write("### 📊 Authors Distribution")

if "authors" in df.columns:
    df["authors"] = df["authors"].apply(lambda x: x if isinstance(x, list) else [])

    authors_expanded = df.explode("authors")
    valid_authors = authors_expanded["authors"].dropna()

    if not valid_authors.empty:
        st.bar_chart(valid_authors.value_counts())
    else:
        st.info("No author entries available to chart.")
else:
    st.info("No authors field available in the dataset.")

# --------------------------------------------------
# Years Distribution
# --------------------------------------------------
st.write("### 📆 Papers by Year")

if "year" in df.columns:
    valid_years = df["year"].dropna()
    st.bar_chart(valid_years.value_counts())
else:
    st.info("No year field available in the dataset.")