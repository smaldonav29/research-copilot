import streamlit as st
import json
import pandas as pd

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="📊 Analytics Dashboard",
    layout="wide"
)

st.title("📊 Analytics Dashboard")

# --------------------------------------------------
# Load catalog
# --------------------------------------------------
@st.cache_data
def load_catalog():
    with open("papers/paper_catalog.json", "r", encoding="utf-8") as f:
        return json.load(f)

catalog = load_catalog().get("papers", [])

if not catalog:
    st.warning("No papers found in the catalog.")
    st.stop()

# --------------------------------------------------
# Build DataFrame
# --------------------------------------------------
df = pd.DataFrame(catalog)

# --------------------------------------------------
# Papers by Year Chart
# --------------------------------------------------
st.header("📈 Papers by Year")

if "year" in df.columns:
    try:
        year_counts = df["year"].value_counts().sort_index()
        st.bar_chart(year_counts)
    except Exception as e:
        st.error(f"Error visualizing papers by year: {str(e)}")
else:
    st.info("No 'year' field available for papers.")

# --------------------------------------------------
# Topic Distribution Chart (Safe)
# --------------------------------------------------
st.header("🔎 Topic Distribution")

if "topics" in df.columns:
    df["topics"] = df["topics"].apply(lambda x: x if isinstance(x, list) else [])
    topics_expanded = df.explode("topics")

    if "topics" in topics_expanded.columns and not topics_expanded["topics"].isna().all():
        topic_counts = topics_expanded["topics"].value_counts()
        if not topic_counts.empty:
            st.bar_chart(topic_counts)
        else:
            st.info("No topics populated to display.")
    else:
        st.info("No valid topic entries found.")
else:
    st.info("No 'topics' field available in dataset.")

# --------------------------------------------------
# Authors Count Chart
# --------------------------------------------------
st.header("🧑‍🔬 Author Contributions")

if "authors" in df.columns:
    try:
        df["author_str"] = df["authors"].apply(lambda a: ", ".join(a) if isinstance(a, list) else str(a))
        author_counts = df["author_str"].value_counts()
        st.bar_chart(author_counts)
    except Exception as e:
        st.error(f"Error visualizing authors data: {str(e)}")
else:
    st.info("No 'authors' field available.")

# --------------------------------------------------
# Summary Metrics
# --------------------------------------------------
st.header("📐 Summary Metrics")

total_papers = len(df)

unique_authors = set()
if "authors" in df.columns:
    for authors in df["authors"]:
        if isinstance(authors, list):
            unique_authors.update(authors)

total_authors = len(unique_authors)

col1, col2 = st.columns(2)
col1.metric("📄 Total Papers", total_papers)
col2.metric("👩‍🔬 Unique Authors", total_authors)

# --------------------------------------------------
# Optional: Show Full Table
# --------------------------------------------------
st.header("📋 Full Papers Table")
try:
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error("Unable to display full table: " + str(e))