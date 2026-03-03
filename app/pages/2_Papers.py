import streamlit as st
import json
from typing import List, Dict

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="📄 Paper Browser",
    layout="wide"
)

st.title("📄 Paper Browser")

# --------------------------------------------------
# Load paper catalog
# --------------------------------------------------
@st.cache_data
def load_catalog() -> Dict:
    with open("papers/paper_catalog.json", "r", encoding="utf-8") as f:
        return json.load(f)

catalog = load_catalog().get("papers", [])

if not catalog:
    st.warning("No papers found in the catalog.")
    st.stop()

# --------------------------------------------------
# Unique filters
# --------------------------------------------------
titles = sorted({paper.get("title", "") for paper in catalog})
authors = sorted({", ".join(paper.get("authors", [])) for paper in catalog})
years = sorted({paper.get("year", "") for paper in catalog})
topics = sorted({topic for paper in catalog for topic in paper.get("topics", [])})

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

selected_title = st.sidebar.multiselect("Title", titles)
selected_author = st.sidebar.multiselect("Author", authors)
selected_year = st.sidebar.multiselect("Year", years)
selected_topic = st.sidebar.multiselect("Topic", topics)

# --------------------------------------------------
# Filtering logic
# --------------------------------------------------
def apply_filters(papers):
    filtered = []
    for paper in papers:
        tmatch = (not selected_title) or (paper.get("title") in selected_title)
        amatch = (not selected_author) or (", ".join(paper.get("authors", [])) in selected_author)
        ymatch = (not selected_year) or (paper.get("year") in selected_year)
        tpmatch = (not selected_topic) or bool(set(paper.get("topics", [])).intersection(set(selected_topic)))

        if tmatch and amatch and ymatch and tpmatch:
            filtered.append(paper)
    return filtered

filtered_papers = apply_filters(catalog)

# --------------------------------------------------
# Display
# --------------------------------------------------
st.markdown(f"### 📚 Showing {len(filtered_papers)} papers")

for paper in filtered_papers:

    with st.expander(f"{paper.get('title', 'Unknown Title')} ({paper.get('year', 'n.d.')})"):

        st.markdown(f"**Authors:** {', '.join(paper.get('authors', []))}")
        st.markdown(f"**Year:** {paper.get('year', 'n.d.')}")
        st.markdown(f"**Venue:** {paper.get('venue', '')}")
        st.markdown(f"**DOI:** {paper.get('doi', '')}")

        abstract = paper.get("abstract", "No abstract available.")
        st.markdown(f"**Abstract:**\n\n{abstract}")

        if paper.get("topics"):
            st.markdown(f"**Topics:** {', '.join(paper.get('topics', []))}")

        st.markdown("---")