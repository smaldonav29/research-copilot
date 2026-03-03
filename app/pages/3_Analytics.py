import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# Load Paper Catalog
catalog_path = os.path.join("papers", "paper_catalog.json")
try:
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    papers = catalog.get("papers", [])
except Exception as e:
    st.error(f"Error reading paper catalog: {e}")
    papers = []

if not papers:
    st.warning("No papers available for analytics.")
    st.stop()

df = pd.DataFrame(papers)

st.title("📊 Analytics Dashboard")

# --------------------------------------------------
# KPI Cards
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Total Papers", len(df))
col2.metric("👥 Unique Authors", df.explode("authors")["authors"].nunique() if "authors" in df.columns else 0)
col3.metric("📅 Year Range", f"{int(df['year'].min())} – {int(df['year'].max())}" if "year" in df.columns else "N/A")
col4.metric("🏛️ Venues", df["venue"].nunique() if "venue" in df.columns else 0)

st.divider()

# --------------------------------------------------
# Papers by Year
# --------------------------------------------------
st.subheader("📆 Papers by Year")
if "year" in df.columns:
    year_counts = df["year"].value_counts().sort_index().reset_index()
    year_counts.columns = ["Year", "Count"]
    fig = px.bar(year_counts, x="Year", y="Count", color="Count",
                 color_continuous_scale="Blues", text="Count")
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------------------------
# Papers by Section/Venue
# --------------------------------------------------
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🏛️ Papers by Venue")
    if "venue" in df.columns:
        venue_counts = df["venue"].value_counts().reset_index()
        venue_counts.columns = ["Venue", "Count"]
        fig2 = px.pie(venue_counts, names="Venue", values="Count", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

with col_b:
    st.subheader("📂 Papers by Section")
    if "section" in df.columns:
        section_counts = df["section"].dropna().value_counts().reset_index()
        section_counts.columns = ["Section", "Count"]
        fig3 = px.bar(section_counts, x="Count", y="Section", orientation="h",
                      color="Count", color_continuous_scale="Purples")
        fig3.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --------------------------------------------------
# Topics Distribution
# --------------------------------------------------
st.subheader("🏷️ Topic Distribution")
if "topics" in df.columns:
    df["topics"] = df["topics"].apply(lambda x: x if isinstance(x, list) else [])
    topics_expanded = df.explode("topics")
    valid_topics = topics_expanded["topics"].dropna()
    if not valid_topics.empty:
        topic_counts = valid_topics.value_counts().head(20).reset_index()
        topic_counts.columns = ["Topic", "Count"]
        fig4 = px.bar(topic_counts, x="Count", y="Topic", orientation="h",
                      color="Count", color_continuous_scale="Greens")
        fig4.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No topic entries available. Add 'topics' field to your paper_catalog.json.")
else:
    st.info("No 'topics' field found in paper catalog.")

st.divider()

# --------------------------------------------------
# Authors Distribution
# --------------------------------------------------
st.subheader("👥 Top Authors")
if "authors" in df.columns:
    df["authors"] = df["authors"].apply(lambda x: x if isinstance(x, list) else [])
    authors_expanded = df.explode("authors")
    valid_authors = authors_expanded["authors"].dropna()
    if not valid_authors.empty:
        author_counts = valid_authors.value_counts().head(15).reset_index()
        author_counts.columns = ["Author", "Count"]
        fig5 = px.bar(author_counts, x="Count", y="Author", orientation="h",
                      color="Count", color_continuous_scale="Oranges")
        fig5.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig5, use_container_width=True)

st.divider()

# --------------------------------------------------
# Full Table
# --------------------------------------------------
st.subheader("📋 Full Paper Catalog")
display_cols = [c for c in ["id", "title", "authors", "year", "venue", "section"] if c in df.columns]
st.dataframe(df[display_cols], use_container_width=True)
